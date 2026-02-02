@echo off
REM 运行所有测试
echo ============================================================
echo Git 配置变更检查工具 - 运行测试
echo ============================================================
echo.

cd /d "%~dp0.."

echo 测试 1: CheckConfig
echo ------------------------------------------------------------
python tests\test_config.py
echo.
echo.

echo 测试 2: GitRepoManager
echo ------------------------------------------------------------
python tests\test_git_repo_manager.py
echo.
echo.

echo 测试 3: ChangeAnalyzer
echo ------------------------------------------------------------
python tests\test_change_analyzer.py
echo.

echo ============================================================
echo 测试完成！
echo ============================================================
pause
