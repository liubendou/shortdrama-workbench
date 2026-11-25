$p = "C:/Users/Administrator/Documents/shortdrama-workbench"
Write-Output "--- where ---"
where.exe ffmpeg
where.exe ffprobe
Write-Output "--- venv versions ---"
& "$p/.venv/Scripts/python.exe" -c "import sys,importlib.metadata as m; print('python', sys.version.split()[0]); [print(q, m.version(q)) for q in ['httpx','pyyaml','fastapi','uvicorn','edge-tts','pytest','python-multipart']]"
Write-Output "--- tests (pytest) ---"
Set-Location $p
& "$p/.venv/Scripts/python.exe" -m pytest -q tests 2>&1 | Select-Object -Last 8
Write-Output "--- tail of setup log (versions) ---"
Select-String -Path "$p/tools/setup_env.log" -Pattern "^(httpx|pyyaml|fastapi|uvicorn|edge-tts|pytest|python) " | ForEach-Object { $_.Line }
