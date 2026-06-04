---
name: iGame 活动 cancel vs recall
description: iGame 活动操作的任务/状态分层——"下线活动"任务下，按当前状态选 recall（部署申请状态）或 cancel（上线中状态）。
type: feedback
originSessionId: c540f3a7-ccbb-44c2-bcba-b55e73c2c111
---
iGame 活动操作的正确分层：

**任务层：**
1. **部署申请** —— `submit` 接口
2. **下线活动** —— recall / cancel 都属于这里，按活动当前状态分两种实现：
   - **部署申请状态**（活动未上线，处于审核中或已审未到 startTime）→ **撤回（recall）**，申请退回，重新审批
   - **上线中状态**（活动已上线，正在跑）→ **取消（cancel）**，取消已生效的活动

**接口：**
- recall：`activity/operation/recall`，**单 id**，多个要循环
- cancel：`activity/operation/cancel`，批量 `ids` + `reason`

**Why:** 用户 2026-04-15 反复纠正过我三次，最终定稿的口径是这版"任务+状态"的分层：
- 不要描述成"按动作分（改 vs 下线）"——recall 不是为了"改"，recall 也是"下线"，
  只是因为活动还在部署申请阶段，所以走的是"撤回审批"的路径
- 关键认知：recall 和 cancel 目的相同（都是不让活动上/让活动停），
  区别只是当前状态决定走哪条路
2026-04-08 已经因为这个混淆出过事故。

**How to apply:** 任何时候想"下线"一个活动：
1. 先确认活动当前状态：还在审批 / 已审未到时间 / 已经上线
2. 部署申请状态 → recall（一次一个 id）
3. 上线中状态 → cancel（批量 ids + reason）
4. 不要用 `del` 接口（对待审核活动无效）
