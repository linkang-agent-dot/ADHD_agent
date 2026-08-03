# PowerShell foreach 语句块不能直接接输出管道

- 日期：2026-08-03
- 任务：盘点待清理的旧流程 skills
- 现象：`foreach (...) { ... } | Format-Table` 报 `An empty pipe element is not allowed`。
- 根因：PowerShell 解析器不会把裸 `foreach` 语句块直接当作可接管道的表达式。
- 处理：先用 `$rows = @(...foreach...)` 收集结果，再执行 `$rows | Format-Table`。同一轮后续命令复制统计模板时也必须沿用该结构；本次修正后曾再次误写裸 `foreach |`，说明不能只修单条命令。
- 状态：open
