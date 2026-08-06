# x3-feature-test 引用的 DebugUtils 全局路径已失效

- 日期：2026-08-06
- 任务：修复并通过 MCP 验收航海之路随机奖励 BUG。
- 现象：按旧惯例读取 `C:\Users\linkang\.claude\skills\DebugUtils\SKILL.md` 失败。
- 根因：DebugUtils 当前随 X3 工程维护在 `C:\x3-project\.claude\skills\DebugUtils\`（Codex 镜像在 `.codex\skills`），不在用户全局 skills 根。
- 处理：用 `rg --files` 定位真实入口，后续从工程内路径读取。
- 状态：open。
