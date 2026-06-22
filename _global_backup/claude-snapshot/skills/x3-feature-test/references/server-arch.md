# 服务端触发架构（X3 GameServer）

测功能时最关键的一步：搞清"这个功能在服务端由什么触发、有哪些解锁门槛"。本文件是常见模式 + 怎么读服务端运行时。

## 进程 & 连接
- 三个 .NET 进程：**GameServer**（玩家逻辑主服）/ **MapServer**（地图）/ **CenterServer**（跨服/联盟），各带 `*.Hotfix` 热更程序集。玩家功能基本在 `GameServer.Hotfix/PlayerMeta/`。
- 本地服 telnet C# / GM REPL：端口 = `23000 + NodeID`。**GameServer NodeID = serverID**（如 serverID 3080 → 26080），MapServer = serverID+1，CenterServer = centerID。源：`TelnetModule.cs` `var port = 23*1000 + Config.NodeID`。
- 跑服务端 C#：DebugUtils `telnet_eval.py --port <port> --command "..."`（若 prompt 不就绪超时，本环境可能只通 GM 通道，见 gm-commands）。Hotfix 类型反射用字符串 meta 查找 `p.GetMeta("numeric")` 而非泛型。
- 日志：`server/GameServer/bin/Debug/net8.0/logs/game-<serverID>.<date>.log`。DebugUtils `log_collector.py local-server-logs` 列出、`search --file X --pattern Y` 搜。先 search 再 analyze，大日志别全读。

## 事件系统（触发功能的主干）
- `Event.RegisterEvent(TEventType.Xxx, handler, owner)` / `Event.FireEvent(TEventType.Xxx, args...)`。
- **测功能=找到"开启它的那个事件 + 监听者 handler + 解锁校验"这条链**。

## 玩家活动触发模式（累充/等级礼包/签到等的通用骨架）
以 `GameServer.Hotfix/PlayerMeta/Activity/ActivityMeta.cs` 为例，多数玩家触发型活动走这套：
- **触发事件 → 收集候选 cfgIds → `HandleNewPlayerActivityInfos(cfgIds)` → 逐个 `CheckActivityIsUnlock` 通过才开**。
- 常见触发入口：
  - 充值：`AddTotalPayMoney`(PayMeta) fire `TEventType.PayOrder(last,now)` → `OnPayOrder` 遍历 `CActvOnline.Instance.PlayerPay2ActivityIds`，对 `last < RechargeAmount <= now`（**跨门槛**）的活动开。
  - 升级：`OnPlayerLevelChanged(last,now)` 遍历 `PlayerLevel2ActivityIds`。
  - 功能解锁：`OnFunctionStateChange`。
  - 登录：`HandleNewPlayerActivityInfos(CActvOnline.Instance.PlayerActivityIds)` —— 登录时按当前状态重评估（**状态式**，不要求"跨"，只要满足条件就开）。
- **`CheckActivityIsUnlock` 典型门槛**（任一不过则不开）：① `PlayerLv` 在配置区间（如 [5,99]，**新号 1 级常卡这**）② TimeCycle 时间窗（注册相对/开服相对/绝对）③ 充值额度 `TotalPayMoney >= RechargeAmount`（状态式）④ RequireFunction 功能解锁。
- **跨门槛 vs 状态式的坑**：`OnPayOrder` 是"跨门槛那一刻"才触发（`last<阈值<=now`）——已高于阈值的老号无法再触发；但**登录重评估是状态式**——若该活动也在 `PlayerActivityIds` 里，满足条件时登录就会开。两条路是否都覆盖该活动，决定了能否靠"升级后重登"补开。

## 玩家触发活动 ≠ 服务端部署活动（重要区分）
- **玩家触发型**（如新手累充 101108，配置 `TriggerType` 玩家触发）：走上面的 `HandleNewPlayerActivityInfos`，activityId == cfgId，按玩家状态开。
- **服务端部署型**：GM `部署单服活动`（`GMDeployServerActivity`）建 ServerActivity 广播给全服。
- ⚠️ **别用错**：对玩家触发型活动用"部署单服活动"GM，建出的 ServerActivity **不会下发给玩家**（实测：部署后登录同步里没有它）。玩家触发型只能靠真实触发事件（充值/升级/...）开。

## 购买 → 充值额的服务端链路（测充值类功能必看）
- 客户端 `BuyGiftReq` → 服务端 `GiftMeta.OnBuyGiftReq`：非 gem 档调 `payMeta.AddTotalPayMoney(priceCfg.Dollar, priceCfg.Points)`（`Dollar` 是分、`Points` 是充值积分）。
- `AddTotalPayMoney` 内部 fire `PayOrder` → 触发上面的累充活动评估。**所以"买现金档礼包"是涨 `TotalPayMoney`、触发累充活动的真实入口**。
- 金砖模式（`IsGoldBrickMode`）会额外扣金砖余额（要够）；非金砖模式（IAP/现金）Editor 下不需货币。
- gem 档（`UseGem=true`）扣钻、**不涨** TotalPayMoney。
- ⚠️ **没有"模拟真实充值"的 GM**（只有模拟退款）；`增加代币` 只加金砖余额，不涨 TotalPayMoney。要涨 TotalPayMoney 必须走 BuyGiftReq 现金档。

## 怎么摸一个陌生功能的触发链
1. grep 服务端：功能关键词 / 配置字段（如 `RechargeAmount`）/ 相关 Meta。
2. 找 `[GMHandler]` 看有没有现成 GM 能开/触发。
3. 找 `Event.RegisterEvent(TEventType.X, OnX, ...)` 看谁监听、`FireEvent(TEventType.X` 看谁触发。
4. 读 `Check*IsUnlock` / `Check*` 把全部门槛列出来 —— 这就是第 5 步要构造的前置状态清单。
