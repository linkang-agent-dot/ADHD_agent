---
name: x3
description: X3 三类常用付费机制的代码+配置实现：重复外显转钻补偿、PiggyBank储蓄罐、WeeklyCard自选周卡
metadata: 
  node_type: memory
  type: reference
  originSessionId: 490ce72b-3baa-4614-9fe0-430f6331e079
---

X3 三类高频付费机制的代码+配置落点，配活动/换皮/出深度款时直接查。代码仓 `C:\x3-project\server\GameServer.Hotfix\`，配置 `C:\x3\gdconfig\tsv\`。

## 一、重复外显 → 钻石补偿（通用所有外显/头衔）
**配置**：各外显表有 `Regained` 字段 = `[单日数量, 最高数量]`（如 HeroSkin 第11列 `1000|10000`）。
**逻辑**（`HeroMeta.Skin.cs UnlockSkin` → `ResMeta.AddCompensate`，ResMeta.cs:391）：
- 已永久拥有再获 num 个 → num 个全转补偿；新获永久 → 第1个解锁、剩 num-1 转补偿。
- **永久皮肤重复**：钻石 = `Regained[1]`(最高数量) × 个数（如海风旅者重复=10000钻/个）。
- **限时皮肤**：钻石 = `Regained[0]`(单日数量) × 天数 × 个数。
- 发 `ResID.GEM`，reason=`PLAYER_UNLOCK_HERO_SKIN_COMPENSATE`。
**通用性**：同款 `Regained`+`AddUnlockCompensate→AddCompensate` 在 英雄皮肤(HeroMeta.Skin)/航迹船皮肤(ShipMeta.Skin)/岛屿主城皮肤(SkinMeta)/头衔铭牌(TitleMeta)/头像框(BasicMeta.Personal) 全有，各自表都有 Regained 字段。
> 注：皮肤打包成"英雄道具"(EffectTypeHero)时，重复英雄走 `Hero.Regained`(单个补偿道具如碎片)×num，跟皮肤钻石补偿是两条路（StorageMeta.Item.cs:188-225）。

## 二、储蓄罐 PiggyBank（可重复·绑养成货币·等级scale深度款）
**表**：`PiggyBank__PiggyBank.tsv`(ID|ResourceID|Level档|PackID|名|倍数/折扣|容量Num|GroupId) + `PiggyBank__Grade.tsv`(酒馆等级→资源数量)。
**机制**：某资源(如金海凭证 Item 1117)随玩法/时间累积进罐 → 付费"砸罐"折扣领走累积量，**可重复刷新**；到手量 `CalBankResNum(piggyCfgId, level)`，level=min(罐档,玩家酒馆等级)→**等级越高领越多**(Grade表:酒馆18→35级,资源80万→800万)。
**代码**：`GiftMeta.cs` PACK_TYPE_PIGGY(line 2295-2328)；三档小/中/大(容量20万/50万/100万)。
**为什么是深度款**：可重复+绑养成货币+等级scale+折扣锚点 → 高R反复买（航海之路金海储蓄罐4鲸鱼买132次=$13199）。第二轮想要的深度样板。

## 三、自选周卡 WeeklyCard（X3 原生·复用即可，无需大改程序）
**表**：`Pack__WeeklyCard.tsv`(ID|有效期天数|DailyRewards每日奖励RewardID) + `Pack__Pack.tsv`(PackType=WEEKLY) + `COptionalPack`(自选奖池ItemIds)。
**逻辑**：`GiftMeta.cs` PACK_TYPE_WEEKLY(line 494-507)购买后每天领 DailyRewards、weeklyInfo.receivedDay++ 计天；自选走 PACK_TYPE_SELF_SELECT + COptionalPack(line 1167)，selfSelectIndexs 记录所选项。
**界面**(client UI/)：UIWeeklyCardBuy(购买) / **UIWeeklyCardReplacement+SupplyItem(自选替换)** / UIWeeklyCardItem+RewardItem(每日领取) / UIRechargeWeeklyCard(入口) / UIOptionalPack。
**X2 自选周卡先例**：3档(9.99/19.99/29.99)+奖池10项玩家**自选4项**+连续7天每日领+BUY ALL打包(原价$59.97→$49.99,15%OFF)。
**工作量**：复用原生 WeeklyCard+Replacement+OptionalPack → 主要改配置+出图。

实战来源：2026-06 深海节策划案。相关 [[reference_x3_datain_asset_query]]、[[reference_x3_voyage_art_chain]]。
