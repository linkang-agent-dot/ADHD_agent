# collaboration 子代理未触发本地 Subagent hooks

- 日期：2026-08-03
- 任务：BTW / sub-agent 持久化回主对话机制真实链路测试
- 现象：通过 `collaboration.spawn_agent` 启动真实测试子代理后，子代理未收到 checkpoint 注入；handoffs 中也没有自动生成对应记录。
- 根因：当前 collaboration 子代理运行时与本机 Codex CLI hooks 是两套生命周期；本地 `SubagentStart` / `SubagentStop` hook 不会拦截 collaboration 工具事件。
- 处理：保留原生 CLI hook 覆盖，同时补充由主 agent 显式执行的 start/message/final 落盘命令，作为运行时无关的接力层。
- 状态：open
