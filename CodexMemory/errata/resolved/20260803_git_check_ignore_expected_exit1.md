# git check-ignore 用退出码 1 表示目标尚未忽略
- 日期：2026-08-03
- 任务：创建项目内 `.worktrees` 前验证忽略规则。
- 现象：`git check-ignore -v .worktrees` 返回退出码 1，工具层显示失败。
- 处理：这是“未匹配任何 ignore 规则”的预期语义，不是命令故障；按流程向 `.gitignore` 添加 `/.worktrees/` 后重新验证。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 同族归并 feedback_shell_composite_exitcode.md
- 状态：resolved
