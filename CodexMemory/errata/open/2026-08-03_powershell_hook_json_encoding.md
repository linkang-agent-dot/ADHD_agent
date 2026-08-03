# PowerShell 管道模拟 hook 时中文 JSON 编码失败

- 日期：2026-08-03
- 任务：BTW / sub-agent 持久化回主对话机制
- 现象：用 PowerShell `ConvertTo-Json | python ... hook` 模拟 `SubagentStop` 时，中文 `last_assistant_message` 触发 `utf-8 codec can't encode ... surrogates not allowed`，留下空的 `final-handoff.md`。
- 根因：Windows PowerShell 管道到原生进程时的文本编码与 Python 标准输入解码不一致，中文经过管道后形成代理字符。
- 处理：测试事件尽量使用 ASCII，或直接用 `apply_patch` 补写 UTF-8 记录；真实 Codex hook 由运行时直接传 JSON，不依赖 PowerShell 文本管道。
- 状态：open
