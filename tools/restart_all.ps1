$s = "C:/Users/Administrator/shortdrama-studio"
Set-Location $s
& powershell -NoProfile -ExecutionPolicy Bypass -File scripts/stop.ps1 *> "$s/tools/restart_stop.log"
Start-Sleep -Seconds 3
& powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start.ps1 -NoUi *> "$s/tools/start_backend.log"
Write-Output ("start exit " + $LASTEXITCODE)
