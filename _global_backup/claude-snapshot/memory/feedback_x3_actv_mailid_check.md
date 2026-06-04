---
name: feedback-x3-actv-mailid-check
description: X3 ActvOnline 配活动必须填 MailID（除 ActvType=8 挑战活动外），否则服务端补发逻辑静默吞未领奖励
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8c95a774-9d05-4760-9550-0dc41ff62e68
---

X3 在 `ActvOnline.xlsx` 配新活动时，**`MailID`（col R / 第18列，表头注释"奖励补发邮件"）必须填**。规则（表头 row 4 注释原文）：

> 除了类型8（挑战活动）外，其他均使用通用补发邮件 101109

**Why：** 服务端补发链路在 `C:\x3-project\server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.cs` 有 4 处 `MailID==0`/`MailID<=0` 守卫直接 `continue`/`return`（行 2185、2532、2690、2718），MailID 漏配则未领奖励静默丢失，玩家无任何感知。许愿池等少数 ActvType 走 `ActivityMeta.WishingPool.cs` 专用路径无 0 守卫，但仍依赖 `cfg.MailID` 实际值。2026-05-25 尼罗 101825「象形密文/拼图」（ActvType=18）就因为 MailID 空被发现。

**How to apply：**
- 每次 [[reference_x3_config]] 里新增 ActvOnline 活动行，**最后一步必须确认 col R MailID**：ActvType=8 可空，其他统一填 `101109`
- 换皮/复用历史活动行时也要查（漏掉很容易，因为 MailID 不在常改字段集里）
- 配 [[reference_x3_score_activity]] 积分活动、累充活动 [[reference_x3_recharge_isolation]] 时同样适用
- 已在历史活动里发现 MailID 漏配时：直接补 101109 + push + [[workflow_x3_auto_jolt_export]] 触发 jolt 即可，无需改服务端
- 通用补发邮件 101109 定义在 `Mail.xlsx`，另有 `MailGlobalCompensation` 页签是全局补偿邮件表
