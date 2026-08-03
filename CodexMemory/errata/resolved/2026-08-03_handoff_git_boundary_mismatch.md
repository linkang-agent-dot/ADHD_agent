# Handoff 文件 staging 使用了错误的 Git 根相对路径

- 日期：2026-08-03
- 任务：提交 BTW/sub-agent handoff 实现
- 现象：在 `git -C C:\ADHD_agent add CodexMemory/...` 中，部分文件仍显示未跟踪，且 errata pathspec 报不存在。
- 根因：尚未重新确认 `C:\ADHD_agent` 与 `C:\ADHD_agent\CodexMemory` 的真实 Git 边界/嵌套仓状态，就混用两套相对路径。
- 处理：已验证两处 `rev-parse --show-toplevel` 均为 `C:/ADHD_agent`；后续统一按该仓根使用 `CodexMemory/...` pathspec。本次 handoff 边界修复已按该路径精确 staging 并核对缓存区清单。
- 状态：resolved
