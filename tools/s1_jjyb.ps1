$s = "C:/Users/Administrator/shortdrama-studio"
Select-String -Path "$s/scripts/start.ps1" -Pattern "jjyb|5000|frontend|socketio|Start-Process|python" | ForEach-Object { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim() }
