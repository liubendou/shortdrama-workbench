Get-Content C:/Users/Administrator/shortdrama-studio/services/engine/cloud/llm.py -Encoding UTF8
Write-Output "--- cost.py? ---"
Test-Path C:/Users/Administrator/shortdrama-studio/services/engine/analysis/cost.py
Get-ChildItem C:/Users/Administrator/shortdrama-studio/services/engine/analysis | ForEach-Object { $_.Name + "  " + $_.Length }
Write-Output "--- cloud.yaml budget/price section ---"
Select-String -Path C:/Users/Administrator/shortdrama-studio/config/cloud.yaml -Pattern "price|cny|cache|output|miss|hit|budget" | ForEach-Object { $_.Line }
