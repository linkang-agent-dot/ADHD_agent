# X3 配置表总览

*来源：X3交接文档.xlsx + data_dev/ 目录*
*整理日期：2026-03-09*

---

## 📊 总体规模

- 配置文件：160 个 xlsx（+ 1 个 i18n 文件夹）
- 子表总数：407 个
- 功能分类：101 个

---

## 🔗 重要链接（来自交接文档总览）

- SVN 仓库：https://svn.tap4fun.com/svn/x3
- 策划案：https://drive.google.com/drive/folders/1023kEv9ZJmKJ1aWMp0PUuxBPpHsDXIow
- 运营规划：https://docs.google.com/spreadsheets/d/16Halv5vTyyL3E60Uyc2ZON_2GOnFjXpxa0rMT45r
- 数值方案：https://drive.google.com/drive/folders/1vBwLojFmvG44zJrIfoz3NbXtElKohfIy
- Wiki：https://wiki.tap4fun.com/display/X3/X3

---

## 🏗️ 功能分类（按规模排序）

### 第一梯队：核心系统（10+ 子表）

| 分类 | 子表数 | 文件数 | 说明 |
|------|--------|--------|------|
| 活动 | 122 | 50 | 最大模块，59种活动类型 |
| 礼包 | 24 | 6 | Pack/PackAllowance/PackHeroPromotion/PackRecommend/PiggyBank/SoldierLvPack |
| 英雄 | 15 | 1 | Hero.xlsx 一个文件包含全部英雄数据 |
| 魔海回声（大KVK） | 14 | 5 | KVK系列配置 |
| 船只装备 | 11 | 1 | ShipEquipData.xlsx |

### 第二梯队：重要系统（5-9 子表）

| 分类 | 子表数 | 文件数 |
|------|--------|--------|
| 船只强化 | 8 | 1 |
| 英雄装备 | 7 | 1 |
| 船只 | 7 | 1 |
| 约会 | 6 | 1 |
| SLG城建 | 5 | 1 |
| 家具 | 5 | 2 |
| 英雄贴纸 | 5 | 1 |
| 钓鱼 | 5 | 1 |
| 情报 | 5 | 1 |
| 道具获取 | 5 | 1 |
| 商店 | 5 | 1 |

### 第三梯队：辅助系统（3-4 子表）

竞技场(4)、黑市(4)、英雄抽卡(4)、新手引导(4)、拜访点赞(4)、邮件(4)、每日新闻(4)、排行榜(4)、科技(4)、开拓航道(4)、酒馆特殊事件(4)、黑市任务(3)、跑马灯/推送(3)、集结怪(3)、船只装备任务(3)、士兵强化(3)

### 第四梯队：基础配置（1-2 子表）

战斗公式、食谱、聊天AI、顾客、每日任务、剧情、功能解锁、采集、章节任务、道具、海域开放、约会回忆、数值、规则说明、时间总表、公会(阶级/标志/捐献/礼物/旗舰/科技/海兽陷阱/日志)、单位表(建筑/怪物/船只/KVK建筑/巢穴)、VIP、天下大势、头像/头像框/头衔、特权、装扮、士兵/士兵装备、全局字段、服务器、多语言 等

---

## 🎮 活动系统详解（59种活动类型）

### 活动编号索引

| 编号 | 活动名称 | 配置文件 | 子表数 |
|------|----------|----------|--------|
| 1 | 周登录 / 14=补签登录 | ActvLogin.xlsx | 1 |
| 2 | 成长奖励 | ActvGrowth.xlsx | 1 |
| 4 | 俘获芳心 | ActvRomance.xlsx | 2 |
| 5 | 任务模板 / 42=公会任务 / 57=士兵装备养成 | ActvTask.xlsx | 1 |
| 6 | 积分排名模板 / 35=实时声望 | ActvScore.xlsx | 1 |
| 7 | 多阶段积分模板 | ActvScore.xlsx | 1 |
| 8 | 挑战活动（周考数值验证） | ActvExercise.xlsx | 3 |
| 9 | 情报怪限时活动 | ActvIntelligence.xlsx | 1 |
| 10 | 大转盘模板 | ActvLuckyWheel.xlsx | 3 |
| 11 | BattlePass | ActvBattlePass.xlsx | 2 |
| 12 | 公会积分排名模板 | ActvScore.xlsx | 1 |
| 13 | 兑换活动 / 21=英雄碎片兑换 | ActvExchange.xlsx | 1 |
| 15 | 开箱抽奖（节日活动） | ActvCrafting.xlsx | 3 |
| 16 | 木桩怪活动 | ActvShipEquipSell.xlsx | 3 |
| 17 | 钓鱼活动 | ActvIdle.xlsx | 2 |
| 18 | 任务拼图 | ActvPuzzle.xlsx | 3 |
| 19 | 海域入侵 | ActvInvasion.xlsx | 3 |
| 20 | 小KVK | ActvKvk.xlsx | 1 |
| 22 | 积分BP | ActvBattlePassScore.xlsx | 2 |
| 23 | 战后恢复 | ActvRevive.xlsx | 1 |
| 24 | 跨服最佳酒馆 | ActvScore.xlsx | 1 |
| 25 | 留存邮件活动 | ActvMail.xlsx | 1 |
| 26 | 钻石许愿池 | ActvWishing.xlsx | 1 |
| 27 | 养成手册 | ActvLoginPurchase.xlsx | 2 |
| 28 | 航海之路 | ActvVoyage.xlsx | 5 |
| 29 | 进度礼包活动 | ActvPack.xlsx | 1 |
| 30 | 赛季KVK | ActvKvkSeason.xlsx | 2 |
| 31 | 捐献排名活动 | ActvDonate.xlsx | 4 |
| 32 | 运输船 | ActvTransport.xlsx | 2 |
| 33 | 赛季BP | ActvKVKBP.xlsx | 3 |
| 34 | 组合任务（英雄星级） | ActvBuildup.xlsx | 1 |
| 36 | 大KVK丰碑争夺 | ActvKvKWonder.xlsx | 2 |
| 37 | 悬赏令 | ActvKVKBounty.xlsx | 3 |
| 38 | 酒馆奇遇 | ActvTavernAdventure.xlsx | 5 |
| 39 | 赛季日常任务 | ActvKVKTask.xlsx | 1 |
| 40 | 钻石冲刺返利 | ActvDiamondRebate.xlsx | 2 |
| 43 | 英雄秘密问答 | HeroSecret.xlsx | 5 |
| 44 | 英雄验证-武道大会 | ActvHeroUpRoute.xlsx | 5 |
| 45 | 社区活动 | ActvCommunity.xlsx | 1 |
| 46 | 公会合并 | ActvGuildMerge.xlsx | 1 |
| 47 | 英雄技能售卖 | ActvHeroSkillSell/TryUse.xlsx | 2 |
| 48 | 远航战备 | ActvDailyRank.xlsx | 2 |
| 49 | 内裤的踪迹 | ActvUnderpants.xlsx | 2 |
| 50 | 许愿池抽奖 | ActvWishingPool.xlsx | 3 |
| 51 | 海瑟技能售卖 | ActvHeroSkillTryUse.xlsx | 1 |
| 52 | 格蕾丝技能售卖 | ActvSaveDwarves.xlsx | 2 |
| 53 | GVG | ActvGvG.xlsx | 8 |
| 54 | 公会内排名 | ActvScoreGuidInternal.xlsx | 2 |
| 55 | 天下第一武道冠军之路 | ActvHeroChampionRoad.xlsx | 4 |
| 56 | 拜访礼包 | ActvVisitPack.xlsx | 2 |
| 58 | 英雄特殊技能通用活动 | ActvHeroVerify.xlsx | 1 |
| 59 | 巢穴积分活动 | ActvWonder.xlsx | 3 |

### 活动总表
- ActvOnline.xlsx 包含 ActvOnline（活动总表）、ActvGroup（活动分组）、ActvGroupSchedule（活动排期）

### 活动模板复用关系
- 积分类模板（6/7/12/24）共用 ActvScore.xlsx
- 任务类模板（5/42/57）共用 ActvTask.xlsx
- 英雄技能售卖（47/51/52）分布在多个文件

---

## 🎁 礼包系统详解

| 文件 | 子表 | 说明 |
|------|------|------|
| Pack.xlsx | Pack, PackTypeInfo, ChainPack, PackPrice, PackShip, PackStall, PackRally, DailyPack, DailyPackHero, SoldierPack, PackWeek, OptionalPack, WeeklyCard, RecommendPack, GrowthFund | 主礼包表（15个子表） |
| PackAllowance.xlsx | PackAllowance | 礼包津贴 |
| PackHeroPromotion.xlsx | PackHeroPromotion | 英雄推广礼包 |
| PackRecommend.xlsx | PackRecommend | 推荐礼包 |
| PiggyBank.xlsx | PiggyBank, Grade | 储蓄罐 |
| SoldierLvPack.xlsx | SoldierLvPack | 推荐士兵礼包 |

---

## ⚔️ 三大跨服活动（补充说明）

1. **风暴逐鹿**：持续7天的小KVK，前5天最佳酒馆备战，第6天新地图打1天
2. **世界入侵**：持续8天，前5天最佳酒馆备战，第6天两服互相入侵
3. **魔海回声（赛季）**：4周一赛季的大型KVK，新地图争夺领地
   - 王座争夺使用风暴逐鹿的活动模板，更换了资源和主题

---

## 🔧 配置规范备忘

- 多语言上传：导表工具(gen_i18n_tool.exe) → AI翻译 → 校对 → 上传
- 美术资源：导入DK库，配置表字段加前缀 "DK_"
- 字段依赖：支持非ID字段依赖，格式【表名.字段名】，被依赖字段加前缀 "BD_"
- GM指令：Unity工程 / igame后台可查看

---

*Nomi 👽 整理*
