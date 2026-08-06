# Unity MCP 反射读取数组长度用 Length

- 日期：2026-08-06
- 场景：读取 `CAllRewardInfos.IDs` 奖励行数组。
- 错误：对运行时实际类型 `System.Int32[]` 求 `.Count`。
- 结果：MCP 反射派发器报 `MissingMemberException: Int32[].Count not found`。
- 正确做法：数组使用 `.Length`；只有集合类型才读取 `.Count`。
- 防复发：配置生成属性虽声明为 `IReadOnlyList<int>`，反序列化后可能是数组；MCP 反射按实际类型解析成员。
