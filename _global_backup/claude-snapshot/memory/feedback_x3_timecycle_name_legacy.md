---
name: x3-timecycle-name-can-be-legacy
description: "X3 TimeCycle 的\"列1\"名字可能是历史换皮残留，看 StartTime/Duration 实际值而非名字判定是否正确"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b1d54617-ced7-46ea-8de4-1270c217b1a4
---

TimeCycle.xlsx 的 `列1`（描述名）有时是历史复用残留——节日换皮时可能只新建活动 ID 复用旧 TimeCycle ID，而 TimeCycle 自身的描述名没改。**不要因为名字写着别的节日就判定为 BUG。**

**Why**: 2026-05-28 排查尼罗装饰礼包触发时段时发现，夏日装饰礼包 (ActvOnline 106101) 的 TimeController=1826 名字是"活动-白色花嫁活动-2026/02/06 UTC 0点开，持续10天"，看似换皮没改 TimeCycle 名。但用户确认实际时间值（2026-02-06 + 10 天）跟夏日恋语部署对齐，是有意复用，**不用修**。

**How to apply**: 看到 TimeCycle 名跟当前节日对不上时，先核对实际 `StartTime` / `Duration` / `TriggerType` 的值是否符合预期，再问策划是否需要重命名。命名只是 staff 注释，运行时不读。

关联：[[reference_x3_timecycle]] TimeCycle 与 ActvOnline 绑定关系
