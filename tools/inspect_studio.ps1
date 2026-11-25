$s = "C:/Users/Administrator/shortdrama-studio"
Write-Output "--- top level ---"
Get-ChildItem $s -Force | ForEach-Object { $_.Name + $(if ($_.PSIsContainer) {"/"} else {"  " + $_.Length}) }
Write-Output "--- key paths ---"
foreach ($k in @("apps/jjyb","services/engine","services/narrato","scripts/studio_batch.py","scripts/e2e_smoke.py","config/cloud.yaml","README.md","docs/architecture.md","data/samples/multi","apps/jjyb/output/jianying_drafts","data/projects/multi_batch/studio/latest.json")) {
  $t = Join-Path $s $k
  Write-Output ($k + " : " + (Test-Path $t))
}
Write-Output "--- git ---"
if (Test-Path "$s/.git") { git -C $s log --oneline -5 2>&1; git -C $s status --short 2>&1 | Select-Object -First 15 } else { Write-Output "no .git" }
Write-Output "--- size of tree (files) ---"
(Get-ChildItem $s -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
