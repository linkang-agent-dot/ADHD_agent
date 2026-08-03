# 误判 Claude 与 Codex skills 已统一单源
- 日期：2026-08-03
- 任务：审计 Codex 与 Claude 资产边界。
- 现象：Codex 文档写“业务 skills 已通过 `.agents/skills` 共用，一处修改两边生效”。用户指出 `.Codex` 路径污染只出现在 `.agents` 侧，证明至少部分 skill 是实体副本。
- 实证：同名 58 个 skill 中，Claude 侧 32 个为 Junction；其余实体目录有 14 个 SKILL.md 哈希相同、8 个哈希不同。分叉名单已写入 `reference_codex_claude_asset_boundary.md`。
- 根因：根据部分 Junction 个案和既有文档，错误外推为全体系单源，没有先检查目录 LinkType 与同名文件哈希。
- 处理：纠正文档为“混合态”；后续设计 Claude→Codex 单向同步，并保留 CODEX-ONLY 附注区块与 frontmatter 校验。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 已修复:asset_boundary文档已更正+skill同步器落地,skill单源假设不再成立的问题已被同步机制解决
- 状态：resolved
