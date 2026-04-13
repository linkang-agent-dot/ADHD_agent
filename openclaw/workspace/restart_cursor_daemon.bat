@echo off
REM 双击本文件 = 完整清理 cursor_daemon 并拉起新进程（不依赖过期的 daemon.pid）
REM Cursor 内置终端常无法杀其它进程；自动化请用：本 bat、计划任务、或 OpenClaw 在本机执行。

powershell -NoProfile -ExecutionPolicy Bypass -File "C:\ADHD_agent\.cursor\skills\async-notify\scripts\stop_cursor_daemon.ps1"
timeout /t 1 /nobreak >nul

python "C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_watchdog.py"
echo Done. daemon 已以 auto-execute 模式启动。
echo 查看日志: type "C:\ADHD_agent\openclaw\workspace\daemon_stdout.log"
