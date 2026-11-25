$urls = @(
 "https://github.com/linyqh/NarratoAI",
 "https://codeload.github.com/linyqh/NarratoAI/zip/refs/heads/main",
 "https://gh-proxy.com/https://github.com/linyqh/NarratoAI/archive/refs/heads/main.zip",
 "https://ghfast.top/https://github.com/linyqh/NarratoAI/archive/refs/heads/main.zip",
 "https://api.github.com/repos/linyqh/NarratoAI"
)
foreach ($u in $urls) {
  try { $r = Invoke-WebRequest -Uri $u -Method Head -UseBasicParsing -TimeoutSec 20; Write-Output ("OK " + $r.StatusCode + " " + $u) }
  catch { Write-Output ("FAIL " + $u + " :: " + $_.Exception.Message) }
}
