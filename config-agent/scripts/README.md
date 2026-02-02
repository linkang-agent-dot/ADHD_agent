# 辅助脚本说明

本目录包含用于快速执行常见任务的批处理脚本。

## 脚本列表

### 1. quick_check.bat

**功能：** 快速执行配置变更检查

**使用：**
```bash
scripts\quick_check.bat
```

**说明：**
- 使用默认配置
- 控制台输出报告
- 适合日常快速检查

---

### 2. generate_reports.bat

**功能：** 生成所有格式的报告文件

**使用：**
```bash
scripts\generate_reports.bat
```

**输出：**
- `reports/git_change_report.md` - Markdown 格式
- `reports/git_change_report.json` - JSON 格式
- 控制台也会显示报告

**说明：**
- 自动创建 `reports/` 目录
- 适合需要保存报告文件的场景

---

### 3. run_all_examples.bat

**功能：** 运行所有示例脚本

**使用：**
```bash
scripts\run_all_examples.bat
```

**执行顺序：**
1. 基本检查示例
2. Markdown 报告生成示例
3. JSON 导出示例
4. 自定义提交范围示例
5. 多格式输出示例

**说明：**
- 依次运行所有示例
- 如果某个示例失败会提示并暂停
- 适合学习和测试功能

---

### 4. run_tests.bat

**功能：** 运行所有单元测试

**使用：**
```bash
scripts\run_tests.bat
```

**执行顺序：**
1. CheckConfig 测试
2. GitRepoManager 测试
3. ChangeAnalyzer 测试

**说明：**
- 验证代码功能正确性
- 开发时建议经常运行
- 修改代码后必须运行

---

## 自定义脚本

### 创建自定义检查脚本

创建 `custom_check.bat`：

```batch
@echo off
cd /d "%~dp0.."

REM 自定义参数
python src\main.py ^
    --repo-path "D:\myrepo" ^
    --target-dir "configs/" ^
    --base-branch "develop" ^
    --format markdown ^
    --output "my_report.md"

pause
```

### 创建定时检查脚本

创建 `daily_check.bat`：

```batch
@echo off
cd /d "%~dp0.."

REM 获取当前日期
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date=%datetime:~0,8%

REM 生成带日期的报告
python src\main.py ^
    --format all ^
    --output "reports\report_%date%.md"

echo 报告已生成: reports\report_%date%.md
```

### 创建多仓库检查脚本

创建 `check_all_repos.bat`：

```batch
@echo off
cd /d "%~dp0.."

echo 检查仓库 1: gdconfig
python src\main.py --repo-path "C:\gdconfig" --output "reports\gdconfig.md"

echo.
echo 检查仓库 2: game-config
python src\main.py --repo-path "C:\game-config" --output "reports\game-config.md"

echo.
echo 所有仓库检查完成！
pause
```

## Linux/Mac 脚本

### quick_check.sh

```bash
#!/bin/bash
cd "$(dirname "$0")/.."
python src/main.py
```

### generate_reports.sh

```bash
#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p reports
python src/main.py --format all
echo "报告已保存到 reports 目录"
```

### 添加执行权限

```bash
chmod +x scripts/*.sh
```

## 注意事项

1. **路径问题**
   - 脚本会自动切换到项目根目录
   - 使用相对路径引用文件

2. **Python 环境**
   - 确保 Python 在系统 PATH 中
   - 或修改脚本指定完整 Python 路径

3. **权限问题**
   - Windows: 以普通用户权限运行即可
   - Linux/Mac: 可能需要执行权限

4. **错误处理**
   - 脚本遇到错误会暂停
   - 查看错误信息后按任意键继续

## 集成到 IDE

### Visual Studio Code

在 `.vscode/tasks.json` 添加：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "快速检查",
      "type": "shell",
      "command": "scripts\\quick_check.bat",
      "group": "test"
    },
    {
      "label": "生成报告",
      "type": "shell",
      "command": "scripts\\generate_reports.bat",
      "group": "build"
    },
    {
      "label": "运行测试",
      "type": "shell",
      "command": "scripts\\run_tests.bat",
      "group": "test"
    }
  ]
}
```

然后使用 `Ctrl+Shift+P` → `Tasks: Run Task` 运行。

### PyCharm

1. Run → Edit Configurations
2. 添加 Shell Script 配置
3. 指定脚本路径

## 计划任务

### Windows 任务计划程序

1. 打开任务计划程序
2. 创建基本任务
3. 选择触发器（每天/每周）
4. 操作：启动程序
5. 程序/脚本：`C:\path\to\scripts\daily_check.bat`

### Linux Cron

编辑 crontab：
```bash
crontab -e
```

添加定时任务：
```
# 每天上午 9 点执行检查
0 9 * * * cd /path/to/config-agent && ./scripts/daily_check.sh
```

---

**提示：** 根据实际需求修改和创建新的脚本文件！
