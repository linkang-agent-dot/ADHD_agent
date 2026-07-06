---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 01 深海罗盘 转盘抽奖 — 配置备份表

> KB 配置备份表（一个功能一个文件夹），非 live tsv。复用换皮（**门槛提示一小块需程序，不挡配置**）。
> **复用源**：尼罗之辉大转盘（ActvOnline 101023 / ActvLuckyWheel 1023 / RewardGroup 319 / OtherRewardGroup 3019）。
> **ID 来源**：GSheet「深海节-开发配置需求」【1】【6】。默认**新建 CID1025**（随夏日惯例，见待确认①）。

## 这个是什么
ActvType=10 大转盘 + 排行榜（自带）。转盘抽外显/养成料/代币；排行榜冲榜拿皮肤+铭牌。

## 表清单（已配换皮骨架+奖池）
| 表 | 新增 | 文件 | 模板 |
|---|---|---|---|
| `ActvOnline__ActvOnline.tsv` | **101025**(ContentID 1025) | `ActvOnline_新增101025.tsv` | 尼罗 101023 |
| `ActvLuckyWheel__ActvLuckyWheel.tsv` | **1025** | `ActvLuckyWheel_新增1025.tsv` | 尼罗 1023 |
| `ActvLuckyWheel__ActvLuckyWheelReward.tsv` | **Group 321**(max320+1) | `LuckyWheelReward_新增Group321.tsv` | 尼罗 Group319 |
| `ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv` | **Group 3020**(max3019+1) | `LuckyWheelOtherReward_新增Group3020.tsv` | 尼罗 Group3019 |

## 链路（怎么串）
`ActvOnline 101025`(ContentID=1025) → `ActvLuckyWheel 1025`(RewardGroup=**321** / OtherRewardGroup=**3020** / Consume=抽奖代币) → 奖池 Group321 + 进度奖励 Group3020。

## 已配好（复用骨架）
- ActvOnline 101025：名「深海罗盘-大转盘」、ContentID=1025、ActvType=10。
- ActvLuckyWheel 1025：RewardGroup=321、OtherRewardGroup=3020、转盘皮 DK 换深海占位。
- 奖池 Group321：养成料（神秘金属55101/材料票4101/传奇技能书19003/加速11003·11002）**复用现成**，尼罗石币1129 标注换深海代币。
- 进度额外奖励 Group3020：x50~x1500 七档结构复用尼罗。

## ⚠️ 待确认 / 待补（转盘比装饰多，GSheet【8】已点名几条）
1. **【设计·GSheet点名】新建 CID1025 vs 原位改尼罗1023** → 本备份表按**新建1025**（GSheet 默认）。若要原位改 1023 需重做。
2. ✅**【已定·用户拍板】转盘核心大奖 = 深海猎手潜艇行军皮 Item15065**（奖池 Group321 已加 SReward 行 32100，权重 10 待数值核）。深海猎手归属=转盘；05 累充顶档是否仍投同一潜艇皮需另行确认（避免与转盘重复）。
3. ✅核心大奖已改潜艇皮 15065（见②）。海风旅者（英雄皮 Item_5303401）原设计的转盘主投 → **降级**，是否仍放奖池次级 or 移到兑换商店，待定。
4. **传说铭牌·航者徽记** → Title 表新增（待建 ID + 出图），排行榜 Top 段投放。
5. **RankCfg 186**（RankType12，GSheet【6】）→ 排行榜配置尚未建（投放卡待确认②④）；**门槛提示「距上榜{0}分」需程序**（复用夏日）。
6. ✅**节日代币已建**：深海罗盘券 **1150**(转盘 Consume) + 深海宝珠 **1151**(兑换币·奖池产出)，见 `配置备份表\_节日通用道具\`。ActvLuckyWheel.Consume 已填 1150、奖池代币已换 1151。（剩道具图标 DK + 数值待补）
7. **OtherReward 的 RewardID**（Group3020 各行 col2）→ 现沿用尼罗的 RewardID，需按深海奖励内容在 Reward 表新建对应行。
8. **DK 入库**：转盘皮/指针/背景/icon（深海转盘活动背景已出·待挑定版）→ `DK_img_Activity_deepsea_turntable*` / `_bg_wheel` / `_icon_wheel`。
9. ActvOnline 的 TimeController 换 **1830**、RankID 换 **186**（现沿用尼罗值，落地时改）。
10. 本地化 TXT。

## 落地顺序
点名待确认①②③ → DK入库 → 代币/铭牌建 → 奖池Group321补海风旅者SReward + Reward表补OtherReward指向 → RankCfg186 → ActvOnline改TC/RankID → 程序门槛提示 → i18n → xlsx+tsv一致过gate → commit → 导表。

_生成 2026-06-18；分支 dev_festival。复用换皮骨架已配，奖池主皮/排行榜投放待点名。_
