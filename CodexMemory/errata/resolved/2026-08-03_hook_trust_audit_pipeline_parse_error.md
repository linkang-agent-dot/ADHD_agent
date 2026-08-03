# Hook 信任审计的 PowerShell 管道出现空管道语法错误

- 日期：2026-08-03
- 任务：逐项核对 handoff hooks 的信任状态
- 现象：在嵌套 `foreach` 后直接接 `| Format-Table`，PowerShell 报 `An empty pipe element is not allowed`。
- 根因：语句块输出与尾部管道的组合写法在当前解析上下文中不合法；后续首次比对还需把 TOML key 中转义的双反斜杠规范化后才能和实际 Windows 路径匹配。
- 处理：改为显式数组收集、规范化 TOML 路径后再格式化。复核结果为 9 个实例中原 4 个受信任，新增 5 个未信任。
- 状态：resolved
