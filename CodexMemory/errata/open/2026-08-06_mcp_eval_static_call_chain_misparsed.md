# Unity MCP eval 静态方法返回值链被误解析

- 日期：2026-08-06
- 场景：尝试 `WndMgr.GetByTypeName(...).gameObject.name` 读取活动 UI 根节点。
- 现象：反射派发器错误地在静态类型 `UI.WndMgr` 上查找 `gameObject`，报 MissingMemberException。
- 原因：轻量 eval 解析器未正确处理带字符串参数的静态调用后继续成员链。
- 正确做法：用 `invoke-chain` 分步骤调用静态方法再读成员，或通过允许多命令/变量的 probe/feval 工具处理。
- 防复发：MCP eval 对“方法调用返回值继续链式取成员”不稳定，改用明确的链式调用接口。
