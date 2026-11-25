"""ffprobe / ffmpeg 封装（需要系统 PATH 中有 ffmpeg 与 ffprobe）。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass


def _run(cmd: list[str], timeout: float = 600) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise MediaError(f"命令超时：{' '.join(cmd[:3])}...") from e


def probe_duration(path: Path) -> float:
    """返回媒体时长（秒）。"""
    r = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)], timeout=60)
    if r.returncode != 0:
        raise MediaError(f"ffprobe 失败：{r.stderr[:300]}")
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise MediaError(f"无法读取时长：{path}") from e


def probe_streams(path: Path) -> dict:
    r = _run(["ffprobe", "-v", "error", "-show_entries", "stream=index,codec_type,codec_name,width,height,duration", "-of", "json", str(path)], timeout=60)
    if r.returncode != 0:
        raise MediaError(f"ffprobe 失败：{r.stderr[:300]}")
    return json.loads(r.stdout)


def run_ffmpeg(args: list[str], timeout: float = 900) -> None:
    r = _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], timeout=timeout)
    if r.returncode != 0:
        raise MediaError(f"ffmpeg 失败：{r.stderr[-500:]}")
