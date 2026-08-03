# AGENTS 中 .Codex memory 路径在本机不存在
- 日期：2026-08-03
- 任务：加载 X3 数据查询知识库
- 现象：读取 `C:\Users\linkang\.Codex\projects\C--Users-linkang\memory\reference_ai_to_sql.md` 报路径不存在；实际文件位于 `C:\Users\linkang\.claude\projects\C--Users-linkang\memory\`。同时 errata README 实际在 `.codex\errata\README.md`，不在 `open\README.md`。
- 初判根因：AGENTS 展示路径与本机真实同步目录不一致，且误判了 errata README 所在层级；后续按 MEMORY.md 的真实位置解析相对路径，并先列目录确认。
- 状态：open

---
## 复核结论（2026-08-03，Claude 巡检）
- double-check：**成立**。根因=桌面版 Import 的机械改名 bug（.claude→.Codex）污染范围比首次发现的大：除 3 个 subagent TOML 外，.agents\skills 下 **16 个 SKILL.md** 同样中招（Codex 读这些 skill 时拿到不存在的 .Codex 路径）。
- 解决方案：批量替换 16 个文件 .Codex→.claude，复查 grep=0 残留；「Import 后必 grep \.Codex」检查范围已扩大到 .agents\skills。
- 写入位置：reference_codex_cli_docs.md 导入坑条目（范围修正）。
- 状态：resolved
