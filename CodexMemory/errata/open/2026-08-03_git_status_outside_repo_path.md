# git status 不能检查仓库外绝对路径

- 日期：2026-08-03
- 任务：Codex skill 清理收工检查
- 现象：在 `C:\ADHD_agent` 执行 `git status -- C:\Users\linkang\.agents\skills\...` 返回 path outside repository。
- 根因：`git status` 的 pathspec 只能指向当前仓库工作树内路径。
- 处理：仓库外 Codex skill 用 `Test-Path`、`Get-Item` 和哈希检查；Git 只检查 `C:\ADHD_agent` 内的同步器、报告与隔离规则。
- 状态：open
