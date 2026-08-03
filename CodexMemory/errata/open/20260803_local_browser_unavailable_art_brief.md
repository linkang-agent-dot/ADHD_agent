# 本地 HTML 验收时内置浏览器不可用
- 日期：2026-08-03
- 任务：检查并完善 X3 周年庆美需 HTML 的页面呈现
- 现象：按 Browser skill 初始化后调用 `agent.browsers.getForUrl(file:///...)` 返回 `No browser is available`，无法在内置浏览器直接渲染本地 HTML；随后又按用户提示误读了不存在的 `errata/open/README.md`，实际 README 在 `errata/README.md`。
- 初判根因：桌面日志已实证当前会话 `019fc63d-...` 缺少 ChatGPT browser route（`No ChatGPT browser route is available`）；插件已启用、通信管道存在、应用也判定 `browser_use available=true`，因此不是 file URL、插件缺失或管道故障，而是该会话没有被桌面渲染器注册到浏览器侧栏。历史正常日志在切入具体 `/local/<conversationId>` 路由后会出现 `set browser route tab mode`，本会话缺这条。需通过 UI 重新进入本会话/刷新窗口触发路由注册，再复测 `agent.browsers.list()`。另：错误仓 README 路径在用户提示与实际目录结构之间存在偏差，实际在 `errata/README.md`。
- 状态：open

## 复测 14:18
- 用户切到其他会话再切回后，`agent.browsers.list()` 仍返回 `[]`。
- 新日志仍报同一会话缺少 browser route，且没有出现历史正常链路中的 `set browser route tab mode`。
- 说明仅切换会话不足以恢复；下一步验证桌面窗口刷新/重启是否会重建会话路由。

## 用户纠正 · 根因确认
- 用户明确当前入口是 Codex 命令行，不是桌面会话。我此前让用户切换会话、`Ctrl+R` 刷新桌面窗口，属于错误场景假设。
- 根因：CLI 会话没有桌面渲染器与浏览器侧栏，本就不会注册 ChatGPT browser route；日志里的 `No ChatGPT browser route` 是入口能力不匹配，不是待修的桌面连接故障。
- 正确处理：CLI 下检查本地 HTML 改用本机 Chrome headless 静态渲染/截图；若任务明确需要可交互的 Browser 插件，则必须换到支持 in-app browser 的桌面入口，不能在 CLI 内“修出”侧栏。

## CLI fallback 首次执行竞态
- Chrome 控制台随后打印 `199885 bytes written`，截图实际成功生成，但 PowerShell 在文件落盘前先执行了 `Test-Path`，误抛“Chrome 未生成截图”。
- 后续 headless 截图命令必须在 Chrome 返回后对目标文件做短轮询，不能紧接着单次 `Test-Path`。
