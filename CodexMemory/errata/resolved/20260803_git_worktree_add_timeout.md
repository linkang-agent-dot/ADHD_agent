# git worktree add 超时
- 日期：2026-08-03
- 任务：创建 `codex/skill-sync` 隔离工作树。
- 现象：`git worktree add` 组合命令运行超过 35 秒被工具超时终止，没有返回完成状态。
- 处理：未重试创建命令；只读检查确认 worktree 已完整注册在 `C:\ADHD_agent\.worktrees\codex-skill-sync`，分支为 `codex/skill-sync`，HEAD 与主分支基线一致。超时发生在命令完成后的返回阶段。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 一次性:大仓worktree add给足超时即可
- 状态：resolved
