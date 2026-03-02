@echo off
chcp 65001 >nul
echo ========================================
echo 安装测试依赖
echo ========================================
echo.

cd /d "%~dp0.."

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请确保已安装 Python 3.8+ 并添加到 PATH
    pause
    exit /b 1
)

echo 当前 Python 版本:
python --version
echo.

echo 正在安装测试依赖...
python -m pip install --upgrade pip
python -m pip install pytest pytest-cov

echo.
echo 验证安装...
python -m pytest --version

if errorlevel 1 (
    echo.
    echo 安装失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 测试依赖安装成功！
echo ========================================
echo.
echo 可以运行测试了: scripts\run_tests.bat
echo.
pause
