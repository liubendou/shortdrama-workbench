"""云端调用的费用记录：每次调用追加一行 JSON 到 runs/cost.jsonl。"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any


def estimate_cny(usage: dict[str, int], prices: dict[str, float]) -> float:
    """按人民币/百万 tokens 估算单次调用费用。usage 键：input_cache_hit / input_cache_miss / output。"""
    hit = usage.get("input_cache_hit", 0)
    miss = usage.get("input_cache_miss", 0)
    out = usage.get("output", 0)
    cost = (
        hit * prices.get("input_cache_hit", 0.0)
        + miss * prices.get("input_cache_miss", 0.0)
        + out * prices.get("output", 0.0)
    ) / 1_000_000
    return round(cost, 6)


def append_cost(log_path: Path, record: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"), **record}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize(log_path: Path) -> dict[str, Any]:
    total_cny = 0.0
    calls = 0
    tokens_in = 0
    tokens_out = 0
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            calls += 1
            total_cny += float(r.get("cny", 0.0))
            tokens_in += int(r.get("prompt_tokens", 0))
            tokens_out += int(r.get("completion_tokens", 0))
    return {"calls": calls, "cny": round(total_cny, 4), "prompt_tokens": tokens_in, "completion_tokens": tokens_out}
