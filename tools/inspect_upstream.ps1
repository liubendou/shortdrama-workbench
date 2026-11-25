$root = "C:/Users/Administrator/Documents/shortdrama-workbench/upstream"
foreach ($n in @("narratoai","jjyb")) {
  $d = Join-Path $root $n
  Write-Output ("==== " + $n + " ====")
  $files = Get-ChildItem $d -Recurse -File -ErrorAction SilentlyContinue
  $size = ($files | Measure-Object -Property Length -Sum).Sum
  Write-Output ("files=" + $files.Count + " bytes=" + $size)
  Get-ChildItem $d -Force | Select-Object -ExpandProperty Name | ForEach-Object { Write-Output ("  top: " + $_) }
  foreach ($lic in @("LICENSE","LICENSE.md","LICENSE.txt","license.md")) {
    $p = Join-Path $d $lic
    if (Test-Path $p) { Write-Output ("--- " + $lic + " (first 12 lines) ---"); Get-Content $p -TotalCount 12 }
  }
  $req = Get-ChildItem $d -Recurse -File -Filter "requirements*.txt" -ErrorAction SilentlyContinue | Select-Object -First 3
  foreach ($r in $req) { Write-Output ("--- " + $r.FullName.Replace($d,"") + " ---"); Get-Content $r.FullName -TotalCount 40 }
}
