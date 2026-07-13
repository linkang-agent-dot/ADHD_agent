---
name: x3-score-activity
description: X3 积分活动配置体系（ActvScore.xlsx 三 sheet 结构、最佳酒馆 ContentID 系列、TaskType 关键编号、Rank/RewardSlotCfg 结构、ScoreID=603 易混淆陷阱）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2698066a-6dc9-4d48-8e43-b75b32db6c72
---

## 文件路径（改 tsv，不碰 xlsx；下方 sheet 名即 tsv 名）
- ActvScore — 3 sheet：`tsv/ActvScore__ActvScore.tsv` / `__ActvScoreMulti.tsv` / `__ActvScoreTask.tsv`
- Rank — `tsv/Rank__RankCfg.tsv` + `tsv/Rank__RankRewardSlotCfg.tsv`
- Reward — `tsv/Reward__*.tsv`（RewardID 内容定义）
- 改法：`x3-config-export` skill 的 `tsv_edit.py`（先 `show` 定位列再 `set`/`remove`）

## ⚠️ X3 有两套 BP，别混（2026-06-29 查 Pack140001 实证）
- **积分BP**：本表 `ActvScore`（ActvType=22，如深海 AO102244）。付费档=Pack（节日通用 130020/130021），奖励走 BattlePassScore。
- **跨服赛季BP**：`ActvKVKBP__ActvKVKBP.tsv`（**ActvType=33**，如深海"魔海密藏"AO103301，ContentID=3302）。列结构：col0 ID(=关联ActvOnline的ContentID) / col2 `Pack`=**普通付费档** / col3 `PlackPlus`=**至尊付费档** / col4 `PlackPlusLv`=至尊额外等级数 / col5 `Reward`=奖励组 / col6 WeekTask / col9 SeasonTask。
  - 实例：Pack **140000**=普通付费、**140001**($39.99「豪华至尊奖励」)=至尊付费、+10级。买至尊档=解锁至尊奖励线 + BP等级+10；Pack.Content/Reward 列空（奖励从 BP 轨道发，不在 Pack 里）。
  - Pack 表里这种 BP 解锁包 col9 UI类型=113、tag 列(col39)=展示用价值%(如9500%，TXT_Pack_Tag_{id})。

## ActvScore.xlsx 三 sheet 结构

| sheet | 用途 | 主键 |
|-------|------|------|
| ActvScore | **本服**积分活动定义，1 行 = 1 个 ScoreID | ScoreID |
| ActvScoreMulti | **跨服**积分活动定义（多阶段），1 行 = 1 个 ContentID×Stage | ContentID + Stage |
| ActvScoreTask | 任务定义池，被 ActvScore / ActvScoreMulti 的 TaskID 列引用 | TaskID |

### ActvScoreTask 列结构（前 7 列有效）
A=ID / B=TaskDesc(TXT_任务描述，存中文字串不是 LC_Key) / C=Score / D=Group / E=TaskType / F=Parameter1 / G=IsHide / 第8列=备注

### 🔑 X3 酒馆计分「费率卡」内在口径（2026-07-10 马戏酒馆720查实，与深海719共用同一批 ActvScoreTask 行）
新计分/积分活动定分值**先对这张卡，别自创**——设计基准 = **1分/钻**：
- 钻石消耗(task100,事件440参数1002)=**1分/钻**（元锚）；加速=**13分/分钟**(建/研/招/治 task101-104，30m≈390分≈1分/钻自洽)
- 技能书消耗：蓝19001=150/紫19002=500/**橙19003=1000分**(=1000钻价，1分/钻)
- 养成稀缺物打**0.6折/钻**：升星(稀有300/史诗600/传奇3000) = 信物兑换(52001=300/52002=600/52003=3000)
- 美酒打0.33：7001/7002=1000分(3000钻价)；好感1000/级；礼包=**150分/充值积分**(task1801,事件900)
- 水手招募13→415分/位(lv1-15)、击杀1→40分/位、采集1分/分钟、情报100/次、船只技能碎片3000、木板20/金属60
- 酒馆阶段档位量级锚：单阶段(1-2天限定行为域)目标=**1w/3w/5w/7w**(一掷千金阶段1w/2w/3.5w/5w)
- 用途实例：马戏节扭蛋机(X2搬运)积分任务直接复用这批 task 行——**别搬 X2 费率**(同价道具 X2 口径=10×且内部不自洽，如金书1w分 vs 升星800分)；跨项目对标积分门槛=先换算到"钻当量"再套本卡。

### ActvScoreMulti 列结构
A=ID / B=备注(中文) / C=ContentID / D=StageName / E=Stage序号 / F=StageDuration / G=ScoreGroup / **H=TaskID(`a | b | c` 拼接串)** / I=RankID

TaskID 串分隔符：` | `（空格-竖线-空格）。修改 TaskID 串时维持分隔符一致。

## TaskType 关键编号
| TaskType | 含义 | 触发位置 |
|---|---|---|
| 440 | 通用"消耗 Parameter1 道具"事件 | 服务端通用钩子，最广泛使用 |
| 441/442/443 | 消耗金/紫/橙技能书 | 升级英雄技能时 |
| 444 | Hero升星消耗 hook | `Hero.HeroStar.UpItem`，**只在升星路径触发** |
| 292 | 提升英雄好感度 | — |
| 900/902 | 充值积分相关 | 见 reference_x3_recharge_isolation.md |

## 最佳酒馆 ContentID 系列（同一活动模板的不同变体）

| ContentID | 名称 | ActvType | 用途 |
|---|---|---|---|
| 701 | 最佳酒馆基底 | 7 (本服) | 模板 |
| 716 | 魔女之夜 | 7 | 已下线节日（万圣节） |
| 717 | 节庆通用-跨服酒馆1 | 7 | 26 元旦/情人/春节复用 |
| 718 | 节庆通用-跨服酒馆2 | 7 | 26 尼罗、夏日恋语 |
| 2401 | 跨服酒馆-入侵 | 24 | 入侵序章备战 |
| 2402 | 跨服酒馆-KVK | 24 | 风暴前夕 |
| 2405 | 远征酒馆-W2 | 24 | 远征 S1-S5 |
| 2406 | 决战前夕-W4 | 24 | 赛季通用决战前夕 |

ActvType=7 是本服最佳酒馆，ActvType=24 是跨服酒馆变体（备战/远征/决战前夕）。

## 英雄信物 Item ID
- 52001 = 通用稀有信物 / 52002 = 通用史诗信物 / 52003 = 通用传奇信物（兑换源头）
- 51001-51058 = 具体英雄信物（"信物-{英雄名}"），HeroStar.UpItem 消耗这套

## ⚠️ 易混淆陷阱：ScoreID=603

ActvScore（本服）sheet 行 8 ScoreID=603 的备注是「**运营大师**」（ActvType=6 声望排名），**不是酒馆活动**。曾被旧 sub-agent 误读为"酒馆大师"。

修最佳酒馆 BUG 时 **不要动 ActvScore.603 这行**，最佳酒馆配置全在 ActvScoreMulti。

## Rank.xlsx 结构

### RankCfg sheet 关键字段
A 列起：A=ID(col1) / B=备注(col2) / C=TXT_名字(col3) / D=**RankType**(col4，6=本服，12=跨服) / E=Sort积分id(col5) / F=DK图标(col6) / G=MaxRankSize(col7) / H=RankRewardTitle(col8) / I=RankRewardTab(col9) / J=NeedSendMailReward(col10) / **K=MailID(col11)** / L=MailMaxRankNum(col12) / M=上榜门槛(col13)

**易错点**：MailID **在 col 11 不是 col 13**。我曾因列号定位错把 MailID 读成 None 误判（X3NEW-735 修复后核验时踩坑）。

### ActvOnline 跨服字段
- col 19 = `CrossServerRank`（1=跨服，空=本服）
- col 21 = `RankID`（指向 RankCfg 的总榜）
- 其他没有 `CrossServerType / ServerGroup / IsMultiServer` 字段，只有 CrossServerRank 单一开关

**没有"显示奖励 vs 实发奖励"分列字段**。每档奖励统一在 RankRewardSlotCfg 用同一个 RewardID（既显示也实发）。

### RankRewardSlotCfg sheet
A=SlotID, B=**RankID**, C=StartRank, D=EndRank, **E=RewardID**

修排名奖励 BUG = 改这张表的 E 列。

## 节日 RewardID 复用规则
**不同节日的最佳酒馆活动复用同一套 RewardID 系列**（策划确认）。例：

| 节日 | 总榜 RewardID 序列 | 数值 |
|---|---|---|
| 春节"千灯贺新岁" RankID=131（跨服） | 30391-30398（8档） | 第1名：高阶技能书×120 + 1H建造/招募/研究令×30 各 |
| 夏日恋语 RankID=160（本服） | 修复后= 30391-30398 | 同上（X3NEW-736 修） |

8 档分布：1/2/3/4-5/6-10/11-20/21-50/51-100

## 写入注意（实操踩坑总结）
1. **改 tsv 不碰 xlsx**：用 `tsv_edit.py`（`set` 断言旧值 / `remove` 删管道列表ID），别再用 Excel COM/openpyxl。
2. **先 `tsv_edit.py show` 读现值再改**，不要凭印象写 TaskID 串。
3. **双重 ID 校验**（用 SlotID + RankID 两个值确认是目标行，避免串行）。
4. **不要复用已被引用的 TaskID 编号**——同一 TaskID 可能被多个 ScoreID/Multi 行引用，新建必须用未占用 ID。
5. **写前 `git branch --show-current` 确认分支**——见 [[feedback_x3_branch_check]]。
6. **写后看 `git diff`**（行级 diff = 没串列、LF 没坏），再 commit → push → `jolt_verify.py` 验证 SUCCESS。

## 实战参考（2026-05-25 X3NEW-734/735/736）
- **X3NEW-734**：消耗通用信物兑换不加分 → 新增 TaskID 208/209/213 (TT=440) 挂到 ActvScoreMulti 7 行
  - ⚠️ **收尾教训（2026-05-29）**：当时只 commit 了 ActvScore.xlsx，**没补 Text.xlsx 翻译** → 208/209/213 的 `TXT_ActvScoreTask_TaskDesc_*` 只有 cn、10 语言全空，俄服面板显中文母版。后补全（commit `5e738e7`，对齐升星兄弟 201/202/203）。**新增带 TXT_ 字段的任务必须同 commit 补翻译**，见 [[reference_x3_i18n_workflow]]「新增任务漏翻」
- **X3NEW-735**：最佳酒馆排行榜应跨服却只显本服 → 方案 C 新建独立跨服 RankID 619-625(阶段) + 626(总)，RankType=12；改 ActvOnline.10071801 CrossServerRank=1 + RankID=626；ActvScoreMulti R27-R33 改 RankID 619-625。**避开与启程补给站(131/601-607)、KVK(601-607)冲突**
- **X3NEW-736**：排行奖励显示与实发不符 → Rank.xlsx RankRewardSlotCfg RankID=160 八档 RewardID 由 785301-785308 → 30391-30398（735 修完后 RankID=160 变孤儿，但保留有占位价值）

## 🔴 占位过期时间在尼罗实战翻车 + 「活动有没有上线」诊断法（2026-06-22）
**背景**：X3NEW-735 把最佳酒馆(10071801)改跨服后，TimeCycle 718 被填占位过期时间 `TT=1 + 2026-02-16 + 14d`（跨服强制 TT=1，真实时间靠 iGame 后台手动设）。
**翻车**：尼罗 6 月滚动批(服 1900-1990，开服 5/05~5/27)上，**所有其它尼罗模块正常**(大转盘 type=10 2.4w人/累充 type=5 等十几个模块全在跑)，**唯独最佳酒馆「蓝莲花宴」type=7 = 0 参与**。服龄都到过/正处「D21开始14天」窗口(1950/1970/1990 此刻在窗口内)却零记录 → iGame 后台漏给酒馆设真实时间，活动套用配置过期时间不触发。本服模块不受 TT=1 跨服约束所以照常上。**教训：跨服活动(CrossServerRank=1)的占位过期 TimeCycle 是真实上线隐患，每次滚动部署必在 iGame 核实酒馆时间窗。**
**诊断法（查"某活动/模块有没有正常上线"，纯数据、不依赖 iGame）**：
1. 配置层先看绑定的 TimeCycle 是不是过期占位(跨服活动尤其)——`awk -F'\t' '$1=="<TC_id>"' TimeCycle__TimeCycle.tsv`，看 TriggerType(col5)/TriggerTime(col6)。
2. 数据层查 `v1090.ods_user_activity`：`activity_type`=ActvType(最佳酒馆=7,大转盘=10)，`activity_id`是运行时雪花ID(≠ContentID,别用它过滤)。按 `server_id`+`partition_date` group 看目标服窗口期内有没有参与记录。
3. **隔离"整个节日没上"vs"单模块没上"**：查目标服该 ActvType 缺席、但同服其它 activity_type 都在 → 单模块问题。
4. **排除"服太新没到窗口"**：`dim_open_server.open_time` 算服龄，对照活动的 D-window(酒馆=D21~D35)。
5. **找对照**：同 type 在别批服(跑别的节日、复用同模板)正常 → 证明 type 本身没坏，是这批没挂上。
⚠️ ContentID 718 = 尼罗 & 夏日恋语共用酒馆模板 → 光看 type=7 区分不了哪个皮肤，必须按"哪批服当前跑哪个节日"(看礼包流水服段)交叉判断。

## 跨服活动配套表清查结论（X3NEW-735 验证后）
- `ActvScoreMultiServer` sheet：**仅 KVK/远征类活动登记**，最佳酒馆系列不需要登记
- `ActvScoreGroup` 71811-71874：本服/跨服共用，无需修改
- `ActvScoreTask` / `ActvScoreTaskGroup` / `ActvScoreGuild` / `SpecialRewardSettlement`：与活动跨服属性无关
- X3 跨服活动只需改 4 处：ActvOnline (1行) + ActvScoreMulti (各 stage) + RankCfg 新增 + RankRewardSlotCfg 新增

## TimeCycle TT 与跨服活动兼容性
- ActvType=7 最佳酒馆历史只用 TT=1（绝对时间）或 TT=4，**无 TT=2 (开服+D20 相对时间) 先例**
- 跨服活动调度可能依赖"所有服在同一绝对时间窗口"做服务器分组匹配
- TT=2 + 跨服 = 未验证组合，X3NEW-735 修完后 QA 验证若仍不显示跨服玩家，先改 TimeCycle 该行为 TT=1

## 🔍 「BP积分没加/海兽击杀没分」诊断链路 — 查哪个日志(2026-06-26 世界杯俄服工单实证)
**先分清:配置层没问题≠运行时加上了。** 世界杯BP(102243)积分途径串实查 = `501|502|503|504|505|506|601|602|1910`,**海兽击杀任务501-506完整挂着**(不是配置漏)。"打了海兽没分"的真因要去**运行时日志**判,不是看配表。
- **积分变化/BP升级落点 = 游戏服 BI 日志 `game-<服号>.bi.log`,事件名(第4列)=`user_activity`**。世界杯BP是积分战令(ActvType=22)→走 `ActivityMeta.BattlePassScore.cs:391 → BIUserActivity.BattlePassScore`(实现在 `client/Assets/Scripts/CSSharedHotfix/Game/Server~/BI/BIUserActivity.cs`),`BIActivityType=BattlePassScore`。关键字段:`activityCfgID`=ActvOnline id(世界杯BP=**102243**)、`activityScore`=变化后progressScore、`activityStep/TotalStep`=完成/总任务数。(简易BP type11走 BattlePass 支;多阶段积分活动走 PlayerMultiPhaseActivityScore,JSON带`stepScore`。)
- **海兽击杀任务触发落点 = 同 bi.log 的 `user_task` 事件**(501-506,TaskType=450)。⚠️**501-506=「集结击杀」N级海兽**(Param=怪等级1-6),**玩家单刷海兽不计、必须是集结(rally)击杀**;海兽等级>6 或没参与该场集结也不计 → 「打了海兽却没分」最常见根因,且与时间窗无关。
- 🔴🔴**BP积分日志「只在升级时写一条」——别把"没记录"当"没加分"(本案真相)**: `user_activity` 的 BattlePassScore 行**不是每次击杀/采集都写**,而是**progressScore 跨过整级门槛时才落一条**(世界杯BP奖励组141每级门槛=**3000**固定,见 `BattlePassScoreReward.tsv` $2==141 needScore列)。本案玩家积分 0→3000→6000→9000 = 升到2/3/4级,各落一条;**单次海兽/采集加的零碎分(100-400/1)夹在两级之间,日志根本不单独记**→玩家/排查者看"没新记录"误判成"没加分"。**判前必先确认:该值是不是每级才写**。
- 🔴🔴**X3 BP积分任务(ActvScoreTask 501-506/601)不进 `ods_user_task` 表**: 查玩家近2天 user_task 只有 task_type 4/8/9/11/12,**没有 450(集结击杀)/143(采集)**——因为这些是**活动积分hook**,不是常规任务系统。海兽集结击杀的战斗事实在 **`ods_user_battle`**(battle_object_type=2/6野怪集结·base_level是玩家本体级非怪级·battle_detail含sceneCfgId/troopBattleType),采集在 march/采集表。601采集TT=143/602情报TT=410/1910竞猜空TT(GM发)。
- **判据树**:①BP `activity_score` 在涨(按3000阶梯)=积分正常入,"没分"是误读日志粒度;②`activity_score` 真不动+活动在窗内=才去查 `UpdateActivityScore` gate(时间窗 `ActivityMeta.cs:699`/score==old);③对账击杀量=去 `ods_user_battle` 数集结海兽胜场×(100-400),别去 user_task。
- 🟢🟢**X3线上玩家行为数仓查得到!上一版"查不到"是错的——根因=`query_trino.py` 默认 `--datasource TRINO_AWS`(老游戏P2/AWS集群),X3必须显式加 `--datasource TRINO_HF`**(`get_game_info` 早写明 1090=TRINO_HF)。打错集群会静默返0行/SHOW CATALOGS只剩hive、误判成"停更/查不到"。**TRINO_HF 上 `v1090.ods_user_activity/ods_user_task/ods_user_battle` 数据新鲜到当天**(本案查到 6/26 当天)。坑:`user_id`/`server_id`/`partition_date` 都是 **varchar**(过滤加引号);时间戳比较用 `TIMESTAMP '...'` 字面量;`created_at` 是**北京时间**;BP活动走部署时 `activity_id`=雪花号,配置号102243藏在 `attribute1` JSON(`activityCfgID`),按 `attribute1 LIKE '%102243%'` 才捞得全。详见 [[reference_ai_to_sql]]。

## 🎫 BP/通行证积分系统(≠ActvScore, 走专用表; 2026-06-17 世界杯实证)
**重要更正**：BP(Battle Pass/通行证)**不走 ActvScore**,走专用三表(WC project memory 旧写"BP走ActvScore"不准):
- `ActvBattlePass__BattlePass.tsv` — BP定义行(每行=一种BP任务类型): ID/IsOn/TaskType/Desc/Param1/Param2/PreTrace/Pack/Group(BattlePassReward.Group)。如 BP-情报循环/BP-登录循环(通用复用)。
- `ActvBattlePassScore__BattlePassScore.tsv` — **积分获取途径**配置(BP经验/积分来源)。**行ID = 该BP的ContentID**(世界杯BP ActvOnline=102240→ContentID=2240→BattlePassScore行2240)。列(0-idx): `[0]ID [1]备注 [2]IsOn [3]ActvScoreTask(管道串=积分途径!) [4]Pack(管道串) [5]BattlePassScoreReward.Group [6]bool`。
- `ActvBattlePass__BattlePassReward.tsv` — BP奖励档位。
- **积分途径就是 [3]列的 ActvScoreTask 管道串**(复用 ActvScore 同一套 ActvScoreTask 池!): 通用BP标配 = `501|502|503|504|505|506`(集结击杀1-6级海兽,100-400分)`|601`(采集每分钟1分)`|602`(情报任务100分); 部分BP加 `1901`(回声战船,KVK)。
- **加一个积分途径** = ①新建 ActvScoreTask 行(若无现成) ②`tsv_edit.py add --file tsv/ActvBattlePassScore__BattlePassScore.tsv --id <BP的ContentID> --cols 3 --ids <新TaskID> --after <锚点ID>` 挂进途径串。
- **★空 TaskType 合规**(301-310 招募水手先例): TaskType列留空=不挂服务端自动计数hook,靠 **GM手动发**积分;Score列仍填(每次发的分值)。世界杯案: 新建 1910"竞猜命中1场比赛"Score=600 空TT(竞猜结果GM手动结算发分),挂入 2240 途径串。
- **★同commit补翻译**: 新增 ActvScoreTask 行的 col2 是 TXT_字段→必须同时往 Text.tsv 加 `TXT_ActvScoreTask_TaskDesc_<id>` 全16语种(否则非中文客户端显空/中文母版,见 X3NEW-734 漏翻教训)。
- **落地后**: sync_xlsx_tsv.py --auto 同步 xlsx(ActvScore/ActvBattlePassScore/Text 各一) → 本地 ExportTable.py 自测 → commit(tsv+xlsx一起) → push → jolt。

### 🎮 GM 给玩家加 BP/活动积分(2026-06-25 世界杯BP·iGame 链路实测·链路通但卡时间窗)
- **🔴🔴🔴 最隐蔽坑:加分卡「计分时间窗」gate——GM 和完成任务两条路一起被静默吞(`ActivityMeta.cs:699`)**:`UpdateActivityScore` 内 `if (now < activityItem.startTime || now > activityItem.endTime) return;`。即**活动能显示/在玩家列表里(在展示窗内),但 `now` 不在 `[startTime,endTime]` 计分窗内时,不管 GM `GMAddActivityScore` 还是玩家真完成任务,加的分全被这行吞掉、不报错、数据纹丝不动**。**判定法**:"GM加不上 + 完成任务也加不上"=典型时间窗 gate(单纯 id 错只会让 GM 报「活动未开启」、不影响任务)。**根因常见两种**:①部署 start 在未来(如 hub 6/27 上线但 6/25 就测,now<start);②iGame 部署时间**按 UTC 直填不换算**([[igame-activity-deploy]]),误按北京时间填会偏 8h 把 now 顶出窗。**解法**:iGame 把 start 改到现在或更早(end 留足)重部署,窗口覆盖 now 后 GM/任务加分才进。**查窗口**=`GMPrintServerActivityByCfgId <配置号>` 返回的 `start:/end:`(UTC) 对当前服时间。
- **加 BP 分的 GM = `GMAddActivityScore(activityId, score)`**(`ActivityMeta.Gm.cs:292`,[活动_活动]增加进度积分,GM_NORMAL)。代码=`UpdateActivityScore(progressScore + score)`;**BP 升级吃的就是 progressScore**(`ActivityMeta.BattlePassScore.cs:339` 同一入口,等级由 progressScore 反推)→ 此 GM 直接给 BP 加分**且绕过竞猜任务**,正合「GM随结算发BP分」SOP。`score<=0` 报 ParamError。
- **🔴🔴🔴 第一个参数 activityId ≠ 配置号(如102243),必须是运行时雪花号(实测踩坑)**: GM 内部 `GetActivityData(activityId)=Data.activityDict[activityId]`:
  - **本地 TimeCycle 触发**的活动: `activityId = cfgId`(`ActivityMeta.cs:1630`)→ 可直接填配置号。
  - **iGame/ark 部署 或 海域活动(TC清0走部署控时,世界杯全hub模块都是)**: `activityId = serverActivity.id`(雪花运行时号,`ActivityMeta.cs:1345`)→ **填配置号 102243 会静默不加(GetActivityData 返 null→ErrCodeActivityIsNotOpened),但 iGame 后台仍显示"成功"**。2026-06-25 实测:填 102243 数据没涨,换雪花号才真涨。
- **★★两步法 SOP(iGame 部署型活动给玩家加积分)**:
  1. **拿雪花 id**: `--cmd GMPrintServerActivityByCfgId --args "<配置号>"`(`Gm.cs:171`,[活动_活动]通过配置ID查询服务器活动,server-scope)→ 返回 `id:<雪花> cfg:<配置号> start:.. end:..`。⚠️结果**异步回 iGame 后台**(send_gm.py stdout 只有网关 ack),需让用户从后台读那行 `id:` 雪花数字回贴。
  2. **用雪花 id 加分**: `--cmd GMAddActivityScore --args "<雪花id>,<分>"`。
  - 没部署则 print 返回 `no server activity found for cfgId=...`。
- **🪤 iGame 网关 `success:true` ≠ GM 真生效**: `ark/gm-operate/add` 只回「网关已登记」,**不回游戏侧 ErrorCode**(连 `__probe_noop__` 也 success:true);真执行结果/报错**异步回 iGame 后台**。所以打完必须**登号/查后台 GM 结果/查数仓**核 progressScore 真涨,别凭网关 success 下结论。
- **🐛 send_gm.py 尾随 `；` bug(2026-06-25 修)**: 旧脚本在 gm JSON 末尾强补全角 `；`,服务端 `ArkModule.Gm.cs:20` 用 `JsonConvert.DeserializeObject` 严格解析整条 body,遇尾随 `；` 抛 `Additional text encountered after finished reading JSON content: ；`→**GM 静默不执行**(网关仍 success)。已删脚本补尾逻辑;SKILL.md「末尾追加 ；」文档亦已纠正。详见 [[reference_igame_gm_send]]。
- **其它「给玩家加分」GM**: `GMAddSubActivityProgress`(子任务进度)/`GMAddNoParamTaskScore`·`GMAddOneParamTaskScore`·`GMAddTwoParamTaskScore`(按TaskType喂任务进度)/`GMPlayerDeltaUpdateCrossPrepareScore`(跨服备战)/`GMAddBountyScore`(悬赏令)/`GMSetArenaScore`(竞技场)。

## 🎫 节日积分BP(ActvType22)标准模板 = 情人节(2236)·配新节日BP照它克隆别抄推币机/世界杯(2026-06-23 深海BP换皮实证)
**踩坑**：深海BP当初从**推币机/世界杯BP(2240)**克隆=**模板错**。世界杯/推币机BP是**2轨**(免费+至尊·单包`2026016`·带推币机专属积分任务`2201`)，不是节日标准。**节日标准BP=3轨**(元旦2233/尼罗2234/情人节2236/春节2238 全同构)。
- **BattlePassScore 行结构(cols)**：[1]ID(=ContentID) [2]备注 [3]IsOn [4]积分途径(pipe串) [5]购买礼包(pipe串) [6]奖励组(BattlePassScoreReward.Group) [7]bool。
- **★节日通用件(跨节日共享·不用克隆·直接指向)**：①积分途径=`501|502|503|504|505|506|601|602`(集结击杀1-6+采集+情报) ②购买礼包=`130020`($9.99**进阶**)`|130021`($19.99**至尊**)。**唯一每节日专属=奖励组**(情人节135/深海142)。
- **奖励组 3轨结构(BattlePassScoreReward)**：每级1行·[1]行id [2]Group [3]等级 [4]升级所需积分 [5]免费轨RewardID [6]**进阶轨** [7]**至尊轨** [8]col8。**2轨BP=col6进阶轨空**(世界杯/推币机就这样)→换成3轨必把col6每级填上进阶轨RewardID。
- **🔴🔴 BattlePassScoreReward 行id 是硬契约 `id = 组号×100 + 等级`（引擎按 id%100 取等级，根本不读「等级」列！2026-06-24 深海BP"等级不连贯"实证）**：客户端 `ActivityUtils.cs:391-412`(`NewBattlePassScoreRewardCfgID=groupId*100+level` / `BattlePassScoreRewardGroupId=id/100` / `BattlePassScoreRewardLevel=id%100`) + 服务端 `ActivityMeta.BattlePassScore.cs:364` 都按 `id%100` 算等级。**组142等级1-20 → 行id 必须是 14201-14220**(正常组135=13501-13520印证)。**坑**：深海BP当初行id被写成连续块 `14121-14140`(满足"id连续"导表校验,但 14121%100=21 → 引擎解码成组141/等级21-40 乱序)→ 玩家看到"等级不连贯"。**修复=行id按 14200+等级 重排**(commit 61768af·dev_festival)。**配/换皮BP奖励组铁律：先定组号G,20级行id 直接写 G×100+1 .. G×100+20,别用"找个连续空块"的思路(连续≠合契约);"等级"列只是冗余备注,引擎不看**。导表的"id连续"校验只兜连续性、不兜 id↔等级映射,所以光过校验≠显示对。
- **换皮深海BP实操(commit 08cc675·feature/x3-deepsea-art)**：BattlePassScore 2244 备注→深海/途径去2201/包2026016→130020|131021/组142；组142补进阶轨col6=新建Reward块4344040-059(克隆至尊轨4344020-039占位)；ActvOnline 102244壳已对没动。备份表`KB\产出-数值设计\X3_深海节\配置备份表\02_远航日志_BP\`。
- **跨节日RewardID隔离铁律**(见[[reference_x3_config]])：克隆奖励组必先克隆**专属Reward块**(深海=4344xxx)别引用原节日的RewardID。Reward表**组内行id(seq)必须连续**。

## 🎫🎫 X3 有「两套」BattlePass — 改BP前必先分清是哪套(2026-06-18 护航令至尊档案实证)
| | 简易战令 `ActvType=11` | 积分战令 `ActvType=22/33` |
|---|---|---|
| 配置 | `ActvBattlePass__BattlePass`(Pack=单包) + `BattlePassReward`(**只有 FreeReward/PackReward 两列=2档**) | `ActvBattlePassScore`(**FreeReward/AdvanceReward/SuperReward 三列=3档**)+UpgradePrice钻石升级列 |
| 客户端 | `UIActvBattlePass.BattlePassItem` **prefab 写死2轨**(`Free`/`Pack` 两个ChildGroupController) | 数据驱动；**3档UI已实现**(世界盃通行證就是它,带"一鍵領取"+"X段/3000"进度) |
| 服务端 | `ActivityMeta.BattlePass.cs` **免费/付费两分支硬编码** | `ActivityMeta.BattlePassScore.cs` **位标志引擎** `Free=1/Advance=2/Super=4`,加档≈零代码 |
| 档位区分 | 靠不同列(FreeReward列 vs PackReward列),非Type字段 | 位标志 `purchased & rewardType`,Pack管道列表index→tier位 |
- **现有2档简易BP实例**(改造对象)：101102新手主线/101110情报循环/101104登录循环/101120兔女郎(都IsOn)。**界面付费列头实际叫「至尊」**(不是"付费/高级")。
- **要给简易BP加档** = 把它改成积分BP那套位标志引擎(抄 `BattlePassScore.cs`)：`BattlePass.Pack` 单包→管道串、`BattlePassReward` 加 `SuperReward` 列、prefab 加第3轨、proto purchased 多位、`BattlePassRwdItem`/`UIActvBattlePassPop` 加第3档分支。改动面=客户端~200-300行+服务端中等+配置schema。**老BP不配第2包+不填SuperReward=保持2档零回归**。
- **「钻石升级」= `BattlePassScore.UpgradePrice`**(花钻跳级),是积分BP独有、可选;护航令至尊档案明确**砍掉不要**。
- **🎫护航令至尊档案(2026-06-18·策划案已落地+task-checker验收通过)**：简易BP 2档→3档(免费/进阶/至尊);现界面"免費/至尊"两列→现付费"至尊"($9.99)**降级改名"进阶"(2格→1格)**,**新增更贵"至尊"顶档(≈$19.99,2格)**,免费压窄;superset买至尊含进阶轨,纯加奖励轨不送等级不双倍,❌不要钻石升级。布局=免费(压)｜進度(偏左,在免费与进阶间)｜进阶(1格)｜至尊(2格)。**策划案GSheet=`1BP_qkISn-YfDDsYoBMQLD9-lLRQebYlz1rFjmOmpgLE`**(9页签,含「组件&节点改造」页);构建脚本+草稿+效果图脚本=`KB\产出-数值设计\X3_护航令至尊档\`(build_design.py/mock_3tier.py可复跑)。真实界面截图`Pictures\X3验收\BP新增档位\`(4张现状+节日BP模板)。**真实UI素材+节点改造已挖**:奖励板=九宫格sprite程序拼无整底图;战令专属素材`client\Assets\Res\UI\Spirits\Activity\ui_battlepass_*`(列头bg_1/2标签·point_1/2菱形·icon_lock)+大背景`ActivityImg_Download\img_battlepass_bg_1.png`(船海场景);加档=行模板复制Pack单元(x+197宽618,HorizontalLayoutGroup)→Super单元+Title复制标签,三列重分x。**效果图真正可拆组件源=真实asset非截图;reward板九宫格程序拼,像素级重建不划算**。**下一步=程序按案改client(prefab复制Pack→Super+脚本+proto)+server(抄BattlePassScore.cs位标志引擎)+配表(BattlePass.Pack管道化+BattlePassReward加SuperReward列)**。

## 关联
- [[reference_x3_gdconfig_repo]] [[reference_x3_tsv_export_migration]] [[reference_x3_reward_table_rules]] [[feedback_x3_branch_check]] [[reference_x3_i18n_workflow]]
- [[feedback_jira_bug_ticket_field_swap]] — BUG customfield 实际/预期可能被 QA 填反，看标题
