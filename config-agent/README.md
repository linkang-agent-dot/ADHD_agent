# Git 配置变更检查工具

## 功能概述

检查 Git 仓库中分支的提交记录，分析 `fo` 目录下的文件变更，识别出需要检查修改的配置表。

## 项目结构

```
config-agent/
├── src/
│   ├── config.py              # 配置参数
│   ├── git_repo_manager.py    # Git 仓库管理器
│   ├── change_analyzer.py     # 变更分析器
│   ├── report_generator.py    # 报告生成器
│   ├── main.py                # 主程序入口
│   └── git_manager.py         # GitHub API 管理器（已有）
├── requirements.txt           # 依赖文件
└── README.md                  # 项目说明
```

## 安装

```bash
# 安装依赖（如需要）
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 使用默认配置（检查 C:\gdconfig 仓库的 fo/ 目录）
python src/main.py

# 指定仓库路径
python src/main.py --repo-path "D:\myrepo"

# 指定目标目录
python src/main.py --target-dir "config/"

# 指定基准分支
python src/main.py --base-branch "develop"
```

### 输出格式

```bash
# 控制台输出（默认）
python src/main.py --format console

# 生成 Markdown 报告
python src/main.py --format markdown --output report.md

# 生成 JSON 报告
python src/main.py --format json --output report.json

# 生成所有格式
python src/main.py --format all
```

### 指定提交范围

```bash
# 使用自定义提交范围
python src/main.py --commit-range "main..feature-branch"

# 比较特定分支
python src/main.py --compare-branch "feature-branch"
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--repo-path` | Git 仓库路径 | `C:\gdconfig` |
| `--target-dir` | 目标检查目录 | `fo/` |
| `--base-branch` | 基准分支 | `main` |
| `--compare-branch` | 比较分支 | 当前分支 |
| `--commit-range` | 提交范围 | `main..HEAD` |
| `--format` | 输出格式：console/markdown/json/all | `console` |
| `--output` | 输出文件路径 | 自动生成 |

## 输出示例

### 控制台输出

```
============================================================
Git 配置变更检查报告
============================================================
检查时间: 2026-02-02 14:30:00
仓库路径: C:\gdconfig
检查目录: fo/
当前分支: feature/update-config
比较基准: main
提交范围: main..HEAD
提交数量: 3

------------------------------------------------------------
变更表汇总 (共 5 个表)
------------------------------------------------------------

【新增】(1个)
  - new_feature_config (fo/new_feature_config.csv)

【修改】(3个)
  - user_config (fo/user_config.csv)
  - item_config (fo/item_config.json)
  - level_config (fo/level_config.csv)

【删除】(1个)
  - deprecated_config (fo/deprecated_config.csv)

------------------------------------------------------------
详细提交记录
------------------------------------------------------------

[1] abc1234 - 2026-02-01 10:00 - developer
    消息: 添加新功能配置
    变更:
          + fo/new_feature_config.csv
          M fo/user_config.csv

[2] def5678 - 2026-02-01 14:00 - developer
    消息: 更新道具配置
    变更:
          M fo/item_config.json
          M fo/level_config.csv

[3] ghi9012 - 2026-02-02 09:00 - developer
    消息: 移除废弃配置
    变更:
          - fo/deprecated_config.csv

============================================================
```

## 核心功能模块

### 1. GitRepoManager (git_repo_manager.py)

负责所有 Git 仓库操作：
- 验证仓库有效性
- 获取分支信息
- 获取提交记录
- 获取文件变更列表
- 获取文件 diff 内容

### 2. ChangeAnalyzer (change_analyzer.py)

负责分析文件变更：
- 提取配置表名称
- 关联提交与文件
- 按变更类型分组
- 去重合并变更记录

### 3. ReportGenerator (report_generator.py)

负责生成各种格式的报告：
- 控制台文本报告
- Markdown 格式报告
- JSON 结构化报告

### 4. CheckConfig (config.py)

配置参数管理：
- 仓库路径配置
- 分支配置
- 输出格式配置

## 扩展功能

可以通过修改代码实现以下扩展功能：

1. **详细 diff 显示**: 在 `ReportGenerator` 中添加文件 diff 内容
2. **过滤规则**: 在 `ChangeAnalyzer` 中添加文件/表名过滤逻辑
3. **多仓库支持**: 扩展 `main.py` 支持检查多个仓库
4. **通知集成**: 添加邮件或消息推送功能

## 注意事项

1. 确保指定的 Git 仓库路径存在且为有效的 Git 仓库
2. 确保有权限访问 Git 仓库
3. Windows 路径建议使用原始字符串 `r"C:\path"` 或双反斜杠 `"C:\\path"`
4. 提交范围格式为 Git 标准格式，如 `branch1..branch2`

## 许可证

MIT License
