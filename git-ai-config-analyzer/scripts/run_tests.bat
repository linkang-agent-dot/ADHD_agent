@echo off
chcp 65001 >nul
echo ========================================
echo Git AI 配置分析器 - 运行测试
echo ========================================
echo.

cd /d "%~dp0.."

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请确保已安装并添加到 PATH
    pause
    exit /b 1
)

echo 检查测试依赖...
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo pytest 未安装，正在安装测试依赖...
    echo.
    python -m pip install pytest pytest-cov
    
    REM 再次检查是否安装成功
    python -m pytest --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo 错误: pytest 安装失败
        echo 请手动运行: python -m pip install pytest pytest-cov
        echo.
        pause
        exit /b 1
    )
    echo pytest 安装成功！
    echo.
)

echo 运行测试...
echo.
python -m pytest tests/ -v --tb=short

if errorlevel 1 (
    echo.
    echo 测试执行出现错误！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 测试全部通过！
echo ========================================
pause
