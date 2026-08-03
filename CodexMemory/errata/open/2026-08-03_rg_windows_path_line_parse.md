# rg 输出含 Windows 盘符时不能直接按冒号取行号

- 日期：2026-08-03
- 任务：复核 Codex hooks / sub-agent 原生能力
- 现象：对 `rg -n` 输出执行 `($_ -split ':')[1]` 并转整数时，取到正文而非行号，连续产生类型转换错误。
- 根因：Windows 完整路径本身含 `C:`，冒号分隔位置与 POSIX 输出不同。
- 处理：PowerShell 中使用 `Select-String` 返回的结构化 `LineNumber`，或限制分割次数并显式处理盘符。
- 状态：open
