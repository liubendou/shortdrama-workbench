$q = "Reply with one word only: the three-letter English abbreviation of Monday. Output just the abbreviation."
$payload = @{ messages = @(@{ role = "user"; content = $q }); temperature = 0 }
$body = ($payload | ConvertTo-Json -Depth 5)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
try {
  $r = Invoke-RestMethod -Uri "http://127.0.0.1:8790/cloud/llm/chat" -Method Post -Body $bytes -ContentType "application/json; charset=utf-8" -TimeoutSec 150
  Write-Output "OK"
  $r | ConvertTo-Json -Depth 6
} catch {
  Write-Output ("FAIL " + $_.Exception.Message)
  if ($_.ErrorDetails) { Write-Output $_.ErrorDetails.Message }
}
