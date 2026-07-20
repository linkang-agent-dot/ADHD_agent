---
name: X3 TimeCycle 配置知识
description: X3 项目里 TimeCycle 表与 ActvOnline 的绑定机制、活动不触发的常见原因
type: reference
originSessionId: f6f8a545-b15c-4f6e-a240-0fc5532e47ae
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
