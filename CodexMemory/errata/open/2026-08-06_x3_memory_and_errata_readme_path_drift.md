# X3 memory 与 errata README 路径漂移

- 日期：2026-08-06
- 任务：只读评估至尊主题英雄主页 UI 改造需求
- 现象：按会话 AGENTS 指令读取 `C:\Users\linkang\.Codex\projects\C--Users-linkang\memory\reference_x3_*.md` 失败；随后误读 `CodexMemory\errata\open\README.md` 也失败。
- 根因：当前机器的共享项目 memory 实际仍在 `.claude\projects\C--Users-linkang\memory`；errata 说明文件位于 `errata\README.md`，不在 `open` 子目录。
- 处理：用 `rg --files` / `Get-ChildItem` 确认真实路径，改从 `.claude` memory 与 errata 根目录读取；本轮未修改 X3 工程。
- 状态：open
