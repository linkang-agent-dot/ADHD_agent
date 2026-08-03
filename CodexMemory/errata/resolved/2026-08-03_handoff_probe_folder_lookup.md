# handoff 探针错误假设目录名包含 session ID

- 日期：2026-08-03
- 任务：BTW / sub-agent 持久化机制真实测试
- 现象：BTW 模拟事件已成功落盘并回注，但测试脚本按 session ID 搜索会话目录，导致末尾误报 `BTW probe folder missing`。
- 根因：会话目录由首条主对话 prompt 的安全标题加 session 后缀生成，不保证包含完整 session ID。
- 处理：新增 `locate --session-id` 命令，内部只读取 `handoffs/_index/<session>.json` 的 `folder` 字段；加入“目录名不含完整 session ID”回归测试。7 项测试通过，并用现存 session 实测定位到正确目录。
- 状态：resolved
