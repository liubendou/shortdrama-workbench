try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing -TimeoutSec 10; Write-Output ("jjyb HTTP " + $r.StatusCode) } catch { Write-Output ("jjyb FAIL " + $_.Exception.Message) }
try { $r2 = Invoke-WebRequest -Uri "http://127.0.0.1:5000/studio" -UseBasicParsing -TimeoutSec 10; Write-Output ("studio HTTP " + $r2.StatusCode) } catch { Write-Output ("studio FAIL " + $_.Exception.Message) }
Write-Output "--- jjyb log tail ---"
Get-Content "C:/Users/Administrator/shortdrama-studio/tools/jjyb_web.log" -Tail 8 -ErrorAction SilentlyContinue
