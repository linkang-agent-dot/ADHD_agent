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

## 沉淀关联
- [[reference_x3_score_activity]] — X3 积分活动配置 + 跨服活动改造
- [[reference_x3_project_repo]] — X3 server 代码仓查询方式
