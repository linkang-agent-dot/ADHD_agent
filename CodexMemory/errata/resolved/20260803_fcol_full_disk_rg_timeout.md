# FCOL 知识库全盘 rg 扫描超时且错误仓 README 路径与说明不一致
- 日期：2026-08-03
- 任务：检索 FCOL4 7 月 20 日后卡价暴涨原因。
- 现象：对 `C:\Users\linkang` 与 `C:\ADHD_agent` 做全盘 `rg` 在 65 秒后超时；随后按 AGENTS.md 所述尝试读取 `C:\Users\linkang\.codex\errata\open\README.md` 又报路径不存在，实际 README 位于 `C:\Users\linkang\.codex\errata\README.md`。
- 初判根因：检索范围包含大量会话与媒体衍生文件，未先按项目目录收窄；AGENTS.md 对 README 的“同目录”表述与实际父目录布局不一致。后续改为定向扫描 `C:\ADHD_agent\FCOL阿三资料库`、竞品目录和结构化文件。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立。检索收窄规矩已入 reference_fcol_analysis_rules.md;README路径表述已随errata迁移修正
- 状态：resolved
