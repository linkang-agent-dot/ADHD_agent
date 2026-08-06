# PowerShell Select-String 复杂正则引号误用

- 日期：2026-08-06
- 场景：在 PowerShell 中定位 Python argparse 参数定义。
- 错误：把含双引号和管道符的复杂正则直接嵌进双引号命令，导致参数被 PowerShell 拆坏。
- 结果：`Select-String` 报 positional parameter 错误。
- 正确做法：文本定位优先使用 `rg -n 'pattern' <file>`；确需 `Select-String` 时用安全的单引号表达式或拆成多个简单 pattern。
- 防复发：遵守全局规则，搜索文本首先使用 `rg`，避免在 PowerShell 命令字符串里叠加多层引号。
