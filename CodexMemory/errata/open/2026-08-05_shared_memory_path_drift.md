# 共享 memory 路径失效，需回退到备份快照

- 日期：2026-08-05
- 任务：X3 节日外显养成线——行军皮肤排期
- 现象：按 AGENTS.md 读取 `C:\Users\linkang\.Codex\projects\C--Users-linkang\memory\reference_x3_timecycle.md` 与 `reference_festival_knowledge_graph.md` 时路径不存在；同时最初误把错误仓 README 定位到 `errata\open\README.md`，实际在 `errata\README.md`。
- 根因：AGENTS.md 登记的旧项目 memory 目录已迁移或尚未同步到当前机器；错误仓 README 位于父目录。
- 处理：从 `C:\ADHD_agent\_global_backup\claude-snapshot\memory\` 读取同名知识库，并将实际路径漂移记录在错误仓；后续需修正全局入口或恢复同步目录。

## 2026-08-06 复发

- 任务：调整 X3 马戏节排行榜奖励顺序。
- 现象：再次照 AGENTS.md 的 `.Codex\projects\...\reference_x3_timecycle.md` 读取，路径仍不存在。
- 处理：通过只读定位确认当前有效共享真源为 `C:\Users\linkang\.claude\projects\C--Users-linkang\memory\reference_x3_timecycle.md`，本轮改从该路径补读；以后先用已记录的有效路径，避免重复撞错。
- 状态：open
