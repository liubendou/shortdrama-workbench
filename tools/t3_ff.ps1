$b = "C:/Users/Administrator/shortdrama-studio/tools/ffmpeg/bin"
Test-Path "$b/ffprobe.exe"; Test-Path "$b/ffmpeg.exe"
& "$b/ffprobe.exe" -version 2>&1 | Select-Object -First 1
$f = "C:/Users/Administrator/shortdrama-studio/data/samples/drama_12ep/_tmp/diag.mp3"
Write-Output "--- ffprobe duration on diag.mp3 ---"
& "$b/ffprobe.exe" -v error -show_entries format=duration -of csv=p=0 $f 2>&1
Write-Output "exit=$LASTEXITCODE"
Write-Output "--- ffprobe on 01.mp3 (E01) ---"
& "$b/ffprobe.exe" -v error -show_entries format=duration -of csv=p=0 "C:/Users/Administrator/shortdrama-studio/data/samples/drama_12ep/_tmp/E01/01.mp3" 2>&1
Write-Output "exit=$LASTEXITCODE"
Write-Output "--- ffmpeg decode check on 01.mp3 ---"
& "$b/ffmpeg.exe" -hide_banner -v error -i "C:/Users/Administrator/shortdrama-studio/data/samples/drama_12ep/_tmp/E01/01.mp3" -f null - 2>&1 | Select-Object -First 5
Write-Output "exit=$LASTEXITCODE"
