@echo off
REM 运行所有示例脚本
echo ============================================================
echo Git 配置变更检查工具 - 运行所有示例
echo ============================================================
echo.

cd /d "%~dp0.."

echo [1/5] 基本检查示例
echo ------------------------------------------------------------
python examples\example_basic.py
if errorlevel 1 (
    echo 示例 1 执行失败
    pause
    exit /b 1
)
echo.
echo.

echo [2/5] Markdown 报告生成示例
echo ------------------------------------------------------------
python examples\example_markdown_report.py
if errorlevel 1 (
    echo 示例 2 执行失败
    pause
    exit /b 1
)
echo.
echo.

echo [3/5] JSON 导出示例
echo ------------------------------------------------------------
python examples\example_json_export.py
if errorlevel 1 (
    echo 示例 3 执行失败
    pause
    exit /b 1
)
echo.
echo.

echo [4/5] 自定义提交范围示例
echo ------------------------------------------------------------
python examples\example_custom_range.py
echo.
echo.

echo [5/5] 多格式输出示例
echo ------------------------------------------------------------
python examples\example_multi_format.py
if errorlevel 1 (
    echo 示例 5 执行失败
    pause
    exit /b 1
)
echo.

echo ============================================================
echo 所有示例执行完成！
echo ============================================================
pause
