# DebugUtils editor_reload 进入 Play 使用 start

- 日期：2026-08-06
- 场景：退出 Unity Play 后重新进入，以加载最新配置 bytes。
- 错误：调用 `editor_reload.py play`。
- 结果：argparse 提示有效子命令只有 `status, stop, start, reload`。
- 正确做法：使用 `editor_reload.py start` 进入 Play。
- 防复发：DebugUtils 的 PlayMode 动作命名为 `start/stop`，不是 `play/stop`；执行前按脚本命令表核对。
