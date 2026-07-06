---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026-06]
---

# 深海大富翁 岛屿显示双 BUG — 修复记录 + 客户端交接单

> 活动：航海之路 ActvVoyage（cfgID 2802 / AO 102802），深海换皮（IslandGroup2 / EventGroup 199-206）。
> 时间：2026-06-25。配置侧（BUG2）已修并 push dev_festival；BUG1 待客户端程序。

## 共同根因（一句话）
单等级改造把幸运岛/钻石岛的 `ExpGroup` 清空了，但这两类是**框架写死的「可升级岛」类型**（`ACTIVITY_VOYAGE_CAN_LEVEL_UP_LAND_TYPE = {GEM=4, LUCKY=5}`，在 `client/.../CSShared/Common/Const/ActivityConst.cs:396`）。于是三方等级口径打架：
- **客户端**靠「ExpGroup 查不查得到」定岛屿等级 → ExpGroup 空 → 算成 **level=0**（`UIActvGridBubble.cs:63/99-122`）。
- **服务端**用 `landInfo.level` → 初值 1、ExpGroup 空升不了级 → 恒 **level=1**（`ActivityMeta.Voyage.cs:172`）。
- **奖励数据**还在 **Level=1** 桶（`ActvVoyageEvent.Level=1`）。
- 奖池 key = `EventGroupID*1000 + level*100`（`ActivityUtils.cs:806`，客户端服务端共用同一份）。

> ⚠️ 陷阱：最「显然」的修法——把 `ActvVoyageEvent` 的 Level 从 1 清空让客户端 level=0 对上——**会让服务端（恒 level=1）查空、静默发不出奖**，把显示 BUG 变成掉奖事故。已排除。

## BUG2（幸运/钻石岛奖池+概率不显示）—— ✅ 已配置修复
客户端 level=0 查 `EG*1000+0` 桶，但数据在 `EG*1000+100` → 查空 → 奖池不显示。
**修法（纯配置，服务端零改动）**：给幸运/钻石岛在 **Level=0 桶补一份奖励副本**（跟宝藏/神秘岛同机制——它们本来就是 Level 空、显示正常）。
- 在 `ActvVoyageEvent` 追加 16 行：ID = 原行 ID−100（=`EG*1000+0+seq`），Level 列**留空**，其余（EventGroupID/EventType/道具/数量/权重/DKImg）照抄原 Level=1 行。
- 覆盖：钻石 EG200(1行) + 幸运 EG201/202/203(各5行)。
- 导出按 `group=EG*1000+Level*100` 分桶、`WeightPercent` 按 `EG*1000+seq` 算（`def/actvvoyageevent_def.py`）→ 副本概率自动正确。
- 效果：客户端 else 分支(level=0)读到副本 → **奖池+概率正常显示**；服务端仍用 level=1 原行发奖 → **完全不受影响**；老配置(EG99-106/IslandGroup1)零改动。
- 提交：gdconfig `dev_festival` commit `608fe72`（仅 ActvVoyageEvent.tsv +16 行）。本地 ExportTable 通过，jolt build #1298。

## BUG1（没配等级却显示「Lv」标）—— ✅ 已修（x3-project dev_festival commit 8e02bb6，不走 MR 直推）
> ⚠️ 客户端代码改动需**重新出客户端包**才在游戏里生效（BUG2 配置走 jolt 导表即生效；BUG1 代码要打包）。
**只剩棋盘格子一处**（气泡 `UIActvGridBubble` 因 ExpGroup 仍空、走 else 分支，本来就不显等级，无需动）。

文件：`client/Assets/Scripts/UI/Actv/GridItem.cs:108-109`
```csharp
// 现状：只按岛型判，不看有没有真配等级 → 幸运/钻石岛永远显示 Lv
var canLvUp = ActivityConst.ACTIVITY_VOYAGE_CAN_LEVEL_UP_LAND_TYPE.Contains(islandCfg.IslandType);
mGoLv.SetActive(canLvUp);
```
**建议改法（一行逻辑）**：再加一个「该岛真的配了经验组才显示」的判断——
```csharp
var canLvUp = ActivityConst.ACTIVITY_VOYAGE_CAN_LEVEL_UP_LAND_TYPE.Contains(islandCfg.IslandType)
              && CActvVoyageLevel.Instance.Group2Exp.ContainsKey(islandCfg.ExpGroup);
mGoLv.SetActive(canLvUp);
```
- ExpGroup 空（深海单等级岛）→ `ContainsKey` false → `canLvUp` false → 不显 Lv，且 line 110 `if(!canLvUp) return;` 顺带跳过进度条。
- 老航海之路（ExpGroup=1）→ 仍 true → 正常显示 Lv。
- 与紧邻的 line 115（`if(!Group2Exp.TryGetValue(ExpGroup)) return;`）口径一致，是把那个判断提到「是否显示 Lv 控件」这一步。
- 改完出客户端包即可，无需动配置/服务端。

## 为什么不在客户端一并把 BUG2 也改了
BUG2 走配置（level=0 副本）能即时上线、零客户端排期、零服务端风险；BUG1 是纯显隐、必须出包。两者解耦，互不依赖。
