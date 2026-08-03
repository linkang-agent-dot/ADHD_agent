# PowerShell 短函数名 H 与 Get-History 别名冲突

- 日期：2026-08-03
- 任务：复现 Codex hook trust hash
- 现象：定义 `function H` 后调用 `H $_` 仍被解析为 `Get-History`，导致把 JSON 当作历史记录 ID 转换失败。
- 根因：使用了 PowerShell 内置别名 `h` 的冲突短名，未采用任务专用函数名。
- 处理：改用唯一函数名 `Get-HookSha256` 后，PreToolUse 复现值与 Codex 已知哈希逐字节一致。
- 状态：resolved
