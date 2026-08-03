# skill 卸载后同步 inventory 未保留 excluded 条目

- 日期：2026-08-03
- 任务：Codex 旧元流程 skill 清理
- 现象：活跃目录移出后，sync dry-run 为 0 blockers 且无 add，但 inventory 的 `excluded` 数量从 10 变成 0，触发“必须仍有 10 条 excluded”断言。
- 根因：待核查 `.claude\skills` 与 `.agents\skills` 是否存在共享/联动关系；该断言把“不会重建”错误地限定成“source 必须仍存在并标为 excluded”。
- 处理：先只读核查源目录和链接关系；最终验证应以排除名单存在、无 add/modify 操作、活跃目录不存在三者为准。
- 状态：open
