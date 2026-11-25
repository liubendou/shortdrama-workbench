"""SRT 字幕读写与校验（标准库实现，无第三方依赖）。"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_TIME = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})$")
_ARROW = re.compile(r"\s*-->\s*")


@dataclass(frozen=True)
class Cue:
    index: int
    start: float  # 秒
    end: float    # 秒
    text: str


class SrtError(ValueError):
    pass


def parse_time(s: str) -> float:
    m = _TIME.match(s.strip())
    if not m:
        raise SrtError(f"时间格式错误：{s!r}")
    h, mi, se, ms = (int(x) for x in m.groups())
    return h * 3600 + mi * 60 + se + ms / 1000.0


def format_time(sec: float) -> str:
    if sec < 0:
        raise SrtError("时间不能为负")
    total_ms = int(round(sec * 1000))
    h, rem = divmod(total_ms, 3_600_000)
    mi, rem = divmod(rem, 60_000)
    se, ms = divmod(rem, 1000)
    return f"{h:02d}:{mi:02d}:{se:02d},{ms:03d}"


def parse_srt(text: str) -> list[Cue]:
    """解析 SRT 文本。忽略 BOM，兼容 CRLF；时间非法或 end<=start 时报错。"""
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    cues: list[Cue] = []
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 2:
            raise SrtError(f"字幕块不完整：{block[:60]!r}")
        if lines[0].strip().isdigit():
            idx = int(lines[0].strip())
            time_line = lines[1]
            body = lines[2:]
        else:
            idx = len(cues) + 1
            time_line = lines[0]
            body = lines[1:]
        parts = _ARROW.split(time_line.strip())
        if len(parts) != 2:
            raise SrtError(f"时间行错误：{time_line!r}")
        start, end = parse_time(parts[0]), parse_time(parts[1])
        if end <= start:
            raise SrtError(f"字幕 {idx} 结束时间不晚于开始时间")
        cues.append(Cue(idx, start, end, "\n".join(x.strip() for x in body).strip()))
    return cues


def read_srt(path: Path) -> list[Cue]:
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "gb18030"):
        try:
            return parse_srt(raw.decode(enc))
        except UnicodeDecodeError:
            continue
        except SrtError:
            raise
    raise SrtError(f"无法解码字幕文件：{path}")


def dump_srt(cues: list[Cue]) -> str:
    out = []
    for i, c in enumerate(cues, start=1):
        out.append(f"{i}\n{format_time(c.start)} --> {format_time(c.end)}\n{c.text}\n")
    return "\n".join(out)


def validate_non_overlapping(cues: list[Cue]) -> None:
    prev_end = -1.0
    for c in cues:
        if c.start < prev_end - 1e-6:
            raise SrtError(f"字幕 {c.index} 与上一条重叠（{c.start:.3f} < {prev_end:.3f}）")
        prev_end = c.end
