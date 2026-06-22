# GM 命令（构造测试前置状态）

测功能时用 GM 把玩家拉到满足触发条件的状态。X3 有两类 GM 通道，**别用错**。

## 两类通道
| 通道 | 走法 | 适用 | 验证 |
|---|---|---|---|
| **客户端 GM / 玩家域** | 客户端 `BasicMeta.SendGmCmd(cmdName, rawCmd, 0)`（eval 驱动）或 Ctrl+G 窗口 | 操作**当前在线玩家**（升级/加资源/跳引导/建号/换号）| 客户端 eval 读状态变化 |
| **server-scope GM** | telnet `!gm <cmd args>`（`x3_gm.py` / `telnet_eval` 到 `23000+NodeID`）| 服务器级操作（导表 reload / 部署活动 / 删活动）| 服务端日志 |

### ⚠️ 玩家域 GM 走客户端，别走 telnet
- 实测：telnet `!gm @<playerId> <cmd>`（player-scope）在本环境**不 dispatch**（server-scope 的 `!gm <cmd>` 能跑）。
- 正解：客户端 `Logic.G.Player.GetMeta("basic").SendGmCmd(cmdName, rawCmd, 0)` —— 以在线玩家身份发，走正常 GM 链路，eval 可驱动、改动对客户端即时可见。
- **cmdName 规则**：服务端 `[GMHandler]` 方法名去掉前缀 `GM`、全小写。如 `GMAddLevel` → `gmaddlevel`。
- **rawCmd 规则**：`"<cmdName> <参数...>"`（cmdName 开头 + 空格分参数）。如升 6 级 = `SendGmCmd("gmaddlevel", "gmaddlevel 6", 0)`。
- server-scope（telnet）同样按 `method.Name.ToLower()` 匹配，`!gm <cmd>` 里 cmd 会自动补 `gm` 前缀。

## 常用 GM（已验证）
| 目的 | GM | 通道 / 调法 |
|---|---|---|
| 升级角色 N 级 | `[角色_成长]增加角色等级` `GMAddLevel(int)` | 客户端 `SendGmCmd("gmaddlevel","gmaddlevel 6",0)` ✓ |
| 跳过所有引导（进主城）| `[系统_引导]跳过所有引导` `GMSkipAllGuide` | 客户端 `SendGmCmd("gmskipallguide","gmskipallguide",0)` ✓（会先弹引导奖励/VIP窗）|
| 随机新建账号 | 客户端 `[角色_账号]随机新建账号`（`GMDebug.Account.cs`）| Ctrl+G 窗口点（建出全新号：TotalPayMoney=0、注册即时、level 1）|
| 加金砖余额 | `[系统_代币]增加代币` `GMAddInnerCurrency(int)`（×100）| 客户端 SendGmCmd —— ⚠️**只加金砖余额，不涨 TotalPayMoney** |
| 配置热更（本地服）| `[程序_热更]ReloadGameServer` | telnet `x3_gm.py "!gm ReloadGameServer"` ✓ |
| 部署单服活动 | `[活动_活动]GM部署单服活动` `GMDeployServerActivity(cfgId,start秒,end秒)` | telnet `!gm DeployServerActivity <cfgId> <start> <end>` —— ⚠️**仅服务端活动；玩家触发型活动用它无效** |
| 删除单服活动 | `[活动_活动]强制删除单服活动` `GMForceRemoveServerActivity(activityId)` | telnet（清理部署的测试活动）|

> 找更多 GM：grep 服务端 `[GMHandler("` + 关键词（充值/等级/资源/活动/任务...）；客户端 GM 在 `client/Assets/Scripts/Debug/GM/`。

## 关键坑
- **TotalPayMoney 只增不减、无重置 GM**：`AddTotalPayMoney` 只 `+=`。测"首充跨门槛"类**必须用新号**（老号已高于门槛，永远无法再"跨"）。
- **新号 level=1**：很多活动门槛要 level≥5。先 `gmaddlevel` 升级再触发，否则 `CheckActivityIsUnlock` 卡等级关（充值跨门槛了活动也不开）。
- **没有模拟真实充值的 GM**：涨 TotalPayMoney 只能走 BuyGiftReq 现金档（见 server-arch / recipes）。
- **顺序**：触发条件要在**触发那一刻**全部满足。如先升级到 ≥5 再购买（在 level≥5 时跨门槛），别先购买后升级（购买时 level 1 已评估失败，升级不会补触发充值事件——除非该活动也走登录状态式重评估）。
