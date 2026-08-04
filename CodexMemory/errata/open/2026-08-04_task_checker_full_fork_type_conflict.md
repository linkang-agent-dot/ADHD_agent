# task-checker 与 full-history fork 参数冲突

- 日期：2026-08-04
- 场景：X3 101831 配置收工前派独立 task-checker 验收。
- 现象：`spawn_agent` 同时指定 `agent_type=task-checker` 与 `fork_turns=all`，工具拒绝：full-history fork 会继承父 agent 类型，不能再覆盖 agent type。
- 根因：没有遵守协作工具的模型/类型继承约束。
- 绕行：使用 `fork_turns=none`，把验收范围、文件路径、目标口径和输出格式完整写入任务消息。
- 后续规则：需要专用 agent 类型时一律不用 full-history fork；显式传递自包含上下文。
