# HTML 单行 CSS 补丁上下文不完整

- 日期：2026-08-03
- 任务：修正 X3 礼包 HTML 表头 sticky 偏移
- 现象：首次 apply_patch 只带了目标 `th{...}` 片段，但实际同一行前面还有 `.tablewrap...table...`，验证匹配失败。
- 根因：压缩 CSS 为长单行，补丁上下文没有覆盖真实整行。
- 处理：先只读定位真实行，再用完整单行做精确替换。后续改压缩产物先检索实际上下文。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(Codex运行时)。已归并入 CodexMemory feedback_apply_patch_context_discipline.md
- 状态：resolved
