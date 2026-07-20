---
name: reference_x3_coinpusher_config
description: "X3 推币机(CoinPusher, ActvType 65)配置全景+HUD显隐判定链——单服版挂自动TimeCycle每周六自动开,不走iGame"
metadata: 
  node_type: memory
  type: reference
  originSessionId: eb65c432-0cbf-4615-82cd-162ed445956a
---

# X3 推币机配置全景（2026-07-18 排查沉淀）

功能整套 2026-05-30 由 gaoyadong `dev_x3_519_CoinPusher` 合入（commit 226809b1），专属表 `CoinPusher__CoinPusher.tsv`，ActvType=65（单服）+22（BP）。

## HUD 显隐判定链（排「HUD出现但没想开活动」类问题先看这）
- **两套入口按版本分流（2026-07-18 实证）**：主界面左侧 HUD 按钮 = `UIMainLeftPart.CoinPusher.cs` RefreshCoinPusher，条件=有 type65 活动实例 **且 `cfg.CrossServerRank==true`（只给跨服版 106502 显示，单服版直接隐藏）** 且 monsterInfo 非空；**单服版入口=家园推币机家具**（MapWidgetPlayerFunctionFurniture + FunctionUnlock 1097）。
- **HUD 出现 = 服务器真有活动实例（含未开打的预告期）**：iGame 部署跨服版后、开打前，按钮就会显示并带「开始于 X」倒计时（RefreshNextBossStartTime / LC_EVENT_start_in）——「HUD出现但点进去没数据」大概率=预告期，先查实例 start_time 再喊 BUG。
- **为什么普通节日活动部署了要到点才出现、推币机却提前露出（2026-07-18 代码实证，非配置）**：①服务端 iGame 部署即建活动实体（StartTime>now 走「延迟开启」定时器，ServerActivityCoinPusherMeta.OnActivityTimeStart），玩家侧 `HandleServerActivityInfo` 塞活动进玩家列表**只判等级/解锁条件不判时间**→部署即下发所有服务器型活动；②普通节日活动的入口 UI 自己判 startTime 所以看不出来，推币机主界面按钮（X2 原样搬）只判「实例存在+跨服+怪快照非空」不判 startTime→提前露出+预热倒计时是 X2 继承设计；③ActvOnline.PreviewTime([25]) 推币机全部为空，预告不是配出来的。开打前怪快照由客户端主动 GetCoinPusherMonsterReq→冷启动时 server 向 Center 定向查询回填。
- 查某服活动实例窗口：`v1090.ods_user_activity WHERE server_id='X' AND attribute1 LIKE '%1065%'`，attribute1 JSON 里 activityCfgID + activity_start_time/end_time 即部署窗口（北京时间）。
- FunctionUnlock 1097（CoinPusher，主城家具按钮/功能开关）：IsOn=1、酒馆10级解锁、TimeCycle 空=无时间门槛，三分支一致常开。
- **「某号看不见」先查等级**：全部 10 行 ActvOnline 的 PlayerLv=10,99 → 酒馆<10级服务端直接不下发活动（HandleServerActivityInfo 的 CheckActivityIsUnlock 拦），连数据都没有；升级即时补下发（OnPlayerLevelChanged→HandleServerActivityInfo，无需重登）。
- **个例「看不见」分流判据**：`v1090.ods_user_activity` 里 `event_id='activity_start'` 是**逐玩家**的活动发放事件（登录/解锁时服务端加活动打一条）——查该玩家 user_id 有无此记录即分流：有=服务端已发、查客户端显示链路（怪快照/版本）；无=服务端没发、查解锁条件（等级口径=酒馆等级）。跨服推币机 AB 实验分组已排除（AbTestService 无推币机）。
- **个例排查时间线三件套（2026-07-18 1930服1730557案）**：①玩家最后事件时间 ②该服该活动第一条 activity_start（=部署下发时刻）③表落库水位（`max(created_at)` 全服）——下「他没登录」结论前必查③，落库只到 12:00 时 12:35 的登录查不到属正常。iGame 部署时刻可用「该服第一条 activity_start」反推。
- **预告期按钮可能全服性不显示**：开打前按钮还依赖跨服组 Center 的怪物快照（TryStartCoinPushSync 要 StartTime<=now 才启动同步）——某跨服组快照未就绪则该组全部服都看不到按钮（活动已发放也一样），开打时自然出现，非 BUG；跨组对照（一服可见一服不可见）即此因。

## ActvOnline 10 行（master）
- 单服 type65：106501(TC 160008=开服第4天起3天) / 106503(TC 160009=开服第14天起3天) / **106504(TC 160010=每周循环开约3天，7-01 tsviewer 加入 master；StartTime`6 2 00:00:00` 按线上数据实测=每周二开、周五收，不是周六——别按字面猜)** / 106505(TC 160006=9999d 永不触发·停用占位)
- 单服 BP type22：102240 / 102242 / 106506(无TC) / 106507(TC 160007=9999d 停用占位)
- 跨服：106502(活动) / 102241(BP)——无 TC，走 iGame 外部控制
- 挂 TC 的行服务器到点自动开，**不走 iGame 部署**；停用手法=换成 9999d 型 TC（160006/160007 即现成占位）。

## TimeCycle TriggerType 枚举（CSShared\Common\Const\TimeCycleConst.cs）
1=绝对 2=开服相对 3=注册相对 4=海域开服 5=开启后计时 6=每周几（StartTime 格式如 `6 2 00:00:00`=周六02:00）。tsv 列：[4]TriggerType [5]StartTime [6]DurationType [7]Duration [8]CycleType [9]ReOpenTime。

## 线上实际运行状态（2026-07-18 数仓实测，BI 事件=`coin_pusher_toss`）
自 6-19 起持续有真实投币，**功能早已上线运营**，两套节奏：
- 全量周轮：每周二开~周五收（7-07~7-10 75服 / 7-14~7-17 81服），日投币玩家 3k-5.6k，单日投币峰值 94.7万次 → 对应 106504 循环 TC。
- 新服生命周期轮：开服第4/14天各3天（106501/106503），非周轮日只有少数新服在开（7-18 周六=8服：2340-2470 段）。
查法：`v1090.ods_user_event WHERE event_name='coin_pusher_toss'`（TRINO_HF）。「HUD出现但以为没上线」类问题先跑这条按日聚合即知真开没开。

相关：[[reference_x3_actvtype_enum]] [[reference_x3_config]]
