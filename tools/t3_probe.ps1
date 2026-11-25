$s = "C:/Users/Administrator/shortdrama-studio"
$out = "$s/data/samples/drama_12ep/_tmp/probe04.mp3"
$text = [string]([char]0x4F60) + [string]([char]0x8FD8)
$payload = @{ text = "probe sentence for synthesis check."; voice = "zh-CN-YunhaoNeural"; rate = "+0%"; output_path = $out } | ConvertTo-Json
try { $r = Invoke-RestMethod -Uri "http://127.0.0.1:8790/cloud/tts/synthesize" -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) -ContentType "application/json; charset=utf-8" -TimeoutSec 150; "resp path=" + $r.path; "resp bytes=" + $r.bytes; "resp voice=" + $r.voice } catch { "FAIL " + $_.Exception.Message }
Start-Sleep -Seconds 2
if (Test-Path $out) { "file size=" + (Get-Item $out).Length } else { "file missing at output_path" }
if ($r -and $r.path -and (Test-Path $r.path)) { "resp path size=" + (Get-Item $r.path).Length } elseif ($r) { "resp path not found: " + $r.path }
Write-Output "--- E01 folder listing ---"
Get-ChildItem "$s/data/samples/drama_12ep/_tmp/E01" -ErrorAction SilentlyContinue | ForEach-Object { $_.Name + " " + $_.Length }
