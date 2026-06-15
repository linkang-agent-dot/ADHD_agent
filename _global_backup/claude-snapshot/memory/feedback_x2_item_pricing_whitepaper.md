---
name: x2-x3
description: X2 道具美金单价一律查 X2 数值白皮书/付费价值表，禁止用「钻石值×比例」折算（那是 X3 口径）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 10d005bc-9ff9-4b28-b888-ca67dbb5ed69
---

X2 给道具定美金单价、做等值替换/换皮时，**单价口径一律以 X2 数值白皮书为准**：
- 白皮书：`C:\ADHD_agent\.cursor\x2-numerical-design\养成线深度手册.md`（各养成线「关键材料单价」表，直接列美金单价）
- 数据源 GSheet：付费价值表 `1aV8VL-81C_VDQfzBhTvqiRbQUOGQuvV3WrcFrk2z3UU`(gid=1593930563) / 道具锚点价值表 `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs`(gid=862716542)

**Why:** 2026-06-08 做拓荒挖矿榜奖励替换(X2-42998)时，我用「装饰券钻石值 D=1000 ÷ 加速 D=100=$0.5」推出装饰券≈$5，被用户指出**那是 X3 的钻石→美金折算规则，X2 不这么算**。X2 装饰券实际就是 $0.5/个（白皮书口径）。

**How to apply:** 要某 X2 道具单价 → 先翻白皮书对应养成线的单价表；查不到再读两个价值表 GSheet。**绝不**拿钻石值按比例换算美金。白皮书里 $0.50 的道具有：宝石升级道具 11111083、传说机能核心 11118501、绿色收藏品、橙色升星道具 11116604、所有加速 $0.50/小时。相关链路见 [[x2-config-library]]。
