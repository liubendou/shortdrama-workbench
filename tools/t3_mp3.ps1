$b = "C:/Users/Administrator/shortdrama-studio/tools/ffmpeg/bin/ffmpeg.exe"
$dir = "C:/Users/Administrator/shortdrama-studio/data/samples/drama_12ep/_tmp/E01"
Get-ChildItem $dir -Filter *.mp3 | Sort-Object Name | ForEach-Object {
  $f = $_.FullName
  $bytes = [System.IO.File]::ReadAllBytes($f)
  $head = (($bytes[0..7] | ForEach-Object { $_.ToString("X2") }) -join " ")
  $err = & $b -hide_banner -v error -i $f -f null - 2>&1 | Select-Object -First 2
  $errText = ($err | ForEach-Object { "$_" }) -join " | "
  $d = & $b -hide_banner -i $f 2>&1 | Select-String "Duration" | ForEach-Object { $_.Line.Trim() }
  "{0} size={1} head={2} dur=[{3}] decode_err=[{4}]" -f $_.Name, $_.Length, $head, $d, $errText
}
