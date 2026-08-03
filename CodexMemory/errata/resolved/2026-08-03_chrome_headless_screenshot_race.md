# Chrome headless 截图完成与文件检查竞态

- 日期：2026-08-03
- 任务：验证 X3 礼包主数据 HTML 报告视觉布局
- 现象：同一 PowerShell 调用里先运行 Chrome headless 截图、紧接 `Get-Item`，`Get-Item` 先报文件不存在，但 Chrome 随后输出已写入截图。
- 根因：Chrome headless 主进程在截图真正落盘前返回/派生子进程，后续文件检查发生竞态。
- 处理：拆成独立的后续只读检查与视觉查看；以后截图命令与文件读取分两次工具调用。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(Codex运行时)。归并 feedback_shell_composite_exitcode.md:截图后轮询等文件就绪
- 状态：resolved
