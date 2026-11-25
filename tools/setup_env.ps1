$ErrorActionPreference = "Continue"
$P = "C:/Users/Administrator/Documents/shortdrama-workbench"
Set-Location $P
Remove-Item -ErrorAction SilentlyContinue "tools/setup_done.txt"
if (-not (Test-Path ".venv/Scripts/python.exe")) { python -m venv .venv }
$idx = "https://pypi.tuna.tsinghua.edu.cn/simple"
& .venv/Scripts/python.exe -m pip install --upgrade pip -i $idx --retries 10 --timeout 60 --quiet
& .venv/Scripts/python.exe -m pip install -r requirements.txt -i $idx --retries 10 --timeout 60 --progress-bar off
if ($LASTEXITCODE -ne 0) {
  Write-Output "MIRROR FAILED, trying official index"
  & .venv/Scripts/python.exe -m pip install -r requirements.txt --retries 10 --timeout 60 --progress-bar off
}
Write-Output "=== versions ==="
& .venv/Scripts/python.exe -c "import sys,importlib.metadata as m; print('python', sys.version.split()[0]); [print(p, m.version(p)) for p in ['httpx','pyyaml','fastapi','uvicorn','edge-tts','pytest']]"
Write-Output "=== ffmpeg ==="
(ffmpeg -version | Select-Object -First 1)
(ffprobe -version | Select-Object -First 1)
Set-Content -Path "tools/setup_done.txt" -Value "DONE"
Write-Output "SETUP DONE"
