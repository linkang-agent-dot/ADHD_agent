---
name: reference_x3_server_activity_duplicate
description: X3 服务器级活动在 dev/beta 莫名出现2条重复实例的根因(runtime创建路径缺去重)+诊断法(查Mongo ServerActivity)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 46f5038a-0474-4334-8d67-e21183ec54be
---

# X3「服务器活动重复2条」根因 + 诊断法（2026-07-01 远航战备案）

## 现象
dev/beta 某**服务器级活动**（数据主体≠玩家）莫名出现「2个一模一样的活动」共存。实案：远航战备 ActvOnline `104801`(ActvType=48 日常小榜) 在 beta 220 有两条相同 ServerActivity。

## 判活动是不是"服务器活动"（3 层）
1. **配置**：TimeCycle 表「数据主体」列(第4列) — `1=玩家(个人活动) / 2=奇观 / 3=天下大势 / 4=服务器`。≠1 就是服务器/共享活动。
2. **运行时**：实例落 Mongo `gs_game_<服>.ServerActivity`（不是玩家 `ServerPlayer`），`isGlobal:true`。
3. **代码**：服务端走 `ActivityMgr` 服务器路径，不是 `ActivityMeta`(玩家个人)。

## 根因（真因 = 两条创建路径去重不一致 + beta 反复拨钟/热重载）
> **2026-07-06 更新（1910服客诉案）**：①`HandleSingleServerTimeStartEvent` 去重缺口**仍未修**（ActivityMgr.cs:503-521，line 520 无条件 CreateNewServerActivity，checkout 93f801ee6be）。②发现**第三条重复路径：iGame/ark 部署无去重**——`OnDeployArkActivityReq`（ActivityMgr.Ark.cs:192）直接 CreateNewServerActivity，`CheckCanDeployArkActivity`（同文件:212-250）只校验 JSON/cfg存在/endTime<now，**没有"同 cfgId 已在线"检查**；同 cfgId 部两次=2条实例。玩家侧按雪花 id 逐实例同步进 `Data.activityDict`（ActivityMeta.cs:1359,1495-1516）→ **2条实例=客户端出现2个一样的活动入口**（线上不拨钟也能复现，重复部署即可）。诊断仍用下面 Mongo 法，看同 cfgId 是否多条 + 各自 arkActivityId。
- **启服路径** `ActivityMgr.InitSingleServerActivities`(ActivityMgr.cs:397-421)：**有去重**——建前查 `mCid2Ids` + `ServerActivity.Equals(originSeaArea,endTime)`(ServerActivity.cs:265 单服时就是 `Data.endTime==endTime`)，已存在就跳过。
- **运行时到点路径** `OnTimeStartEvent → HandleSingleServerTimeStartEvent`(ActivityMgr.cs:503-521)：**无去重**——直接 `CreateNewServerActivity`，TimeCycle 开始事件每 fire 一次就建一条。
- `OnTimeStartEvent` 订阅 `TimeCycleMgr.OnTimeStartEvent`，**服务器游戏时钟每越过一次 TimeCycle 开始时间就 fire**。beta/本地服为测节日反复拨钟(220 钟常在未来)，时钟第二次越过绝对开始时间(或 TimeCycle 热重载重新入队)→start 事件再触发→走无去重路径→多建一条。
- 配置表头注释「其他主体类型改 timeCycle 会额外创建一个活动(2个共存)」= 同一去重缺口的**配置热重载版本**；拨钟是另一种触发。
- ⚠️**别赖到配置头上**：不间断活动 endTime 是固定常量(`GameTime.MaxTimestamp`=253402300799999=9999年)，永不变；个人活动(数据主体=1)是原地更新玩家时间不会重复。两条实例 endTime 完全相同 = 证明 endTime 没变过、不是有人改表。

## 诊断法（照做，别猜）
1. **查有几条实例(权威)**：`python scripts/mongo_query.py find --server <服> --collection ServerActivity --filter '{"cfgId": <ActvOnline六位号>}' --limit 20`（test-env-prepare-x3 skill）。字段=`cfgId/startTime/endTime/isGlobal/dailyRank`；有 `arkActivityId` 才是 iGame 部的，无=纯配置/TimeCycle 触发。
2. **确认配置没被改**：`git blame` tsv 那行 + `git log -S "<活动名>" -- data/TimeCycle.xlsx`；必要时 python+openpyxl 逐版本抽该行关键列去重(实案 76 版本 zero 变动)。
3. ⚠️**beta 服 OS 日志读不了**：林康 JumpServer 账号对 `x3-beta-qa-00N-sv-x3a3` 报「没有资产」(`p` 列全部授权也空)→抓不到 `.log` 文件；ServerActivity Mongo 就是权威运行时状态，别在日志上耗。

## 清理
GM 一条：`GMTakedownServerOrCrossActivityByCfgId <cfgId>`(ActivityMgr.GmTakedown.cs)——把该 cfgId **所有**实例都下掉+通知客户端，下次 Init 按当前配置**只建1条**(endTime一致后不再重复)。跑完复查 Mongo 剩1条。
## 根治 + 责任人
给 `HandleSingleServerTimeStartEvent` 补上和启服路径一致的去重(建前查 `mCid2Ids`+`Equals`)，堵住 runtime 重复触发。
- **作者/根**：两条路径都由 **陈宝成(chenbaocheng/cbc)** 在同一提交 `2eaa5cca`(2024-07-31, Jira **X3-5953**「大转盘·修改时间至第三次活动开启时活动无法开启」)加入——**启服 Init 路径加了去重(ActivityMgr.cs:397-421)、运行时 OnTimeStartEvent 路径漏了(503-521 直接 CreateNewServerActivity)**，去重不对称就是根，非后人改坏、非配置问题。该活动模块归 cbc(ServerActivity.Equals 有 `// TODO ... by cbc`)。要根治找他。
- 讽刺点：X3-5953 本身就是修「调时间导致活动开不了」的单，结果 runtime 路径自己留了去重缺口→调时间/热重载再触发就多建一条。

## 关联
[[reference_x3_timecycle]]（数据主体/TriggerType 枚举）· [[reference_x3_kadmin_deploy]]（Mongo/JumpServer 入口）· [[reference_x3_score_activity]]（积分/服务器活动）
