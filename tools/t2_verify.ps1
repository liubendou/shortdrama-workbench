$s = "C:/Users/Administrator/shortdrama-studio"
Write-Output "--- pricing.yaml ---"
Get-Content "$s/config/pricing.yaml" -Encoding UTF8 -TotalCount 3
Write-Output "--- ledger.py first lines ---"
Get-Content "$s/services/engine/cloud/ledger.py" -Encoding UTF8 -TotalCount 4
Write-Output "--- stray files under repo root (new in last hour) ---"
Get-ChildItem $s -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-2) } | ForEach-Object { $_.FullName }
