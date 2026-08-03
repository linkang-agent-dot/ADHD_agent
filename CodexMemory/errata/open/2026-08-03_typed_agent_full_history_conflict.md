# 专用 agent 类型不能与 full-history fork 同时使用

- 日期：2026-08-03
- 任务：Codex skill 清理收工验收
- 现象：`spawn_agent(agent_type=task-checker, fork_turns=all)` 被拒绝，提示完整历史 fork 会继承父 agent 类型。
- 根因：当前 collaboration runtime 只允许在 `fork_turns=none` 或有限正整数 fork 时显式覆盖 agent type。
- 处理：给 task-checker 提供自包含任务说明，并改用 `fork_turns=none`。
- 状态：open
