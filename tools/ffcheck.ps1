Write-Output "--- filters ---"
ffmpeg -hide_banner -filters 2>$null | Select-String -Pattern " gradients | drawtext | adelay | amix " | ForEach-Object { $_.Line.Trim() }
Write-Output "--- encoders ---"
ffmpeg -hide_banner -encoders 2>$null | Select-String -Pattern " libx264 | aac " | ForEach-Object { $_.Line.Trim() }
Write-Output "--- fonts ---"
Test-Path "C:/Windows/Fonts/msyh.ttc"
Test-Path "C:/Windows/Fonts/simhei.ttf"
