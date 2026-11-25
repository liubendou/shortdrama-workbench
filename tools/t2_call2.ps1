$q = "Reply with one word only: the three-letter English abbreviation of Tuesday. Output just the abbreviation."
$payload = @{ messages = @(@{ role = "user"; content = $q }); temperature = 0 }
$body = ($payload | ConvertTo-Json -Depth 5)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
try {
  $r = Invoke-RestMethod -Uri "http://127.0.0.1:8790/cloud/llm/chat" -Method Post -Body $bytes -ContentType "application/json; charset=utf-8" -TimeoutSec 150
  Write-Output "OK"
  $r | ConvertTo-Json -Depth 6
} catch {
  Write-Output ("FAIL " + $_.Exception.Message)
}
Write-Output "--- ledger (last 3 lines) ---"
Get-Content "C:/Users/Administrator/shortdrama-studio/runs/cost.jsonl" -Tail 3 -ErrorAction SilentlyContinue
Write-Output "--- health ---"
try { (Invoke-WebRequest -Uri "http://127.0.0.1:8790/health" -UseBasicParsing -TimeoutSec 8).StatusCode } catch { "health FAIL" }
try { (Invoke-WebRequest -Uri "http://127.0.0.1:8791/health" -UseBasicParsing -TimeoutSec 8).StatusCode } catch { "narrato FAIL" }
