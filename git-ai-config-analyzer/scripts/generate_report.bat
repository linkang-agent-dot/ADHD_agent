@echo off
chcp 65001 >nul
echo ============================================
echo Git AI 配置分析器 - 生成完整报告
echo ============================================
echo.

cd /d "%~dp0.."

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请确保已安装并添加到 PATH
    pause
    exit /b 1
)

REM 获取当前日期
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date=%datetime:~0,8%
set time_str=%datetime:~8,4%

REM 创建报告目录
if not exist "reports" mkdir reports

REM 运行分析并生成报告
python src\main.py ^
    --format all ^
    --output "reports\ai_config_analysis_%date%_%time_str%.md"

echo.
echo 报告已生成到 reports 目录
echo.
pause
