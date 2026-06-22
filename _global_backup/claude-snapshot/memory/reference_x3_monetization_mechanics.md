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

### 可重复购买 + CD + 界面打开链路（2026-06-18 异国美酒储蓄罐改造案实测）
**「多次购买/封顶/购买间CD」基本靠 Pack 表配置，非新代码**——`GiftMeta.cs` 购买校验链原生支持：
- `Pack.BuyCount`(col21 购买次数限购)：`purchaseNum >= BuyCount` 拦截(line~1279)。空=不限次。
- `Pack.ColdTime`(col25 冷却时间，值如`72h`)：`now - lastBuyingTime < ColdTime` 拦截(line~1290)；`lastBuyingTime` 按 `Pack.Group`(col44>0 走 groupBuyingTimes) 否则按 `Pack.ID`(buyingTimes) 记录 → **多档共用一个 Group = 串成同一条 CD 时间线**。
- `Pack.Prepack`(col24 前置礼包)：可做顺序解锁链（tierN+1.Prepack=tierN）；对 PackType=21 是否生效需程序确认。
- 储蓄罐礼包 `Pack.PackType=21`、`Pack.PlayerLv` 解锁等级(如金币罐=18)、`Pack.Price`(col8)→PackPrice点id。
- **金币储蓄罐(Pack 500000)就是「不限次+72h冷却」可重复款**；某罐「只能买一次」=它自己 BuyCount/单档/无CD 配出来的，不是系统不支持。
- ★**通用CD技巧「买N次才进CD」(2026-06-18异国美酒每日双档案)**：`ChangeGiftBuyInfo`(共享层`client\Assets\Scripts\CSShared\Game\DataModel\GiftData.cs:360`)记CD时间戳的条件是 `if(!beDonate && cfg.ColdTime>0)`——**只有 ColdTime>0 才写 groupBuyingTimes/buyingTimes**；CD检查(GiftMeta.cs:1290)也是 `if(ColdTime>0)` 才查。故同一 Group 内：**前档配 ColdTime=0(买它不写不拦、穿透) + 末档配 ColdTime=N(买它触发全组N冷却)** = 实现「一个周期能买多次、砸到末档才进CD」，纯配置零后端。坑：ColdTime=0 的档服务端完全不拦次数(CD检查跳过)，严格防刷需另加校验。异国美酒每日双档即用此法(档1$9.99 ColdTime=0 + 档2$19.99 ColdTime=24h 共用Group=每天2次)。
- **真要新增的只有「档位提升(越买越贵+量也涨)」**(2026-06-18异国美酒案用户dev实测校准)：现有储蓄罐**已经有CD、能重复砸、CD内暂停攒酒+CD到期恢复都是现状**；「只能买一次」真实含义=只配单档、买完同价重复、没档位往上爬。涨价需「按购买次数推进档位」=要么多档递增Price+Prepack顺序链(偏配置,需确认Prepack对PackType21生效)，要么服务端记购买次数N按N选档(偏代码,界面更易表达第N/5档)。ColdTime本身只是同价重复,不带涨价。
- 异国美酒罐现状(实测Pack 500031)：**BuyCount空=本就无购买数量上限**，ColdTime=24h，Price=$9.99(107)，PlayerLv=3，Group=8，单档同价同量(10)。即「只能买一次」是口误,实指「只有单档同价、没越买越贵」,不是真的限1次。
- ⚠️读tsv坑：PiggyBank.tsv行尾多空列,Read工具显示会串列(曾把异国美酒PackID误读成500000=金币罐,真值500031)→用python csv按列名取,别数格子。

**界面打开路径**：储蓄罐界面 `UIPiggyBankContent`(client `UI/ItemObtain/`，UIData带itemID+needCount) 是**「道具获取」面板 `UIItemObtain`(`UI/Common/`)的子区块**(跟UIIOPackContent/UIIOEntryListContent并排)，**不在活动日历入口**。按资源item分组：`CPiggyBank.GroupInfo[itemCfgID]` 查该item所有储蓄罐(异国美酒罐 key=item 7002，7002=招募英雄专用美酒货币)。
- dev里打开 = 点该item图标→「获取途径」面板→储蓄罐区块；显示条件：对应Pack `IsOn=1` + 在TimeCycle窗口内 + 等级≥Pack.PlayerLv + `giftMeta.CheckCanShowGift(PackID)` 通过。缺窗口/等级就弹不出来。
- prefab：`client\Assets\Res\UI\Prefab\ItemObtain\UIPiggyBankContent.prefab` + `UICoinPiggyBankTips.prefab` + 父 `UIItemObtain.prefab`。看布局直接Unity开prefab最快，不用跑服务器。
- 配置：`PiggyBank__PiggyBank.tsv`(行46=异国美酒) + `PiggyBank__Grade.tsv`(GroupId 260=恒定Num10,不随酒馆等级scale)；发奖走 `GiftUtils.CalBankResNum(piggyCfgId,level)`，level=min(piggyLevel, BasicMeta.Level)。
- 改造案策划案：`KB\产出-数值设计\X3_异国美酒储蓄罐\异国美酒储蓄罐_可重复购买改造_策划案.md`。

## 三、自选周卡 WeeklyCard（X3 原生·复用即可，无需大改程序）
**逻辑**：`GiftMeta.cs` PACK_TYPE_WEEKLY(line 494-507)购买后每天领、receivedDay++ 计天；自选走 PACK_TYPE_SELF_SELECT。
**界面**(client UI/)：UIWeeklyCardBuy(购买) / UIWeeklyCardReplacement+SupplyItem(自选替换) / UIWeeklyCardItem+RewardItem(每日领取) / **UIRechargeWeeklyCard(入口=充值/付费页里的「周卡」页签，不在活动日历列表)** / UIOptionalPack。
**X2 自选周卡先例**：3档(9.99/19.99/29.99)+奖池10选4+连领7天+BUY ALL打包(原价$59.97→$49.99,15%OFF)。

### X3 实际配置链路（2026-06 实测，新 agent 接管/换皮直接照这张图查）
五张表串起来（真源=tsv，改 tsv 不碰 xlsx）：
1. `ActvWeeklyCard__ActvWeeklyCard.tsv`：内容配置。ContentID **61001** = ClaimDays领取天数(7)/DailyPickCount每日自选数(4)/RewardPoolSize奖池数(10)。
2. `ActvWeeklyCard__ActvWeeklyCardTier.tsv`：**4档结构**=3个单卖档(Tier1/2/3) + 1个打包全购(Tier4)。各档列：Pack(关联礼包ID)/BuyReward(买送)/UnlockTierIds(打包档填前3档ID=BUY ALL)/PoolRewards(每日自选奖池,10个RewardID)。实测档ID 6100101~6100104 → Pack 2026101~2026104。
3. `Pack__Pack.tsv`：**周卡名称/价格在这里**。4个礼包行 ID 2026101~2026104(物理行2141~2144)。关键列:**col6=备注价格(显示用,人读)、col7=Price(指向PackPrice表的价格点id,游戏真读这个)、col8=GemPrice、col35=Name(名称i18n源文案)、col36=Desc(描述)**。⚠️名称看 col35 不是 col2(col2是备注名)。
4. `Pack__PackPrice.tsv`：价格点表(id→美分→商城key)。常用:105=$4.99 / 107=$9.99 / 111=$19.99 / 112=$29.99 / 116=$49.99 / 114=$59.99 / 115=$99.99。改价=改 Pack col7 指向不同价格点 id。
5. `Reward__Reward.tsv`：买送+奖池的实际道具内容(按 RewardID 分组,col1=RewardID col2=ItemType col3=ItemID col5/6=Min/Max)。Item 1002=钻石。
**活动入口**：ActvOnline 第109101行(ActvType=63,ContentID=61001) → GM 用 cfgID=109101 开(见 [[workflow-x3-local-server-gm-telnet]])。MainEntrance/Calendar 空=不进活动列表,走 UIRechargeWeeklyCard 入口。
**模板出厂态全占位**：3档价都105($4.99)、名称都"活动周卡"、Desc"(策划待填)"、奖池30项全是钻石x50、备注col6 4.99/9.99 → 换皮/正式配=改 col6备注+col7价格+col35名称(走i18n) + Reward奖池内容。
**工作量**：复用原生程序，纯改配置+出图+i18n。

实战来源：2026-06 深海节策划案。相关 [[reference_x3_datain_asset_query]]、[[reference_x3_voyage_art_chain]]。

## 四、累计充值/首笔付费 触发链（2026-06-18 newbie-recharge首充弹窗排查中确认）
做"首充/累充达标→弹窗/发奖"类需求时的链路（读代码确认）：
- **服务端加累充唯一口径 `PayMeta.AddTotalPayMoney(payMoney, points)`**(`server\GameServer.Hotfix\PlayerMeta\PayMeta.cs:411`)：`newTotalPayMoney += payMoney` + 发 `TotalPayMoneyChangeNtf` + fire `TEventType.PayOrder`。3个调用入口：PayMeta:374(IAP发货) / GiftMeta:442 / GiftMeta:721(礼包)。
- **钻石(useGem)不计累充**：GiftMeta 购买分支 `if(useGem){扣GEM}else{AddTotalPayMoney(priceCfg.Dollar)}`(GiftMeta.cs:430)——**钻石购买走useGem分支不加累充；现金IAP/金砖模式走else分支才加**。所以"首充/累充"天然排除钻石、含IAP+金砖。
- 客户端 `PayMeta.OnTotalPayMoneyChangeNtf`(client `Entity/Player/PayMeta.cs`) 收 ntf 更新 `Data.newTotalPayMoney`+fire `OnTotalPayMoneyChange`。判"首充"=`oldTotal==0 && new>0`(仅一次)。
- ⚠️**cfgId 硬编码弹活动的常见坑**：handler 里 `GetActivityIdsByCfgID(cfgId).FirstOrDefault()`，**该活动没在本服部署/没开 → 取到0 → 静默 return 不弹**(不是代码错,是活动没开)。排查"按cfgId弹窗没生效"先确认该 cfgId 活动在测试服真部署了。X3活动名易混(如104801=远航战备排行 ≠ 101108=新手累充累计充值)。
- **本地按cfgId部署活动 GM**：`[活动_活动]GM部署单服活动` = `GMDeployServerActivity(int cfgId, long startSec, long endSec)`(`server\GameServer\Modules\ActivityMgr.Ark.cs:295`,传秒,跨服活动不支持)。本地起活动验证用。
