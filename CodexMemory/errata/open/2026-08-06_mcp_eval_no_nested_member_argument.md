# Unity MCP eval 不支持复杂成员表达式作调用参数

- 日期：2026-08-06
- 场景：把 `RewardInfos[81901].IDs[0]` 直接作为 `CReward.I(...)` 的参数。
- 现象：表达式解析器报 FormatException，无法解析嵌套成员字面量。
- 原因：EditorDebugMCP 的轻量表达式语法不等同完整 C#，调用参数不支持该复杂链。
- 正确做法：分两次求值：先读取 ID，再把得到的常量传给下一次 `CReward.I(<id>)`；复杂链使用 invoke-chain。
- 防复发：MCP eval 遇到嵌套调用参数时拆成原子步骤，不假设支持完整 C# 语法。
