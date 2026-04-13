# 强制结束所有「正在跑 cursor_daemon.py」的 Python 进程（按命令行匹配，不依赖 daemon.pid）
# 用法：在资源管理器中双击，或由计划任务 / OpenClaw 在本机执行（勿依赖 Cursor 内置终端沙箱）。
$ErrorActionPreference = 'SilentlyContinue'
$pattern = [regex]::Escape('async-notify\scripts\cursor_daemon.py')

# 1) 优雅退出：新 daemon 会轮询删除此文件并自行退出
$flag = 'C:\ADHD_agent\openclaw\workspace\cursor_daemon_restart.flag'
New-Item -Path $flag -ItemType File -Force | Out-Null
Start-Sleep -Seconds 6

# 2) 按命令行强杀（覆盖 PID 文件过期、多开、旧进程无 flag 逻辑等情况）
$killed = @()
Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -match '^python(w)?\.exe$' -and
    $_.CommandLine -and
    ($_.CommandLine -match $pattern)
  } |
  ForEach-Object {
    $procId = $_.ProcessId
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    $killed += $procId
  }

if ($killed.Count -gt 0) {
  Write-Host "[stop_cursor_daemon] 已结束 PID: $($killed -join ', ')"
} else {
  Write-Host '[stop_cursor_daemon] 未发现运行中的 cursor_daemon.py 进程'
}

# 3) 仍尝试按 pid 文件补刀（防止命令行查询偶发拿不到）
$pidFile = 'C:\ADHD_agent\openclaw\workspace\daemon.pid'
if (Test-Path $pidFile) {
  try {
    $j = Get-Content $pidFile -Raw | ConvertFrom-Json
    $old = [int]$j.pid
    if ($old -gt 0) {
      Stop-Process -Id $old -Force -ErrorAction SilentlyContinue
      Write-Host "[stop_cursor_daemon] 已按 daemon.pid 尝试结束 PID=$old"
    }
  } catch {}
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
Write-Host '[stop_cursor_daemon] 已删除 daemon.pid（watchdog 会重写）'
