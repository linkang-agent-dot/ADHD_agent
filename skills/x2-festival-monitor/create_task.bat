@echo off
REM 拓荒节期间每小时刷新日报（节日结束后删除此任务）
schtasks /create /tn "ClaudeX2FestivalMonitor" /tr "cmd /c set PYTHONIOENCODING=utf-8 & python C:\ADHD_agent\skills\x2-festival-monitor\x2_festival_daily.py > C:\Users\linkang\_x2_festival_daily_log.txt 2>&1" /sc hourly /mo 1 /st 00:05 /f
echo Done. 每小时刷新；节日结束后用 schtasks /delete /tn ClaudeX2FestivalMonitor /f 清除
