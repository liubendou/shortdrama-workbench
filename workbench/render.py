"""渲染：按脚本切片、配音叠加、拼接。所有中间片段统一编码参数，保证 concat 无需重编码。"""
from __future__ import annotations

from pathlib import Path

from .media import probe_duration, run_ffmpeg
from .tts import TtsResult

ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p", "-r", "25",
       "-s", "640x360", "-c:a", "aac", "-b:a", "96k", "-ar", "24000", "-ac", "1"]


def cut_original(video: Path, start: float, end: float, out: Path) -> Path:
    """切原片（保留原声）。"""
    dur = end - start
    run_ffmpeg(["-ss", f"{start:.3f}", "-i", str(video), "-t", f"{dur:.3f}",
                "-map", "0:v", "-map", "0:a", *ENC, str(out)])
    return out


def cut_with_voiceover(video: Path, start: float, voice: TtsResult, out: Path,
                       *, bg_volume: float = 0.12, pad_s: float = 0.3) -> Path:
    """切原片并用配音替换（原声压低到 bg_volume）。片段时长 = 配音时长 + pad。"""
    dur = voice.duration_s + pad_s
    run_ffmpeg([
        "-ss", f"{start:.3f}", "-i", str(video), "-i", str(voice.path),
        "-filter_complex",
        f"[0:a]volume={bg_volume}[bg];[1:a]volume=1.4,apad[nar];"
        f"[bg][nar]amix=inputs=2:duration=longest:normalize=0[a]",
        "-map", "0:v", "-map", "[a]", "-t", f"{dur:.3f}", *ENC, str(out),
    ])
    return out


def concat(parts: list[Path], out: Path, workdir: Path) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    lst = workdir / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)])
    return out


def clip_duration(path: Path) -> float:
    return probe_duration(path)
