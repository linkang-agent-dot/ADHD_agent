# 指定 task-checker 时错误同时使用 full-history fork

- 日期：2026-08-03
- 任务：独立验收 Codex hook 信任配置
- 现象：`spawn_agent` 同时指定 `agent_type=task-checker` 与 `fork_turns=all`，工具拒绝并提示 full-history fork 会继承父 agent 类型。
- 根因：忽略了协作工具关于“显式 agent type 需使用 none 或有限 turns fork”的约束。
- 处理：改用 `fork_turns=none` 并在任务消息中完整提供验收路径和目标；task-checker 随后完成检查，blockers=0。
- 状态：resolved
