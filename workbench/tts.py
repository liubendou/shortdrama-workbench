"""语音合成：Edge TTS（主，在线免密钥）→ Windows SAPI（离线兜底）。

- Edge TTS 通过 edge-tts 库调用 Microsoft 在线语音服务。
- SAPI 通过 PowerShell 调用 System.Speech，文本经 UTF-8 临时文件传入，避免命令行转义问题。
"""
from __future__ import annotations

import asyncio
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .media import probe_duration

_SAPI_SCRIPT = r"""
param([string]$TextFile, [string]$OutFile, [int]$Rate)
Add-Type -AssemblyName System.Speech
$text = [System.IO.File]::ReadAllText($TextFile, [System.Text.Encoding]::UTF8)
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = $Rate
$synth.SetOutputToWaveFile($OutFile)
$synth.Speak($text)
$synth.Dispose()
"""


class TtsError(RuntimeError):
    pass


@dataclass(frozen=True)
class TtsResult:
    engine: str
    path: Path
    duration_s: float


async def _edge_save(text: str, voice: str, rate: str, out: Path, timeout_s: float) -> None:
    import edge_tts  # 延迟导入，便于无网络时单测

    comm = edge_tts.Communicate(text, voice, rate=rate)
    await asyncio.wait_for(comm.save(str(out)), timeout=timeout_s)


def synth_edge(text: str, out: Path, *, voice: str, rate: str = "+0%", timeout_s: float = 60) -> TtsResult:
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(_edge_save(text, voice, rate, out, timeout_s))
    except Exception as e:  # 网络、超时、服务端拒绝都归为 Edge 失败
        raise TtsError(f"Edge TTS 失败：{type(e).__name__}: {e}") from e
    if not out.exists() or out.stat().st_size < 200:
        raise TtsError("Edge TTS 产出文件为空")
    return TtsResult("edge", out, probe_duration(out))


def synth_sapi(text: str, out: Path, *, rate: int = 0, timeout_s: float = 120) -> TtsResult:
    """Windows SAPI 离线合成为 WAV。rate 范围 -10..10。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        text_file = td_p / "text.txt"
        script = td_p / "sapi.ps1"
        text_file.write_text(text, encoding="utf-8")
        script.write_text(_SAPI_SCRIPT, encoding="utf-8")
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
            "-TextFile", str(text_file), "-OutFile", str(out.resolve()), "-Rate", str(rate),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=timeout_s)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            raise TtsError(f"SAPI 失败：{e}") from e
    if not out.exists() or out.stat().st_size < 200:
        raise TtsError("SAPI 产出文件为空")
    return TtsResult("sapi", out, probe_duration(out))


def synth(text: str, out: Path, *, voice: str, fallback: bool = True, rate: str = "+0%") -> TtsResult:
    """主引擎失败时回退 SAPI（若 fallback=True）。"""
    try:
        return synth_edge(text, out, voice=voice, rate=rate)
    except TtsError as primary_err:
        if not fallback:
            raise
        wav = out.with_suffix(".wav")
        try:
            return synth_sapi(text, wav)
        except TtsError as fb_err:
            raise TtsError(f"主引擎与兜底均失败：{primary_err}；{fb_err}") from fb_err
