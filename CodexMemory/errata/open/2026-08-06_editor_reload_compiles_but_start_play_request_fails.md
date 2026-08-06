# Editor 重载编译成功但进入 Play 请求失败

- 日期：2026-08-06
- 任务：MCP 验收航海奖励随机修复。
- 现象：`editor_reload.py reload --project x3-project/client` 完成编译（88.44s、hasErrors=false），随后在 `start_play_mode` 报 `Failed to request Play Mode`。
- 根因：domain reload 后 HTTP 桥虽已恢复到可完成编译响应，但进入 Play 的控制请求未成功；业务代码编译本身没有错误。
- 处理：先用 `editor_reload.py status` 读取实际状态，再单独调用 `start`，避免重复完整重编译。
- 状态：open。
