# Handoff hooks 多文件补丁因 AGENTS 上下文漂移整体失败

- 日期：2026-08-03
- 任务：接入 BTW/sub-agent 持久化 handoff hooks
- 现象：一次 `apply_patch` 同时修改 hooks.json、全局 AGENTS.md 并新增 handoffs 文档；其中 AGENTS.md 的预期句子与真实文件略有差异，导致整个补丁校验失败，其他本可应用的文件也全部未落地。
- 根因：没有先读取 AGENTS.md 尾部的精确上下文，且把多个独立文件绑在同一个补丁事务中，放大了单点上下文漂移的影响。
- 处理：先读取目标文件精确尾部；之后按 hooks.json、AGENTS.md、handoffs 文档拆成独立小补丁，逐个验证。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 同族归并 feedback_apply_patch_context_discipline.md:多文件拆小补丁
- 状态：resolved
