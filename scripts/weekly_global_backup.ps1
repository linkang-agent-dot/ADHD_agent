# weekly_global_backup.ps1
# Mirror custom global ~/.claude content into the ADHD repo (snapshot only).
# Commit + push is handled by the existing daily task PushADHD (18:00).
# Schedule: Monday 12:00 mirror -> picked up & pushed by PushADHD same evening.
# NOTE: ASCII-only on purpose (Windows PowerShell 5.1 mis-reads UTF-8 .ps1 without BOM).
$ErrorActionPreference = "Continue"
$snap   = "C:\ADHD_agent\_global_backup\claude-snapshot"
$claude = "$env:USERPROFILE\.claude"
$log    = "C:\ADHD_agent\_global_backup\backup_log.txt"
function Log($m){ Add-Content -Path $log -Value ((Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "  " + $m) }

New-Item -ItemType Directory -Force $snap | Out-Null
Log "===== weekly mirror start ====="

# agents (all, mirror)
if (Test-Path "$claude\agents") {
  robocopy "$claude\agents" "$snap\agents" /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
  Log "agents mirrored"
}
# hooks (if any)
if (Test-Path "$claude\hooks") {
  robocopy "$claude\hooks" "$snap\hooks" /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
  Log "hooks mirrored"
}
# settings.json
if (Test-Path "$claude\settings.json") {
  Copy-Item "$claude\settings.json" "$snap\settings.json" -Force
  Log "settings.json backed up"
}
# skills: text/code/config only, AND skip any single file > 512KB
# (big .json/.html are data blobs e.g. base64/translation_memory -> would bloat git).
# /MIR also prunes previously-copied big/binary files from the snapshot.
if (Test-Path "$claude\skills") {
  robocopy "$claude\skills" "$snap\skills" *.md *.py *.mdc *.json *.txt *.yml *.yaml *.template *.toml *.cfg *.ps1 *.css *.html *.js /MIR /MAX:524288 /XD __pycache__ /NFL /NDL /NJH /NJS /NP | Out-Null
  Log "skills (code/config, <512KB) mirrored"
}
# memory (all .md, mirror)
$mem = "$claude\projects\C--Users-linkang\memory"
if (Test-Path $mem) {
  robocopy $mem "$snap\memory" *.md /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
  Log "memory mirrored"
}

# prune oversized files (data blobs e.g. translation_memory.json) that /MIR keeps
# because they still exist in source — guarantees a lean, code/config-only snapshot.
$big = Get-ChildItem $snap -Recurse -File | Where-Object { $_.Length -gt 524288 }
foreach ($f in $big) { Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue }
if ($big) { Log ("pruned " + $big.Count + " oversized data file(s)") }

Log "===== mirror done (commit+push handled by daily PushADHD) ====="
