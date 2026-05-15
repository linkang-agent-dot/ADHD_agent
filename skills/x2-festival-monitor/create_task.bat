@echo off
schtasks /create /tn "ClaudeX2FestivalMonitor" /tr "cmd /c set PYTHONIOENCODING=utf-8 & python C:\ADHD_agent\skills\x2-festival-monitor\x2_festival_daily.py > C:\Users\linkang\_x2_festival_daily_log.txt 2>&1" /sc daily /st 09:00 /f
echo Done.
