"""剧集目录加载：每集为 epNN.mp4 + epNN.srt（可选 epNN.json）。"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .media import probe_duration
from .srt import Cue, read_srt

_EP = re.compile(r"^ep(\d{2,3})\.mp4$", re.IGNORECASE)


@dataclass
class Episode:
    id: int
    video: Path
    srt: Path
    cues: list[Cue]
    duration: float
    meta: dict = field(default_factory=dict)


def load_episodes(folder: Path, *, limit: int = 0) -> list[Episode]:
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"剧集目录不存在：{folder}")
    found = []
    for p in sorted(folder.iterdir()):
        m = _EP.match(p.name)
        if m:
            found.append((int(m.group(1)), p))
    if not found:
        raise FileNotFoundError(f"目录中没有 epNN.mp4：{folder}")
    found.sort()
    if limit:
        found = found[:limit]
    eps: list[Episode] = []
    for num, video in found:
        srt = video.with_suffix(".srt")
        if not srt.exists():
            raise FileNotFoundError(f"缺少字幕：{srt}（当前阶段要求 SRT 作为转写来源）")
        cues = read_srt(srt)
        dur = probe_duration(video)
        if cues and cues[-1].end > dur + 0.5:
            raise ValueError(f"第{num}集字幕结束于 {cues[-1].end:.1f}s，超过视频时长 {dur:.1f}s")
        eps.append(Episode(num, video, srt, cues, dur))
    return eps
