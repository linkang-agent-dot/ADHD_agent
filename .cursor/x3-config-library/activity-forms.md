# X3 活动形式目录（activity-forms）

> 换皮的核心理念：**不创造新结构，找上一期最接近的活动形式 → 整段复制 → 只换该换的（ID/皮肤/文案/少量数值）**。
> 这份目录回答两个问题：① X3 现有哪些活动形式可复用 ② 每种形式涉及哪些表、改哪些字段、上一期实例是谁。
> 字段细节见 `table-reference.md`；必检见 `must-check.md`。
> 来源：`C:\x3\gdconfig\tsv\` 全量 `Actv*__*.tsv` 扫描（2026-05-29，127 文件 / 49 玩法模块）。

---

## 0. 统一装配原则

1. **锚点**：几乎所有 Actv 主表第一列都是 `ActvOnline.ContentID`。换皮**先在 `ActvOnline__ActvOnline.tsv` 建活动行**（填 TimeController / ActvType / MailID / 美术 DK），再挂玩法表。
2. **奖池拆子表**：主表存玩法参数 + 引用 `*Reward`/`*Group` 子表存实际奖励。换皮主要改子表道具。
3. **换皮三类接口列**：`DK_*`（美术）/ `TXT_*`（本地化 key）/ 奖励道具 ID。视觉替换重点是前两类。
4. **本服 vs 跨服**：转盘/合成/积分等主表多带「本服排行榜」列且仅支持本服；跨服改造见 `table-reference.md §5`。

### 一个节日通常由这些拼装（典型装配模板）
```
ActvGroup（节日聚合入口外观）
 ├─ 累充活动        ActvOnline + ActvTask(902) + RechargePointPackWhitelist   ← 几乎每节日必有
 ├─ 礼包链          ChainPack(A线连锁11) + 锚点(15) + 皮肤(1) + 家具/主城(16)   ← 变现主力
 ├─ 1~2 个玩法      积分/酒馆/许愿池/转盘/兑换/拼图/航行 任选            ← 节日玩法主题
 ├─ 排行榜          RankCfg + RankRewardSlotCfg（若玩法带榜）
 └─ 外观奖励        Skin / FurnitureSkin / FurnitureDecorate / MemorialCard / PackHeroPromotion
```

---

## 1. 节日换皮主力形式（适配度：高）

> 这 13 种是节日换皮的主力。换皮 = 选其一为模板，复制结构改下面「换皮可改项」。

### 1.1 ActvScore — 积分活动 ⭐最高频
- **玩法**：做任务攒积分，积分达档领奖 + 排行榜奖励。最经典的节日积分通用框架。
- **表**：主 `ActvScore__ActvScore`（ScoreGroup/TaskID）＋ `ActvScoreGroup`(积分档→Reward) ＋ `ActvScoreTask`(任务/Score/TaskType) ＋ `ActvScoreTaskGroup`(任务组) ＋ 跨服 `ActvScoreMulti`(ContentID×Stage)
- **换皮可改项**：任务奖励(子表道具)、积分门槛(AimScore)、皮肤(DK_)、文案(TXT_)、排行榜 RewardID
- **历史实例**：最佳酒馆系列（ContentID 701 基底 / 717·718 节庆通用跨服 / 716 万圣魔女之夜）；ActvType=7 本服 / 24 跨服
- ⚠️ 陷阱：ScoreID=603 是「运营大师」声望榜不是酒馆；跨服必 TimeCycle TT=1；不同节日复用同套 RewardID(30391-30398 八档)

### 1.2 ActvTavernAdventure — 酒馆冒险（开箱抽奖）
- **玩法**：用代币开箱抽奖（开箱币+刷新币+每日刷新+单次分数+大奖），开箱攒分领开箱积分奖
- **表**：主 `TavernAdventureMain` ＋ `Details`(内容组) ＋ `GlassGroup`/`GlassRewards`(酒杯奖池) ＋ `OpenScoreReward`(开箱积分奖)
- **换皮可改项**：代币道具、奖池道具、皮肤、文案
- 节日常驻开箱玩法

### 1.3 ActvWishingPool — 许愿池（投放抽奖）
- **玩法**：投放道具到许愿池抽奖，奖励池 + 阶段奖励 + 触发 Pack 礼包
- **表**：主 `ActvWishingPool`(IsOn/奖励组/阶段奖组/关联Pack) ＋ `ActvWishingPoolReward`(奖池) ＋ `ActvWishingPoolStageReward`(阶段奖)
- **换皮可改项**：投放/产出道具、阶段门槛、关联礼包、皮肤
- ⚠️ ActvType=50，TimeCycle 疑似硬编码 TT=1；许愿池礼包(如 1002001)跨节日复用要加各节日累充白名单

### 1.4 ActvWishing — 许愿/兑换简版
- **玩法**：消耗道具换指定道具，按许愿次数递进。轻量许愿/兑换。
- **表**：单表 `ActvWishing`
- **换皮可改项**：消耗道具、产出道具、次数。配置极简，节日轻量兑换首选

### 1.5 ActvLuckyWheel — 幸运转盘
- **玩法**：消耗道具单/十连转盘，奖池 + 单日上限 + 超级大奖保底 + 累抽触发礼包 + 本服排行榜
- **表**：主 `ActvLuckyWheel`(含 DK_转盘图/指针/底图) ＋ `ActvLuckyWheelReward`(奖池) ＋ `ActvLuckyWheelOtherReward`
- **换皮可改项**：转盘美术(DK_)、奖池、保底、皮肤。换美术+奖池即变节日转盘

### 1.6 ActvMechaWheel — 机甲转盘（双层转盘）
- **玩法**：LuckyWheel 进阶，内圈+外圈双盘、付费/免费各奖池、可选机甲、保底翻倍、阶段奖、本服排行榜
- **表**：主 `ActvMechaWheel` ＋ `Inner/OuterReward`(内外圈) ＋ `OtherReward` ＋ `MechaItemMap`(机甲映射)
- **换皮可改项**：内外圈美术(DK_)、奖池、可选机甲、皮肤。节日大型转盘

### 1.7 ActvExchange — 兑换商店
- **玩法**：代币换道具/食谱蓝图，单次数量+兑换上限+排序+特惠标记，每天 UTC0 刷新
- **表**：单表 `ActvExchange`
- **换皮可改项**：代币、商品、限购、特惠标记。节日兑换商店标配
- ⚠️ ActvType=13，TimeCycle 用 TT=1/3/4

### 1.8 ActvCrafting — 合成/制作
- **玩法**：消耗道具制作商品，奖励池 + 阶段奖励组 + 本服排行榜
- **表**：主 `ActvCrafting`(DK_箱子开关图/底图) ＋ `ActvCraftingReward`(奖池) ＋ `ActvCraftingOtherReward`
- **换皮可改项**：制作材料、产物、箱子美术、皮肤

### 1.9 ActvDonate — 捐赠（全服共建）
- **玩法**：捐献道具攒积分，个人奖励 + 集体(全服)奖励，每日请求上限 + 急需加成
- **表**：主 `ActvDonate` ＋ `ActvDonateItem`(捐献道具组) ＋ `ActvDonatePersonalReward`(个人) ＋ `ActvDonateServerReward`(全服)
- **换皮可改项**：捐献道具、个人/全服奖励、皮肤。社区共建型节日

### 1.10 ActvPuzzle — 拼图
- **玩法**：做任务集拼图块，集齐领阶段奖，行×列网格。强节日视觉主题
- **表**：主 `ActvPuzzle`(DK_拼图/格子/背景/底图 + TXT_拼图名) ＋ `ActvPuzzleReward`(阶段奖) ＋ `ActvPuzzleTask`(任务)
- **换皮可改项**：拼图图(DK_)、任务、阶段奖、皮肤
- **历史实例**：26尼罗 101825「象形密文/拼图」(ActvType=18)

### 1.11 ActvVoyage — 航行/航海抽卡
- **玩法**：普通/精准/神秘三种道具抽岛屿，登岛触发事件，阶段奖励 + 角色模型展示
- **表**：主 `ActvVoyage`(岛屿组/三种抽卡道具/阶段奖/DK_角色模型) ＋ `ActvVoyageIsland` ＋ `ActvVoyageLevel` ＋ `ActvVoyageEvent` ＋ `ActvVoyageOtherReward`
- **换皮可改项**：岛屿、抽卡道具、模型、奖励。节日大型探索玩法

### 1.12 ActvLoginPurchase — 登录购买/累登礼包
- **玩法**：挂 ActvOnline 的登录领奖 + 购买组合，奖励分组
- **表**：主 `ActvLoginPurchase` ＋ `ActvLoginRewardGroup`(奖励组)
- **换皮可改项**：奖励、皮肤。节日累登/登录购买

### 1.13 ActvVisitPack — 拜访礼包
- **玩法**：礼包 + 邀请函机制（每日邀请函数量 + 邀请函奖励）+ 阶段奖励
- **表**：主 `ActvVisitPack`(礼包ID/阶段奖/邀请函道具/每日数量/DK_礼包图标) ＋ `ActvVisitPackReward`
- **换皮可改项**：礼包内容、邀请函奖、皮肤
- ⚠️ **MainBg 必须空**（见 must-check）；历史实例 210417圣诞/210617尼罗/210717情人节/210816新春/210921夏日

### （附）ActvIdle — 放置/钓鱼
- **玩法**：放置型(钓鱼)，限定/加成英雄上阵打关卡组，达关卡数发额外奖
- **表**：主 `ActvIdle`(加成英雄/系数/限定英雄/关卡组) ＋ `ActvIdleLvReward`
- **换皮可改项**：关卡组、奖励、主题

---

## 2. 可节日化但偏运营/付费框架（适配度：中）

| 模块 | 玩法 | 表 |
|------|------|----|
| **ActvNewQueuePkg** | 队列礼包（免费CD包/充值礼包/一键购买，分 Craft/Dispatch/Build 页签） | 单表 `ActvNewQueuePkg` |
| **ActvPack** | 活动礼包（挂 ActvOnline 的礼包容器，IsOn 控导出） | 单表 `ActvPack` |
| **ActvDailyRank** | 每日排行（积分任务+阶段奖+排名奖+TXT主题名） | 主 `ActvDailyRank` ＋ `ActvDailyRankReward` |
| **ActvLogin** | 登录签到/补签（钻石补签，可显英雄立绘） | 单表 `ActvLogin` |
| **ActvTransport** | 运输护送（护送船只+劫掠+船只配置） | 主 `ActvTransport` ＋ `ActvTransportShip` |
| **ActvWonder** | 奇迹/任务刷新（每次刷新每组任务，巢穴/KVK类型） | 主 `ActvWonder` ＋ `ActvWonderReward` ＋ `ActvWonderTask` |
| **ActvExercise** | 演习/Boss讨伐（Buff加成+伤害奖励+伤害排行） | 主 `ActvExercise` ＋ `ActvExerciseReward` |
| **ActvSaveDwarves** | 拯救矮人（情报任务剧情解谜） | 主 `ActvSaveDwarves` ＋ `ActvSaveDwarvesBase` |
| **ActvUnderpants** | 内裤猜测（情报任务猜谜小游戏） | 主 `ActvUnderpants` ＋ `ActvUnderpantsBase` |
| **ActvRomance** | 浪漫任务（阶段任务链，绑定情人节主题） | 主 `ActvRomanceTask` ＋ `ActvRomanceReward` |
| **ActvBuildup / ActvGrowth / ActvIntelligence** | 任务-奖励型（阶段/分档/情报） | 各自单/双表 |

---

## 3. 不做节日换皮（适配度：低 / 否）

- **跨服战 PvP（否）**：ActvGvG · ActvKvk · ActvKvkSeason · ActvKVKTask · ActvKVKBP · ActvKVKBounty · ActvKvKWonder · ActvInvasion · ActvGuildMerge
- **付费/养成杂项（低）**：ActvDiamondRebate(钻石返利) · ActvRevive(复活购买) · ActvHeroSkillSell / HeroSkillTryUse / HeroUpRoute / HeroChampionRoad / HeroVerify(英雄养成) · ActvShipEquipSell(船装出售) · ActvBattlePass / BattlePassScore(战令) · ActvScoreGuidInternal(内部引导)
- **基础设施（非玩法）**：ActvOnline(调度根/锚点) · ActvTask(通用任务池) · ActvMail(活动邮件) · ActvCommunity(FB/Discord 关注奖)

---

## 4. 完整 Actv* 模块清单（51 组，速查）

| 模块 | 主表 | 子表 | 节日适配 |
|------|------|------|:---:|
| ActvScore | ActvScore | ScoreGroup/Guild/Multi/MultiServer/Task/TaskGroup | 高 |
| ActvTavernAdventure | TavernAdventureMain | Details/GlassGroup/GlassRewards/OpenScoreReward | 高 |
| ActvWishingPool | ActvWishingPool | Reward/StageReward | 高 |
| ActvWishing | ActvWishing | — | 高 |
| ActvLuckyWheel | ActvLuckyWheel | Reward/OtherReward | 高 |
| ActvMechaWheel | ActvMechaWheel | Inner/Outer/Other Reward/MechaItemMap | 高 |
| ActvExchange | ActvExchange | — | 高 |
| ActvCrafting | ActvCrafting | Reward/OtherReward | 高 |
| ActvDonate | ActvDonate | Item/PersonalReward/ServerReward | 高 |
| ActvPuzzle | ActvPuzzle | Reward/Task | 高 |
| ActvVoyage | ActvVoyage | Event/Island/Level/OtherReward | 高 |
| ActvLoginPurchase | ActvLoginPurchase | LoginRewardGroup | 高 |
| ActvVisitPack | ActvVisitPack | Reward | 高 |
| ActvIdle | ActvIdle | LvReward | 高 |
| ActvNewQueuePkg | ActvNewQueuePkg | — | 中 |
| ActvPack | ActvPack | — | 中 |
| ActvDailyRank | ActvDailyRank | Reward | 中 |
| ActvLogin | ActvLogin | — | 中 |
| ActvTransport | ActvTransport | Ship | 中 |
| ActvWonder | ActvWonder | Reward/Task | 中 |
| ActvExercise | ActvExercise | Reward | 中 |
| ActvSaveDwarves | ActvSaveDwarves | Base | 中 |
| ActvUnderpants | ActvUnderpants | Base | 中 |
| ActvRomance | ActvRomanceTask | Reward | 中 |
| ActvBuildup | ActvBuildup | — | 中 |
| ActvGrowth | ActvGrowth | — | 中 |
| ActvIntelligence | ActvIntelligence | — | 中 |
| ActvDiamondRebate | DiamondRebateMain | DiamondCostGoto | 低 |
| ActvRevive | ActvRevive | — | 低 |
| ActvHeroChampionRoad | ActvHeroChampionRoad | ChampionRoadContent/StageCondition/StageProgress | 低 |
| ActvHeroSkillSell | ActvHeroSkillSell | — | 低 |
| ActvHeroSkillTryUse | ActvHeroSkillTryUse | TryTask | 低 |
| ActvHeroUpRoute | ActvHeroUpRoute | ChapterInfo/Dialogue/HeroStrengthen/ProgressReward | 低 |
| ActvHeroVerify | ActvHeroVerify | — | 低 |
| ActvShipEquipSell | ActvShipEquipSell | Item/Monster | 低 |
| ActvBattlePass | BattlePass | Reward | 低 |
| ActvBattlePassScore | BattlePassScore | Reward | 低 |
| ActvScoreGuidInternal | ActvScoreGuidInternal | Reward | 低 |
| ActvGvG | GVGBase | RoundTime/FlagShip/LuckyWheel(+Reward)/Rank(Base/Reward/Stage) | 否 |
| ActvKvk | ActvKvk | — | 否 |
| ActvKvkSeason | ActvKvkSeason | KvkTemplate | 否 |
| ActvKVKTask | ActvKvkTask | — | 否 |
| ActvKVKBP | ActvKVKBP | Reward/Task | 否 |
| ActvKVKBounty | ActvBounty | Reward/Task | 否 |
| ActvKvKWonder | ActvKvKWonder | SeasonAward | 否 |
| ActvInvasion | ActvInvasion | Debuff/Task | 否 |
| ActvGuildMerge | ActvGuildMerge | — | 否 |
| ActvOnline | ActvOnline | ActvGroup/ActvGroupSchedule | 基础设施 |
| ActvTask | ActvTask | — | 基础设施 |
| ActvMail | ActvMail | — | 基础设施 |
| ActvCommunity | ActvCommunity | — | 基础设施 |

---

## 关联
- 字段细节 → `table-reference.md` · 必检细则 → `must-check.md`
- 收益参考（哪些形式在哪些服赚钱）→ `memory/reference_x3_festival_performance.md`
- 积分活动深挖 → `memory/reference_x3_score_activity.md`
