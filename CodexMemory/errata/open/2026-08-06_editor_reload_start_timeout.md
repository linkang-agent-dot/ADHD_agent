# DebugUtils editor_reload start 超时需复核实际状态

- 日期：2026-08-06
- 场景：Unity 退出 Play 后用 `editor_reload.py start` 重新载入配置。
- 现象：命令等待约 126 秒后以 exit 124 超时，无输出。
- 风险：命令超时不等于 Unity 未进入 Play，重复 start 可能扰动当前 Editor。
- 正确做法：超时后先运行 `editor_reload.py status` 和 MCP `ping/eval isPlaying`，根据实际状态决定是否重试。
- 防复发：Editor 启动类命令超时后只做只读状态确认，禁止盲目重复启动。
