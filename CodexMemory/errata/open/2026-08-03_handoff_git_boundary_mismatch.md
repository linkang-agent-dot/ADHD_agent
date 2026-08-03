# Handoff 文件 staging 使用了错误的 Git 根相对路径

- 日期：2026-08-03
- 任务：提交 BTW/sub-agent handoff 实现
- 现象：在 `git -C C:\ADHD_agent add CodexMemory/...` 中，部分文件仍显示未跟踪，且 errata pathspec 报不存在。
- 根因：尚未重新确认 `C:\ADHD_agent` 与 `C:\ADHD_agent\CodexMemory` 的真实 Git 边界/嵌套仓状态，就混用两套相对路径。
- 处理：立即读取两处 `rev-parse --show-toplevel`、文件存在性和 ignore 结果；按真实仓根分别精确 staging，不跨 Git 边界。
- 状态：open
