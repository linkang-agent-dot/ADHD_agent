# X3 补偿调查开工路径漂移与 Errata README 重复误址

- 日期：2026-08-03
- 任务：调查 2026-07-30 X3 拼图活动误上线玩家，并准备补偿邮件
- 现象：按会话 AGENTS 文本读取 `.Codex\projects\...\memory` 四份知识库失败；随后又误读 `errata\open\README.md` 失败。
- 根因：本机共享知识库实际仍在 `.claude\projects\...\memory`；Errata 说明位于 `errata\README.md`，此前已有同类记录但本轮未先检索复用。
- 处理：通过实际目录与 `rg --files` 定位正确路径；后续读取共享 KB 先验证根目录存在，Errata 模板固定读取根目录 README。
- 状态：open
