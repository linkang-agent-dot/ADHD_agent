---
name: feedback_x3_progression_price_from_x2_handbook
description: "X2→X3 换皮数值必须走相对守恒缩放(照抄原案投放结构×ROI系数),别手搓凑盘子;X2养成线手册单价只是旁证"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 74f31af4-2067-4bc8-b0da-37b9c6cad350
  modified: 2026-07-24T10:25:24.636Z
---

**头号纪律（2026-07-24 被用户纠正）：X2→X3 换皮/搬运案定数值，必须走「相对守恒缩放法」，不许自己挑道具凑盘子。**

做法：直购线各档**照抄对标 X2 档的投放结构（道具比例原样不动），数量 ×k 同比放大，k = 目标ROI ÷ ROI_x2**。数学上 `ROI_new = k × ROI_x2 = 目标ROI`，**由构造精确守住，不需要任何道具绝对钻值**——皮肤随机宝箱/成长自选等无估值容器在守恒法下**天然不需要定价**。

**Why**：X3 养成线估值地图缺失（x3-numerical-design past-references 空白清单确认"养成线深调 X3 完全缺价值地图"；限时秒杀/限购也在空白清单）。换皮案本就对标 X2 原案投放，守恒缩放保结构+守 ROI，是 x3-numerical-design 护栏①/foundation「相对守恒法」的核心。**踩坑实证**：X3 限时抢购 v1 我手搓（自己挑英雄美酒/金币凑盘子、丢了 X2 原有的英雄粉尘、还造出"待拍皮肤宝箱 V/成长自选 W 两个绝对值"的伪阻塞），被用户点"你得走一遍数值换皮 skill"。改回守恒缩放后 V/W 伪阻塞直接消失、task-checker 10/10 0 blocker。

**How to apply**：① 先建档位映射表（X3档←对标X2档 + k=目标ROI÷ROI_x2）；② 每档 X3量 = X2量×k，道具比例不动；③ **道具层判定**（换皮框架 `reskin-numerical-framework.md`）：游戏系统养成道具（碎片/图纸/技能书/天赋/升星/金羽/经验）→沿用映射 X3 对应；节日品牌/玩法道具（如"大富翁骰子"）→换 ID；机制道具→本节日新建。换 ID 时若替换物单价≠原道具，须按值重算数量守恒。④ 落配置过流通度审计（存在性/i18n/图标/流通度/功能出口）。⑤ **只有想核绝对价值时**才查 X2 养成线手册（`C:\ADHD_agent\.cursor\x2-numerical-design\养成线深度手册.md`，7线关键材料单价×500=钻石；万能碎片$2/军备图纸$1/金羽$0.17/技能书$1/收藏品升星$0.5）——**手册是旁证不是主路径**。⑥ 收工前必派 task-checker type=numerical 复查（skill 第4步，别漏）。

关联 [[reference_x2_progression_kb]] + x3-numerical-design skill 护栏①相对守恒法 + reskin-numerical-framework.md 道具层。
