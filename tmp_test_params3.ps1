$params = '{"spreadsheetId":"1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($params)
Write-Output "Bytes (first 5): $($bytes[0..4])"
Write-Output "Param length: $($params.Length)"

# Try alternative quoting
$params2 = "{`"spreadsheetId`":`"1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8`"}"
$bytes2 = [System.Text.Encoding]::UTF8.GetBytes($params2)
Write-Output "Bytes2 (first 5): $($bytes2[0..4])"
