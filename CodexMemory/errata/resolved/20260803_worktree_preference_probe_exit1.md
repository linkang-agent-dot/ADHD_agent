# Worktree 目录偏好探测因无匹配返回退出码 1
- 日期：2026-08-03
- 任务：为 Skill 同步器建立隔离 worktree。
- 现象：候选目录均不存在，CLAUDE.md 也没有 worktree 目录偏好；`Select-String` 无匹配使组合命令退出码为 1。
- 处理：已有输出足以确认“无现有目录、无既定偏好”；按 worktree 流程向用户选择项目内或全局目录，不把无匹配当功能故障。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 同族归并 feedback_shell_composite_exitcode.md
- 状态：resolved
