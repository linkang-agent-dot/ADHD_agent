@echo off
REM 无 AI 分析脚本（不需要 API Key）

cd /d "%~dp0.."

echo ========================================
echo Git AI 配置分析器 - 基础分析（无AI）
echo ========================================

python src\main.py --no-ai --format markdown --output "reports\basic_analysis.md"

echo.
echo 报告已生成: reports\basic_analysis.md
pause
