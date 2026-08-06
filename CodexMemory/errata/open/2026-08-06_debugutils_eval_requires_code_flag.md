# DebugUtils eval 必须使用 --code

- 日期：2026-08-06
- 场景：用 `DebugUtils/scripts/client.py` 对 Unity Editor HTTP MCP 执行表达式。
- 错误：将表达式作为 `eval` 的位置参数传入，触发 argparse 报错：缺少 `--code`。
- 原因：该客户端的 `eval` 子命令只接受显式 `--code CODE`，不是位置参数。
- 正确做法：使用 `python client.py --port <port> eval --code "<C# expression>"`。
- 防复发：发起第一次 MCP eval 前先按 SKILL 示例核对子命令参数；后续统一使用 `--code`。
