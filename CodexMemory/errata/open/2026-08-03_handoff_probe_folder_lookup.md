# handoff 探针错误假设目录名包含 session ID

- 日期：2026-08-03
- 任务：BTW / sub-agent 持久化机制真实测试
- 现象：BTW 模拟事件已成功落盘并回注，但测试脚本按 session ID 搜索会话目录，导致末尾误报 `BTW probe folder missing`。
- 根因：会话目录由首条主对话 prompt 的安全标题加 session 后缀生成，不保证包含完整 session ID。
- 处理：测试与运维定位统一读取 `handoffs/_index/<session>.json` 的 `folder` 字段，不再猜目录名。
- 状态：open
