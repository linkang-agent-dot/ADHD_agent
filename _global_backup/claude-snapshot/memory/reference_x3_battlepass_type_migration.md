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

## 三活动上线监控口径(2026-07-07 沉淀)
- **2026-07-03(周五) 正式上线**，首单 07-03 08:14 北京时间。监控 SQL：`v1090.ods_user_order` (TRINO_HF)，`pay_status=1 AND iap_id IN ('130038'~'130043')`。
- 活动↔付费包映射(BattlePassScore c5 Pack 列顺序=高级|至尊)：
  - 102247 登录好礼(BPcfg 2247)：130039 高级$9.99 | 130038 至尊$19.99
  - 102248 海盗猎人的赏金(BPcfg 2248)：130040 高级$14.99 | 130041 至尊$39.99
  - 102249 猎杀时刻(BPcfg 2249)：130042 高级$9.99 | 130043 至尊$19.99
- 首5日(07-03~07)规律：登录好礼一档独大(~59%收入)；**登录好礼/猎杀时刻的至尊档单量反超高级档**，赏金(唯一$14.99/$39.99高定价)单量最少。
- **周五–周一UTC0同窗对比(07-03~06 vs 前两周)**：老包(130002/003/004)迁移后**仍在卖**(TimeController=0存量实例跑完为止，该窗贡献$1,623=43%)；BP线合计 $2,647(W0619)→$2,802(W0626)→**$3,772(W0703, 环比+34.6%)**，BP线ARPU(分母=窗口总付费人数,节日监控口径) $0.94→$0.97→**$1.28(+32%)**。增量≈至尊档新增收入$1,479，基础档没被明显分流。且该窗撞深海节D0仍正增长。⚠️ 130038-043 不在任何节日累充白名单，节日日报看不到这块增量，属常态盘。下周窗口老包存量应耗尽，注意复查老包是否归零。

## ★新老活动兼容官方字段=ActvOnline.BaseActvID(2026-07-15 dev 发现,换皮/迁移通用)
`ActvOnline` col52 在 dev 已由 `ExcludeActvIDs`(互斥活动ID) **改名为 `BaseActvID`**(中文"活动互斥基准ID·参照x2的BaseCfg",注释仍"互斥活动ID列表",**列位置没变=同一列改名**)。**这就是"新老活动兼容/互斥基准"的官方落地**,用法=**新活动填老活动ID**(单向,非双向互指):
- 老 Type11 `101102/101104/101110` BaseActvID=自身;新 Type22 `102248/102247/102249` BaseActvID=**对应老活动**(102247→101104 等);英雄手册 102702(新)→102701(老)。服务端按 BaseActvID 把新老版本归一(玩家数据/互斥/累充隔离)。
- **换皮/常驻化做"新活动接管老TC、老活动TC=0"时,兼容配置一律用 BaseActvID=老活动ID,别再用双向 ExcludeActvIDs**(旧列名,dev 上已改)。dev_festival 分支可能还是老名 ExcludeActvIDs——改前先 `git show origin/dev:tsv/ActvOnline__ActvOnline.tsv` 看 col52 现名。
- 关联新列(dev 新增):`ForbidRestartOpen`(col53,非0=禁止服务器重启回填开启,触发式活动防玩家进半程)、`BaseActvID`(col52)、`LoginPanelImg/LoginChestImg`(col54/55,登录手册DK)。**dev 的 ActvOnline=56列**(dev_festival/旧=53列),跨分支换皮 append 行必按目标分支列宽对齐,否则高位列(累充白名单 col49/DKVideo col50/BaseActvID col52)错位。

## 单档BP盘点(2026-07-14 dev_festival扫描)
扫描法=BattlePassScore c4按"|"计档+ActvOnline(type22/11)对IsOn；价格查Pack c7→Pack__PackPrice(105=$4.99/107=$9.99/109=$14.99/111=$19.99/113=$39.99)。在线单档：**传奇战令全系7期(cfg2217/2227/2228/2235/2237/2239/2243,均仅至尊$19.99)**+**夺宝通行证(cfg2240/2241,仅$9.99,Pack 2026016/17)**+**会员签到好礼(Type11 cfg1120,130015 $9.99,唯一还真活着的老Type11)**；老三样101102/101104/101110=TimeController=0存量壳已迁双档。
**传奇战令7期上线节点(ods_user_order首单口径,07-14查)**：尼西斯130026=25-09-08首发1周+两次返场(25-12-22~26-01-05/26-06-29~在售)；玛琳娜130028=25-10-19起**常驻滚动**；艾娃130029=25-11-03~11-10仅1期未返场；130032共用ID两期各3周=S4窗26-01-26~02-16(300403)+S5窗03-16~04-06(300503)；阿什顿130033=26-02-05起**个人生命周期滚动**(TimeCycle702=注册第13天开5天)；林若雪130034=26-06-29起在售。三种投放形态=赛季档期/常驻滚动/生命周期触发。**触发方式核实(07-14)**：仅阿什顿走生命周期(TimeCycle702 TriggerType=3注册时间)；其余6期ActvOnline c7/c8全空=时间完全由iGame后台部署给定(绝对时间窗)，玛琳娜的"常驻"=部署层长窗口非配置触发；等级门槛分层=玛琳娜lv5/阿什顿lv7/其余lv12(TimeCycle TriggerType枚举:1绝对2开服3注册4海域5触发后6开服第几周)。

## BP付费礼包(通行证Pack)结构速查(2026-07-06 Pack主数据扫描沉淀)
- 链路：Pack__Pack.tsv 礼包行 ←BattlePassScore c4(PackID·可"|"多档)← BPcfg ←ActvOnline c4 引用。
- **130020/130021=节庆通用高/至尊通行证，18+个节日BP共用同一对ID**(2207春风饮酒~2242世界杯都引)——换皮/建新节日BP默认复用这对，**主数据Name没法按节命名**；要按节命名须拆专属ID(先例：深海130036/37航海通行证、修女130030/31、赛季战令130026-034各自专属)。
- Pack c35(AJ)=主数据Name(纯中文·dim.iap用·表头标"必填禁空格")，与i18n TXT_Pack_Name是两套，改名两边都要动。
- **主数据Name命名口径(用户2026-07-06定)**：多档同产品必须带档位标识(「节日高级/至尊通行证」「深海节高级/至尊通行证」)，别两档同名；战令类带英雄名区分(「传奇战令-尼西斯」)。跨赛季共用ID(如130032 S4+S5)写谁都错→保持通用名或拆ID。
