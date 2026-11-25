"""生成合成测试样片：12 集 mp4 + SRT + 剧本 JSON。

流程：Edge TTS 逐句合成 → 计算时间轴（句间留白）→ ffmpeg 渐变背景 + 字幕 + 混音 → 输出。
用法：python scripts/gen_samples.py [--out data/samples/drama_demo] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.drama_demo_script import EPISODES, TITLE, VOICES  # noqa: E402
from workbench.media import probe_duration, run_ffmpeg  # noqa: E402
from workbench.srt import Cue, dump_srt  # noqa: E402
from workbench.tts import synth  # noqa: E402

GAP_S = 0.7      # 句间留白
TAIL_S = 1.2     # 每集结尾留白
FONT = "C\\:/Windows/Fonts/msyh.ttc"


def build_episode(ep_no: int, lines, out_dir: Path) -> dict:
    work = out_dir / f"_work_ep{ep_no:02d}"
    work.mkdir(parents=True, exist_ok=True)
    # 1) 逐句合成
    clips = []
    for i, (speaker, text) in enumerate(lines):
        mp3 = work / f"line_{i:02d}.mp3"
        res = synth(text, mp3, voice=VOICES[speaker], fallback=True)
        clips.append({"speaker": speaker, "text": text, "path": res.path, "dur": res.duration_s, "engine": res.engine})
    # 2) 时间轴
    t = 0.0
    timeline = []
    for c in clips:
        start = t
        end = t + c["dur"]
        timeline.append({**c, "start": round(start, 3), "end": round(end, 3)})
        t = end + GAP_S
    total = t - GAP_S + TAIL_S
    # 3) 音频：adelay 叠加
    inputs, parts, labels = [], [], []
    for i, seg in enumerate(timeline):
        inputs += ["-i", str(seg["path"].resolve())]
        ms = int(seg["start"] * 1000)
        parts.append(f"[{i}:a]aformat=sample_rates=24000:channel_layouts=mono,adelay={ms}|{ms},volume=1.6[a{i}]")
        labels.append(f"[a{i}]")
    audio_graph = ";".join(parts) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[aout]"
    wav = work / "mix.wav"
    run_ffmpeg([*inputs, "-filter_complex", audio_graph, "-map", "[aout]", "-t", f"{total:.3f}", "-ar", "24000", "-ac", "1", str(wav)])
    # 4) 字幕文本文件（drawtext 用 textfile，避免转义问题）
    filters = []
    for i, seg in enumerate(timeline):
        tf = f"sub_{i:02d}.txt"
        (work / tf).write_text(f"【{seg['speaker']}】{seg['text']}", encoding="utf-8")
        filters.append(
            f"drawtext=fontfile='{FONT}':textfile={tf}:fontcolor=white:fontsize=20:borderw=2:bordercolor=black"
            f":x=(w-text_w)/2:y=h-62:enable='between(t,{seg['start']:.3f},{seg['end']:.3f})'"
        )
    title_txt = f"{TITLE} 第{ep_no}集（合成测试样片）"
    (work / "title.txt").write_text(title_txt, encoding="utf-8")
    filters.insert(0, f"drawtext=fontfile='{FONT}':textfile=title.txt:fontcolor=0xdddddd:fontsize=16:x=16:y=12")
    mp4 = out_dir / f"ep{ep_no:02d}.mp4"
    vf = ",".join(filters)
    run_ffmpeg(
        [
            "-f", "lavfi", "-i", f"gradients=s=640x360:c0=0x2b1d3a:c1=0x0f3d4f:speed=0.01:rate=25:duration={total:.3f}",
            "-i", str(wav),
            "-vf", vf,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-t", f"{total:.3f}",
            "-movflags", "+faststart", str(mp4),
        ],
        timeout=900,
    )
    real = probe_duration(mp4)
    cues = [Cue(i + 1, s["start"], s["end"], f"【{s['speaker']}】{s['text']}") for i, s in enumerate(timeline)]
    (out_dir / f"ep{ep_no:02d}.srt").write_text(dump_srt(cues), encoding="utf-8")
    script = {
        "episode": ep_no,
        "title": f"{TITLE} 第{ep_no}集",
        "synthetic": True,
        "duration_s": round(real, 3),
        "lines": [{"speaker": s["speaker"], "text": s["text"], "start": s["start"], "end": s["end"], "tts_engine": s["engine"]} for s in timeline],
    }
    (out_dir / f"ep{ep_no:02d}.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"episode": ep_no, "mp4": str(mp4), "duration_s": round(real, 2), "lines": len(lines)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/samples/drama_demo")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    eps = EPISODES[: args.limit] if args.limit else EPISODES
    report = []
    for n, lines in enumerate(eps, start=1):
        info = build_episode(n, lines, out_dir)
        print(json.dumps(info, ensure_ascii=False), flush=True)
        report.append(info)
    (out_dir / "manifest.json").write_text(
        json.dumps({"title": TITLE, "synthetic": True, "episodes": report}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("OK", len(report), "episodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
