# Windows rg 路径参数再次误用通配符

- 日期：2026-08-06
- 场景：定位 Center 跨服活动管理模块。
- 错误：把 `C:\x3-project\server\CenterServer*` 作为 rg 搜索根。
- 结果：Windows 报路径语法错误（os error 123）。
- 根因：rg 不展开路径参数中的 Windows 通配符；这是已有教训的重复发生。
- 正确做法：用 `rg --files C:\x3-project\server | rg '^...CenterServer'` 先筛文件，或把明确存在的 `CenterServer`、`CenterServer.Hotfix` 路径分别传入。
- 防复发：搜索根目录永远写已解析的明确路径，不在 path 参数中使用 `*`。
