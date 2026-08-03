# 共享项目记忆路径误用 .Codex
- 日期：2026-08-03
- 任务：沉淀 X3 8–10 月周年美需新口径
- 现象：先按旧摘要尝试读取 `C:\Users\linkang\.Codex\projects\...\memory`，目录不存在；实际唯一真源在 `C:\Users\linkang\.claude\projects\...\memory`。
- 修正原则：记忆读写严格使用会话 AGENTS.md 指定的 `.claude` 路径，不从历史摘要或同名目录猜测。
- 状态：open
