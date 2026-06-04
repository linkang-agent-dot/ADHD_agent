---
name: feedback_x3_token_actual_charge_unit
description: X3 数仓 TOKEN 货币 actual_charge 自 2026-06-02 改记代币单位(=USD×100)，收入口径必须改用 pay_price
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d08657aa-47ba-47bb-bcc4-d93d481e8c29
---

X3 数仓 `v1090.ods_user_order` 中 `currency_type='TOKEN'` 的订单，`actual_charge` 字段**自 2026-06-02 起单位变了**：从 USD 改成代币单位（= USD × 100），同笔订单 `pay_price` 才是真实 USD。

实测（2026-06-03）：210702 TOKEN actual=499.0/pay=4.99、210706 actual=1999.0/pay=19.99，整整 100 倍。全大盘 TOKEN actual vs pay：05-29~06-01 相等(正常) → 06-02 起背离($1152 vs $164) → 06-03 暴增($18670 vs $187)。

**Why**：夏日日报脚本 `x3_festival_daily.py` 沿用 X2 旧口径 `REV_EXPR = CASE WHEN currency_type IN ('usd','TOKEN') THEN actual_charge ELSE pay_price`，把 TOKEN 订单放大 100 倍 → D5 节日流水虚高 9 倍（$12216 假 vs $1359 真）、总流水虚高 5 倍。表现为"某天数据暴涨、付费人数没涨而 ARPPU 炸"。

**How to apply**：X3 任何按 USD 统计收入的 SQL，口径改成 **只有 `currency_type='usd'` 取 actual_charge，其余(含 TOKEN/本地币)一律取 pay_price**（pay_price 始终是 USD 归一价；usd 的 actual==pay 不受影响，历史数据回算不变）。已修 `x3_festival_daily.py` 的 REV_EXPR + ltv_join 两处。X2 同源脚本 [[x3]] 若也用 IN('usd','TOKEN') 取 actual_charge 需同步排查。日报数据"暴涨/异常"先查这条。
