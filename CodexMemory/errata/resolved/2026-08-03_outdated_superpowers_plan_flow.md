# 过时的 superpowers 规划流程不应覆盖当前 Codex CLI 原生流程

- 日期：2026-08-03
- 任务：实现 BTW/sub-agent 回主对话的持久化机制
- 现象：设计获批后机械执行 `brainstorming → writing-plans → using-git-worktrees` 的旧流程，用户明确纠正很多 skill 已落后，应按当前 Codex CLI 原生流程实施。被中断的 worktree 初始化还留下了 `locked initializing` 的半成品工作树。
- 根因：把 skill 内的流程要求当成高于当前运行时能力与用户最新指令的固定编排，没有根据 Codex CLI 已具备的原生 hooks、SubagentStart/SubagentStop 和当前脏仓状态裁剪流程。
- 处理：立即停止 writing-plans 及其派生流程；后续以当前 Codex manual 和 CLI 实际能力为准，直接用原生 hooks + 小型可测试脚本实施。半成品 worktree 不自行删除，遵守清理前确认规则。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 用户已裁决:旧superpowers流程让位Codex原生流程;半成品worktree已清理
- 状态：resolved
