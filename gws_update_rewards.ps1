$ErrorActionPreference = "Stop"

$SpreadsheetId = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
$BodyPath = "C:\ADHD_agent\batch_update_2115_rewards_easter.json"

$body = Get-Content -Raw -Encoding UTF8 $BodyPath
$params = '{"spreadsheetId":"'+$SpreadsheetId+'"}'

Write-Host "[dry-run] validating batchUpdate payload..."
gws sheets spreadsheets values batchUpdate --params $params --json $body --dry-run

Write-Host "[write] applying batchUpdate..."
gws sheets spreadsheets values batchUpdate --params $params --json $body

