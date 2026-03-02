# Git AI 配置分析器 - 使用指南

## 目录

- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用场景](#使用场景)
- [命令行参数](#命令行参数)
- [报告说明](#报告说明)
- [常见问题](#常见问题)

---

## 快速开始

### 1. 安装依赖

```bash
# 方式一：使用脚本（推荐）
scripts\install_deps.bat

# 方式二：手动安装
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`：

```bash
copy .env.example .env
```

编辑 `.env` 文件，填入你的 OpenAI API Key：

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 运行分析

```bash
# 快速分析（控制台输出）
scripts\quick_analyze.bat

# 生成完整报告
scripts\generate_report.bat
```

---

## 配置说明

### 环境变量配置 (.env)

```env
# 必需：OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# 可选：自定义 API 地址（用于代理或兼容 API）
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选：默认使用的模型
AI_MODEL=gpt-4
```

### 默认配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 仓库路径 | `C:\gdconfig` | Git 仓库根目录 |
| 目标目录 | `fo/` | 要检查的配置文件目录 |
| 基准分支 | `bugfix` | 比较的基准分支 |
| AI 模型 | `gpt-4` | 使用的 AI 模型 |
| 输出格式 | `markdown` | 报告输出格式 |

---

## 使用场景

### 场景 1：检查当前分支与主分支的差异

```bash
python src\main.py --base-branch main
```

**适用于**：功能开发完成后，检查相对于主分支新增了哪些配置

### 场景 2：检查两个分支之间的差异

```bash
python src\main.py --base-branch release --compare-branch feature/new-system
```

**适用于**：对比两个特定分支的配置差异

### 场景 3：快速查看变更（不使用 AI）

```bash
# 使用脚本
scripts\analyze_no_ai.bat

# 或命令行
python src\main.py --no-ai --format console
```

**适用于**：
- 没有 API Key 时
- 只需要快速查看变更列表
- 节省 API 调用成本

### 场景 4：生成多种格式报告

```bash
python src\main.py --format all
```

**输出**：
- Markdown 报告（易读）
- JSON 报告（机器处理）
- 控制台输出（即时查看）

### 场景 5：使用 GPT-3.5 节省成本

```bash
python src\main.py --ai-model gpt-3.5-turbo
```

**说明**：日常开发可以使用 gpt-3.5-turbo，重要发布前使用 gpt-4

---

## 命令行参数

### 基本参数

```bash
python src\main.py [选项]
```

### 所有参数

| 参数 | 类型 | 默认值 | 说明 | 示例 |
|------|------|--------|------|------|
| `--repo-path` | 路径 | `C:\gdconfig` | Git 仓库路径 | `--repo-path "D:\myrepo"` |
| `--target-dir` | 路径 | `fo/` | 目标检查目录 | `--target-dir "config/"` |
| `--base-branch` | 分支名 | `bugfix` | 基准分支 | `--base-branch main` |
| `--compare-branch` | 分支名 | 当前分支 | 比较分支 | `--compare-branch feature/xxx` |
| `--commit-range` | 范围 | 自动 | 提交范围 | `--commit-range HEAD~5..HEAD` |
| `--format` | 格式 | `markdown` | 输出格式 | `--format json` |
| `--output` | 文件路径 | 自动 | 输出文件 | `--output report.md` |
| `--ai-model` | 模型名 | `gpt-4` | AI 模型 | `--ai-model gpt-3.5-turbo` |
| `--no-ai` | 开关 | - | 禁用 AI | `--no-ai` |
| `--max-diff-lines` | 数字 | `500` | 最大差异行数 | `--max-diff-lines 1000` |

### 输出格式选项

| 格式 | 说明 | 输出文件 |
|------|------|----------|
| `console` | 控制台文本输出 | 无，直接显示 |
| `markdown` | Markdown 格式报告 | `ai_config_analysis_report.md` |
| `json` | JSON 格式数据 | `ai_config_analysis_report.json` |
| `all` | 生成所有格式 | 所有上述文件 |

---

## 报告说明

### Markdown 报告结构

生成的 Markdown 报告包含以下章节：

#### 1. 执行摘要
- 分析时间、仓库信息
- 变更统计（总数、功能新增、高优先级）

#### 2. AI 分析总结
- 整体变更概览
- 主要发现和建议

#### 3. 功能新增配置（重点）
- 需要特别关注的新功能配置
- 包含详细的影响评估

#### 4. 变更分类汇总
- 按类别分组：功能新增、参数调整、Bug修复等
- 表格形式展示，便于快速浏览

#### 5. 高优先级变更
- 需要立即关注的变更
- 潜在影响较大的修改

#### 6. 需要同步的配置
- 以 checkbox 形式列出
- 方便跟踪同步进度

#### 7. 所有变更详情
- 每个配置文件的完整分析
- 包含目的、影响、建议等

### JSON 报告结构

```json
{
  "summary": {
    "check_time": "2026-02-02 10:30:00",
    "total_changes": 10,
    "new_feature_count": 3,
    ...
  },
  "ai_summary": "...",
  "new_feature_configs": [...],
  "all_changes": [...],
  "by_category": {...},
  "by_priority": {...}
}
```

### 变更分类说明

| 分类 | 说明 | 示例 |
|------|------|------|
| **功能新增** | 新功能需要的配置 | 新增用户等级系统配置表 |
| **参数调整** | 现有功能的参数修改 | 调整道具掉落概率 |
| **Bug修复** | 修复问题的配置 | 修正错误的经验值配置 |
| **结构重构** | 配置结构优化 | 重组配置表结构 |
| **废弃移除** | 废弃或移除的配置 | 删除旧活动配置 |

---

## 常见问题

### Q1: 报告中没有 AI 分析结果？

**原因**：
- 未配置 `OPENAI_API_KEY`
- API Key 无效或过期
- 网络连接问题

**解决**：
1. 检查 `.env` 文件中的 API Key 是否正确
2. 尝试使用 `--no-ai` 选项生成基础报告
3. 检查网络连接和代理设置

### Q2: 如何分析特定提交范围？

```bash
# 最近 5 个提交
python src\main.py --commit-range HEAD~5..HEAD

# 特定提交之间
python src\main.py --commit-range abc1234..def5678
```

### Q3: 如何减少 API 成本？

**建议**：
1. 日常开发使用 `gpt-3.5-turbo`
2. 使用 `--max-diff-lines` 限制分析的内容量
3. 只在重要发布前使用 `gpt-4` 详细分析
4. 使用 `--no-ai` 进行初步筛选

### Q4: 报告太长，如何只看重点？

```bash
# 只输出到控制台，快速查看摘要
python src\main.py --format console

# 然后查看 Markdown 报告的"功能新增配置"章节
```

### Q5: 如何集成到 CI/CD？

```bash
# 在 CI 脚本中
python src\main.py \
  --repo-path . \
  --base-branch main \
  --format json \
  --output ci_report.json

# 解析 JSON 并进行后续处理
```

### Q6: 未发现任何变更？

**检查**：
1. 确认当前分支和基准分支不同
2. 确认 `target_dir` 配置正确
3. 确认有提交记录

```bash
# 查看提交范围
git log bugfix..HEAD --oneline

# 查看变更文件
git diff bugfix..HEAD --name-only -- fo/
```

### Q7: 如何自定义分析提示词？

编辑 `prompts/config_analysis.txt` 文件，修改提示词模板。
（注意：当前版本提示词是硬编码的，未来版本会支持模板文件）

---

## 高级用法

### 批量分析多个分支

创建批处理脚本 `analyze_branches.bat`：

```batch
@echo off
for %%b in (feature/A feature/B feature/C) do (
    echo 分析分支: %%b
    python src\main.py --compare-branch %%b --output "reports\%%b.md"
)
```

### 定期生成报告

使用 Windows 任务计划程序，定期运行 `generate_report.bat`

### 与其他工具集成

```python
# 读取 JSON 报告并处理
import json

with open('reports/ai_config_analysis_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
# 提取高优先级变更
high_priority = data['by_priority']['高']
for change in high_priority:
    print(f"⚠️ {change['table_name']}: {change['summary']}")
```

---

## 技术支持

如有问题，请检查：
1. [README.md](README.md) - 项目概述
2. [USAGE.md](USAGE.md) - 本使用指南
3. 项目 Issues

---

*最后更新: 2026-02-02*
