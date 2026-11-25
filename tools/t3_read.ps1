$s = "C:/Users/Administrator/shortdrama-studio"
Write-Output "--- schemas TTS ---"
$lines = Get-Content "$s/services/engine/schemas.py" -Encoding UTF8
$i = 0; foreach ($l in $lines) { $i++; if ($i -ge 83 -and $i -le 100) { "{0}: {1}" -f $i, $l } }
Write-Output "--- main tts route ---"
$lines = Get-Content "$s/services/engine/main.py" -Encoding UTF8
$i = 0; foreach ($l in $lines) { $i++; if ($i -ge 164 -and $i -le 185) { "{0}: {1}" -f $i, $l } }
Write-Output "--- where samples generated? ---"
Select-String -Path "$s/scripts/*.py","$s/services/engine/**/*.py","$s/apps/jjyb/backend/**/*.py" -Pattern "drawtext|gen_sample|synth_sample|make_sample|multi_demo" -ErrorAction SilentlyContinue | ForEach-Object { "{0}:{1}: {2}" -f $_.Path.Replace($s,""), $_.LineNumber, $_.Line.Trim() } | Select-Object -First 25
Write-Output "--- multi dir sample ---"
Get-ChildItem "$s/data/samples/multi","$s/data/samples/test" -ErrorAction SilentlyContinue | ForEach-Object { $_.Name + "  " + $_.Length }
Write-Output "--- edge-tts in engine venv? ---"
& "$s/services/engine/.venv/Scripts/python.exe" -c "import edge_tts,httpx; print('edge', edge_tts.__version__ if hasattr(edge_tts,'__version__') else 'ok')"
