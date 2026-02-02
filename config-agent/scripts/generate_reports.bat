@echo off
REM 生成所有格式的报告
echo ============================================================
echo 生成所有格式的配置变更报告
echo ============================================================
echo.

cd /d "%~dp0.."

REM 创建 reports 目录
if not exist "reports" mkdir reports

REM 生成所有格式的报告
python src\main.py --format all

echo.
echo 报告已保存到 reports 目录
echo - git_change_report.md (Markdown 格式)
echo - git_change_report.json (JSON 格式)
echo.

pause
