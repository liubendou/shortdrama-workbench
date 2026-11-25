$s = "C:/Users/Administrator/shortdrama-studio"
$f = "$s/data/samples/drama_12ep/_tmp/E01/01.mp3"
if (Test-Path $f) { $fi = Get-Item $f; "size=" + $fi.Length; $b = [System.IO.File]::ReadAllBytes($f); "head hex=" + (($b[0..15] | ForEach-Object { $_.ToString("X2") }) -join " ") } else { "missing" }
Write-Output "--- call gateway ---"
$payload = @{ text = "test sentence one."; voice = "zh-CN-XiaoxiaoNeural"; rate = "+0%"; output_path = "$s/data/samples/drama_12ep/_tmp/diag.mp3" } | ConvertTo-Json
try { $r = Invoke-RestMethod -Uri "http://127.0.0.1:8790/cloud/tts/synthesize" -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) -ContentType "application/json; charset=utf-8" -TimeoutSec 120; $r | ConvertTo-Json } catch { "FAIL " + $_.Exception.Message }
$d = "$s/data/samples/drama_12ep/_tmp/diag.mp3"
if (Test-Path $d) { "diag size=" + (Get-Item $d).Length; $b2 = [System.IO.File]::ReadAllBytes($d); "diag head=" + (($b2[0..15] | ForEach-Object { $_.ToString("X2") }) -join " ") } else { "diag missing" }
