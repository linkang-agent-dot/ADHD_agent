# 使用示例

本文档提供了 Git AI 配置分析器的实际使用示例。

## 目录

- [基础示例](#基础示例)
- [高级示例](#高级示例)
- [实际场景](#实际场景)
- [报告示例](#报告示例)

---

## 基础示例

### 示例 1: 最简单的使用

```bash
# 分析当前分支相对于 bugfix 分支的变更
python src\main.py
```

**输出**：
```
========================================
Git AI 配置分析器
========================================

[1/6] 连接仓库: C:\gdconfig
      当前分支: feature/user-system
      基准分支: bugfix

[2/6] 获取提交记录: bugfix..HEAD
      找到 3 个提交
      找到 2 个变更文件

[3/6] 提取差异内容...
      提取了 2 个配置差异

[4/6] AI 分析配置变更...
正在分析 [1/2]: user_level_config
正在分析 [2/2]: reward_config

[5/6] 生成整体总结...

[6/6] 生成报告...

Markdown 报告已保存到: ai_config_analysis_report.md

========================================
分析完成!
  - 总变更数: 2
  - 功能新增配置: 1
  - 高优先级变更: 1
========================================
```

### 示例 2: 快速查看（控制台输出）

```bash
python src\main.py --format console
```

**输出**：
```
======================================================================
Git AI 配置分析报告
======================================================================
分析时间: 2026-02-02 15:30:00
仓库路径: C:\gdconfig
分析目录: fo/
...
----------------------------------------------------------------------
功能新增配置（重点关注）
----------------------------------------------------------------------

[user_level_config]
  文件: fo/user_level_config.csv
  摘要: 新增用户等级配置表，支持新的等级系统
  目的: 实现新的用户成长体系
  影响: 用户系统、经验系统、奖励系统
  优先级: 高
  需要同步: 是
...
```

### 示例 3: 生成 JSON 报告

```bash
python src\main.py --format json --output analysis.json
```

**输出文件** `analysis.json`：
```json
{
  "summary": {
    "check_time": "2026-02-02 15:30:00",
    "total_changes": 2,
    "new_feature_count": 1,
    "high_priority_count": 1
  },
  "ai_summary": "...",
  "new_feature_configs": [
    {
      "table_name": "user_level_config",
      "summary": "新增用户等级配置表",
      "is_new_feature_config": true,
      ...
    }
  ],
  ...
}
```

---

## 高级示例

### 示例 4: 指定不同的基准分支

```bash
# 与 main 分支比较
python src\main.py --base-branch main

# 与 release 分支比较
python src\main.py --base-branch release
```

### 示例 5: 比较两个特定分支

```bash
# 比较 feature-A 和 feature-B 分支
python src\main.py --base-branch feature-A --compare-branch feature-B
```

### 示例 6: 分析特定提交范围

```bash
# 最近 5 个提交
python src\main.py --commit-range HEAD~5..HEAD

# 特定两个提交之间
python src\main.py --commit-range abc1234..def5678

# 最近一周的提交
python src\main.py --commit-range "@{1 week ago}..HEAD"
```

### 示例 7: 使用不同的 AI 模型

```bash
# 使用 GPT-3.5（更便宜）
python src\main.py --ai-model gpt-3.5-turbo

# 使用 GPT-4（更准确）
python src\main.py --ai-model gpt-4
```

### 示例 8: 无 AI 模式（不需要 API Key）

```bash
python src\main.py --no-ai --format markdown
```

### 示例 9: 生成所有格式的报告

```bash
python src\main.py --format all
```

**生成文件**：
- `ai_config_analysis_report.md`
- `ai_config_analysis_report.json`
- 控制台输出

### 示例 10: 自定义输出路径

```bash
# Markdown 报告
python src\main.py --format markdown --output reports\my_analysis.md

# JSON 报告
python src\main.py --format json --output reports\my_analysis.json
```

---

## 实际场景

### 场景 1: 功能开发完成，准备合并

**背景**：开发了新的用户等级系统，需要检查新增了哪些配置

```bash
# 当前在 feature/user-level 分支
python src\main.py --base-branch main --format markdown --output reports\user_level_review.md
```

**使用报告**：
1. 查看"功能新增配置"章节
2. 检查是否有遗漏的配置
3. 确认需要同步的配置列表
4. 将报告作为 Code Review 的参考

### 场景 2: 发布前配置检查

**背景**：准备发布新版本，需要确认所有配置变更

```bash
# 比较 release 分支和当前分支
python src\main.py --base-branch release --format all
```

**检查清单**：
- [ ] 功能新增配置是否完整
- [ ] 高优先级变更是否已处理
- [ ] 需要同步的配置是否已同步
- [ ] Bug 修复配置是否正确

### 场景 3: 快速查看本地修改

**背景**：本地修改了一些配置，想快速查看变更

```bash
# 无 AI 模式，快速查看
python src\main.py --no-ai --format console --commit-range HEAD~1..HEAD
```

### 场景 4: 定期配置审查

**背景**：每周审查一次配置变更

```bash
# 创建批处理脚本 weekly_review.bat
@echo off
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date=%datetime:~0,8%

python src\main.py ^
    --commit-range "@{1 week ago}..HEAD" ^
    --format markdown ^
    --output "reports\weekly_review_%date%.md"

echo 本周配置审查报告已生成
```

### 场景 5: 多分支对比

**背景**：对比多个功能分支的配置变更

```bash
# 创建批处理脚本 compare_branches.bat
@echo off
set BASE_BRANCH=main

for %%b in (feature/A feature/B feature/C) do (
    echo 分析分支: %%b
    python src\main.py ^
        --base-branch %BASE_BRANCH% ^
        --compare-branch %%b ^
        --format markdown ^
        --output "reports\%%b_analysis.md"
)

echo 所有分支分析完成
```

### 场景 6: CI/CD 集成

**背景**：在持续集成中自动分析配置变更

```yaml
# .gitlab-ci.yml 或类似配置
analyze_config:
  script:
    - pip install -r requirements.txt
    - python src/main.py --format json --output ci_report.json
    - python scripts/check_high_priority.py ci_report.json
  artifacts:
    paths:
      - ci_report.json
```

**检查脚本** `scripts/check_high_priority.py`：
```python
import json
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

high_priority = data['by_priority']['高']
if high_priority:
    print(f"⚠️ 发现 {len(high_priority)} 个高优先级配置变更，请审查！")
    for change in high_priority:
        print(f"  - {change['table_name']}: {change['summary']}")
    sys.exit(1)  # 阻止部署
```

---

## 报告示例

### Markdown 报告示例

```markdown
# Git AI 配置分析报告

## 执行摘要

- **分析时间**: 2026-02-02 15:30:00
- **仓库路径**: `C:\gdconfig`
- **分析目录**: `fo/`
- **当前分支**: `feature/user-system`
- **比较基准**: `bugfix`
- **提交范围**: `bugfix..HEAD`
- **变更配置数**: 3
- **功能新增配置**: 2
- **高优先级变更**: 1
- **需要同步**: 2

## AI 分析总结

本次分析发现 3 个配置表发生变更，主要围绕用户等级系统和奖励系统的功能开发。
其中 2 个配置为功能新增，需要重点关注并同步到测试环境。建议优先处理高优先级
的用户等级配置，确保新功能正常上线。

## 功能新增配置（重点关注）

### 1. user_level_config

- **文件**: `fo/user_level_config.csv`
- **变更类型**: 新增
- **摘要**: 新增用户等级配置表，支持新的等级系统
- **目的**: 实现新的用户成长体系，包含等级、经验值、奖励等配置
- **影响范围**: 用户系统、经验系统、奖励系统、UI 显示
- **审查优先级**: 高
- **需要同步**: 是
- **相关系统**: 用户系统, 奖励系统, 任务系统

### 2. reward_config

- **文件**: `fo/reward_config.csv`
- **变更类型**: 修改
- **摘要**: 新增 5 条等级奖励配置项
- **目的**: 配合用户等级系统，添加各等级对应的奖励
- **影响范围**: 奖励系统
- **审查优先级**: 中
- **需要同步**: 是
- **相关系统**: 奖励系统, 道具系统

## 变更分类汇总

### 功能新增 (2个)

| 配置表 | 文件 | 摘要 | 优先级 |
|--------|------|------|--------|
| user_level_config | `fo/user_level_config.csv` | 新增用户等级配置表... | 高 |
| reward_config | `fo/reward_config.csv` | 新增 5 条等级奖励配置项 | 中 |

### 参数调整 (1个)

| 配置表 | 文件 | 摘要 | 优先级 |
|--------|------|------|--------|
| exp_config | `fo/exp_config.csv` | 调整经验值获取参数 | 低 |

## 需要同步的配置

- [ ] **user_level_config** (`fo/user_level_config.csv`)
- [ ] **reward_config** (`fo/reward_config.csv`)

---

*报告由 Git AI 配置分析器自动生成*
```

### 控制台输出示例

```
======================================================================
Git AI 配置分析报告
======================================================================
分析时间: 2026-02-02 15:30:00
仓库路径: C:\gdconfig
分析目录: fo/
当前分支: feature/user-system
比较基准: bugfix
提交范围: bugfix..HEAD
变更配置数: 3
功能新增配置: 2
高优先级变更: 1

----------------------------------------------------------------------
AI 分析总结
----------------------------------------------------------------------
本次分析发现 3 个配置表发生变更...

----------------------------------------------------------------------
功能新增配置（重点关注）
----------------------------------------------------------------------

[user_level_config]
  文件: fo/user_level_config.csv
  摘要: 新增用户等级配置表，支持新的等级系统
  目的: 实现新的用户成长体系
  影响: 用户系统、经验系统、奖励系统
  优先级: 高
  需要同步: 是

[reward_config]
  文件: fo/reward_config.csv
  摘要: 新增 5 条等级奖励配置项
  ...

----------------------------------------------------------------------
所有变更列表
----------------------------------------------------------------------
  [+] user_level_config: 新增用户等级配置表...
  [M] reward_config: 新增 5 条等级奖励配置项
  [M] exp_config: 调整经验值获取参数

======================================================================
```

---

## 技巧和最佳实践

### 1. 日常开发

```bash
# 使用快速脚本
scripts\quick_analyze.bat
```

### 2. 重要发布

```bash
# 使用 GPT-4 详细分析
python src\main.py --ai-model gpt-4 --format all
```

### 3. 成本优化

```bash
# 先用无 AI 模式查看
python src\main.py --no-ai --format console

# 如果发现重要变更，再用 AI 详细分析
python src\main.py --format markdown
```

### 4. 团队协作

```bash
# 生成报告并分享
python src\main.py --format markdown --output reports\team_review.md
# 将 team_review.md 添加到 Pull Request 描述中
```

---

*更多示例请参考 [USAGE.md](../USAGE.md)*
