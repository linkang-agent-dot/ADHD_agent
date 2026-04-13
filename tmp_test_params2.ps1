$params = '{"spreadsheetId":"1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8"}'
$result = & "C:\Users\linkang\AppData\Roaming\npm\gws.ps1" sheets spreadsheets get --params $params
Write-Output "Result type: $($result.GetType())"
Write-Output "Result: $result"
