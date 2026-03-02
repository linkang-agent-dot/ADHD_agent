@echo off
REM 生成 AI 分析报告脚本

cd /d "%~dp0.."

echo ========================================
echo Git AI 配置分析器 - 生成报告
echo ========================================

REM 创建报告目录
if not exist "reports" mkdir reports

REM 获取当前日期
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date=%datetime:~0,8%

REM 生成报告
python src\main.py ^
    --format all ^
    --output "reports\ai_analysis_%date%.md"

echo.
echo 报告已生成到 reports 目录
pause
