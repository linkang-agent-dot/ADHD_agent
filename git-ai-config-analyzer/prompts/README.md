# AI 提示词模板

本目录包含 AI 分析使用的提示词模板。

## 文件说明

- `config_analysis_template.txt` - 单个配置文件分析的提示词模板
- `summary_template.txt` - 整体总结报告的提示词模板

## 使用说明

当前这些模板是参考模板，实际使用的提示词已经硬编码在 `src/ai_analyzer.py` 中。

如果需要自定义提示词，可以：

1. 修改这些模板文件
2. 更新 `ai_analyzer.py` 中的 `_build_analysis_prompt` 和 `_build_summary_prompt` 方法，从文件读取模板
3. 使用 Python 的字符串格式化功能填充变量

## 模板变量

### config_analysis_template.txt 变量：
- `{file_path}` - 文件路径
- `{table_name}` - 表名
- `{change_type}` - 变更类型
- `{commits}` - 相关提交信息
- `{added_lines}` - 新增的行
- `{removed_lines}` - 删除的行
- `{context_lines}` - 上下文行

### summary_template.txt 变量：
- `{total_changes}` - 总变更数
- `{new_feature_count}` - 功能新增配置数
- `{high_priority_count}` - 高优先级变更数
- `{changes_summary}` - 所有变更的摘要列表
