---
name: igame-actv recall/cancel 判断待实测
description: 用户要求下次"下活动 / 撤回活动"时，主动测一下 skill 里 recall vs cancel 的分层判断是否能正确执行。
type: project
originSessionId: c540f3a7-ccbb-44c2-bcba-b55e73c2c111
---
igame-actv skill 里的"下线活动"分层判断（recall vs cancel）刚改完文档，
**还没有在真实场景下被验证过**。

**Why:** 用户 2026-04-15 在三轮纠正后定稿了"任务+状态"分层规则
（详见 feedback_igame_cancel_vs_recall.md）。用户明确要求：下次"下活动 /
撤回活动"时，喊一下让我测这块。

**How to apply:**
- 触发条件：用户说"下活动" / "下线活动" / "撤回活动" / "取消活动" 等涉及
  recall 或 cancel 的场景
- 要做的事：主动按 SKILL.md 的"下线活动：撤回 vs 取消"小节走一遍判断
  1. 先确认目标活动当前状态（部署申请状态 vs 上线中状态）
  2. 按状态选 recall 或 cancel
  3. 跟用户口头复述一遍判断逻辑再执行
- 验证完后把结果反馈给用户，如果文档还有歧义就继续修
- 测完可以删掉这条 memory
