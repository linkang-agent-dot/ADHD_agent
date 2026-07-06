---
name: project_x3_july_gantt
description: X3 2026年7月并行排期甘特（世界杯×深海节）——两节日并行排期事实入口、比赛日SOP、GM加分命令、深海节档期调整原因
metadata: 
  node_type: memory
  type: project
  originSessionId: 6662964b-398d-4bbb-a4b2-089beb425648
---

# X3 7月并行排期甘特（世界杯 × 深海节）

## 唯一入口
- `KB\产出-数值设计\X3_7月排期_世界杯+深海节甘特.html` — 两节日并行排期的**事实入口**，排期问题先看它。

## 比赛日 SOP
每个比赛日固定两件事：
1. **发邮件结算**（竞猜结算）
2. **GM 加 BP 分**

时限：**末场打完 24 小时内发奖**。

## GM 命令
- `GMAddActivityScore <活动id> <分>`
- 代码位置：`ActivityMeta.Gm.cs:292`
- 作用域：player-scope；权限：普通权限。

## 深海节档期调整
- 为避开世界杯**半决赛(7/15)**、**决赛(7/19)**，深海节**提前到 7/3 全服**上线；D1–D10 跑到 **7/12**。
- （注：后续深海节主体实际定为 14 天 7/3–7/16，会盖到半决赛，用户已接受——最新状态以 [[project_x3_deepsea_festival]] 为准。）

## 文档视角原则
- 活动排期文档按**甘特视角**写，**不写配置 ID**；原则详见 [[feedback_activity_doc_gantt_view]]。
