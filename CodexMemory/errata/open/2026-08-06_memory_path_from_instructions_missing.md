# 指令中的旧 Codex memory 路径当前不存在

- 日期：2026-08-06
- 场景：查找本地服 telnet 工作流。
- 错误：直接把 AGENTS 中的 `C:\Users\linkang\.Codex\projects\C--Users-linkang\memory` 作为 rg 搜索根。
- 结果：目录不存在，rg exit 1。
- 正确做法：先用 `Test-Path` 验证知识库根；当前应优先在 `C:\ADHD_agent\CodexMemory`、`C:\ADHD_agent\KB` 或实际存在的共享 memory 根中检索。
- 防复发：文档路径可能迁移，任何非工作区固定路径在递归搜索前先做存在性检查。
