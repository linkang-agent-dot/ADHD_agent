@echo off
REM 夏日恋语期间每小时刷新日报（节日约 10 天，结束后删除此任务）
schtasks /create /tn "ClaudeX3FestivalMonitor" /tr "cmd /c set PYTHONIOENCODING=utf-8 & python C:\ADHD_agent\skills\x3-festival-monitor\x3_festival_daily.py > C:\Users\linkang\_x3_festival_daily_log.txt 2>&1" /sc hourly /mo 1 /st 00:00 /f
echo Done. 每小时刷新；节日结束后用 schtasks /delete /tn ClaudeX3FestivalMonitor /f 清除
