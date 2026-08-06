# BUG 排查再次命中知识库与 errata 路径漂移

- 日期：2026-08-06
- 任务：排查 X3 航海之路奖励疑似恒为最低档。
- 现象：按会话 AGENTS 中的 `.Codex\projects\...\memory` 路径读取 4 份知识库失败；随后又误读 `errata\open\README.md`。
- 根因：未先吸收已有 errata 中的两条已知路径漂移经验，也未在批量读取前用 `Test-Path` 验证路径；errata README 的真实位置在 `errata\README.md`。
- 处理：用 `rg --files` 定位真实文件，切换到 `.claude\projects\...\memory`，并从 errata 根目录读取格式说明。
- 状态：open（重复发生，后续应把“知识库路径预检 + errata README 固定根路径”固化为开工检查）。
