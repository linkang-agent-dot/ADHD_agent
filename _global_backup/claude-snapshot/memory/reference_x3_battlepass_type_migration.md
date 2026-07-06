---
name: reference-x3-battlepass-type-migration
description: X3 BP加档/迁移落地知识——ActvType11(BATTLE_PASS)→22(BATTLE_PASS_SCORE)+ScoreMode直出/累加分叉+三Bug连锁
metadata:
  node_type: memory
  type: reference
  originSessionId: bp-type-migration-study
---

# X3 BP 加档位 / Type 迁移落地知识（ActvType 11 → 22）

来源：zhangli 在 `dev_festival` 的英雄手册迁移（2025-06-29~07-01，关联 `X3NEW-hero-handbook-deluxe`）。唯一入口 HTML `C:\Users\linkang\Pictures\hero-handbook-type11-to-type22-migration.html`。**这是「给 BP 加档 / 迁 BP 类型」的实证范式**，跟 [[project-x3-hero-handbook]] 的 ActvType=27 登录购买豪华版是**两码事**，别混。

## 背景：两种 BP 的核心差异（决定为什么要分叉）
| 维度 | Type 11 (BATTLE_PASS，旧) | Type 22 (BATTLE_PASS_SCORE，新) |
|---|---|---|
| 积分来源 | `GetTaskProgress` **直出** → `newScore = progress` | `taskScore × progress` **累加** → `newScore = oldScore + score` |
| 阈值判断 | `UpgradeTotalCount + Count`（累计值） | `UpgradeTotalCount`（原子值） |
| 进度显示 | 真实天数/次数（"登录了3天"） | 等级 |
| 典型 | 登录3天→分=3 | 每次登录+10→累计30 |

三个活动迁移：登录好礼 101104→102247(累计登录天数321)、海盗猎人赏金 101102→102248(主线情报412)、猎杀时刻 101110→102249(情报循环410)。

## ★核心手法：ScoreMode 运行时分叉（不新建 Activity 类型）
**决策=用配置字段区分行为，而非新增 TriggerType**（避免全套 Condition/Meta/Prefab 样板）。`BattlePassScore` 表加 `ScoreMode` 字段：
- `BATTLE_PASS_SCORE_MODE_ACCUMULATE = 0`（Type 22 原行为，累加）
- `BATTLE_PASS_SCORE_MODE_DIRECT = 1`（对齐 Type 11，直出）

常量在 `CSShared/.../ActivityConst.cs`。同一个 `ActivityBattlePassScoreCondition` 类内靠运行时分支同时支持两种语义。

## 落地改动点（服务端 + UI + 配置三层）
1. **`ActivityBattlePassScoreCondition.cs`**（CSSharedHotfix，X3 共享代码靠 `#if !_CLIENTLOGIC_`/`_SERVERLOGIC_` 宏分编，服务端逻辑在此不在 server/）：
   - `SetTaskProgress` 分叉：`newScore = DIRECT ? progress : oldScore + score`
   - `GetTaskProgress` 修复（见 Bug1）
   - 登录天数补偿（见 Bug3）
2. **`ActivityMeta.cs`**（server）：`HandleNewPlayerActivityInfos` 对 `TimeController=0` 优雅降级——已有实例跑完 endTime 自然关闭、新玩家不创建（没这段，TimeController=0 会误删已有玩家实例）。
3. **UI**：`UIActvBattlePassScore.cs`（顶部数字 DIRECT→progressScore / ACCUMULATE→level）、`UIBattlePassScoreItem.cs`（slider 公式 + 显示文本分支）、新增 `UIActvBattlePassMulti.prefab`（多轨 BP 界面）。档位解锁判断：`reached = DIRECT ? score >= UpgradeTotalCount+Count : score >= UpgradeTotalCount`。
4. **gdconfig**：`ActvOnline`(新活动+老活动 TimeController=0)、`BattlePassScore`(三档 ScoreMode)、`BattlePassScoreReward`(组145/146/147 + Count 修正)、`Reward`(奖励重做)。

## ★三 Bug 连锁（改 BP 必踩，按此顺序排查）
1. **`GetTaskProgress` 写死 `return 0`** → `SetTaskProgress` 里 `score = taskScore × 0 = 0` → 积分永不涨、活动完全不可用。修复=遍历 contentId 下活动实例返回真实 progressScore（仅服务端编译）。
2. **`Count` 语义被当"本档增量"** → 累计阈值 1/4/7/10... 被累加成 0/1/5/12... → 玩家 Lv1 立即 finished + 后续门槛超难。**修复走配置侧不动代码**：把 Count 填成累计阈值（组146=1→4→7...→97，与源 Type 11 一致）。
3. **登录当天 `OnDayUpdate` 未执行** → progressScore=0 → DIRECT 模式首日不触发。修复=DIRECT + `PlayerTotalLoginDay` 任务，活动初始化后 `Master.UpdateActivityScore(activityId, 1, startTime)` 补成 1。

## 关键决策沉淀
- 老活动**不删除**，设 `TimeController=0` 让已有玩家数据保留、自然到期——避免数据迁移和退款问题。
- `Count` 语义修正**只改 gdconfig 填值**，不动代码。
- 迁移是 cherry-pick 到 dev（登录补偿 commit `9ca796d0ba0`→`7f6de5d2013`）。

关联：BP 双档价值锚点复盘见 [[project-x3-hero-handbook]] 世界杯至尊 BP 段；ActvType 枚举真源 [[reference_x3_actvtype_enum]]；付费机制 [[reference_x3_monetization_mechanics]]。
