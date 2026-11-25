$p = "C:/Users/Administrator/Documents/shortdrama-workbench"
if (Test-Path "$p/tools/setup_done.txt") { Write-Output "SETUP_READY" } else { Write-Output "SETUP_PENDING" }
Write-Output "--- setup log tail ---"
Get-Content "$p/tools/setup_env.log" -Tail 6 -ErrorAction SilentlyContinue
Write-Output "--- python procs ---"
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, StartTime | Format-Table -HideTableHeaders
Write-Output "--- project files (excluding upstream/.venv) ---"
Get-ChildItem $p -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*\upstream\*" -and $_.FullName -notlike "*\.venv\*" } | ForEach-Object { $_.FullName.Replace($p, ".") + "  " + $_.Length }
