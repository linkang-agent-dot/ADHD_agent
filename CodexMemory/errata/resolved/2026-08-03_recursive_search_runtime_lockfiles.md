# 全量递归搜索误扫运行时锁文件与历史会话

- 日期：2026-08-03
- 任务：调查 Claude Code/ Codex 旁支对话回传机制
- 现象：对 `.claude`、`.codex` 全量 `rg --hidden`，命中大量 session JSONL，且读取 `.codex\tmp` 与 SQLite 锁文件时报 os error 33，命令退出 1。
- 根因：搜索范围包含运行时目录、数据库和历史会话，glob 排除未覆盖深层实际路径。
- 处理：改为先枚举 settings/hooks/scripts 等配置入口，只在小范围文本文件搜索；以后禁止直接扫整个 `.codex` 运行时根。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(Codex运行时)。检索排除sessions/tmp/sqlite,同族参考 feedback_shell_composite_exitcode.md
- 状态：resolved
