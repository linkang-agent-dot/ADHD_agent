# rg 零匹配被组合命令误判为工具失败
- 日期：2026-08-03
- 任务：定位 Codex CLI 验收纪要在 KB 方法论目录中的归档位置
- 现象：目录枚举成功，但末尾 `rg -n "domain/agent开发|Codex CLI"` 无匹配并返回 exit 1，导致整次 `shell_command` 显示 `Script failed`。
- 初判根因：PowerShell 组合命令未单独接住 `rg` 的“无匹配”退出码；后续探索性搜索应显式区分 exit 1（零结果）与真实执行错误，或拆成独立调用。
- 状态：open

## 复现 2026-08-03 · X3 周年美需
- 在同一条 PowerShell 中先 `rg` HTML 命中、再跨目录搜索生成器；第二个 `rg` 无匹配返回 exit 1，导致整次 `shell_command` 被标成失败并把内嵌 base64 命中输出放大。
- 后续对单文件自包含 HTML：先剥离 `data:image/...;base64` 再查文本；生成器搜索单独执行并显式接住 exit 1。
