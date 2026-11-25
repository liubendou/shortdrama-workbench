$s = "C:/Users/Administrator/shortdrama-studio"
foreach ($port in 8790,8791,5000) {
  try { $r = Invoke-WebRequest -Uri ("http://127.0.0.1:" + $port + "/") -UseBasicParsing -TimeoutSec 8; Write-Output ("port " + $port + " HTTP " + $r.StatusCode) }
  catch { Write-Output ("port " + $port + " FAIL " + $_.Exception.Message) }
}
foreach ($u in @("http://127.0.0.1:8790/health","http://127.0.0.1:8791/health")) {
  try { $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 8; Write-Output ($u + " -> " + $r.StatusCode + " " + $r.Content.Substring(0,[Math]::Min(200,$r.Content.Length))) }
  catch { Write-Output ($u + " FAIL " + $_.Exception.Message) }
}
Write-Output "--- start log tail ---"
Get-Content "$s/tools/start_backend.log" -Tail 15 -ErrorAction SilentlyContinue
