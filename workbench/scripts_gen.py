"""三种模式的剪辑脚本生成（均输出 JSON，可被渲染器直接消费）。

- hook：开场钩子，总时长 10–15 秒，由高分高光片段组成（保留原声，不做 TTS）。
- highlight：高光混剪，总时长 60–90 秒，按剧情时间顺序排列（保留原声，不做 TTS）。
- narration：剧情解说，逐集生成旁白，每段含原片时间戳与配音文本（走 TTS）。
"""
from __future__ import annotations

import json
from typing import Any

from .analysis import SYSTEM
from .episodes import Episode
from .llm import DeepSeekClient
from .schema import SchemaError, check_list, check_num, check_str, require

HOOK_RANGE = (10.0, 15.0)
HIGHLIGHT_RANGE = (60.0, 90.0)
MAX_CLIP_S = 6.0      # 开场钩子单段上限，保证节奏
MIN_CLIP_S = 2.0


def _clip_from_hook(h: dict, max_len: float) -> tuple[float, float]:
    length = min(max_len, h["end"] - h["start"])
    return round(h["start"], 2), round(h["start"] + max(MIN_CLIP_S, length), 2)


def make_hook_script(analysis: dict, episodes: list[Episode]) -> dict:
    dur = {e.id: e.duration for e in episodes}
    picked: list[dict] = []
    total = 0.0
    used_eps: set[int] = set()
    # 先选不同集数的高分片段，保证多样性；不足再补同集
    for pass_same_ep in (False, True):
        for h in analysis["hooks"]:
            if total >= HOOK_RANGE[0]:
                break
            if not pass_same_ep and h["episode"] in used_eps:
                continue
            s, e = _clip_from_hook(h, MAX_CLIP_S)
            e = min(e, dur[h["episode"]])
            if e - s < MIN_CLIP_S:
                continue
            if total + (e - s) > HOOK_RANGE[1]:
                e = s + (HOOK_RANGE[1] - total)
                if e - s < MIN_CLIP_S:
                    continue
            picked.append({"episode": h["episode"], "start": round(s, 2), "end": round(e, 2), "score": h["score"], "reason": h["reason"]})
            total += e - s
            used_eps.add(h["episode"])
    require(HOOK_RANGE[0] <= total <= HOOK_RANGE[1] + 1e-6, f"开场钩子总时长 {total:.1f}s 不在 10-15 秒内，候选不足")
    picked.sort(key=lambda x: (x["episode"], x["start"]))  # 播放顺序按集数，便于观众理解
    return {"mode": "hook", "total_s": round(total, 2), "clips": picked, "audio": "original"}


def make_highlight_script(analysis: dict, episodes: list[Episode]) -> dict:
    dur = {e.id: e.duration for e in episodes}
    picked: list[dict] = []
    total = 0.0
    for h in analysis["hooks"]:
        s, e = _clip_from_hook(h, 8.0)
        e = min(e, dur[h["episode"]])
        if e - s < MIN_CLIP_S:
            continue
        if total + (e - s) > HIGHLIGHT_RANGE[1]:
            break
        picked.append({"episode": h["episode"], "start": round(s, 2), "end": round(e, 2), "score": h["score"], "reason": h["reason"]})
        total += e - s
    require(total >= HIGHLIGHT_RANGE[0], f"高光混剪总时长 {total:.1f}s 不足 60 秒，候选不足")
    picked.sort(key=lambda x: (x["episode"], x["start"]))
    return {"mode": "highlight", "total_s": round(total, 2), "clips": picked, "audio": "original"}


NARRATION_USER = (
    "请为第{ep}集写剧情解说旁白（口语化、有悬念，像短视频解说）。\n"
    "本集时长 {dur:.1f} 秒。字幕（[序号 起止秒] 台词）：\n{body}\n\n"
    "输出 JSON：{{\"segments\": [{{\"timestamp\": 秒(原片中对应的时间点), \"text\": \"旁白文字，不超过{per_seg}字\"}}]}}\n"
    "要求：segments 为 4 到 8 段，timestamp 按时间递增且在 0 到 {dur:.1f} 之间，"
    "所有 text 合计不超过 {budget} 字。只输出 JSON。"
)


def validate_narration(obj: Any, ep: Episode, budget: int) -> list[dict]:
    require(isinstance(obj, dict), "解说结果必须是对象")
    segs = check_list(obj.get("segments"), "segments")
    require(4 <= len(segs) <= 8, f"segments 数量 {len(segs)} 不在 4-8 之间")
    out, total_chars, prev_t = [], 0, -1.0
    for i, s in enumerate(segs):
        require(isinstance(s, dict), f"segments[{i}] 必须是对象")
        t = check_num(s.get("timestamp"), f"segments[{i}].timestamp", 0, ep.duration)
        require(t >= prev_t, f"segments[{i}] 时间戳未递增")
        text = check_str(s.get("text"), f"segments[{i}].text", 80)
        total_chars += len(text)
        prev_t = t
        out.append({"episode": ep.id, "timestamp": round(t, 2), "text": text})
    require(total_chars <= budget + 10, f"解说总字数 {total_chars} 超过预算 {budget}")
    return out


def make_narration_script(client: DeepSeekClient, episodes: list[Episode], *, chars_per_episode: int = 120) -> dict:
    segments: list[dict] = []
    per_seg = max(20, chars_per_episode // 4)
    for ep in episodes:
        body = "\n".join(f"[{c.index} {c.start:.1f}-{c.end:.1f}] {c.text}" for c in ep.cues)
        user = NARRATION_USER.format(ep=ep.id, dur=ep.duration, body=body, per_seg=per_seg, budget=chars_per_episode)
        last: Exception | None = None
        for attempt in range(2):
            extra = "" if attempt == 0 else f"\n上一次输出未通过校验：{last}。请修正后重新输出。"
            raw = client.chat_json(SYSTEM, user + extra, stage=f"narration_ep{ep.id:02d}", temperature=0.5, max_tokens=1200)
            try:
                segments.extend(validate_narration(raw, ep, chars_per_episode))
                break
            except SchemaError as e:
                last = e
        else:
            raise SchemaError(f"第{ep.id}集解说两次未通过校验：{last}")
    return {"mode": "narration", "chars_per_episode": chars_per_episode, "segments": segments}


def write_script(path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
