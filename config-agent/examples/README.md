# 使用示例

本目录包含各种使用示例，展示如何使用 Git 配置变更检查工具。

## 示例列表

### 1. 基本检查 (`example_basic.py`)

最简单的使用方式，使用默认配置检查配置变更。

```bash
python examples/example_basic.py
```

**功能**：
- 连接到 Git 仓库
- 分析 fo/ 目录下的变更
- 在控制台显示报告

---

### 2. Markdown 报告生成 (`example_markdown_report.py`)

生成 Markdown 格式的报告文件。

```bash
python examples/example_markdown_report.py
```

**功能**：
- 分析配置变更
- 生成 Markdown 格式报告
- 保存到 `reports/config_changes.md`

**输出示例**：
```markdown
# Git 配置变更检查报告

## 摘要信息
- **检查时间**: 2026-02-02 14:30:00
- **变更表数**: 5

## 变更表汇总
### 新增 (1个)
- **new_config**: `fo/new_config.csv`
```

---

### 3. JSON 导出 (`example_json_export.py`)

导出 JSON 格式的结构化数据，便于程序化处理。

```bash
python examples/example_json_export.py
```

**功能**：
- 生成 JSON 格式报告
- 保存到 `reports/config_changes.json`
- 适合自动化处理和 API 集成

**JSON 结构**：
```json
{
  "summary": {
    "check_time": "2026-02-02 14:30:00",
    "total_commits": 3,
    "total_tables": 5
  },
  "changes_by_type": {
    "A": [...],
    "M": [...]
  },
  "tables": [...],
  "commits": [...]
}
```

---

### 4. 自定义提交范围 (`example_custom_range.py`)

展示如何使用不同的提交范围进行检查。

```bash
python examples/example_custom_range.py
```

**功能**：
- 比较两个分支：`main..develop`
- 检查最近 N 次提交：`HEAD~5..HEAD`
- 检查特定提交范围：`abc123..def456`

---

### 5. 多格式输出 (`example_multi_format.py`)

一次生成所有格式的报告。

```bash
python examples/example_multi_format.py
```

**功能**：
- 控制台显示报告
- 生成 Markdown 文件
- 生成 JSON 文件

---

## 运行所有示例

### Windows

```bash
scripts\run_all_examples.bat
```

### Linux/Mac

```bash
# 逐个运行
python examples/example_basic.py
python examples/example_markdown_report.py
python examples/example_json_export.py
python examples/example_custom_range.py
python examples/example_multi_format.py
```

---

## 自定义使用

### 修改仓库路径

在示例脚本中修改 `CheckConfig`：

```python
config = CheckConfig(
    repo_path=r"D:\your_repo",  # 修改为你的仓库路径
    target_dir="config/",       # 修改目标目录
    base_branch="develop"       # 修改基准分支
)
```

### 修改输出路径

```python
config = CheckConfig(
    markdown_output_path="my_reports/report.md",
    json_output_path="my_reports/data.json"
)
```

---

## 常见问题

### Q: 示例运行失败？

**A**: 请检查：
1. 仓库路径是否正确
2. 是否为有效的 Git 仓库
3. 目标目录是否存在变更

### Q: 如何只检查特定分支？

**A**: 使用 `--commit-range` 参数：

```python
config = CheckConfig(
    commit_range="main..feature-branch"
)
```

### Q: 如何忽略某些文件？

**A**: 可以在 `ChangeAnalyzer` 中添加过滤逻辑，修改 `analyze_changes` 方法。

---

## 下一步

- 查看 [测试用例](../tests/) 了解更多使用方式
- 阅读 [项目文档](../README.md) 了解详细配置
- 参考 [实现计划](../docs/git_config_check_plan.md) 了解技术细节
