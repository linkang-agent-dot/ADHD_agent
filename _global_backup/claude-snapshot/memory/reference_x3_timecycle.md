---
name: X3 TimeCycle 配置知识
description: X3 项目里 TimeCycle 表与 ActvOnline 的绑定机制、活动不触发的常见原因
type: reference
originSessionId: f6f8a545-b15c-4f6e-a240-0fc5532e47ae
modified: 2026-07-29T08:01:31.919Z
---
## 配置表位置（2026-05-25 迁移到 Git）
- **新仓库**：`C:\x3\gdconfig\`（remote `https://git.tap4fun.com/x3/gdconfig`）
- **数据目录**：`C:\x3\gdconfig\data\`
  - `C:\x3\gdconfig\data\TimeCycle.xlsx`
  - `C:\x3\gdconfig\data\ActvOnline.xlsx` — 主活动表。openpyxl 加载会因 WPS 写的非标 table ref（`ref="6:244"`）报错，需 monkey-patch：

> ⚠️ 旧路径 `C:\X3\`（SVN 时代）和 `C:\x3dev\` 都已过期，不要再读写。
  ```python
  import openpyxl.worksheet.table as tbl_mod
  from openpyxl.descriptors.base import String
  tbl_mod.Table.ref = String(allow_none=False)
  ```

## 🔴 铁律：下线/迁移活动用 `TC=0` 保配置，别用 `IsOn=0`（IsOn=0 会清实例=丢数据）
（2026-07-23 冠军之路排期迁移事故坐实，详见 [[project-x3-wonder-schedule-mismatch]]）
- **`IsOn` 是 ActvOnline 的导表过滤列**（tsv col7=bool；生成的运行时 `client/.../CfgProtos/ActvOnline.cs` 里**没有这个字段**）→ IsOn=0 的行**不导入配置** → 运行时 `CActvOnline.I(cfgId)` **返回 null**。
- 后果：`ActivityMgr.OnLoadActivity`（ActivityMgr.cs:963-967，**服启动全量 load 实例时**）遇 `cfg==null` 就把该 ServerActivity `DeleteActivity`（日志「cfgId is off, remove activityId」）→ **跑过/在跑该活动的服一重启，实例被删、玩家进度/名次/结算奖励丢失**。purge **只在重启触发，配置热更不触发**（其它 cfg==null 处只 continue/return 不删）→ 没重启的服实例还在、可救。
- **正确姿势**：要停一个还在跑/已产生玩家数据的活动 → **`IsOn=1` 保留 + `TimeController(TC)=0`**（配置行在=实例不被清+照常结算；TC=0=无触发不再开新实例）。=船只手册迁移范式「老TC=0+新活动互斥」。
- ⚠️**TC=0 会被导表校验拦，必须同时改导表器放行（2026-07-23 实测）**：`gdconfig/Tools/table_exporter/PostProcessData.py:1804 deal_actv_online_data` 对 IsOn=1 的行强制 `TimeController≠0`，报「活动ID:X 时间控制器ID:0 不能是0」。豁免三口（line 1668/1802）：①`SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE`（按 ActvType，已含 MULTI_STAGE_RANK/WONDER_SCORE/WC_GUESS 等榜类）②`kvkSeasonActivityCfgId` ③`ScheduleActvIDSSet`=表 `ActvGroupSchedule.ActvIDS`（但那是"子活动随主活动开"表，塞进去会改成子活动语义，别用）。**正解=把该活动 ActvType 加进 `SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE`**（冠军之路 case 已加 `ACTV_TYPE_HERO_CHAMPION_ROAD`=55）。**这条导表器改动必须随 tsv 一起提交 gdconfig 并传到 qa/master**，否则只推 tsv、jolt 导表必挂 line 1804。⚠️另 line 1695 `if not item.IsOn: continue`=IsOn=0 行整行不导出的铁证（跨表通用，ActvGroupSchedule 表头注释也写「IsOn 0/空=不导出」）。
- **例外**：`IsOn=0` 只适合「彻底废弃、且确认没有在途实例/玩家数据」的活动（等于顺带清库）。**例外的四条核对清单（2026-07-29 马戏庆功宴 101028 实操，照着走一遍再动手）**：①**线上从未部署**——`TC=0`（从不进时间轮）+ 备注已标【勿部署】+ `ActvGroup` 空（不在任何节日面板、批量部署不会带上）三者齐 = 没有在途实例；②**本地/测试服的实例是 GM 开的测试数据**，被清正是目的，不算数据丢失；③**引用面清干净**——全表 grep 该 AO id，逐个判「真引用 vs 撞号」（怪物表/情报表常有同数字撞号）；指向它的 `ItemObtain`(type5 跳活动) 等要确认已零引用；④**改完跑本地 ExportTable 验 exit0**，日志应出现 `Skip row [<id>, ...]` = 确认该行不导出且没触发别的表的引用校验。⑤🔴**还要查「有没有别的界面把它当数据源」**（2026-07-29 补，我当天就栽在这条上）：前四条只查了"活动自己有没有数据"，漏了**宿主界面依赖**——101028 被 IsOn=0 后实例被清，扭蛋机 101027 底部那条积分轨道跟着整条消失（`InitScoreTrack` 拿不到实例即 `SetActive(false)`）。判法=全客户端 grep 该 cfgID（`grep -rn "<cfgID>" Assets/Scripts --include=*.cs`），命中常量/旁挂读取就是被人当数据源了。这类「旁挂数据源活动」正确的隐藏姿势不是 IsOn=0，见 KB\方法论\活动程序开发\X3客户端GUI知识.md「第四种情况：旁挂数据源活动」。
- 🪤**清空 `ActvGroup` 并不能让活动"隐身"（2026-07-29 实证，别拿它当下线手段）**：101028 的 group 被清空后，本地实例反而出现在**「酒馆活动」页签**下——客户端在 group 为空时会按 `ActvType` 归到该类型的默认面板（101028 是 ActvType=7 最佳酒馆类）。所以「清 group」只能让它不进节日 hub，**只要有活动实例它就会在别处冒出来**。真要断根：没数据的用 `IsOn=0`（走上面四条核对），有数据的用 `TC=0` + 不部署。凡「迁移开启时机 / 换排期 / 临时停」都用 TC=0。
- 迁移开启时机时**两件事一起查**：①本铁律（下线姿势 IsOn vs TC）②服龄带交集双开（老关前已开过的服 + 新窗口覆盖同批 → 双开，见 [[project-x3-wonder-schedule-mismatch]]）。

## 活动→TimeCycle 绑定机制
活动的时间调度**不看**子活动表（ActvLuckyWheel / ActvExchange 等）或 TimeCycle 编号是否等于 ContentID，而是看：

**`ActvOnline.xlsx` 的 H 列 `TimeController`**（第 8 列）

所以新增 TimeCycle 行后，必须同步改 ActvOnline.TimeController 让活动指过去，否则 TimeCycle 是孤儿行。

## TimeCycle 表结构（`C:\x3\gdconfig\data\TimeCycle.xlsx`）
数据从 row 6 开始，列含义：
- A 编号 / B 备注 / C IsOn / D 数据主体
- E TriggerType：1=绝对时间 2=开服时间 3=注册时间 4=海域开放 5=触发后计时 6=开服第N周
- F TriggerTime（按 E 解释）
- G DurationType / H 持续时间
- I CycleType / J 再次开放时间点
- K 循环结束方式 / L 循环结束时间

## 已知约束（TriggerType 隐性限制，未100%验证）
不同 ActvType 对绑定的 TimeCycle.TriggerType 有限制，可能在服务器代码硬编码：
- **ActvType=50 许愿池**：历史上所有许愿池活动（105009/105011/105012）都用 TT=1（绝对时间），疑似硬编码要求。ActvOnline 的 TriggerType 列描述里也专门点名许愿池。
- ActvType=7 最佳酒馆：历史用 TT=1 或 TT=4，无 TT=2 先例
- ActvType=13 兑换：历史用 TT=1/3/4，无 TT=2 先例
- ActvType=10 大转盘：TT=2 有先例（101001/101010），可安全使用

如果想把某个活动改成 D21 开服相对时间触发，先确认该 ActvType 是否支持 TT=2，不支持的要走绝对时间（每期配新 TimeCycle 行）或找后端改代码。

## 导表报错"应该是绝对时间"
- 没有行号提示，只能靠二分或问后端
- 大概率是 ActvType 对 TimeCycle.TriggerType 的硬编码校验

## 🔴 跨服活动硬约束：必须 TT=1（绝对时间）

**校验位置**：`Tools/table_exporter/PostProcessData.py` 的 `deal_actv_online_data()` line 1633

**触发条件**：`ActvOnline.CrossServerRank=1` 的活动，其绑定的 TimeCycle 行 TriggerType 必须 = 1。

报错示例：
```
ActvOnline配置错误：必须是绝对时间 timeCycleId :718 activityIds: {'Vals': [10071801]}
```

**原因**：跨服活动需要在 CenterServer 端做所有 GameServer 的时间锚定聚合，必须用绝对时间；TT=2/3/4/5/6 都是按服各自计算的相对时间，无法跨服对齐。

**实战记录 X3NEW-735**：最佳酒馆 ActvID=10071801 改成跨服（CrossServerRank=空→1）后导表失败。TC=718 原是 TT=2 + "20d 00:00:00"（开服+D20相对），改成 TT=1 + 占位绝对时间 "2026-02-16 00:00:00" 即过校验。

**占位时间选择**（如实际上线时间未定、需 iGame 后台手动设）：
- 选**已过去的过期时间**（如 2026-02-16）：代码 `TimeCycleMgr.cs L708` `if (now >= start && now <= end)` 判断 → now > endTime → 不触发 OnTimeStartEvent，活动状态"已过期"，dev 环境无奖励/无入口
- 选**未来时间**（如 2030-01-01）：进定时队列，状态"未开始"
- 两者行为基本一致（都不发奖），二选一看团队偏好

## 🔴 改已有 TimeCycle 行 = 双开叠加（2026-07-15 永恒之岛 5578e75 实锤，决定合master方案）
- **实锤**：beta 330 上永恒之岛积分活动 101207 出现 **count=4 个完全相同的 live 实例**（start/end 全等）。成因=服务器活动实例化路径**没有去重/关旧守卫**，每次触发 open 就新建一个。触发源可以是"配置重部署/reload"（07-09 钓鱼案）或"窗口内反复跨天 day-update"（本次跳时 artifact）——同一个引擎缺陷。
- **含义**：直接改在用的 TimeCycle 行 → 部到"改配置时活动正开着"的老服，会给这些服**叠加重复实例、双份发奖**。
- **安全落法（✅ 2026-07-15 e13db23 实测通过，可合master）**：**只增不改**——回滚旧行为原值 + 新建 TimeCycle id(1211/1212) + ActvOnline 新行(101211/101212)。判据 **V3 实证**：某服有 101211 live 实例时，重部署同份配置 → 101211 实例数**保持 1**（不叠加）。`TimeCycleMgr.OnReload` 对已知 cfgID 直接 return，只对新增 cfgID 建实例、不碰在飞实例。对照旧方案(改旧行 5578e75)→count=4 双开。
  - **部署机制（本次实操）**：改配置生效 = **先热更(id1250 sync config)→再 deploy_app 重部署**（重部署恢复被热更打断的GM网关，且**不会冲掉热更同步的配置**，两者叠加=最新配置+GM可用）。🪤 **服务端 bin/配置管线比客户端导表慢十几分钟**：e13db23 15:41提交、客户端导表15:44、但服务端 15:46/15:54 部署仍 "config not found"，~15:5x 才追上——验服务端配置到没到用 `addserveractivitybycfgid <cfgId> --player`（返回 created=已加载 / "activity config not found"=没到）。

## ✅ 解码 TimeCycle.bytes + beta 跳时验活动实例（2026-07-15 实操机制，复用必读）
- **解码运行时值**（不启动 Unity）：`~/.claude/skills/x3-config-export/scripts/decode_protogen_timecycle.py <TimeCycle.bytes> <ID...>`。导表把 "26d 00:00:01"/"7 2 00:00:01" 转毫秒，回换速查：26d00:00:01=2246401000 / 5d23h59m59s=518399000 / 48h=172800000 / 21d=1814400000 / 15d=1296000000。TT=6 "第N周周M" 导表按 (N-1)*7+M 天线性转(仅占位)，真实开窗运行时按开服周历重算到真周M。
- **查服务器活动实例 GM**：`printserveractivitybycfgid <cfgId>` **必须带 `--player <该服玩家>`**（不带会用 serverId 当 uid → 假报 "entity is not existed"）。返回 count + 每实例 id/start/end。
- **beta 跳时验开窗**（test-env skill `gm_execute setservertime`）：
  - 🪤 **绝对跳时不触发活动开窗**：活动靠**自然跨过日界的 day-update** 建实例。方法=设到日界前 5-10s、等 10-15s 让它自然跨过。
  - 🪤 **日界不在 UTC0，在"开服当天的时分秒"**（如开服 00:08:14 → 日界在每天 00:08:14，passDay 在此进位）。跨 UTC0 但没跨这个点 passDay 不动、day-update 不 fire。
  - 🪤 **setservertime 不能回拨**（往回设静默失败、时钟继续往前走）→ 跳过了某活动开窗点就补不回，只能找时钟还没过该点的另一台服。
  - ✅ **TT=2 与 TT=6 开窗机制其实相同**：都在**窗口内任意跨天 day-update** 建实例（→跳时易造 count 多实例）。2026-07-15 更正：之前以为"TT=6 只在周界开窗打不开"是**算错日历**——TT=6 "第N周周M" 用**日历周**（周一起算、**第1周=开服当周**），不是开服后每7天一段。例：开服 07-31(周五)，"第7周周二" = 第1周含07-31那周(07-27~08-02) + 6周 → 09-07(周一)起，周二=**09-08**（不是 07-31+65d 线性算的 09-15；09-15 已过窗口所以 no server）。算准日历周落进窗口就能正常开。
  - 🪤 **容器重启(deploy_app)会清掉 setservertime 的偏移**，时钟回自然态。
  - `addserveractivitybycfgid <cfgId> --player` 用 TimeCycle 配置的**时长**但 **startTime=now**（立刻开），验不了"开窗相位/周几"，只验时长。

## 沉淀关联
- [[reference_x3_score_activity]] — X3 积分活动配置 + 跨服活动改造
- [[reference_x3_project_repo]] — X3 server 代码仓查询方式
- [[reference_x3_kadmin_deploy]] — 热更打断GM网关坑 + printserveractivity/setservertime GM 用法

## ★两个活动「绑定开」三种机制速查（2026-07-27 推币机+拼图双实证，按优先级选）
1. **🥇ActvGroupSchedule 主子活动绑定表（`tsv/ActvOnline__ActvGroupSchedule.tsv`）——通用真绑定，首选**：一行=MainActvID(主AO)+ActvID(子AO)+StartTime(相对主开启的偏移秒)+DurationType(2=终点跟主活动同窗/1=固定DurationTime)。服务端 `ServerActivityBasicMeta.CreateGroupActivityIds`：主活动实例创建时自动拉起子活动，**继承主活动圈服+ArkActivityId**，iGame 只需部署主活动。**通用不挑 ActvType**（在用：航海之路带美人鱼拼图/记录册/金海浮市、入侵、风暴、30留转盘、修女、马戏巡游102803→拼图101829=行10006、寻宝103101→门票阶梯103102=行10007）。⚠️主活动 IsGlobal（跨服全局）不触发；GM 提前下掉主活动子活动不会跟着掉（子实例创建时定死终点）。
2. **双胞胎 TC**（推币机手法，适合 TC 排期的常驻活动）：推币机 106505→TC160006、夺宝通行证 106507→TC160007，两条 TC 参数逐字段相同 → 到点各自开、时间必然同步。变体=两 AO 共用同一条 TC（有先例，改窗口一处生效；代价见 [[feedback_x3_timecycle_name_legacy]]）。
3. **iGame 同窗部署**（无配置绑定时的兜底运营纪律）。
- ⚠️`ActvOnline.BaseActvID` **不是**绑定机制（服务端零逻辑消费，只作 BP 新旧版本迁移标记）；ActivityMeta 里的 `SubActivity` 是活动内任务子项，也不是这回事。
案例落地：马戏 103101 寻宝 + 103102 门票阶梯礼包走机制1（行10007），见 [[project-x3-ticket-ladder-pack]]。
