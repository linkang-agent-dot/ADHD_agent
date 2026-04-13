$params = '{"spreadsheetId":"1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8"}'
Write-Output "Params: $params"
$result = & "C:\Users\linkang\AppData\Roaming\npm\gws.ps1" sheets spreadsheets get --params $params
$obj = $result | ConvertFrom-Json
Write-Output "Sheets count: $($obj.sheets.Count)"
if ($obj.sheets.Count -gt 0) {
    $obj.sheets[0..4] | ForEach-Object { 
        Write-Output "  Sheet: $($_.properties.sheetId) - $($_.properties.title)" 
    }
}
