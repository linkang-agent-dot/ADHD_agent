# functions.exec V8 isolate 不提供 TextEncoder

- 日期：2026-08-06
- 任务：用 Base64 安全传递 RuleTips40001 的 Unicode 多语言文本
- 现象：在 `functions.exec` JavaScript 中调用 `new TextEncoder()` 立即报 `ReferenceError: TextEncoder is not defined`，尚未调用 shell、未写文件。
- 根因：该 V8 isolate 虽支持常规 JS，但未暴露 Web API `TextEncoder`，不能按浏览器/Node 环境假设。
- 处理：改用纯 JavaScript UTF-8 编码函数（按 code point 生成 UTF-8 bytes 后 `btoa`），或让 PowerShell 从 JSON/字符数组构造；写入前仍先 dry-run。
- 状态：open
# 复发记录

- 2026-08-06：马戏节 dev 文案定向校验脚本再次误用了 `TextEncoder`，在执行 shell 前即失败；后续统一改用 `btoa(unescape(encodeURIComponent(text)))` 兼容编码。
- 同次绕道确认该 isolate 也没有 `btoa`；可靠做法改为 `encodeURIComponent`，再由 PowerShell `[Uri]::UnescapeDataString()` 还原 UTF-8 脚本。
