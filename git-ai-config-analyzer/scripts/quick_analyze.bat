@echo off
REM 快速分析脚本 - Git AI 配置分析器

cd /d "%~dp0.."

echo ========================================
echo Git AI 配置分析器 - 快速分析
echo ========================================

python src\main.py --format console

pause
