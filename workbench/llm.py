"""DeepSeek（OpenAI 兼容接口）客户端：JSON 输出、重试、费用记录。

密钥只从环境变量读取（默认 DEEPSEEK_API_KEY），不写入任何文件、不打印。
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

from .cost import append_cost, estimate_cny


class LLMError(RuntimeError):
    """云端模型调用失败（网络、鉴权、配额或输出无法解析）。"""


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_json_text(text: str) -> Any:
    """解析模型返回的 JSON；容忍 ```json 代码块包裹。"""
    cleaned = _FENCE.sub("", text.strip()).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        snippet = cleaned[:300].replace("\n", " ")
        raise LLMError(f"模型输出不是合法 JSON：{e}; 片段={snippet!r}") from e


class DeepSeekClient:
    def __init__(
        self,
        llm_cfg: dict[str, Any],
        cost_log: Path,
        *,
        http: httpx.Client | None = None,
        sleep=time.sleep,
    ) -> None:
        env_name = llm_cfg.get("api_key_env", "DEEPSEEK_API_KEY")
        self._api_key = os.environ.get(env_name, "")
        if not self._api_key:
            raise LLMError(f"环境变量 {env_name} 未设置，无法调用云端模型")
        self.base_url = str(llm_cfg.get("base_url", "https://api.deepseek.com")).rstrip("/")
        self.model = str(llm_cfg.get("model", "deepseek-chat"))
        self.timeout_s = float(llm_cfg.get("timeout_s", 180))
        self.max_retries = int(llm_cfg.get("max_retries", 3))
        self.prices: dict[str, float] = dict(llm_cfg.get("price_cny_per_million", {}))
        self.cost_log = Path(cost_log)
        self._http = http or httpx.Client(timeout=self.timeout_s)
        self._sleep = sleep

    def chat_json(
        self,
        system: str,
        user: str,
        *,
        stage: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Any:
        """发送请求并返回解析后的 JSON 对象。失败抛出 LLMError。"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        url = f"{self.base_url}/chat/completions"
        last_err: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._http.post(url, json=payload, headers=headers)
            except httpx.HTTPError as e:
                last_err = e
            else:
                if resp.status_code == 200:
                    body = resp.json()
                    content = body["choices"][0]["message"]["content"]
                    self._record_cost(stage, body.get("usage", {}))
                    return parse_json_text(content)
                if resp.status_code in (401, 403):
                    raise LLMError(f"鉴权失败（HTTP {resp.status_code}），请检查 DEEPSEEK_API_KEY")
                if resp.status_code == 402:
                    raise LLMError("账户余额不足（HTTP 402）")
                last_err = LLMError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            if attempt < self.max_retries:
                self._sleep(2 ** attempt)
        raise LLMError(f"云端调用在 {self.max_retries} 次重试后仍失败：{last_err}")

    def _record_cost(self, stage: str, usage: dict[str, Any]) -> None:
        hit = int(usage.get("prompt_cache_hit_tokens", 0))
        miss = int(usage.get("prompt_cache_miss_tokens", usage.get("prompt_tokens", 0) - hit))
        out = int(usage.get("completion_tokens", 0))
        counts = {"input_cache_hit": hit, "input_cache_miss": miss, "output": out}
        cny = estimate_cny(counts, self.prices)
        append_cost(
            self.cost_log,
            {
                "stage": stage,
                "model": self.model,
                "prompt_tokens": hit + miss,
                "completion_tokens": out,
                "cny": cny,
            },
        )
