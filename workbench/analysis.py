"""整剧分析：逐集摘要 + 高光/悬念候选 + 全剧汇总。所有输出经 schema 校验，时间戳必须落在对应集时长内。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .episodes import Episode
from .llm import DeepSeekClient
from .schema import SchemaError, check_list, check_num, check_str, require

SYSTEM = (
    "你是短剧剪辑策划。只输出一个 JSON 对象，不要输出任何解释文字或 Markdown。"
    "时间单位统一为秒（小数），必须落在给定剧集时长之内。"
)


def episode_user_prompt(ep: Episode) -> str:
    lines = [f"[{c.index} {c.start:.1f}-{c.end:.1f}] {c.text}" for c in ep.cues]
    body = "\n".join(lines)
    schema = (
        '{"episode": 集数整数, "summary": "本集剧情概括，100字以内", '
        '"characters": ["出场人物"], "key_events": ["关键事件，每条不超过40字"], '
        '"hooks": [{"start": 秒, "end": 秒, "score": 1到10的整数, "reason": "为什么是高光或悬念，40字以内"}]}'
    )
    return (
        f"剧集：第{ep.id}集，时长 {ep.duration:.1f} 秒。\n"
        f"字幕（格式：[序号 起止秒] 台词）：\n{body}\n\n"
        f"请输出 JSON，结构为：{schema}\n"
        "hooks 给出 3 到 5 个最适合剪进高光混剪或开场钩子的片段，每段长度 3 到 12 秒，"
        "起止时间取自字幕时间轴。"
    )


def validate_episode_analysis(obj: Any, ep: Episode) -> dict:
    require(isinstance(obj, dict), "逐集结果必须是对象")
    n = int(check_num(obj.get("episode"), "episode", 1, 999))
    require(n == ep.id, f"episode 字段 {n} 与实际集数 {ep.id} 不一致")
    summary = check_str(obj.get("summary"), "summary", max_len=200)
    chars = [check_str(x, "characters[]", 20) for x in check_list(obj.get("characters", []), "characters")]
    events = [check_str(x, "key_events[]", 80) for x in check_list(obj.get("key_events", []), "key_events")]
    hooks_out = []
    for i, h in enumerate(check_list(obj.get("hooks"), "hooks")):
        require(isinstance(h, dict), f"hooks[{i}] 必须是对象")
        s = check_num(h.get("start"), f"hooks[{i}].start", 0, ep.duration)
        e = check_num(h.get("end"), f"hooks[{i}].end", 0, ep.duration)
        require(e > s, f"hooks[{i}] end<=start")
        require(2.0 <= e - s <= 15.0, f"hooks[{i}] 时长 {e - s:.1f}s 不在 2-15 秒内")
        score = int(check_num(h.get("score"), f"hooks[{i}].score", 1, 10))
        reason = check_str(h.get("reason"), f"hooks[{i}].reason", 80)
        hooks_out.append({"episode": ep.id, "start": round(s, 2), "end": round(e, 2), "score": score, "reason": reason})
    require(len(hooks_out) >= 1, "hooks 至少 1 条")
    return {"episode": ep.id, "summary": summary, "characters": chars, "key_events": events, "hooks": hooks_out}


def analyze_series(client: DeepSeekClient, episodes: list[Episode], out_dir: Path, *, use_cache: bool = True) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    per_ep: list[dict] = []
    for ep in episodes:
        cache = out_dir / f"ep{ep.id:02d}.json"
        if use_cache and cache.exists():
            per_ep.append(json.loads(cache.read_text(encoding="utf-8")))
            continue
        last_err: Exception | None = None
        for attempt in range(2):  # 结构错误时重试一次（附带错误原因）
            extra = "" if attempt == 0 else f"\n上一次输出未通过校验：{last_err}。请严格按结构修正后重新输出。"
            raw = client.chat_json(SYSTEM, episode_user_prompt(ep) + extra, stage=f"analysis_ep{ep.id:02d}", temperature=0.2, max_tokens=2000)
            try:
                item = validate_episode_analysis(raw, ep)
                break
            except SchemaError as e:
                last_err = e
        else:
            raise SchemaError(f"第{ep.id}集分析两次都未通过校验：{last_err}")
        cache.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        per_ep.append(item)

    # 全剧汇总（只用逐集摘要与候选，避免超长输入）
    brief = [
        {"episode": x["episode"], "summary": x["summary"], "characters": x["characters"], "events": x["key_events"][:4]}
        for x in per_ep
    ]
    user = (
        "下面是一部短剧各集的摘要。请输出 JSON："
        '{"series_summary": "全剧概括，200字以内", "main_characters": ["角色"], '
        '"arc": ["主线转折，按时间顺序，每条不超过40字"]}\n'
        + json.dumps(brief, ensure_ascii=False)
    )
    series_cache = out_dir / "series.json"
    if use_cache and series_cache.exists():
        series = json.loads(series_cache.read_text(encoding="utf-8"))
    else:
        raw = client.chat_json(SYSTEM, user, stage="analysis_series", temperature=0.2, max_tokens=1500)
        series = {
            "series_summary": check_str(raw.get("series_summary"), "series_summary", 300),
            "main_characters": [check_str(x, "main_characters[]", 20) for x in check_list(raw.get("main_characters", []), "main_characters")],
            "arc": [check_str(x, "arc[]", 80) for x in check_list(raw.get("arc", []), "arc")],
        }
        series_cache.write_text(json.dumps(series, ensure_ascii=False, indent=2), encoding="utf-8")

    hooks = [h for x in per_ep for h in x["hooks"]]
    result = {"series": series, "episodes": per_ep, "hooks": sorted(hooks, key=lambda h: (-h["score"], h["episode"], h["start"]))}
    (out_dir / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
