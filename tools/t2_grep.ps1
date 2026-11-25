$s = "C:/Users/Administrator/shortdrama-studio"
Set-Location $s
Select-String -Path "services/engine/*.py","services/engine/cloud/*.py" -Pattern "@app\.|router\.|def chat|cost|cny|ledger|jsonl|model" | ForEach-Object { "{0}:{1}: {2}" -f $_.Path.Replace($s,""), $_.LineNumber, $_.Line.Trim() } | Select-Object -First 90
Write-Output "--- cloud dir ---"
Get-ChildItem services/engine/cloud | ForEach-Object { $_.Name + "  " + $_.Length }
Write-Output "--- runs/ or logs dirs ---"
Test-Path runs; Test-Path data/runs; Test-Path data/cost
