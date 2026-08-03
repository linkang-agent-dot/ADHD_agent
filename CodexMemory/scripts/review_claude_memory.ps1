param(
    [string]$SourceDir = 'C:\Users\linkang\.claude\projects\C--Users-linkang\memory',
    [string]$CheckpointFile = 'C:\ADHD_agent\CodexMemory\CLAUDE_REVIEW_CHECKPOINT.md'
)

$checkpointLine = Select-String -LiteralPath $CheckpointFile -Pattern '^last_reviewed_utc:\s*(.+)$' | Select-Object -First 1
if (-not $checkpointLine) {
    throw "Missing last_reviewed_utc in $CheckpointFile"
}

$sinceUtc = [DateTime]::Parse($checkpointLine.Matches[0].Groups[1].Value).ToUniversalTime()
$sourceRoot = (Resolve-Path -LiteralPath $SourceDir).Path

$changes = Get-ChildItem -LiteralPath $sourceRoot -Recurse -File -Filter '*.md' |
    Where-Object { $_.LastWriteTimeUtc -gt $sinceUtc } |
    Sort-Object LastWriteTimeUtc |
    ForEach-Object {
        [pscustomobject]@{
            relative_path = $_.FullName.Substring($sourceRoot.Length).TrimStart('\\')
            last_write_utc = $_.LastWriteTimeUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
            length = $_.Length
        }
    }

if ($changes.Count -eq 0) {
    'NO_CLAUDE_MEMORY_CHANGES'
} else {
    $changes | ConvertTo-Json -Depth 3
}
