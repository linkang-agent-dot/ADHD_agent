---
name: arpu
description: 节日日报ARPU口径 = 节日流水 / 当日总付费人数（所有付费玩家），不是只算节日付费人数
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d85a4e25-0b5a-4f0e-862d-4d42bcee2238
---

节日日报里 **ARPU = 节日流水 ÷ 当日总付费人数**（当天买了任何东西的人），**不是** ÷ 节日付费人数（只买节日礼包的人）。

**Why:** ARPU 看的是节日对**整个付费盘**的人均拉动/贡献，分母要含没买节日的付费玩家；除节日付费人数那是"节日买家客单价(ARPPU)"，是另一个指标。用户 2026-05-29 明确："ARPU应该是当日登录付费总人数（不仅仅节日付费）"。

**How to apply:** [[reference_x3_festival_monitor]] 脚本里主区 renderARPU 用 `d.payers`(总付费)本就对；对比区 renderCompare 原来误用 `fest_payers`，已改成 `payers`。两处统一除总付费人数。
（注意：这覆盖了早期 MEMORY 里"节日整体ARPU=模块收入/节日付费人数"的旧表述——以总付费人数为准。）
