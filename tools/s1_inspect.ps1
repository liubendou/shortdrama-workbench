$s = "C:/Users/Administrator/shortdrama-studio"
Set-Location $s
Write-Output "--- scripts ---"
Get-ChildItem scripts | ForEach-Object { $_.Name }
Write-Output "--- services/engine ---"
Get-ChildItem services/engine -Force | ForEach-Object { $_.Name }
Write-Output "--- services/narrato ---"
Get-ChildItem services/narrato -Force | ForEach-Object { $_.Name }
Write-Output "--- venvs ---"
Test-Path apps/jjyb/.venv/Scripts/python.exe
Test-Path services/engine/.venv/Scripts/python.exe
Test-Path services/narrato/.venv/Scripts/python.exe
Write-Output "--- env files (presence only) ---"
Test-Path services/engine/.env
Test-Path services/engine/.env.example
Write-Output "--- DEEPSEEK_API_KEY set in env (bool) ---"
[bool]$env:DEEPSEEK_API_KEY
Write-Output "--- data samples ---"
Get-ChildItem data/samples -Force | ForEach-Object { $_.Name }
Get-ChildItem data/samples/multi -Force -ErrorAction SilentlyContinue | ForEach-Object { $_.Name + "  " + $_.Length }
Write-Output "--- config/cloud.yaml head ---"
Get-Content config/cloud.yaml -Encoding UTF8 -TotalCount 60
