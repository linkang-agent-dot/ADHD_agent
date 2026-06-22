---
name: feedback_constraint_framing_onetime_cost
description: "别把\"一次性成本\"误当\"不可逾越的硬约束\"——识别红线是值\"一次\"还是\"永久\"，付一次买永久收益往往更优"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: aa81a569-cf03-433a-becf-37475d030549
---

做方案时，先分清面前的约束是**永久红线**还是**一次性成本**，别把后者误当前者去绕。

**Why**：X3 世界杯竞猜重构复盘。当时我要让"换对阵可热更"，把"新增 proto 字段 = 走客户端打包（proto 是客户端 bundle，热更只服务端）= 不可接受"当成硬墙，于是选了唯一不动客户端的路——复用已有 `progressPackData` proto，用 `day=0/day=1` 硬塞两队（hack，语义模糊）。大哥（X3NEW-1432）没把"新增 proto"当死墙：识别出它只是**一次性**客户端打包成本，付一次上线专属 proto，换来永久干净架构 + 未来所有对阵切换照样零打包。proto 本身改起来是机械活（生成工具自动出 250 行），根本不卡。卡住的是我的**约束框定**。

**How to apply**：
1. 遇到"绝不能动 X"的红线，先问一句：动 X 是**每次都要付**，还是**一次性付完就翻篇**？
2. 若是一次性成本 → 算账：一次成本 vs 绕开它欠下的长期 hack 债。常常付一次更划算。
3. 红线常被自己无意识抬成"绝对"（我把"零客户端打包"从"换对阵时零打包"悄悄扩成了"任何时候都不准动客户端"）——警惕这种范围蔓延。
4. 当下没发版窗口/只能先发车时，hack 是合理的"先上线"动作；但要留个 TODO：有窗口了做对。hack 不等于错，长期当正解才错。

关联：[[reference_x3_customparam_activity_pattern]]（这次重构的代码决策模板）、[[feedback_surface_problems_not_thrash]]。
