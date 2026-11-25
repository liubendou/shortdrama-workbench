"""输出 JSON 的轻量校验（不依赖 jsonschema）。校验失败抛 SchemaError，并给出具体字段。"""
from __future__ import annotations

from typing import Any


class SchemaError(ValueError):
    pass


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaError(msg)


def check_num(v: Any, name: str, lo: float | None = None, hi: float | None = None) -> float:
    require(isinstance(v, (int, float)) and not isinstance(v, bool), f"{name} 必须是数字")
    f = float(v)
    if lo is not None:
        require(f >= lo, f"{name}={f} 小于下限 {lo}")
    if hi is not None:
        require(f <= hi, f"{name}={f} 大于上限 {hi}")
    return f


def check_str(v: Any, name: str, max_len: int | None = None) -> str:
    require(isinstance(v, str) and v.strip() != "", f"{name} 必须是非空字符串")
    if max_len is not None:
        require(len(v) <= max_len, f"{name} 超过 {max_len} 字（当前 {len(v)}）")
    return v.strip()


def check_list(v: Any, name: str) -> list:
    require(isinstance(v, list), f"{name} 必须是数组")
    return v
