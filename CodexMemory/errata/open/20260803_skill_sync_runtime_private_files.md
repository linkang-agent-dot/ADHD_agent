# Skill 同步 dry-run 纳入运行态与密钥配置

- 日期：2026-08-03
- 任务：实现 Claude → Codex Skill 单向同步器并审计首次 dry-run。
- 现象：初次清单把 `x3-media/state/`、`state/history.jsonl`、含 `grfal_cookie`/`art_token` 字段的实际 `config.json`，以及活动部署批次结果 JSON 纳入 add/modify；查 errata 模板时还误把 README 预期在 `errata/open/README.md`，实际位于 `errata/README.md`。
- 根因：排除规则只覆盖缓存、日志和临时后缀，没有落实“运行状态与密钥配置永不进入同步”的资产边界；读取模板前未先用 `rg --files` 核实路径。
- 处理：在 apply 前的只读审计中拦截；补 `state/`、实际 `config.json`、批次/结果 JSON 排除测试与实现；模板路径改为先检索再读取。整个过程中未执行 live apply，Codex Skills 树指纹未变化。
- 状态：open
