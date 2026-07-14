# 帕鲁情报巡检调度脚本（12:00/18:00）— 架构照搬 daily_report_scan.ps1 精简版
$ErrorActionPreference = "Continue"
$toolDir  = "C:\ADHD_agent\skills\palworld-tools"
$logFile  = Join-Path $toolDir "_intel_log.txt"
$report   = "C:\ADHD_agent\KB\_自动流水\帕鲁情报\帕鲁情报_latest.md"
$promptFile = Join-Path $toolDir "palworld_intel_prompt.txt"
$claude   = Join-Path $env:APPDATA "npm\claude.cmd"

New-Item -ItemType Directory -Force (Split-Path $report) | Out-Null
function Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Out-File $logFile -Append -Encoding utf8 }

Set-Location "C:\Users\linkang"   # cwd 决定 claude -p 加载哪个项目 memory（必须 linkang）
Log "start"

$delays = @(0, 120)   # 最多2次，带退避
$ok = $false
foreach ($d in $delays) {
    if ($d -gt 0) { Start-Sleep -Seconds $d }
    $attemptStart = Get-Date
    Get-Content $promptFile -Raw -Encoding UTF8 |
        & $claude -p --output-format text --model sonnet --max-budget-usd 6 `
          --dangerously-skip-permissions --settings '{"hooks":{"Stop":[]}}' 2>&1 |
        Out-File (Join-Path $toolDir "_intel_last_output.txt") -Encoding utf8
    # 新鲜度闸门：报告须在本次尝试开始后写过，且首行含今日日期
    if (Test-Path $report) {
        $fresh = (Get-Item $report).LastWriteTime -gt $attemptStart
        $head  = (Get-Content $report -TotalCount 1 -Encoding UTF8)
        $today = Get-Date -Format 'yyyy-MM-dd'
        if ($fresh -and $head -match [regex]::Escape($today)) { $ok = $true; break }
    }
    Log "attempt not fresh, retrying"
}
Log $(if ($ok) { "OK" } else { "FAILED after retries" })
