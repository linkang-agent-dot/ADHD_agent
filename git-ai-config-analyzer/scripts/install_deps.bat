@echo off
chcp 65001 >nul
echo ========================================
echo Git AI 配置分析器 - 安装依赖
echo ========================================
echo.

cd /d "%~dp0.."

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo 当前 Python 版本:
python --version
echo.

echo 正在安装依赖包...
pip install -r requirements.txt

echo.
echo 依赖安装完成！
echo.
echo 请复制 .env.example 为 .env 并配置你的 OpenAI API Key
echo.
pause
