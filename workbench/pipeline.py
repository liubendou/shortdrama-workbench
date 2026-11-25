"""端到端流水线：剧集目录 → 整剧分析 → 三种模式脚本 → TTS → 渲染 → 报告（含云成本与耗时）。"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .analysis import analyze_series
from .cost import summarize
from .episodes import Episode, load_episodes
from .llm import DeepSeekClient
from .media import probe_duration
from .render import concat, cut_original, cut_with_voiceover
from .scripts_gen import make_highlight_script, make_hook_script, make_narration_script, write_script
from .tts import synth

ALL_MODES = ("hook", "highlight", "narration")


def _ep_by_id(eps: list[Episode]) -> dict[int, Episode]:
    return {e.id: e for e in eps}


def render_clips(script: dict, eps: list[Episode], out_dir: Path, name: str) -> Path:
    by = _ep_by_id(eps)
    parts = []
    work = out_dir / f"_parts_{name}"
    work.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(script["clips"]):
        p = work / f"clip_{i:03d}.mp4"
        cut_original(by[c["episode"]].video, c["start"], c["end"], p)
        parts.append(p)
    final = out_dir / f"{name}.mp4"
    concat(parts, final, work)
    return final


def render_narration(script: dict, eps: list[Episode], cfg: dict, out_dir: Path) -> Path:
    by = _ep_by_id(eps)
    work = out_dir / "_parts_narration"
    (work / "tts").mkdir(parents=True, exist_ok=True)
    voice = cfg["tts"]["voice_female"]
    fallback = cfg["tts"].get("fallback") == "sapi"
    parts = []
    for i, seg in enumerate(script["segments"]):
        ep = by[seg["episode"]]
        tts = synth(seg["text"], work / "tts" / f"seg_{i:03d}.mp3", voice=voice, fallback=fallback)
        need = tts.duration_s + 0.3
        start = min(seg["timestamp"], max(0.0, ep.duration - need))
        p = work / f"seg_{i:03d}.mp4"
        cut_with_voiceover(ep.video, start, tts, p)
        parts.append(p)
        seg["tts_engine"] = tts.engine
        seg["tts_duration_s"] = round(tts.duration_s, 2)
        seg["source_start"] = round(start, 2)
    final = out_dir / "narration.mp4"
    concat(parts, final, work)
    return final


def run_pipeline(folder: Path, out_dir: Path, cfg: dict, *, modes=ALL_MODES, limit: int = 0,
                 chars_per_episode: int = 120, use_cache: bool = True) -> dict[str, Any]:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    cost_log = out_dir / "cost.jsonl"
    timings: dict[str, float] = {}

    eps = load_episodes(folder, limit=limit)
    client = DeepSeekClient(cfg["llm"], cost_log)

    s = time.time()
    analysis = analyze_series(client, eps, out_dir / "analysis", use_cache=use_cache)
    timings["analysis_s"] = round(time.time() - s, 1)

    results: dict[str, Any] = {}
    if "hook" in modes:
        s = time.time()
        sc = make_hook_script(analysis, eps)
        write_script(out_dir / "scripts" / "hook.json", sc)
        mp4 = render_clips(sc, eps, out_dir, "hook")
        results["hook"] = {"mp4": str(mp4), "planned_s": sc["total_s"], "actual_s": round(probe_duration(mp4), 2)}
        timings["hook_s"] = round(time.time() - s, 1)
    if "highlight" in modes:
        s = time.time()
        sc = make_highlight_script(analysis, eps)
        write_script(out_dir / "scripts" / "highlight.json", sc)
        mp4 = render_clips(sc, eps, out_dir, "highlight")
        results["highlight"] = {"mp4": str(mp4), "planned_s": sc["total_s"], "actual_s": round(probe_duration(mp4), 2)}
        timings["highlight_s"] = round(time.time() - s, 1)
    if "narration" in modes:
        s = time.time()
        sc = make_narration_script(client, eps, chars_per_episode=chars_per_episode)
        mp4 = render_narration(sc, eps, cfg, out_dir)
        write_script(out_dir / "scripts" / "narration.json", sc)
        planned = sum(seg.get("tts_duration_s", 0) + 0.3 for seg in sc["segments"])
        results["narration"] = {"mp4": str(mp4), "planned_s": round(planned, 2), "actual_s": round(probe_duration(mp4), 2),
                                "segments": len(sc["segments"]), "episodes_covered": len({x["episode"] for x in sc["segments"]})}
        timings["narration_s"] = round(time.time() - s, 1)

    cost = summarize(cost_log)
    total_s = round(time.time() - t0, 1)
    report = {
        "episodes": len(eps),
        "source_total_s": round(sum(e.duration for e in eps), 1),
        "modes": results,
        "timings_s": {**timings, "total_s": total_s},
        "cost": cost,
        "budget": cfg.get("budget", {}),
        "within_budget": {
            "cny": cost["cny"] <= float(cfg.get("budget", {}).get("max_cny_per_drama", 30)),
            "minutes": total_s / 60 <= float(cfg.get("budget", {}).get("max_minutes_per_drama", 30)),
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
