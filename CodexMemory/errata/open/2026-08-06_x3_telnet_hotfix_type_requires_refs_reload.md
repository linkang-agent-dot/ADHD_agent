# X3 telnet Roslyn 引用未刷新导致 Hotfix 类型不可见

- 日期：2026-08-06
- 任务：通过本地 telnet 调用 `ActivityMeta.UpdateActivityRankScore`，给 3080/3090 两个玩家写跨服榜测试分。
- 现象：脚本已有 `using Play`，但编译仍报 `CS0246 ActivityMeta could not be found`。
- 根因：`ActivityMeta` 位于运行时加载的 GameServer.Hotfix 程序集；telnet Roslyn 初始化时的程序集引用集未包含/未刷新该 Hotfix 引用。`ReloadGameServer` 不等于刷新脚本引用。
- 处理：先在各 Game telnet 执行 `!refs reload`，再运行表达式；必要时用完整类型名复核。
- 补充失误：`!refs reload` 的返回明确提示会创建新 ScriptState、丢失 `pm` 等初始化变量，随后的表达式仍直接使用 `pm`，报 `CS0103`。修正为刷新后在表达式内重新声明 `using Play; var pm=ModuleHelper.GetModule<PlayerMgr>();`，不依赖旧 state。
- `!refs reload` 仍未把自定义 Hotfix 加进可编译引用（`added=0`），直接泛型引用 `ActivityMeta` 继续 CS0246；尝试 `dynamic` 又因脚本引用集缺 `Microsoft.CSharp.RuntimeBinder` 报 CS0656。最终改用基类可见的 `GetMeta("ActivityMeta")` + `System.Reflection.MethodInfo.Invoke`，完全绕开编译期 Hotfix 类型引用。
- 状态：open
