# PowerShell 中 client.py eval 嵌套字符串引号拆参

- 日期：2026-08-06
- 场景：用 Unity MCP 求值 `string.Join(",", ...)`。
- 错误：在 PowerShell 双引号命令中嵌套 C# 双引号字符串。
- 结果：C# 表达式被拆成额外 CLI 参数，`client.py` 报 `unrecognized arguments`。
- 正确做法：优先把表达式改写为不含字符串字面量的多个只读求值（Count/索引），或使用 PowerShell 安全单引号包住完整表达式。
- 防复发：`client.py eval --code` 遇到 C# 字符串字面量时先处理 PowerShell 与 C# 双层引号，避免直接嵌套。
