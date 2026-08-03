# Codex memory 必须位于 ADHD_agent Git 仓库
- 日期：2026-08-03
- 任务：建立 Codex 独立持久记忆。
- 现象：首次把记忆建在 `C:\Users\linkang\.codex\memory\`，虽然与 Claude 隔离，但未进入用户已有的 Git 定期同步链路。
- 根因：只考虑模型能力隔离，没有同时检查持久化、版本管理和跨设备同步边界。
- 处理：把唯一真源迁至 `C:\ADHD_agent\CodexMemory\`；`.codex\memory` 仅留兼容指针；errata 也改入同一仓库。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 已落地:CodexMemory迁入ADHD_agent Git仓
- 状态：resolved
