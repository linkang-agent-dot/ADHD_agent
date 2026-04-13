$ErrorActionPreference = "SilentlyContinue"
$openclawDir = "C:\ADHD_agent\openclaw"
$sessionDir = "$openclawDir\agents\main\sessions"
$logFile = "$openclawDir\watchdog.log"
$maxSessionKB = 500
$checkIntervalSec = 120

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $msg" | Out-File -Append $logFile
    Write-Host "$ts $msg"
}

function Get-ActiveSession {
    Get-ChildItem "$sessionDir\*.jsonl" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch "backup" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

function Test-GatewayAlive {
    $procs = Get-WmiObject Win32_Process -Filter "Name='node.exe'" |
        Where-Object { $_.CommandLine -match "openclaw" }
    return ($procs.Count -gt 0)
}

function Restart-Gateway {
    Log "Killing gateway processes..."
    Get-WmiObject Win32_Process -Filter "Name='node.exe'" |
        Where-Object { $_.CommandLine -match "openclaw" } |
        ForEach-Object { taskkill /F /PID $_.ProcessId 2>&1 | Out-Null }
    Start-Sleep -Seconds 2
    Remove-Item "$openclawDir\gateway.lock" -Force -ErrorAction SilentlyContinue
    Log "Starting gateway..."
    Start-Process -FilePath "openclaw.cmd" -ArgumentList "gateway" -WindowStyle Hidden
    Start-Sleep -Seconds 10
    if (Test-GatewayAlive) {
        Log "Gateway restarted successfully"
    } else {
        Log "WARNING: Gateway failed to start"
    }
}

Log "=== Watchdog started (max session: ${maxSessionKB}KB, interval: ${checkIntervalSec}s) ==="

while ($true) {
    $session = Get-ActiveSession
    if ($session) {
        $sizeKB = [Math]::Round($session.Length / 1024)
        if ($sizeKB -gt $maxSessionKB) {
            Log "Session too large: ${sizeKB}KB > ${maxSessionKB}KB limit. Cleaning up..."
            $ts = Get-Date -Format "yyyyMMdd_HHmmss"
            $backupName = "$($session.BaseName)-backup-$ts.jsonl"
            Rename-Item $session.FullName $backupName
            Log "Session backed up as $backupName"
            Restart-Gateway
        }
    }

    if (-not (Test-GatewayAlive)) {
        Log "Gateway is down! Restarting..."
        Restart-Gateway
    }

    Start-Sleep -Seconds $checkIntervalSec
}
