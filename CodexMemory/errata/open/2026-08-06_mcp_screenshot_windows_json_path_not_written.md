# MCP 截图的 Windows JSON 路径未落文件

- 日期：2026-08-06
- 任务：截取航海随机修复的 Unity 验收画面。
- 现象：`ScreenCapture.CaptureScreenshot` 调用返回 ok，但传入带反斜杠和额外 JSON 引号的路径后目标文件不存在。
- 根因：`client.py --args` 会先尝试 JSON 解析，Windows 反斜杠路径与 PowerShell 引号组合导致实际字符串参数不可靠。
- 处理：改用正斜杠绝对路径作为普通字符串参数，调用后轮询文件存在与非零长度。
- 状态：open。
