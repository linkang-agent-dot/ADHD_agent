# X3 知识库与错误仓路径漂移导致读取失败

- 日期：2026-08-03
- 任务：查询 X3 礼包内容并更新 dim.iap 主数据表
- 现象：按会话 AGENTS.md 中 `.Codex\projects\...` 路径读取 X3 memory 失败；随后误把错误仓 README 读成 `errata\open\README.md`，再次报路径不存在。
- 根因：本机共享项目 memory 的实际真源仍为 `.claude\projects\...`；错误仓规则文件位于 `CodexMemory\errata\README.md`，`open\` 只存待复核记录。
- 处理：改读实际真源路径；按 `errata\README.md` 格式记录本条。后续遇 AGENTS.md 与磁盘路径不一致时先用 `rg --files` 定位，避免猜路径。
- 状态：open
