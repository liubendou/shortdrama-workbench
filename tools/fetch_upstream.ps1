$root = "C:/Users/Administrator/Documents/shortdrama-workbench/upstream"
New-Item -ItemType Directory -Force -Path $root | Out-Null
$items = @(
  @{ name="narratoai"; url="https://codeload.github.com/linyqh/NarratoAI/zip/refs/heads/main"; zip="narratoai.zip" },
  @{ name="jjyb";      url="https://codeload.github.com/jianjieyiban/JJYB_AI_VideoAutoCut/zip/refs/heads/videoautocut"; zip="jjyb.zip" }
)
foreach ($it in $items) {
  $zip = Join-Path $root $it.zip
  Write-Output ("downloading " + $it.name)
  Invoke-WebRequest -Uri $it.url -OutFile $zip -UseBasicParsing -TimeoutSec 900
  $dst = Join-Path $root ($it.name + "_tmp")
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  Expand-Archive -Path $zip -DestinationPath $dst -Force
  $inner = Get-ChildItem $dst | Select-Object -First 1
  $final = Join-Path $root $it.name
  if (Test-Path $final) { Remove-Item -Recurse -Force $final }
  Move-Item -Path $inner.FullName -Destination $final
  Remove-Item -Recurse -Force $dst
  $sum = (Get-FileHash $zip -Algorithm SHA256).Hash
  Write-Output ("OK " + $it.name + " sha256(zip)=" + $sum + " size=" + (Get-Item $zip).Length)
}
Set-Content -Path (Join-Path $root "fetch_done.txt") -Value "DONE"
Write-Output "ALL DONE"
