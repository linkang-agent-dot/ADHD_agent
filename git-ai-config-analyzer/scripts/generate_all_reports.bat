@echo off
chcp 65001 >nul
echo ========================================
echo Git AI 配置分析器 - 生成所有格式报告
echo ========================================
echo.

cd /d "%~dp0.."

REM 获取当前日期
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date=%datetime:~0,8%

echo 正在生成报告...
python src\main.py --format all --output "reports\ai_config_report_%date%.md"

echo.
echo 报告已生成:
echo   - reports\ai_config_report_%date%.md
echo   - reports\ai_config_analysis_report.json
pause
