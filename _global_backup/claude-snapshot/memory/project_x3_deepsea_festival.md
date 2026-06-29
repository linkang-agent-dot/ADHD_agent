---
name: x3
description: X3 2026 深海节开发案，双周双核心循环主攻付费深度；含唯一入口/11模块/ID分配总表
metadata: 
  node_type: memory
  type: project
  originSessionId: f62aaf0b-2522-4962-afda-ba39e6e04fd1
---

# X3 2026 深海节（开发中，2026-06-18 进入配置落地阶段）

**核心路线**：提高付费深度。夏日恋语验证 breadth 成功、depth 没起来 → 深海节=**双周双核心循环**，第二周专攻 depth。
- 第一周(D1-D7)：英雄皮肤转盘抽奖+排行榜（铺 breadth）
- 第二周(D8-D14)：主城皮肤大富翁+航海通行证（**付费深度大头**）
- 开启范围：D50+ 老服。

## ⚠️分支铁律（2026-06-24踩坑·必看）
深海配置改 push **目标分支=`origin/dev_festival`**。但 `C:\x3\gdconfig` 本地有个 **`dev` 分支 tracking `origin/dev`**(ahead/behind 几十个)——**别在 `dev` 上干深海活**！否则 `dev` 的本地化/红包/timecycle/Merge-into-dev 等提交会混进来,push 时 non-fast-forward,且容易把 dev 污染推进 dev_festival。
- **干活前先 `git checkout dev_festival` 确认**(branch --show-current)。
- 若已在 dev 上误提交:`git fetch` → `git reset --hard origin/dev_festival` → `git cherry-pick <我的深海提交hash>` → `git push origin HEAD:dev_festival`(只挑深海提交,丢掉dev的)。验证用 `git rev-list --left-right --count HEAD...origin/dev_festival` 应是 `N 0`(只领先自己的N个,不落后)。
- 远端 dev_festival 是多 agent 在途(大富翁/世界杯/深海各 agent)·push 前 fetch 看分歧·只推自己文件。

## ★唯一入口（换人接管先读）
0. **数值体系总览_投放感受 HTML**（2026-06-25·11模块价位带/ROI/R级阶梯/节奏/投放感受诊断）：`C:\ADHD_agent\KB\产出-数值设计\X3_深海节\深海节数值体系总览_投放感受.html`。诊断出的待调点：①ROI口径不统一(累充50%/成就800%/装饰标称3200%虚高) ②价位带断层($29.99/$59.99空·$99.99→$200→$2000三连跳) ③大富翁后6档$99.99重复 ④罗盘券多点投放或稀释转盘 ⑤外显钩子散5处无招牌皮。
1. **对齐总览 HTML**（全貌+11模块+投放明细+依赖+拆agent参考）：`C:\ADHD_agent\KB\产出-数值设计\X3_深海节\深海节开发对齐总览.html`
2. 策划案 GSheet：`1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI`（页签：深海节策划案 / 各活动模块 / 大富翁×7 / 节日周卡 / **深海节-开发配置需求**=ID分配总表）
3. 本地文档 `KB\产出-数值设计\X3_深海节\`：深海节策划案.md / 航海之路大富翁换皮_信息交接.md / Jira单拆分_给制作人.txt
4. 程序需求：`KB\产出-交互原型\X3_2026深海节\珍珠贝进度系统_程序落地需求.md`

## 11 模块（题材命名）
- **需程序(5)**：01深海罗盘(转盘) / 03怦然心动(每日礼包·切换) / 04深海印记(头像框·通用礼包模块) / 10大富翁(珍珠贝进度+海盗金币弹脸+成就礼包+存钱罐,搬X2代码) / 11节日周卡(自选4项,X2有先例)
- **纯配置(6)**：02远航日志BP / 05深海馈赠累充 / 06深海居所装饰(19.99×3) / 07海滨之约拜访(99.99) / 08许愿池(仅换背景) / 09最佳酒馆(仅换背景)

## ★排期 + 酒馆真相（2026-06-25 用户确认/实测）
- **排期=10天**（非14天，策划案的D1-D14是抄情人节基线）。**所有内容 D1 开局就开**，仅 **周卡 + 拜访(海滨之约)错峰到后7天(D4-D10)**。原"双周分两段"框架作废。BINGO=大富翁的"累计地格任务升级模块"(免费层·50%活跃可玩)，随大富翁D1开，非独立活动。
- **最佳酒馆719——查证：不是bug，换皮已完整**（我一度误报"719积分空"=自己用脆弱grep `\t719\t`扫空了的误判，**教训：验配置存在性别用裸grep，按正确key列awk**）。真相：深海酒馆 AO10071704 ContentID=**719**(自己的)，是717的**完整换皮**——ScoreMulti **7191-7197**(7阶段·阶段时长合计**正好10天**) + ScoreGroup **7191-7197**(28行) + **自己的奖励组786035-786038**(都存在)。**共享框架**：阶段榜RankCfg601-607 + 总榜RankID131(4个节庆酒馆元旦/情人节/春节/深海共用·"节庆通用跨服酒馆"设计如此)。**14天也是误会**(719阶段时长合计10天，跟节日对齐)。→ 无需改；若要深海专属任务/奖励/铭牌=「新扩内容」(真活儿非修bug)。**跨服酒馆换皮法**=clone ScoreMulti+ScoreGroup+rewards(各自ContentID)，rank框架共享。
- **拜访pack小图**：DK=`DK_img_Activity_deepsea_visit_pack`·client=`ActivityImg_Download/img_Activity_deepsea_visit_pack.png`(368×260·不在图集·reimport即生效)。候选在 `KB\产出-本地化与美术\X3\深海节\07_拜访\deepsea_visit_pack_v2_{1,2}.png`(海滨小屋立绘) vs `07_海滨之约_拜访礼包\_入库FINAL\拜访礼包图_368x260.png`(画框门头场景)。
- Jira 已拆给制作人（程序5/纯配置6）。

## ID 分配总表（已落地，扫 tsv 防撞，2026-06-18，无半成品）
GSheet「深海节-开发配置需求」页签。规律见 [[X3 配置知识库]]（AO=100000+ContentID）。
- 转盘CID1025/AO101025 · 兑换1340/101340 · BP2242/102242 · 累充598/100598 · 拜访5606/105605 · 许愿池5013/105013 · 酒馆717复用/10071704 · 大富翁2801复用原位/102801(TC2702海域开放链)
- ActvGroup140 · TimeCycle主1830/拜访1831/周卡1832 · Pack块211016-211025 · WeeklyCard2008-2010 · RankCfg186(RankType12)

## 本地服一键开全套（2026-06-25 实测）
深海节落地后实际分 **ActvGroup 140(深海节)+141(深海航行/大富翁线)** 两组，共 **10 个 AO**（按 `ActvOnline col38∈{140,141}` 枚举，方法见 [[workflow-x3-local-server-gm-telnet]]）：100598累充5 / 102244BP22 / 101025转盘10 / 101340兑换13 / 101341大富翁兑换13 / 106103装饰阶梯礼包63 / 105605拜访56 / 10071704签到7 / 102802航海之路成就礼包版28 / **105013许愿池50**。
- 本地 3080 用 `!gm @<uid> GMAddServerActivityByCfgId <AO> 43200` 逐个开：**9/10 成功**；**唯一开不了=105013(type50许愿池跨服)**，本地单服结构性限制（需 CenterServer），要测得另搭本地 center(见 telnet workflow 的 KVK 段)。开完登被测号(活动建在其海域)看，没刷新就退登重进。

## 配置搬运状态（2026-06-22·进行中）
- **gdconfig 已切 dev_festival**(领先origin 2提交·树净·游离`_fix_reward_seq.py`)。配置备份仍是KB草稿,**尚未搬进live tsv**。
- **搬前跑了格式防线**(列数vs目标表+id占用核对·在dev_festival上)——发现2类问题:
- **①id冲突→已修(2026-06-22·用户要求高位重排留间隔防冲)**:深海item全套1150-1155→**1200-1205**(1200罗盘券/1201宝珠/1202大富翁代币/1203深海罗盘/1204珍珠贝/1205海神罗盘)·RankCfg1005→**2000**·拜访Reward30600-04→**40000-04**。已字段精确替换所有交叉引用(兑换货币1151→1201/转盘Consume1150→1200+奖池/大富翁README+DK清单1152-55→1202-05)+文件重命名+复核新id全空。
- **②列数/格式问题→大部已修(2026-06-22)**:转盘AO101025+许愿池AO105013(51→52,从live模板101023/105012整行克隆补全) / LuckyWheelReward 32100行补到11列 / 拜访Reward211020补到14列。**仍待**:头像框Pack211019(不是列bug=「通用礼包模块需程序·PackType待定」竖排占位·程序定型前搬不了) / PersonalizeAvatarFrameCfg live表名要重找。
- **③TC配0(用户定2026-06-22·不建TC行)**:全部深海AO的TimeController=**0**(靠iGame部署submit控时)。⚠️配0会被导表`PostProcessData.deal_actv_online_data`校验「时间控制器0不能是0」→**已改导表工具** `C:\x3\gdconfig\Tools\table_exporter\PostProcessData.py:1646` 的 `SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE` 加入节日类型(累充5/酒馆7/转盘10/兑换13/BP22/许愿池50/拜访56;28大富翁/63周卡/64竞猜原已在)→节日活动现支持TC=0。**此改动随配置一起commit到dev_festival**。
- **④ActvGroup140已建**:`配置备份表\_ActvGroup深海节入口\ActvGroup_新增140.tsv`(克隆通用组101 cm chrome·排序97·入口图标DK待出·i18n auto key)。
- **❗共享依赖行没建**:backup漏了 TimeCycle 1830-1833 + ActvGroup 140 的snippet,但所有ActvOnline行引用它们→直接搬`ExportTable.py`必报depend_checks失败。**搬运前必先建这两组共享行**。(DK字符串不影响导表·runtime才需注册)

## 大富翁成就礼包+存钱罐 已落表(2026-06-24·commit7634213·导表build#1211 SUCCESS)
> 落地实录详表(11档映射/Reward口径/踩坑)见 `配置备份表\10_大富翁\成就礼包数值_配置草稿.md` §落地实录。冷启动接手点:
- **独立HUD「深海航行」(2026-06-24·ActvGroup141)**:大富翁要自己的HUD(含大富翁盘面+兑换商店两tab),不跟其他8个深海活动挤组140「深海节」→ 新建 **ActvGroup141**(`ActvOnline__ActvGroup.tsv`·11列:c1 id/c3 入口名/c4 入口图标DK/c5 排序/c6-11 chrome·克隆140深海cm·图标复用`DK_img_Activity_icon_Monopoly_deepsea`)+把大富翁102802/兑换101341的 **`ActvOnline.ActvGroup`(c39) 从140改141**。**ActvGroup机制=HUD入口:多个AO同c39组=一个HUD多tab**;组名本地化key=`TXT_ActvGroup_MainEntranceName_{组id}`;AO标题母版=`ActvOnline.c3`,本地化key=`TXT_ActvOnline_ActvName_{AO}`(扫描生成)。大富翁102802原标题是旧"航海之路"且无i18n→改母版c3=深海航行+建TXT×16。commit走worktree(见[[feedback_confirm_before_touching_inflight_repo]]worktree隔离法)。
- **珍珠贝图标(item1204·DK_icon_global_deepsea_pearl)重画**:原图扁平卡通描边画风怪→x3-media item_icon写实半厚涂重出(2026-06-24派worker)。纯换client png不改配置,需reimport/AB。
- **程序写完**:`server\...\ActivityMeta.Voyage.cs`跑圈→`GiftMeta.AchievePack.cs CheckAchievementPackUnlockByVoyageLap`(解锁条件`ACHIEVE_PACK_UNLOCK_TYPE_VOYAGE_LAP=3`/`TRIGGER_TYPE_ACTIVITY=14`,值在`client\...\CSShared\Common\Const\ActivityConst.cs:412/415`)。
- **程序作者已建桩**:`Pack__AchievePack.tsv`行**104**(11档·门槛10/20/.../100/200圈)+11桩Pack**2801001~011**(DK/i18nkey/type全配好),我只填真价值(桩全指向占位Reward组100)→**行104无需动**。
- **成就礼包11档**=封板6价值档($1.99/4.99/9.99/19.99/49.99/99.99),$99.99重复6档(lap60~200·whale milking);Reward组**1028021~026**(罗盘1057+钻石1002+VIP2022+纪念卡180080·ROI~8×·$99.99共用1028026)。**罗盘用老骰1057非新1203**(骰子复用老的)。
- **存钱罐**Pack280001→$19.99/超值10×/Reward组1028027(罗盘45+钻石1万+VIP50)。
- **Reward表口径**:c1=行唯一id(只需不重复)·**c2=组id**(Pack.c14指向它)·c3=1道具·c4=item·c6=数量·c8=1·c9=10000(100%)。
- ⏳**待玩法验**:跑圈解锁触发的`TriggerParamVals[0]==actvData.cfgID`——桩c6=2802(Target)/c10=102802(TriggerParameter),若不触发查`actvData.cfgID`取2802还是102802。
- **宝箱报错最终修(2026-06-24·commit58aacd4·经历误诊更正)**:三字段语义=`TreasureItemID`(c6)=神秘宝箱**发的奖励箱道具**(老=1059)·`OtherReward`(c7)=**「额外奖励」表组id非宝箱开关**(=100,清零会删掉额外奖励进度条且联动停神秘宝箱)·`ProgressItemID`(c12=1204)=珍珠贝独立进度。**真BUG=早先误把c6 1059→1204(珍珠贝非奖励箱)→报`TreasureItemID cfg error`→修回c6=1059+c7=100**(我中途误判c7是宝箱开关清零过=51e9cee错,已回退)。**"全岛宝箱铺满"=客户端AB未重建非配置错**(DK/PNG/配置全对·岛图各异正确)。详见 `配置备份表\10_大富翁\岛屿数值_配置草稿.md` §换皮坑(最终结论)。**仅动2802不碰2801**。
- **规律(回写)**:配置备份搬tsv前必跑格式防线(列数/id占用)；backup常漏共享行(TC/ActvGroup/Reward)→导表depend_checks失败；本地`cd Tools/table_exporter && python ExportTable.py`先验比等Jenkins快。
- **✅首批已落地 dev_festival(2026-06-22·commit d2eb3dd已push)**:8模块搬进live tsv(转盘ActvLuckyWheel+AO101025/兑换ActvExchange+AO101340/铭牌PlayerTitle105+Text/装饰Pack链+Reward/拜访ActvVisitPack+Pack/许愿池/酒馆AO/通用道具Item1200-1201/ActvGroup140)+PostProcessData SKIP集改。本地ExportTable**导表0异常通过**。
- **撤出本批(草稿留着待配全)**:累充100598/BP102244=**空壳**(只AO行·没配ActvTask598/BattlePassScore→depend_checks挂)/头像框Pack211019=通用礼包需程序/大富翁=行未生成。
- **rebase经过**:push遇远程分叉(festival团队8提交)→`git rebase origin/dev_festival`**干净**:①gdconfig有智能合并驱动`tsv_merge_pro`/`xlsx_merge_pro`自动行级合数据 ②PostProcessData自动3-way合(保住别人**周卡ActvType 63→70/竞猜64→71改号** + 我的节日SKIP添加)。rebase后重验导表仍过才push。
- **★周卡ActvType改号(2026-06-22 festival团队·影响11周卡落地)**:WEEKLY_CARD **63→70** / WC_GUESS **64→71**(actvonline_def.py+PostProcessData)。11节日周卡落地用70不是63。
- **★搬运踩坑规律(回写·下次搬必扫)**:①backup数字列里的TODO占位**文本**(抽奖券`<待建>`/累充白名单col49/RankCfg MailID)→导表ConvertError·搬前必scrub成真id或空 ②转盘ActvLuckyWheelReward:SReward唯一(只1行=1)+正好10项 ③Pack.TimeCycleID/ChainPack.TimeCycle不能指不存在的TC→用**6001永久** ④空壳活动(只AO·缺content表ActvTask/BattlePassScore)→depend_checks挂·撤批 ⑤ExportTable前必`sync_xlsx_tsv --from-tsv`补xlsx(否则verify_xlsx_tsv abort)·openpyxl重存会污染同xlsx其他页签→子页签带齐一起sync。
- ✅ **jolt Jenkins导表 SUCCESS(build #1114·dev_festival)**——首批配置落地链路全绿(搬tsv→本地ExportTable→rebase→push→Jenkins #1114)。
- **❗❗DK 全没注册(2026-06-22 关键待办)**:首批8模块配置导表过但**DK一个没入库**(导表不校验DK存在→#1114绿但runtime缺图)。待入库=各活动背景/icon/岛图/代币/铭牌DK(client Display_*.asset数字系统·美术多为方向稿需终稿+切图+注册)。**配置层绿≠能显示·DK入库是最后一公里·量不小**。

## 下一批配置(2026-06-22 用户greenlight·进行中)
- **数值解锁**:累充/BP **数值先用旧的**(克隆模板原档位/奖励·到时改)→不卡了。**头像框改黑猫模式**=Pack(PackType=1+TriggerType=1+TriggerParam=深海TC+推送字段Head/Icon/MainBg/PopUp)**无独立ActvOnline·无需"通用礼包模块"程序**·纯配置(参黑猫神龛Pack210616)→头像框解锁了。
- **⚠️id漂了**:festival已合dev·团队并行占号(框定义10076已被占·max10079)→**每模块搬前当前dev_festival重扫防撞·别照搬旧备份号**。
- **★深海纪念卡(用户定2026-06-22)**:**MemorialCard 80 / Item 180080 / 霍普金斯(海风旅者Hero1034 skin01)主题**。⚠️澄清:**世界杯纪念卡是79绿茵之星不是80**(git确认80从没存在·没掉配置·MemorialCard连续到79);深海顺接80。**完整recipe照搬`KB\产出-数值设计\X3_世界杯\_系列卡_配置落地清单.md`**(clone源MemorialCard76/Item180076):MemorialCard80(11列)+Item180080(42列·Type9/UseEffect15/UseParameter80/DK_Icon)+Text 7条(TXT_MemorialCard_Name/Desc/GetTips/GetMoreTips_80 + TXT_Item_Name/Desc/ObtainTips_180080)+PropertyGroup1011复用。★坑:**纪念卡走字符串DK系统**(Path_Item.asset DK_icon_card_image_80→小图256 + Path_Memory.asset DK_img_card_image_80→大图384·**非活动的数字DK系统**)·必写Text表否则空·2图(256道具图标斜放梯形/384大图竖版金框)。**美术:竖版角色卡=霍普金斯全身(Role_F_ios_34_skin.png)+深海航海背景+金框(格式锚=世界杯卡WC_MemorialCard_img_big_79)·大图**已出2变体待用户挑**(`KB\产出-本地化与美术\X3\深海节\11_纪念卡\深海纪念卡_霍普金斯_big.png` + `_v2`·竖版金框+霍普金斯全身+深海航海背景)。已挑定big主版+霍普金斯。**256道具图标=斜放梯形**:⚠️**别自己估倾斜角度(我瞎试2次都错)**——梯形角是量游戏现有卡icon`icon_card_image_76.png`的4角(TL68,32/TR218,21/BR191,231/BL36,223·右上最高),把big透视warp进这梯形+多边形遮罩透明。**直接复用脚本** `KB\产出-本地化与美术\X3\世界杯纪念卡\_warp_trapezoid.py`(改SRC/OUT路径)。256已出。下一步:配MemorialCard80+Item180080+Text7条→字符串DK(Path_Memory DK_img_card_image_80 + Path_Item DK_icon_card_image_80·Display双补)照recipe。****
- **待配全再搬(本批)**:大富翁(克隆行·不含程序件)/累充(ActvTask旧档)/BP(BattlePassScore旧档)/头像框(黑猫Pack·框定义重分配id)/纪念卡80(图好后配3表+字符串DK)/i18n。

## ✅ 活动背景DK全入库 + HUD统一 + 累充/BP背景换深海（2026-06-23·feature/x3-deepsea-art·两仓·solo）
- **★★分支规则已变更(2026-06-23晚·覆盖下面旧铁律)**：**统一到 `dev_festival`，不再用 feature/x3-deepsea-art**(feature的深海工作已合进dev_festival·`git merge-base --is-ancestor fa1cf4 dev_festival`=在✓)。**两仓都在dev_festival上做**。⚠️**多agent并发dev_festival·会切你工作目录分支**→commit前必`git branch --show-current`(我累充/BP commit曾误落对的dev_festival纯属走运)。⚠️**data/*.xlsx已被gitignore**(纯tsv工作流正式生效·只commit tsv·别再-f加xlsx)。
- **★HUD用各模块专用图·非通用(2026-06-23用户定·覆盖并发agent的"deepsea_hud_icon统一5模块")**：gdconfig dev_festival commit `818ef85` 已把 兑换/转盘/拜访/许愿池/酒馆 ActvIcon 改回各自专用(exchange/turntable/visit/wishpool/tavern)+累充fund/BP bp·本地ExportTable过·已push。client专用图DK均入库双补。**待**:①~~client累充/BP DK没push~~**✅已push(2026-06-24·8207462)**——并发agent脏树+behind死结用 **`git stash -u → git pull --rebase origin dev_festival → git push → git stash pop`** 干净解开(rebase无冲突·pop把并发agent的Unity churn[Display_Item/Path_Item/atlas/.meta·可弃重生成物]原样还回)。**多agent脏并发分支安全集成法=stash看不懂的churn+pull--rebase+push+pop**。 ②**重导表regen ProtoGen .bytes到client仍待做**(并发agent e23c5d05导的hud_icon版·我gdconfig 818ef85改dedicated后要重导一遍·专用图才显示·jolt或本地ExportTable→GenCSharp→commit client)。
- ~~**★用户铁律(2026-06-23)**：深海节配置/DK 只做到 feature/x3-deepsea-art~~（**已废·见上·改统一dev_festival**）。已核两仓 feature 均基于 origin/dev 最新。
- **client(x3-project) feature 领先dev 6 commit(纯深海DK)**：9cf1cf6(转盘大潜艇bg)/cf47b44(纪念卡80)/7592208(头像框)/fac814bc(visit/fund/wishpool bg+补turntable_bg Display)/0d19fd0(兑换/酒馆bg)/610668c(BP v2 bg)。
- **✅所有活动背景DK已入库(Display+Path双补·sort-safe)**：turntable_bg/visit_bg/fund_bg/wishpool_bg/exchange_bg/tavern_bg/bp_bg + 早先hud_icon/转盘皮3/铭牌2。Path_Activity=1226。⚠️**入库后必Unity Ctrl+T save**(见DK清单文末)。
- **★槽位尺寸真相(解了"对不上竖版"卡点)**：兑换/酒馆/BP 槽位都是 **540×500**(矮宽·查模板VD_bg_6/VD_bg_12/WC_Pass_Bg实测)·累充540×960·拜访1152×2048·转盘1080×1344。gpt源图全1536×2048竖版→crop-fill取中段裁到槽位。**BP用v2**(用户选·明亮暖光舵轮+海图+罗盘构图饱满)。
- **✅live tsv(gdconfig feature) ActvOnline 9处改**：累充100598 ActvImg WC_Fund_Bg→deepsea_fund_bg·BP102244 ActvImg coinpusher_bp_bg→deepsea_bp_bg·**7模块ActvIcon全统一`DK_img_Activity_deepsea_hud_icon`**(转盘/兑换/拜访/许愿池/酒馆/累充/BP/每日礼包·潜艇共用)。大富翁(另agent)+周卡(原生复用)不碰。
- **★导表验证新工作流踩坑(2026-06-23·xlsx彻底下线后)**：① **data/*.xlsx 已.gitignore下线·不进git·由`sync_xlsx_tsv --from-tsv --all`从tsv全量重建到工作树**(新人setup自动跑·我本地没跑过→data/空→ExportTable的verify_xlsx_tsv报orphan=440 abort)。本地导表前必先跑 `--from-tsv --all` 建xlsx(440表·几分钟)。② **改完tsv要把xlsx同步上**：`--auto`(git diff推断tsv→xlsx)走**增量cell patch**·遇ActvOnline这种**多行cell表会行坐标错位**(BP那处patch没写进)→改用 `--from-tsv --files <表>` 整表重建·但**tsv_to_xlsx是patch模式需base xlsx存在**(我删了文件→没重建→orphan)→正解=别删·直接`--from-tsv --all`或保留base后--files。③ ExportTable verify过(mismatch=0)才算数。
- ✅**已闭环(2026-06-23)**：ExportTable导表通过→gdconfig commit 68b0a87 push feature(⚠️pre-commit hook的`sync_xlsx_tsv --auto`在ActvOnline多行cell crash·xlsx已`--from-tsv --all`重建一致+--check全绿+ExportTable过→`--no-verify`提交安全[xlsx gitignore不进git·jolt自重建])。client 6 commit已push。**Unity Ctrl+T save 已做(用户2026-06-23·DK注册正式生效)**。jolt触发验证中。
- ⏳**剩余**：装饰展示视频DK/拜访礼包图DK入库·04头像框弹窗DK·i18n补全·累充/BP数值占位→真值·MR合dev(用户定时机)。

## DK 入库（client·feature/x3-deepsea-art 分支·2026-06-22）
- **新分支=`feature/x3-deepsea-art`**(用户喊人建·我在上面)。**同事已起头并按正确方式做**:转盘整套(`img_Activity_deepsea_turntable`/`_pointer`/`_bg_wheel`/`hud_icon`)+铭牌(`deepsea_icon_title`)已 **Display_Activity + Path_Activity 双补**入库。
- **★DK入库铁律(否则白做)**:必须 **Display_*.asset(真源,key/type/desc/guid从png.meta读/exportCode:0) + Path_*.asset(运行时,DK_前缀→objPath,两段平行) 双补**。只手编Path不登Display→下次Unity「生成dk」全量重导出**静默清掉**(e255事故清了278个·世界杯整套外显被清)。机制+恢复脚本逻辑见 [[reference_x3_client_resources]] + `scratchpad/restore_e255_dk_v2.py`(Display追加+Path父锚点插入+guid从.meta)。
- **终稿已就绪待入库(_选定/_FINAL)**:大富翁8件(`_FINAL_正式版\`地图/4岛/代币/珍珠贝)+铭牌(已入)+转盘皮底台/指针/盘面(已入bg)+头像框(深海框+弹窗bg)+累充bg+装饰banner+拜访bg。⚠️**同事正活跃编辑同批Display/Path→并行手编会冲突,DK入库需跟同事分工(哪些归我)别盲目并行**。纪念卡走字符串DK(Path_Item/Path_Memory,图出后)。

## ★Ctrl+T全量重导出清掉Path-only DK事故(2026-06-23·根治法·必看)
- **现象**:用户DK入库后Ctrl+T save→client工作区90个DisplayKey asset全改。集合对比(提取`- DK_`行做**集合diff·排序无关**)发现:绝大多数=Ctrl+T换排序规则的**纯重排(无害·key集合不变)**;但**3个DK真被删**:纪念卡80大图`img_card_image_80`(Path_Memory)/icon`icon_card_image_80`(Path_Item)/深海头像框`Img_Player_AvatarFrame_deepsea`(Path_Personalise)。
- **根因(非pull·用户pull了)**:这3个入库时**只写Path没登Display**(误以为"纪念卡76-79是Path-only跟着做"·实际76-79都登了Display_Memory/Item·winemaking框也登了Display_Personalise)。**Ctrl+T=从Display全量重新生成Path**→Display无条目的Path-only DK被漏清(=e255机制)。对照证实:双补的76-79/winemaking被Ctrl+T保留;只Path的80/deepsea框被清。
- **诊断法**:`git show HEAD:<Path文件>`vs工作区,提取`- DK_`行**集合diff**(别看±行·重排让同key同时出现±)。集合相同=纯重排安全;集合少=真删。
- **修复(根治·commit 1cabdda)**:①Path/Display还原HEAD(我注册版含全部DK·已jolt#1125验证·丢弃Ctrl+T纯重排无损)②3个DK**补Display条目**(Display_Memory/Item/Personalise各+1·key去DK_前缀·type=Memory/Item/Personalise·guid从png.meta·exportCode0)→下次Ctrl+T不再删。
- **★铁律强化**:**任何DK入库必Display+Path双补**(纪念卡/头像框这种"看着Path-only的系统"也要补Display·76-79其实都有Display)。Ctrl+T前先git pull。

## ✅ 纪念卡属性改斗士(2026-06-23·用户拍板·已commit gdconfig feature a500e9f)
- **用户定**:纪念卡属性改斗士系·**世界杯卡79绿茵之星=斗士攻击·深海卡80远航之歌=斗士防御**(原都射手防御)。⚠️79是已上线世界杯活动·改属性=改已发卡buff(用户授权balance)。
- **★纪念卡属性机制(可复用)**:`MemorialCard.col9`=MemorialCardLevel.Group→该Group每级`col5`=BuffTemplate.ID(属性类型)+`col7`=数值(万分比·30级200→6000)。**显示属性名走BuffTemplate.AffixName(TXT_BuffTemplate_AffixName_<id>·16语言齐·已校对)·不是col1**(col1中文是冗余备注·颜色00B309≠BuffTemplate82b03d为证)→**改Group即改属性+i18n自动全语言·零i18n工作**。
- **关键省事=斗士攻防有现成成熟Group(大量卡在用)直接改引用不新建**:**斗士攻击Group1005(BuffTemplate220003)/斗士防御Group1012(220013)/射手防御Group1011(220012)**·三组数值梯度完全一致→改Group数值不变。属性ID速查:220003斗士攻·220013斗士防·220012射手防·220002射手攻·220011猎人防·220010猎人攻等(220xxx系兵种攻防)。
- **改动**=MemorialCard 79 col9 1011→1005+col1斗士攻击;80 col9 1011→1012+col1斗士防御。

## ★xlsx下线后导表(2026-06-23·cxy已给标准流程·必照做)
- **xlsx已被commit 68685d2「下线data/xlsx不进git」移出git**(changxiaoyun重构·.gitignore`data/**/*.xlsx`)·tsv唯一权威源·xlsx由`sync_xlsx_tsv --from-tsv --all`从tsv重建到工作树(setup自动跑)。
- **★cxy标准流程(2026-06-23发·合dev到开发分支照做)**:① **合dev报xlsx冲突`modify/delete: data/X.xlsx`→全部选删**:`git status`看冲突xlsx→`git rm`全删→`git commit`完成合并。② 合完data/无xlsx=**正常不用慌**。③ 要Excel看表→本地`python scripts/sync_xlsx_tsv.py --from-tsv --all`重生成(只自己看·不上传)。④ 之前卡导表的分支→合完dev再跑导表就好(jolt CI已适配·会自重建xlsx)。⑤ **以后改表只改tsv·绝不改xlsx**(改xlsx不生效也不进版本)。
- **历史(已解)**:jolt #1142 FAILURE曾因CI没适配·我的feature卡过;cxy修CI后合dev再导表即过。**别手动git add -f还原xlsx到分支**(违下线)。
- **本地导表验证**:`sync --from-tsv --all`重建xlsx→`Tools/table_exporter/ExportTable.py`(verify一致+数据校验)。深海纪念卡斗士+许愿池改动已本地导表通过(mismatch0/protoc/MD5全绿·2026-06-23)。
- **★sync增量patch对多行cell表(ActvOnline/MemorialCard等col含长文本)不生效坑**:`--auto`/`--from-tsv --files`走cell patch遇多行cell行坐标错位→改的cell没写进xlsx→--check报mismatch。**解=删该xlsx+`--from-tsv --all`整表重建**(--files对删掉文件不重建·tsv_to_xlsx patch需base)。pre-commit hook的`--auto`也因此crash→已一致时`--no-verify`提交安全(xlsx gitignore不进git·只提tsv)。
## ✅ 纪念卡80「远航之歌」已全套落地(2026-06-23·jolt #1125 SUCCESS)
- **gdconfig**(feature/x3-deepsea-art,commit a7a8cf3):MemorialCard 80(克隆76·PropGroup1011·DK_img/icon_card_image_80)+Item 180080(克隆180076·UseEffect15/UseParam80)+Text纪念卡7条key+**兑换商店替换**(ActvExchange 134002 深海兑换纪念卡槽 180077情人节→**180080深海卡**)。
- **客户端DK**(feature/x3-deepsea-art,commit cf47b44):icon_card_image_80.png(256梯形,_warp_trapezoid脚本)+img_card_image_80.png(384×523大图)→Path_Item DK_icon_card_image_80 + Path_Memory DK_img_card_image_80(字符串DK双列表·76-79是Path-only无Display·跟着做即可)。美术终稿`KB\产出-本地化与美术\X3\深海节\11_纪念卡\深海纪念卡_霍普金斯_big.png`+`_256.png`。
- **★附带修复2个bug**:①**深海兑换1340曾被损坏**——行134000(万能传奇信物)col11有个**未闭合引号**`"<size=40>50%</size>`,csv把134001-134014(含纪念卡)全吞成1个cell→14个兑换项失效(我之前搬运带进的)。删引号即修。②**误删WIP道具82005「航者徽记(头衔)」已恢复**——我`git checkout HEAD -- Item`回退自己csv乱改时,连带丢了别的会话留的铭牌发放道具82005(传说铭牌模块·克隆82004发PlayerTitle105·备份`01_传说铭牌_航者徽记`漏记Item行)。已克隆82004重建。
- **★★关键教训(回写·下次配置/导表必看)**:
  1. **jolt「X3导配置」job 会在 client(x3-project) checkout 同名分支** 做C# proto→**gdconfig分支名必须==client分支名**,否则`client remote branch does not exist`+`exit -1` FAILURE(build#1124踩)。配置走feature分支时两仓统一用 **`feature/x3-deepsea-art`**(深海client DK分支),#1125即过。
  2. **含多行单元格的表(Item/ActvExchange/Text·物理行≠逻辑行)必须用`csv.reader(delimiter=\t)`解析**(=gate的`read_tsv`@sync_xlsx_tsv.py:633),`split('\t')`物理行会错位;sync xlsx用**csv逻辑行坐标**喂`tsv_to_xlsx.py`手术(base=git HEAD,new=当前,compute_changes要求新行在**文件末尾**·中插会block→append到末尾)。`MemorialCard`无多行cell可split。
  3. **回退tsv前必`git status`查WIP**(别像我盲目`checkout HEAD --`丢了82005)。dev分支共享·常有别人未提交WIP(Rank/Reward/ActvLuckyWheel/ActvOnline转盘排名+铭牌82005)。
  4. **pre-commit hook auto-sync会把工作树所有一致的tsv/xlsx一并暂存**→`git add`选择性文件也会被hook扩到全部(本次纪念卡8文件→17文件含转盘WIP·用户拍板合并推)。
  5. **dev是受保护默认分支·直推被classifier拦**→走feature分支+MR。MR API当时500(GitLab服务端)·用push返回的手动链接建。
  6. **client gdconfig是独立子模块**(`C:\x3-project\gdconfig`·≠我改的`C:\x3\gdconfig`)·在别的分支(newbie-recharge)+有队友GenProto.py WIP→pre-commit hook要子模块干净·提交client用`子模块git stash push GenProto.py→提交→stash pop`保住队友WIP。

## ✅ 累充+BP+大富翁补充 已配(2026-06-23·feature/x3-deepsea-art·数值用旧值占位)
- **累充**(commit 6a7482e):克隆世界杯597→**CID598/AO100598**(TC0/组140)+ActvTask **59811-820**(CID598/额外参1=598)+**专属Reward块59850-859**(克隆WC内容·占位1146抽奖券·到时候改)。
- **BP**(6a7482e→**换皮修正08cc675**):~~克隆世界杯2240~~=**模板错(世界杯是2轨)**→**2026-06-23已换情人节(2236)3轨标准模板**(commit 08cc675):途径去推币机任务2201·包2026016→节日通用`130020|130021`($9.99进阶+$19.99至尊)·奖励组142补进阶轨col6=新Reward块**4344040-059**(原4344000-039只free+super=2轨·"三轨"是当初误记)。详见[[reference_x3_score_activity]]「节日积分BP标准模板」。CID2244/AO102244(TC0/组140·壳已对)。★**坑(已修·371bcdc)**:Reward表要求**同RewardID组内行id连续**(导表`rewardID:X ID不连续`),克隆多行组必须**按组分配连续行id**,别按文件顺序(会插花)。★★**等级不连贯BUG已修(2026-06-24·commit 61768af·dev_festival)**:组142的20行行id被写成`14121-14140`(连续但`14121%100=21`)→引擎按`id%100`取等级解码成等级21-40乱序(玩家看到"等级不连贯")。**改回 14201-14220**(BattlePassScoreReward行id硬契约=`组×100+等级`·引擎不读「等级」列·之前371bcdc只满足"id连续"导表校验没满足id↔等级映射故没修到)。详见[[reference_x3_score_activity]]「BattlePassScoreReward 行id 硬契约」。
- **大富翁=102802**(非2803!程序已配"航海之路成就礼包版"·已霍普金斯深海主题+框架齐[珍珠贝1150/存钱罐280001/成就礼包677/IslandGroup1复用]):我**补充**(371bcdc)=组110→**140**(深海入口)+顶部资源1057|1060→**1200|1201**(深海罗盘券|深海宝珠)。⚠️**里子未动**:ActvVoyage 2802 抽卡/掉落仍程序旧货币(1057/1058/1059/1060)·全货币reskin+大富翁深海DK入库=**另一个agent干**(用户2026-06-23明确)。深海大富翁专属item 1202-1205**未建**(程序复用旧的)。
- **数值/DK/购买礼包/积分方式/白名单全=世界杯占位·到时候改**。tsv-only(新工作流xlsx自动·见下)。
- ⚠️**头像框(04)黑猫式 卡住**:黑猫Pack(210616)靠**TimeCycle触发**(TriggerType1+TriggerParam=TC1825),但**深海全活动TC=0部署驱动·无深海TC**(1830-1833都不存在)→黑猫pack没TC可骑。框定义新id=10080(10076已占)·Pack211019空·框道具走UseEffect。**待定:头像框pack骑哪个TC**(建深海master TC? 还是换触发方式?)→需design/用户拍板才能配。

## 美术/换皮串味修复三连(2026-06-25·gdconfig dev_festival·本agent)
> 共同根因:深海多模块当初按「仅换背景」做,奖励道具/图标本体没换皮→串源节日资产。换皮"仅换背景"模块**必回查奖励道具+ActvIcon是否还指源节日**。
- **①许愿池气泡奖励 串味+失能(✅commit1bf77a4·jolt#1313)**:`ActvWishingPoolReward`组按节日各有专属许愿令牌道具(1114海兽牙/1118/1124糖牌/1128埃及女王卷/1134情书VD/**1138祈愿红灯笼=春节cny图标**...每节日一个token,玩家从池赢取→拿去节日兑换商店花)。深海许愿池(CID5013·奖励组**105**)复用了春节1138→气泡飘红灯笼,**且深海兑换商店(ActvExchange1340)收的是1201深海宝珠不认1138→玩家赢了没处花**(双重bug)。**修=组105的5档(25/20/16/14/12)1138→1200深海藏宝图**(投罗盘探索代币·自带深海图标DK_icon_global_deepsea_treasuremap)。154002幸运家具木匣(超级大奖)不动。**坑澄清**:1200=深海藏宝图(转盘抽取券)·1201=深海宝珠(兑换商店货币)·别搞反(memory旧记"1200罗盘券"是过时名)。
- **②装饰礼包下面页签图标(✅commit63db8c0)**:`ActvOnline.ActvIcon`(**col22**)=底部HUD页签图(≠PackTypeInfo.Icon那是商城tab·≠ChainPack.Icon弹窗头像)。深海7模块ActvIcon曾统一共享潜艇图`DK_img_Activity_deepsea_hud_icon`,后大多换专用(818ef85改exchange/turntable/visit/wishpool/tavern+fund/bp),**装饰礼包106103漏掉→还挂潜艇图**(扫全表只剩它1处用hud_icon)。**修=col22→`DK_img_Activity_deepsea_icon_decor`**(装饰本体图·海滨遮阳椅·已注册Display_Activity+有png)。**⚠️2026-06-29纠错:deepsea_icon_decor是RGB无透明的整张海滩场景图→塞进木框页签显得乱不贴框,且漏了名称→正在重修(下条)**。
- **②b HUD页签图标格式+名称纠错(2026-06-29·进行中)**:用户反馈装饰页签「图标有问题+没名称」。**两根因**:①**图标格式错**:页签图必须**RGBA透明+徽章式**(深海珊瑚/贝壳华丽框+居中主体·对齐同组`deepsea_tavern_icon`金杯款·124×136 RGBA);deepsea_icon_decor是**RGB无alpha的海滩场景图**(整张不透明矩形)→渲染乱。**规律:ActvIcon/HUD页签图=RGBA透明·别用RGB场景图**。**⚠️但别套圆框/华丽徽章(2026-06-29用户纠正:我一度做成圆徽章框被打回)——页签木框是HUD自己的,图标只要干净主体**(参建造/船只/制造队列页签=锤子/船/工具裸主体·遮阳椅就遮阳椅)。徽章框留给「外面的HUD」别处用。修=重出徽章图标(椰风遮阳椅+阳伞主体·酒馆图作风格ref·x3-media task20260629-112343-a7b2)→新DK替col22。②**名称缺失**:`TXT_ActvOnline_ActvName_106103`i18n key不存在(其他深海AO累充/BP/转盘/兑换/拜访都有·只106103漏)→页签下空白。**规律:AO加进HUD组(ActvGroup)必须有`TXT_ActvOnline_ActvName_{AO}`否则页签无名;漏了走x3-translation-automatic扫ActvOnline补**(scan读data/xlsx·需先`sync_xlsx_tsv --from-tsv --all`重建·复用`TXT_Pack_Name_211016`「深海居所特惠Abyssal Abode」术语)。
- **③许愿池双图层(进行中·派x3-media出图)**:许愿池有2层独立图—`ActvOnline.ActvImg`=`deepsea_wishpool_bg`(540×500整块场景panel bg·已深海)+`ActvWishingPool.DK`(**col8**)=`fountain_bg_7`(**540×540透明喷泉对象·居中**·还是旧古典金边石喷泉)。换皮要分层看。喷泉对象层重出深海版(珊瑚/贝壳/珍珠·gpt图生图对比老图保构图·task20260625-223131-f7a3·出图存`KB\产出-本地化与美术\X3\深海节\08_许愿池\deepsea_wishpool_fountain_v1.png`+_alt+_compare)。**老图fountain_bg_7=540×540 RGBA真透明**(新图必须对齐此规格)。收尾=新图抠真透明→缩540×540→入client→col8改指新DK+DK入库(Display+Path双补)。**⚠️fountain_bg_7是通用共享图**:`ActvWishingPool` CID5007/5008/5009(通用池)都用它,**不能覆盖**(污染通用池)。各节日池有专属图(5010埃及Egypt_bg_9/5011情人VD_bg_16/5012春节CNY_bg_17),深海5013漏配=还挂通用fountain_bg_7→**建深海专属新图`img_Activity_deepsea_wishpool_fountain`+新DK,只改5013 col8指向**。DK注册结构=Display_Activity加`key:img_Activity_xxx/type:Activity/guid:<png.meta的guid>/exportCode:0`(本repo DisplayKey目录只见Display_*.asset·Path由Unity Ctrl+T从Display生成·入库后必Unity Ctrl+T save)。喷泉图终稿=v3(`deepsea_wishpool_fountain_v3.png`·X3 scene风格·用户2026-06-26定稿·**v1/v2作废**)→remove_background抠透明→`deepsea_wishpool_fountain_FINAL_540.png`(540×540 RGBA真透明)。**✅已执行入库(2026-06-26)**:①client新图`img_Activity_deepsea_wishpool_fountain.png`+meta(clone fountain_bg_7.meta换新guid8cebe625·同Sprite设置)+Display_Activity注册(commit`8a1cbf5f928`·dev_festival已推·走stash+rebase+push+pop避并发WIP)②gdconfig `ActvWishingPool`CID5013 col8→新DK(commit`8fc22d3`·jolt验证)。**⏳剩2步(都Unity/构建侧)**:见下「★配置DK改真显示的完整传播链」。
- **★★配置DK改要真在游戏显示的完整传播链(2026-06-29踩透·必看·不止改tsv+jolt)**:改`ActvWishingPool.col8`这种「配置指向某DK」后,游戏要显示新图需**4环全通**,缺一不显:①**gdconfig tsv改col8+jolt**(✅但jolt只导到构建服`client_master`·**不回提dev_festival的.bytes**);②**client新图+meta+Display_Activity注册**(✅源);③**Unity Ctrl+T save**→把DK从`Editor/Config/DisplayKey/Display_Activity.asset`(源)生成进`Res/Config/DisplayKey/Path_Activity.asset`(**runtime真源·DK→sprite解析**·grep新DK判断Ctrl+T做没做);④**本地ExportTable重导配置.bytes**→`Res/Config/ProtoGen/ActvWishingPool.bytes`里col8才变新DK(**jolt不更新这个·grep .bytes判断**)。**验证**:`Path_Activity.asset`(runtime DK·文本·grep可靠)+`ActvWishingPool.bytes`(配置col8)都要有新DK·Ctrl+T管前者·ExportTable管后者。**⚠️`.bytes`是Git LFS跟踪**:`git cat-file/show <ref>:x.bytes`返回的是**128字节LFS指针不是内容**,grep它必假阴性(我2026-06-29踩此·查半天矛盾)→正确验证committed版=`git diff --stat`(无输出=工作树同HEAD)或rebase报`patch already upstream`(=已在upstream);验证工作树用`grep -a`真smudge内容(383字节真文件)。**实战收尾(2026-06-29全闭环·已push origin/dev_festival)**:①col8 commit8fc22d3+jolt#1321 ②png+meta+Display commit8a1cbf5f928 ③Ctrl+T runtime(Path_Activity/PathAssetList/Path_Item/Display 4文件)commit71f3a7e2ff3 ④bytes(并发agent也重导了·我的成冗余被rebase丢·LFS已在origin)。4环齐→游戏显示深海喷泉。**坑:多agent并发dev_festival·client repo推送走`git stash -u→pull --rebase→push→stash pop`隔离并发WIP(font/lessons/gdconfig指针/Path_Item等别人的churn)·只commit自己的DK文件**。**本地ExportTable法**=`cd Tools/table_exporter && python ExportTable.py`(直接读tsv→输出`temp_dev/ProtoGen`·**不碰xlsx**·`__main__`硬编码`export_tables('../../temp_dev','../../tsv',[])`·有depend_checks必须全表导不能单表)→生成后**只拷需要的`temp_dev/ProtoGen/ActvWishingPool.bytes`→client对应位置→commit**(并发WIP的别的表bytes不拷不带过去)。
- **★踩坑4·gpt图生图要transparent出"假透明棋盘格"**:prompt写transparent background时gpt会**把灰白棋盘格画进RGB像素**(非真alpha·`PIL mode=RGB`+四角像素≈(233灰)/(254白)为证),且白色水柱/水雾跟棋盘白重叠→**事后没法靠颜色抠**。`transparify_asset.py`双底差分**只支持纯文生图(--prompt)或现成白底+黑底两图(--white/--black)·不支持图生图带reference_images**。解法二选一:①重出时背景要**纯绿幕/纯色**(gpt对纯色忠实)→chroma key;②**grfal remove_background**抠(本案用户选这个)。生成透明资产别信gpt的transparent参数。
- **★踩坑5·X3出背景/物件图风格锚=default-styles.md的「scene」锁定风格**:X3不是手绘也不是写实,是**「clean stylized 3D cartoon render + cel-shaded toon shading + plastic-smooth塑感 + 鲜亮饱和 + not painterly/not hand-painted/not anime-CG」**(default_prompt在`~\.claude\skills\x3-media\references\default-styles.md`scene/poster行·一字不差抄)。喷泉重出v1太朦胧手绘→打回,v2太写实3D渲染→打回,**v3套scene锁定风格全文+老图同槽位资产(fountain_bg_7)作风格+构图双ref才对路**。规律:X3换皮出图,**用同槽位老资产当风格+构图ref + scene default_prompt全文**,别让gpt自由发挥(必漂)。装饰本体家具151043椰风遮阳椅是夏日源资产但**投放对**(海滨居所配遮阳椅·用户确认不换)。
- **★踩坑1·tsv手编Edit工具裁尾tab(犯2次)**:Edit的new_string**结尾的tab会被裁掉**→改字段值若末尾要保留tab(列分隔)就会列粘连/丢列(NF少1)。**安全法=要改的span把后面非tab字段一起纳入match**(如`深海藏宝图	25	0	2`整段换),或**用awk按字段split→insert('')→rejoin重建**(已验证可靠·见本次ActvOnline col22修复)。改完必`awk -F'\t' '{print NF}'`对比同表他行确认列数。
- **★踩坑2·共享分支被并发agent切走**:dev_festival多agent在途,**jolt_verify或别的agent进程会把本地工作目录checkout到qa等别的分支**(工作树净·静默)。我的commit已push到origin安全,本地切回=`git checkout dev_festival`。干活/commit前必`git branch --show-current`(本次commit后被切到qa,幸亏已push)。
- **★踩坑3·jolt_verify本地轮询超时≠构建失败**:jolt_verify.py触发后会轮询Jenkins,慢的时候打印`[!] 构建轮询超时,去Jenkins看`就退出——**这不代表构建失败,只是本地等不及**。查真结果=`curl -s "http://172.20.110.29:8080/job/X3%E5%AF%BC%E9%85%8D%E7%BD%AE/<build#>/api/json?tree=result,building,number"`(无需auth·返回`"result":"SUCCESS"`即真过)。本次#1320轮询超时但实为SUCCESS。

## 许愿池气泡道具图标透明度 + 礼包加VIP(2026-06-29·本agent·已push dev_festival)
- **①藏宝图道具1200图标透明度坏(✅commit663aa5c68a3·client)**:`icon_global_deepsea_treasuremap.png`(256·DK_icon_global_deepsea_treasuremap)主体只~54%不透明(发虚透光)+边缘黑matte污染(低alpha像素RGB=纯黑0)→气泡里发虚。**诊断坑**:`alpha==255`严判误报"只1%不透明"·实际grfal抠完主体alpha中位254(视觉实心)→**量透明度用`>=240`不用`==255`**(软抠边AA达不到255)。**修法对比**:PIL alpha-levels拉满→主体实心但**黑matte边显形**(拉alpha把黑RGB显出来·失败);**grfal remove_background去背景→主体实心+去黑边+真透明(成·62%有效不透明·无黑边)**。规律:**道具图标"半透明/黑边"=alpha处理坏·走grfal remove_background修(别用levels拉)·还不行重出**。纯换client png不改DK/配置·Unity reimport即生效。
- **②许愿礼包加VIP(✅commit938cdb6·gdconfig·jolt验证)**:许愿池`ActvWishingPool.Pack`=**1002001「许愿礼包」$4.99**·Reward组`4024325`(Pack.col14)。加VIP=item**2022「VIP点数」(UseParameter=100·每个100点·奖励num=N给N×100点·标准节日礼包num=5=500点)**。**★Reward表加道具到单行组要迁连号**:同组行id必须**连续**(导表`rewardID:X ID不连续`)·组4024325单行19584·加第2行但邻号19585被占→**整组迁到就近空闲连号对(23156/23157)+删旧19584**(Reward行id=纯唯一键·无别处按行id引用·改安全·Pack按组id4024325引用不受影响)。py脚本克隆原行结构避免手敲tab错列。结果:2500钻+500VIP点数。

## 大富翁岛屿显示双BUG修复(2026-06-25·gdconfig dev_festival commit608fe72)
> 完整记录+客户端单:`KB\产出-数值设计\X3_深海节\大富翁岛屿显示BUG_修复记录与客户端单.md`。
- **共同根因**:单等级改造清空了幸运岛(LUCKY=5)/钻石岛(GEM=4)的`ExpGroup`,但这两类是框架写死的「可升级岛型」(`ActivityConst.ACTIVITY_VOYAGE_CAN_LEVEL_UP_LAND_TYPE`)。三方等级口径打架:**客户端**按ExpGroup有无定级→空→level=0(`UIActvGridBubble.cs:63/99-122`);**服务端**用landInfo.level→恒1(`ActivityMeta.Voyage.cs:172`);**奖励数据**在Level=1桶。奖池key=`EG*1000+level*100`(客户端服务端共用`ActivityUtils.cs:806`)。
- **⚠️陷阱**:清空ActvVoyageEvent.Level让客户端level=0对上=**会让服务端(恒1)查空静默掉奖**,排除。
- **BUG2(奖池+概率不显)=✅纯配置修**:给幸运/钻石岛在**Level=0桶补一份奖励副本**(跟宝藏/神秘岛同机制,它们本就Level空显示正常)。ActvVoyageEvent追加16行:ID=原-100(`EG*1000+0+seq`)·Level留空·其余照抄(钻石EG200×1+幸运EG201/202/203×各5)。客户端else分支(level=0)读到→显示;服务端仍用level=1原行发奖**零影响**;老配置零改动。导出按`group=EG*1000+Level*100`分桶、WeightPercent按`EG*1000+seq`算→副本概率自动对(`def/actvvoyageevent_def.py`)。本地ExportTable过·jolt#1298。
- **BUG1(没配等级却显Lv标)=✅已修(x3-project dev_festival commit8e02bb6·不走MR直推)**:只剩棋盘格子一处(`GridItem.cs:108-109` mGoLv按IslandType显隐,不看ExpGroup);气泡因ExpGroup仍空走else分支本就不显。改法=`canLvUp`加`&& CActvVoyageLevel.Instance.Group2Exp.ContainsKey(islandCfg.ExpGroup)`,没配经验组不显Lv,老航海之路(ExpGroup=1)不受影响。配置改不掉(IslandType是行为开关不能动)→必须改代码。**⚠️客户端代码改动需重新出客户端包才在游戏里生效**(BUG2配置走jolt导表即生效·BUG1代码要打包)。
- **★可复用规律**:航海之路「可升级岛型(LUCKY/GEM)」的等级=客户端读ExpGroup(空→0)、服务端读landInfo.level(恒1),**两者天然不一致**;给这类岛塌单等级时客户端奖池/Lv显示都会炸。最稳纯配置修=**在level=0桶补奖励副本**(不动Level=1原行不动服务端),把可升级岛在客户端显示上「降维」成无级岛。`ActvVoyageLevel`表ID=全表唯一主键且兼当组内等级键(`actvvoyagelevel_def.py`按ID建Vals)→**新建ExpGroup无法有level1(ID=1被占)**,别走「补单级ExpGroup」(会出`0/2147483647`脏经验文本)。

## ✅ 大富翁(102802)岛屿换皮 配置隔离+DK入库已落地(2026-06-23·feature/x3-deepsea-art·本agent)
- **用户铁律**:岛屿走**新配置·不动老配置**(2801与2802共用IslandGroup1·原位改会污染老航海之路)。
- **配置(gdconfig commit 7298a58·已push·本地ExportTable exit0)**:新建 **IslandGroup2**(克隆组1的24格→编号201-224·EventGroupID+100) + **EventGroup199-206**(克隆EG99-106·行id+100000·DKImg按岛型换深海DK·保留升级机制不动奖励)。repoint:ActvVoyage2802 IslandGroup1→2 + ActvOnline102802 ActvIcon→Monopoly_deepsea/ActvImg→Monopoly_deepsea_bg。反查2801仍组1、组1仍24格、老EG99-106仍101行=老配置零改动。
- **★EG→岛型→深海岛DK映射**:99起始→`DK_img_Activity_deepsea_island_start`/100钻石→diamond/101-103幸运→lucky/104-105宝藏→treasure/106神秘→mystery。地图bg=`DK_img_Activity_Monopoly_deepsea_bg`。
- **客户端DK(x3-project·已commit+push `dev_festival` 1a7f150·待Ctrl+T)**:6个DK(5岛+地图)Display+Path纯追加双补·png终稿来自`10_大富翁\_FINAL_正式版\`·objPath=`Assets/Res/UI/Spirits/ActvVoyage/img_Activity_deepsea_island_*.png`+`Monopoly_deepsea_bg.png`。岛184×224、地图540×960(与老槽位一致)。入库脚本scratchpad `dk_voyage_deepsea.py`可重跑。
- **✅岛屿i18n已落地(2026-06-23·gdconfig dev_festival d64835f·已push·ExportTable exit0)**:ActvVoyageIsland group2母版改深海cn + Text新增**10行**(5名+5故事·按类型合并key`TXT_..._201|..._208|...`·16语言齐·status=AI)。深海名:启航港/沉船宝藏/珊瑚秘境/海风礁/迷雾漩涡。故事基于老岛同类最小改。脚本scratchpad `island_i18n.py`+`island_names_cn.py`。
- **⚠️⚠️分支统一到 `dev_festival`(2026-06-23晚)**:旧铁律"深海只做feature/x3-deepsea-art·dev_festival别碰"**作废**。**feature/x3-deepsea-art 已merge进 dev_festival**(gdconfig acf4c58/14b8d26)→**两仓(gdconfig+x3-project)现都在 dev_festival·团队在此干活**。我的全部提交都在dev_festival历史里(结构7298a58/i18n d64835f/client DK 1a7f150)。**未提交改动两次被切分支冲掉**→教训:做完**立刻commit别裸放工作区**。
- **里子货币reskin 改我做(用户2026-06-24"都你做")**:转盘1200藏宝图(cc500e7·treasuremap)/1201宝珠(4d75d85·orb)是团队转盘的。**大富翁货币里子(本agent·用户2026-06-24定)**:①**骰子直接复用老的不做新**——普通骰`1057航海罗盘`/付费骰`1058海神罗盘`保留(无专属图·UI是转盘指针样式·成就礼包/存钱罐给的"深海罗盘"=1057)。②**只建2个新item(已生成`货币里子_新item.tsv`)**:`1202深海代币`(clone**1060**·图06·DK`DK_icon_global_deepsea_token`)+`1204珍珠贝`(clone**1150**老珍珠贝[非1059·1150更对口·已是珍珠贝]·图07·DK`DK_icon_global_deepsea_pearl`)·ItemObtain已清。③repoint清单(`货币里子_配置草稿.md`):宝藏岛EG/兑换 1060→1202·ActvVoyage2802 TreasureItem1059→1204+ProgressItem1150→1204·ProgressReward组200 1059→1204。**单等级EG tsv已remap 1060→1202(14处·神秘岛1058骰子保留)**。④角色`DK_Role_Bunny`不变。⚠️成就礼包/存钱罐草稿"深海罗盘1203"=实际复用1057(落表用1057)。**DK入库✅(client dev_festival c3415d6·已push)**:2货币图标(token/pearl)——只提**Display_Item(真源)+png+meta·没提Path_Item**(working tree的Path_Item含另agent的key重排WIP·不连提·靠Ctrl+T从Display重生成)。client DK全齐(islands 1a7f150+currencies c3415d6·都待用户Ctrl+T)。**✅货币里子+单等级已落live(2026-06-24·gdconfig dev_festival commit 48c15f9·已push·本地ExportTable exit0·jolt验证中)**:建item1202/1204+EG199-206多级101行→单等级32行(代币1060→1202·骰子1057/1058复用)+2802 TreasureItem/ProgressItem→1204+ProgressReward组200→1204×17+Island组2清ExpGroup×16(停升级)。老EG99-106/2801零改动。**✅i18n已落(2026-06-24·commit c6969fc·已push)**:TXT_Item_Name/Desc_1202(深海代币/Abyssal Token)+_1204(珍珠贝/Pearl Shell)·16语言·status=AI·ExportTable过。**✅深海兑换商店已建(2026-06-24·commit dd6dd53·已push)**:clone航海之路兑换CID1332→**CID1341/AO101341**(深海珍宝集市/Abyssal Bazaar·type13·组140·深海icon+exchange_bg·顶部资源1057|1202)·11兑换行(消耗代币1060→1202·纪念卡180041→180080·月心珍珠81101/霍普金斯5303401/养成料沿用)·i18n ActvName/Desc_101341 16语·老1332/AO101332零改动·ExportTable过。**⏳剩(全是非数值/待依赖)**:①成就礼包(ActvAchievePack)+存钱罐(Pack280001改真值)落表待程序monopoly_lap结构 ②用户Ctrl+T(client DK生效)。**★大富翁配置侧(除程序件)基本齐活**:岛屿单等级/货币里子(1202/1204)/货币i18n/兑换商店1341 全落live+DK入库。
- **★坑(回写)**:①岛名/故事走i18n按**岛id**取key`TXT_ActvVoyageIsland_IslandName/IslandStory_{id}`(tsv中文只母版不读)→克隆新id**必补i18n否则岛名空白**(导表不报);②同名岛在Text**合并成一行**(key=`TXT_A|TXT_B|...`)·按类型写一行合并key不是每id一行;③美术每类型1张图→克隆101 EventGroup行**所有等级DKImg都指同一深海DK**;④**升级机制=单等级(用户定2026-06-23·砍升级)**:克隆来的多级EG199-206需塌单档(每组只留Lv1加权奖池·删Lv2-5·Level表停用·岛屿升级flag关)→对齐ROI8单档E值方案;别再按"保留升级"做(早先误记已纠)。
- **数值换皮方案(2026-06-23·待用户拍板)**:`KB\产出-数值设计\X3_深海节\深海大富翁数值换皮方案.html`(已打开)。**经济盘沿用现成`航海之路数值框架.html`+`ROI8_v1.html`(2026-06-02·已压平加速器到ROI=8·变现侧不改)**,只调流量侧。原则=**流量侧改(门槛/产出节奏/珍珠贝阈值/成就礼包圈数)·变现侧不改(ROI8/主城皮肤月心珍珠300000钻=原航海之路/海神罗盘价)**。★**成就礼包(跑X圈·策划案待定项)已对X2真数值重做**:**X2成就礼包(机甲/军备)实证=定价带$1.99~$99.99·ROI≈185-225%(≈2×)·按养成节点解锁·每实体一套·+触发礼包配套**(源`.cursor/x2-numerical-design/机甲_活动明细.md`+`军备_活动明细.md`+`养成线深度手册.md`)。⚠️**关键坑:成就礼包ROI≈2×·跟抽奖盘ROI=8是两套独立口径·别混**(我初稿误写成就礼包ROI8·已纠)。大富翁套X2结构=6档(跑5/15/30/55/80/100圈→$1.99/4.99/9.99/19.99/49.99/99.99·两头都要:$1.99铺广度+$99.99吃深度·只中段3档=丢两头量)。**用户定(2026-06-23)**:①节点按真实run-rate微调 ②**触发礼包不上** ③**成就礼包投纪念卡**=深海纪念卡180080「远航之歌」放$99.99顶档当cosmetic headline·**价值按X2装饰物口径(cosmetic不按3%战力高估)**·ROI由档内养成料撑·纪念卡是封面附赠。**X2装饰物≈$10/个(用户定2026-06-23)→纪念卡计≈$10(≈5000钻)·占$99.99档($187.5)~5%·其余靠料**。折算:500钻=$1/远洋金币1060=10钻/钻石=1钻。纪念卡兑换价400深海宝珠(1201·ActvExchange134002)仅参考。**成就礼包v1具体版已出(2026-06-23·照X2口径直接折·用户要求直接出别等)**:6档$1.99-99.99·ROI201%→188%·道具钻值[深海罗盘250/海神罗盘5000/代币10/纪念卡5000/1h加速200]·低档纯罗盘高档海神罗盘+代币(兑皮肤)+纪念卡headline(详见`成就礼包数值_配置草稿.md`§二)。剩:跑圈节点真实run-rate微调+养成料包具体料定盘换(总钻值不变ROI不变)+Pack677结构待程序对齐(跑圈触发=程序项)。夏日骰子根因教训已带(产出别<设计·门槛按真实活跃校准·满级料降200-250思路)。
- **★★ROI口径重大纠错(2026-06-24·用户指正)**:成就礼包**不能用X2的ROI(≈2×)**！**X3礼包ROI标准在数值库`KB\方法论\节日活动形式知识图谱.md`**:抽奖礼包(行350)=保底1.1-1.5×/安慰1.4-1.9×/**大奖9-9.55×**;掉落福利活动(行783)=**615-678%**;雷达BP(行140)=614%。**成就礼包是跑圈福利包→走~700%(福利/大奖)档·非保底1.5也非X2的2×**。★**跨游戏换皮铁律:ROI口径用目标游戏(X3)的标准·别套源游戏(X2)的**——只借结构(节点解锁/价位带),ROI重定。**v5定稿(用户2026-06-24·迭代到9档)**:**ROI=8×·投放=深海罗盘1203+钻石+VIP点数·9档·节点3/5/10/20/30/50/70/100/150圈(第3圈就能买)**。价位$1.99/4.99/9.99/19.99/49.99 + **$99.99×4**(50/70/100/150圈·同内容·深R跑越多解锁越多档=可重复变现"再加2档99刀"意图)。骰子价值=抽奖产出2000钻/个·ROI(计罗盘+钻石+纪念卡)=8×·VIP点数=scaling bonus(20→1000·钻值口径未定暂不计ROI)。**纪念卡180080:$49.99×1·每$99.99×2**(集卡升级·重复=升级料/Regained·⚠️全买whale拿9张待确认集卡吃得下·否则高档改纪念卡碎片)。各档罗盘+钻石+VIP。**v7封板(用户2026-06-24确认)**:**不出代币**(只罗盘+钻石+VIP点数)·**钻石=实付1:1**(用户确认$49.99→25000/$99.99→50000·=充值量级·各档1k/2.5k/5k/10k/25k/50k)·罗盘×3/9/17/35/85/170·VIP点数500/1k/2.5k/5k/10k/25k(=道具2022×5/10/25/50/100/250·bonus不计ROI)·纪念卡$49.99×1/$99.99×2。已回写草稿+HTML封板。**存钱罐封板(用户2026-06-24)**(`存钱罐数值_配置草稿.md`):走主表inline·Pack280001 **价$19.99·超值10×**·内容=罗盘×45+钻石×10000+VIP×5000(不出代币)·产出≈100000钻。占位($0.99/Content组100)待改成真价+Reward组。**★X3礼包钻石/VIP参考锚点(2026-06-24实证·可复用)**:①钻石充值天花板 $99.99=**50000钻**/$49.99=**25000钻**(纯钻ROI1·Pack1006);Reward组给钻常见5000-50000。②VIP点数=道具**2022**(100/个),常见量×5/10/25/50/100/250/500=500~50000VIP点。③**钻石与VIP极少同组**(全表0组同含·通常分开给)。④节日value包(礼包付费A线连锁210708/210710·PackType11)奖励走**嵌套/链式**·Content(Pack col14)指不到Reward组·没法干净dump明细。**v6提案(待用户确认钻石/VIP量·未落files避第6次重写)**:钻石25k/50k($49.99/$99.99·按充值量级)+VIP 1万/2.5万+罗盘填ROI8×。**成就礼包机制(config表tab确认)**:=ActvAchievePack(复用X2 activity_hero_achievement.tsv·程序搬X2)·完成条件Fincond JSON`{"op":"ge","typ":"monopoly_lap","val":圈数}`(需程序加monopoly_lap条件类型)·Iap非0=付费限购1次·存钱罐=PiggyBank复用X2。
- **★数值已备份落地(2026-06-23·另agent在改live故先放备份)**:`配置备份表\10_大富翁\成就礼包数值_配置草稿.md` + `岛屿数值_配置草稿.md`(待live稳定后合)。**岛屿数值已全定盘(用户2026-06-23)**:①**E值=原航海之路Lv1值·已做**(ROI8_v1确认·克隆的EG199-206 Lv1行现成有真实道具/数量/权重→不用重配·我之前误标"待定"已纠) ②**阶段奖励按之前的**(原OtherReward 4200001-8原值·不压平) ③**单等级**(删EG各组Lv2-5留Lv1) ④**神秘岛"经验+2"事件砍**(删EG206 EventType2后退/3经验·留EventType1随机奖励) ⑤**珍珠贝进度系统保留**(序列1,2,3,4,4,4,6,6,6,8,8,8,8,10+箱值15300·程序件)。**合live落地动作**:删EG199-206各组Lv2-5+删EG206 EventType2/3+Level停用+阶段奖/珍珠贝沿用原配。成就礼包剩:跑圈节点真实run-rate微调+各档道具数量配比。
- **⏳剩**:①**用户Ctrl+T**(git pull→LoadFromDisk→Save And Generate Code·dev_festival上)使6个DK运行时生效+规范Path排序 ②ActvVoyage抽卡里子货币reskin(团队在做·非我) ③数值方案拍板后回填tsv(EG199-206/OtherReward/ProgressReward)+成就礼包Pack677。**结构+岛DK+岛i18n=本agent已交付·数值方案待拍板**。
- **★大富翁配置完备度审计(2026-06-24)**:✅已备份=ID分配(README)/岛屿数值(单等级EG tsv+删行delta)/阶段奖(按之前)/珍珠贝(保留)/成就礼包数值草稿v5/DK清单。⏳**gap**:①**存钱罐**=草稿已起(`存钱罐数值_配置草稿.md`)·**引擎=主表inline(用户2026-06-24定·投骰满10次敲碎Pack280001·不走资源储蓄罐PiggyBank表那套)**。Pack280001现$0.99占位(Content组100)需改。参考:资源储蓄罐超值18-42倍·礼包价小$19.99/大$99.99。v1提案=Pack280001 价$19.99·超值~20×·内容深海罗盘80+钻石30k+代币1k(待确认价格/超值倍/配比)。②成就礼包最终落表(钻石/VIP定后落ActvAchievePack+Pack行) ③i18n(6档Pack名+成就礼包/存钱罐/纪念卡Text) ④**货币里子=本agent做(用户2026-06-24"都你做")·已简化**:骰子1057/1058复用不做新·只建1202代币+1204珍珠贝(图齐·待clone item+DK入库+repoint·详见上"里子货币reskin"行)。

## ★深海BINGO=拼图ActvPuzzle(2026-06-23发现·12th模块·待配)
- **X3无独立Bingo表·BINGO机制=拼图ActvPuzzle**(5×5格·ActvPuzzleReward.Type 1=行/2=列/3=最终·连行列给奖=连线BINGO)·**ActvType18·纯换皮无程序**(已换27版1801-1827)。深海版**没配**(最新1827春节)。
- ★**拼图最终奖=纪念卡**(尼罗→尼罗回响/情人节→我对你的誓言/春节→新春特辑180078+信物+钻)→**深海拼图最终奖=纪念卡180080远航之歌**(本轮已配·闭环)。
- **封面落地链路**:DK_拼图(col3 PuzzleImg)/格子(col7)/背景框(col8)/活动bg(ActvOnline col22)/icon(col21)→`client/Assets/Res/UI/Spirits/ActivityImg/img_Activity_{主题}_*.png`→注册`Path_Activity.asset`(双列表)。
- **配深海拼图**(克隆1827):ActvPuzzle1828+ActvPuzzleReward组1028(11行克隆1027)+Reward最终新组(发180080)+行列奖复用603934+TaskGroup复用109+ActvOnline101828(CID1828/type18/组140)+i18n。美术5图待出。
- **★美术资源落地清单(接管入口)**:`KB\产出-本地化与美术\X3\深海节\12_拼图BINGO\拼图BINGO_美术资源落地清单.md`。

## ★深海节模块配置权威清单(2026-06-23·dev上全在·别再误报"没配")
**11模块+兑换+纪念卡 配置层基本齐活**(我2026-06-23反复把已配/原生复用误报成没配被批·教训:查"配没配"前必核ALL相关表+精确名+type码·别凭印象):
| 模块 | CID/AO | type | 备注 |
|---|---|---|---|
| 01转盘 | 1025/101025 | 10 | +排名Rank2000+传说铭牌82005 |
| 02 BP远航日志 | 2244/102244 | 22 | 旧值占位 |
| **03砰然心动**(每日礼包) | 2901/102901 | 29 | ⚠️名字是**砰**不是怦·组140空(待定是否归深海入口)·TC2901非0 |
| 04头像框 | Pack211019 | 黑猫式 | 无独立AO·框定义10080/框道具80100 |
| 05累充 | 598/100598 | 5 | 旧值占位 |
| 06装饰阶梯 | 700/**106103** | **63** | ✅已补活动壳(jolt#1181 SUCCESS)·曾漏建致不显示·见下"装饰礼包不显示根因";尾巴=ActvImg暂用deepsea_turntable_bg占位(无装饰专属bg DK) |
| 07海滨之约拜访 | 5606/105605 | 56 | 首批 |
| 08许愿池 | 5013/105013 | 50 | 首批 |
| 09远航酒馆 | 717/10071704 | 7 | 首批 |
| 10大富翁 | 2802/102802 | 28 | 程序配的航海之路成就礼包版·我补组140+顶部资源 |
| **11周卡** | 61001/109101 | 70 | ⚠️**原生复用**(自选周卡"周卡特惠"·4档自选6100101-104从Pack__WeeklyCard池2000-2007挑·7天·深海期iGame部署带上)·**不需深海专属新配·别当没配** |
| 兑换 | 1340/101340 | 13 | +纪念卡槽180080 |
| 纪念卡80 | Item180080 | | 远航之歌 |
- ⚠️**查周卡两张表**:`ActvWeeklyCard`(活动壳·只61001) + `Pack__WeeklyCard`(卡池1000-2007·自选源)。深海周卡=原生复用61001,不在这俩表新增深海行。
- **真正pending**:①i18n全16语言(新模块cn+en兜底·跑x3-translation-automatic) ②数值占位→真值(累充/BP世界杯旧值) ③merge损坏修复+我的jolt(见下) ④砰然心动102901是否归组140(待用户) ⑤大富翁里子货币(顶部资源改了表面·ActvVoyage抽卡掉落仍旧货币·另一agent)。

## ★转盘券礼包(2026-06-24·✅已建·用户拍板归我建)
- **机制(可复用)**:转盘"活动礼包"靠 **ActvOnline.col32(ChainPack)** 挂,**不是**ActvLuckyWheel.PackID(尼罗/深海都空)。ChainPack.col5=PackList(竖线分隔礼包id)。礼包内容(发的券)在 **Reward表·col2=RewardID=礼包id**(不是col1!col1是行id)·col4=item。转盘消耗券:尼罗1128女王恩典卷/深海**1200藏宝图**。
- **✅深海已建(commit 04df8fa·参尼罗ChainPack482全套克隆)**:Pack **211021-031**(6免费券+5付费$4.99/9.99/19.99/49.99/99.99·价格档复用105/107/111/116/115)+Reward **40122-40142**(21行·券1128→1200·钻石1002/VIP2022保留·数量照尼罗:免费1/5/10/20/50/100·付费20/40/80/200/400)+**ChainPack701**(活动豪礼·PackList=211021-031)+**101025.col32=701**。本地ExportTable验证中。
- ✅**i18n已补**:TXT_Pack_Name_211021-031(11礼包名16语言·6免费=免费礼包/Free Pack复用现成·5付费=深海礼包2-6/Abyssal Value Pack克隆尼罗之辉礼包2-6逐语言换词)。无Desc key(尼罗转盘礼包本就无)。手写直入tsv·未过GSheet评审(可后补)。jolt #1199已过(礼包/概率0.001%/HUD);i18n本地导表验证中→过即推+jolt。
- ⚠️**数值=照尼罗原样**(券量/钻石/VIP),如要按深海转盘经济调需跟做1200产出的agent对齐。
- **✅本轮已落地**:转盘bg重出(v2_2·client 1aa7d502d9d·KB 01_转盘/_落地说明)·累充bg重出(v2_1·05_累充/_落地说明)·ActvIcon全7个已核对(config/DK双补/美术都对·HUD页签若错=Editor没pull+reimport+生成DK,非配置bug)。

## ★酒馆/拜访/头像框 残留奖励reskin(2026-06-24·世界杯/情人节残留→深海)
深海多模块克隆自世界杯/情人节,**奖励/道具/任务有残留**,共同修法=换深海(藏宝图1200等)。已修+待定:
- **✅BP抽奖券+数值**:①道具(51be90c):BP组142 Reward块4344000-059 **245004夺宝游戏币(世界杯残留)** ×45→**1200藏宝图**。②数值(✅整套对齐情人节·option A):深海BP原是世界杯clone(高级藏宝图-only,删多余级会空组→导表报`depend_keys not existed`,因情人节那些级给别的道具不是空)。最终方案=**整套克隆情人节BP组135的60个reward组→深海4034xxx**(=情人节组id+3000·道具+数量+分布全一致),仅**邀请函1134→深海藏宝图1200**(33处)。组142重指20级:**按情人节同级引用+3000**指向克隆组(⚠️**别对深海自己旧引用4344xxx+3000**=4347xxx不存在,这是我踩的坑·必须读情人节135的level→引用再+3000)。藏宝图分布=情人节:免7级/高6级/尊20级=**137抽**。⚠️**Reward行连续性坑**:改藏宝图存在性要整组重写成末尾连续块,别中间插行(qty对齐版#1208已被本方案取代)。
- **✅拜访奖励**(两处都是1134一封情书·情人节·均与夏日5605共享→都建深海专属):①**邀请函奖**(commit 8aee855):2065→新**Reward组2067**(藏宝图×1)·5606.**c7**指2067。②**里程碑奖**(漏改后补):StageReward组5(ActvVisitPackReward·次数10/20/30/50→Reward组2066=情书)→新**StageReward组6**+新**Reward组2068**(藏宝图×5)·5606.**c4**指组6。夏日5605仍用2065/组5不动。**拜访奖励已全藏宝图**。
- **✅拜访邀请函道具(2026-06-24·别只改奖励忘了道具本身)**:拜访的**邀请函道具**(玩家每日领来拜访的item)原是5606.**c5=1137婚礼邀请函**(夏日/誓言残留),描述写"深海邀请函"但道具是婚礼的。各节日有专属(圣诞1121/尼罗1132/誓言1137/新春1141)。建深海专属:**Item1151深海邀请函**(克隆1141·desc=拜访【海滨假日】装扮酒馆·icon=`DK_icon_global_deepsea_invitation`✅已注册[guid d63efab5...·client `Assets/Res/UI/Spirits/ItemIcons/icon_global_deepsea_invitation.png`+Display_Item.asset+Path_Item.asset·client dev_festival已推]·c11 ItemObtain=100361)+**ItemObtain100361**(26深海-拜访礼包·c6=105605深海拜访AO·c7=`DK_img_Activity_deepsea_visit_icon`·c8=海滨假日)+5606.c5=1151+i18n4key16语言(深海酒馆装扮名=**海滨假日**Seaside Holiday·译名抄家具152017)。⚠️**ItemObtain列**:c6=拜访活动ActvOnline id/c7=图标/c8=装扮名;深海拜访AO=105605(CID=5606)。
- **✅头像框icon**(已推):211019 c26 尼罗`Egypt_icon_10`→深海`DK_Img_Player_AvatarFrame_deepsea`。⏳触发待定(用户要"跟装饰一样":加ChainPack700 or 独立装饰式活动)。
- **✅酒馆改藏宝图(方案A·建独立ScoreID·查表踩坑必看)**:酒馆奖励**不在**任务(ScoreMulti.c8)或排行榜(c9)·**在积分组**!链路=ScoreMulti.**c7积分组**→**ActvScoreGroup**(AimScore分档10000/30000/50000/70000)→**Reward组786031-034**→原**item1134一封情书(情人节)**(备注骗人写钻石/加速)。
  - ⚠️**ScoreID717跨节日共享**(元旦10071701/情人节10071702/春节10071703/深海10071704)·尼罗独立718→深海不能改共享786031-034。
  - **✅A已建(2026-06-24)**:深海独立 **ScoreID719**(克隆717的ScoreMulti7行→7191-7197·id+20)+**积分组7191-7197**(ActvScoreGroup克隆28行·id+200/组+20)+**Reward组786035-038**(藏宝图1200×1/2/3/4·同情人节)+**ActvOnline10071704 CID 717→719**。元旦/情人节/春节仍用717不动。
  - **教训**:积分活动(ActvScore)奖励查 **ScoreMulti.c7积分组→ActvScoreGroup.c4 Reward**·别把c8任务ID/c9排行榜ID当奖励。备注列(Reward.col5)常stale·认item id。跨节日共享ScoreID要改其一→建独立ScoreID(仿尼罗718)别动共享组。
  - **教训**:积分活动(ActvScore)奖励查 **ScoreMulti.c7积分组→ActvScoreGroup.c4 Reward**·别把c8任务ID/c9排行榜ID当奖励(我先查错浪费)。备注列(Reward.col5)常stale骗人·认item id。

## ★拜访礼包(海滨之约·AO105605/CID5606/type56)换皮未尽事项体检(2026-06-23·必看)
拜访模块是**夏日柔情海湾克隆体**,换皮只改表面文字,机制/美术多处留着夏日的。逐项:
| # | 项 | 现状(错) | 应为 | 状态 |
|---|---|---|---|---|
| 1 | ActvGroup140入口图标c4 | `icon_Monopoly_deepsea`(大富翁·错配) | `deepsea_hud_icon`(潜艇=节日入口图) | ✅**已改+提交+推**(dev_festival `6716183`) |
| 2 | 邀请函道具(ActvVisitPack5606 c5) | `1137`「婚礼邀请函」(情人节) | 深海专属(参尼罗1132·每节日各有) | ⚠️**item仍1137待建**·但**desc i18n已按「深海邀请函/Abyssal Invitation」补**(见#i18n)→**建item时名字必对齐此名**(EN=Abyssal Invitation/16语见Text_5606) |
| 3 | visit_bg(尺寸+构图) | 1152×2048满铺压UI | 540×960·主体上半+下半干净给UI | ✅**v2_2已落地client**(`8ee0a638b6f`)·KB`07_拜访\_落地说明.md` |
| 4 | 门头三件套(FurnitureSkin1001009/2001013/3001010) | 「海滨假日」=夏日沙滩套(复用·内部一致) | 主题非深海·换不换待用户 | ⚠️复用(未动) |
| 5 | 小图visit_pack(368×260) | RGB实底满框水下场景·无缎带 | 透明RGBA抠图+底部缎带(参尼罗Egypt_bg_20) | ✅**v2_2已落地client**(`8ee0a638b6f`,RGBA透明) |
| i18n | TXT_ActvVisitPack_DailyRewardDesc_5606(每日奖励说明) | 漏生成(夏日_5605有/深海无)→面板那段缺本地化 | 16语言齐 | ✅**已补+提交+推**(dev_festival `cb3db80`)·克隆5605换词·CN对齐配置种子·⚠️手写直入tsv**未过GSheet 2025Q4评审**(可后补) |
- **共同根因**:夏日克隆只换表面文字,邀请函/门头/奖励/背景尺寸全留夏日。
- **★出图铁律**:换皮出图前必扒同槽位参考图逐项比(格式/构图/尺寸/缎带)→[[workflow-x3-decoration-video]]置顶。深海拜访没比·出完进游戏一张张发现·耗麻用户。**兑换图同问题(2026-06-23用户又点)→同方案重出**。
- ⚠️此模块另一agent活跃改(feature共享)·动前对分工。

## ★装饰阶梯礼包"不显示"根因 + 显示机制(2026-06-23·feature/x3-deepsea-art·必看)
- **现象**:深海装饰礼包游戏内不出来。**根因=活动壳(ActvOnline)从没建**——ID分配总表把它写成`无独立AO·Pack直售`(判断有误)。实际装饰阶梯礼包**必须靠一条 ActvOnline 活动挂 ChainPack 才显示**(跟夏日106101一样),ChainPack700+Pack211016-018早配好但没活动壳→游戏内无入口。
- **显示链路(装饰阶梯礼包·参夏日106101)**:`ActvOnline(type=63·ContentID=col5=ChainPack id·ChainPack=col32=同id) → Pack__ChainPack(700·入口图col4/视频col9/挂Pack列表) → Pack×3(211016-018)`。ActvIcon=col22(HUD图标)·ActvImg=col23(活动背景)·ActvGroup=col39。
- **★ActvType=63(用户2026-06-23拍板·不是62)**:夏日106101历史用62,但装饰阶梯**正确type=63**(周卡63→70腾出的号·客户端按63路由装饰阶梯UI)。深海106103用63。
- **深海补的活动壳**:克隆夏日106101→**AO 106103**(ContentID/ChainPack=700·type=63·**TC=0**部署驱动·ActvGroup=140·ActvIcon=deepsea_hud_icon·ActvImg=deepsea_turntable_bg[占位·无装饰专属bg DK])。3个Pack逐字段diff夏日210917-919只差id/名/描述,余全同(TC/MainBg/奖励椰风遮阳椅151043都标准·别动)。视频DK_video_deepsea_decoration+入口图DK_img_Activity_deepsea_icon_decor客户端已注册。
- **★TC=0必须把type加导表SKIP**(否则导表报`时间控制器不能是0`):`PostProcessData.py:1656 SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE` 加 `ACTV_TYPE_DECORATION_LADDER=63`(随配置一起commit)。
- **★数据主体坑(我踩了)**:别给非玩家活动配玩家主体TC。**TC1830是"玩家主体"TC**(在PlayerUseCfgIdsSet),只有注册进ActvOnline meta`PlayerActivityIds`的活动(如转盘101025·带排行榜算玩家活动)才能骑;装饰活动跟夏日一样**非玩家活动**→骑1830报`数据主体不能是玩家`(PostProcessData:1796)。非玩家深海活动一律TC=0+type进SKIP(同兑换/拜访/许愿池)。
- **教训**:①导表报错先读、别甩锅"别人WIP/环境问题"(106103那条就是我的) ②查"配没配/能不能显示"必追到活动壳那层,Pack链齐≠能显示。

## ★DK双补状态 + HUD缺图backlog + 尼罗reskin对照(2026-06-23)
- **我这轮client DK现都Display+Path双补**(纪念卡80 icon/img·深海框·深海拼图封面)。★坑:深海拼图封面`DK_img_Activity_deepsea_puzzle`当初手编只进Path_Activity漏Display_Activity→会被Ctrl+T「生成dk」清(e255同源)→已补Display_Activity。**铁律:活动类DK手编Path_Activity后必补Display_Activity;Ctrl+T Save前先git pull**(见[[reference_x3_client_resources]])。
- **★9个深海DK still缺(美术没出+没入库·Unity报not found)**:HUD入口图标(124×136)=兑换/酒馆/拜访/许愿池/红包 deepsea icon + 大富翁icon_Monopoly_deepsea + 珍珠贝道具icon_Monopoly_pearl(大富翁那几个归美术agent)。转盘已有deepsea_hud_icon(但配置/客户端还引用旧名deepsea_turntable_icon→出图或改引用)。
- **★HUD图标参考库(归档·接管入口)**:`KB\产出-本地化与美术\X3\_HUD图标参考库\`(全节日HUD分组+尼罗Egypt全套分类→深海各活动reskin源对照+20张参考图)。**深海HUD reskin源对照(尼罗Egypt)**:累充←Egypt_icon_1/酒馆←_2/BP←_3/兑换←_4/许愿池←_6/转盘←_7(+总入口·已有)/拼图←_8/拜访←_11。

## ✅ 头像框黑猫式 已配(2026-06-23·feature/x3-deepsea-art·gdconfig cd3cf30 + client 7592208)
- **黑猫式礼包**(无独立ActvOnline·靠Pack的TimeCycle被活动带出):**Pack 211019**(克隆黑猫神龛210616·PackType=1+TriggerType=1+触发参数1col15=TC1830+触发检查col18=1+周期限购col20=1+入口有效期col26=1830+Content col13=Reward组211019+价格col7=107[$9.99])+**框定义PersonalizeAvatarFrameCfg 10080**(克隆Egypt10026·深海之冠·DK_资源col4=DK_Img_Player_AvatarFrame_deepsea·名字col9/来源col5走auto-key)+**框道具Item 80100**(克隆80000·Type9/UseEffect4头像框/UseParameter col8=`10080|-1`永久/DK20=框DK)+**Reward组211019**(发框道具80100×1)+Text7条。
- **★TC解法(用户2026-06-23拍板·黑猫pack需TC但深海全TC=0)**:**新建TimeCycle 1830「过期占位」**(克隆1825·开始时间计算方式col4=1绝对·开始时间col5=`2020-01-01 00:00:00`过去·靠iGame部署带上)→**挂到转盘AO101025的TimeController**(0→1830)→头像框pack骑同一个TC1830「跟着上」。★**坑**:转盘是server活动·**TC.数据主体col3必须=4服务器**(克隆1825来的=1玩家→导表报`数据主体不能是玩家`);1=玩家/2=奇观/3=天下大势/4=服务器。
- **★深海框DK入库(修了"没进包")**:深海框美术`深海头像框_选定.png`(256²RGBA)之前只在KB**没入库client**=DK不存在=没进包。补:拷png→`client/Assets/Res/UI/Spirits/Personalise/AvatarFrame/Img_Player_AvatarFrame_deepsea.png`+meta(克隆mermaid改guid)+注册`Path_Personalise.asset`(m_Keys列表+key/objPath对·两处·插mermaid后)。**框DK走Path_Personalise·Path-only(无Display)**。
- ⚠️数值=Egypt占位(框buff属性220010/150·到时候改)。

## ★本地导表快速迭代流程(2026-06-23用户拍板·jolt太慢)
**改tsv→tsv_to_xlsx派生→本地ExportTable验证修错(快)→打通了才push+jolt(最后一次)**。别用jolt来回试错。
- 本地ExportTable卡`verify_xlsx_tsv不同步abort`(新ExportTable没改这检查)→先派生xlsx:**用`~/.claude/skills/x3-config-export/scripts/derive_xlsx_from_changed_tsv.py`**(已固化复用·读git status所有改过tsv·base=HEAD·new=工作树·csv逻辑行喂tsv_to_xlsx手术·结构保留不openpyxl·从文件名推xlsx/sheet)→再`cd Tools/table_exporter && python ExportTable.py`(0异常=过)。脚本已存scratchpad可复用。
- **导表常见硬校验(本地秒抓)**:①Reward同RewardID组内**行id必须连续**(克隆多行组按组分配id别按文件顺序插花)②BP开启活动**满级lv20升级钻石col7不能空**(克隆139源是空·得填如1500)③ActvOnline server活动TC.数据主体≠玩家(=4服务器)④TC=0要ActvType在SKIP_TIMECYCLE_CHECK。

## ★merge损坏修复(2026-06-23·进行中·跨表LIVE config)
- **根因**:坏合并(`0f07698`合dev_festival→dev / `ac2e54f`)是**那台没装tsv3way driver的机器**干的→naive行级合并→blank列/删行/挪行。**driver防未来不修过去**。我这台已装driver(见下新工作流·重跑install_hooks.py确认)。
- **损坏面(已查)**:①**ActvOnline col2备注**:推币机/赛季6活动(109002/102241/102242/106501/106502/106503)tsv+xlsx**都空**→xlsx救不了·靠git史(但41bcbc4/5286315/ac2e54f等merge前commit都没找到109002备注·**待用户给好版本ref**) ②**ActvOnline col7 TimeController**:5个世界杯活动(101516开箱1513/100597累充597/101403签到1403/102240BP160002/101339兑换1339)tsv被blank=0·**xlsx留了好值**·★**用户2026-06-23定世界杯TC=0没问题→xlsx派生成0即可不恢复** ③**ActvOnline col38**:102240世界杯BP tsv=139/xlsx空→tsv对·xlsx派生成139 ④**MarqueeRuntips**:merge取festival侧(95行)·tsv+xlsx都变了·xlsx救不了·待git史 ⑤**配置顺序**:merge把现有活动挪到文件末尾·新工作流xlsx自动派生**不再受tsv_to_xlsx末尾追加限制·新行应插回id原位**(我之前都append末尾被用户批)。
- **我的深海round jolt卡在②③**(ActvOnline xlsx≠tsv)·解法=ActvOnline.xlsx按tsv重新派生(world cup col7→0/col38→139)→xlsx==tsv过·不碰备注/MarqueeRuntips/顺序(那些待用户给ref一起修)。

## ★新工作流(2026-06-22 changxiaoyun重构·必知)
- **tsv是唯一权威源·xlsx改成tsv→xlsx单向自动同步**。hook/Jenkins gate软化(只warn·exit0)。data/将来加.gitignore下线xlsx。
- **配置只改tsv·别手动碰xlsx**(用户2026-06-23明确)。pre-commit hook会`sync_xlsx_tsv --auto`自动生成xlsx。
- ⚠️**老分支(软化重构前branch的)仍带旧硬hook**→feature分支要先`git rebase origin/dev`拿到新软工作流再提交。rebase遇ActvOnline.xlsx二进制冲突=取一侧`--theirs`即可(xlsx自动派生·tsv权威)。
- ⚠️**jolt「X3导配置」要求gdconfig分支名==client(x3-project)分支名**(在client checkout同名分支做proto·找不到=exit-1 FAILURE)。深海统一用`feature/x3-deepsea-art`(两仓同名)。

## 累充/BP 模板(2026-06-22·数值用旧值克隆)
- **累充**:克隆世界杯100597→深海AO100598/CID598。**ActvTask** `ActvTask__ActvTask.tsv` CID597有10档(id59801-59810·TaskType902累充·col4阈值100/400/1000/2000..·col2=CID·col5额外参1=597·col8奖励RewardID=59801..)→克隆10档改CID597→598+新防撞id+额外参1=598;**Reward**克隆59801系奖励组(数值照旧);**白名单col49**=深海累充packs(没建·暂空或占位)。
- **BP**:克隆 BattlePassScore 2240(世界杯)→深海;BattlePassScore+BattlePassScoreReward(免/高/至尊三轨·★跨节日共享RewardID坑见[[reference_x3_config]]:克隆后改奖励要先克隆专属Reward块别动原节日)。AO102244(已撤批的壳)配全后再搬。

## 上线排期（2026-06-22 定·甘特已出）
- **7月档·按节日月度周期**：7/8(周三)部署灰度环境→7/9(周四)灰度D0→7/10(周五)全服D1→D1-D14到7/23。D50+老服。
- **活动内投放窗口**(全部7/9部署时一次配好·靠TimeController/iGame定时开·非分次部署)：D1(7/10)转盘/BP/每日礼包/头像框/累充/许愿池/酒馆 · D3(7/12)装饰阶梯 · D7(7/16)拜访 · **D8(7/17)大富翁+周卡(第二周depth核心)**。
- **⚠️与世界杯并行撞车(待用户拍板)**：世界杯运营到7/19,深海D1-D14(7/10-23)整段压其尾段→**两付费节日同台9天**;最尖锐=深海depth核心(大富翁+周卡D8=7/17)正面撞世界杯决赛周(7/18-19多实例高潮),抢同一批大R(深海主城皮肤≈$300 vs 世界杯开箱+足球宝贝皮肤≈$250)。三解:①错峰(深海延到7/21) ②**维持并行但大富翁+周卡推到7/20避开决赛周(我推荐)** ③接受重叠监控D8双活动ARPU互蚀。
- **关键路径风险=外部程序Jira**:头像框通用礼包模块(PackType待定)+大富翁(取消升级/成就/存钱罐/弹脸)卡程序,今起到7/8仅~12工作日→需向制作人确认两单能否7/4前交付,否则降级/砍出本期。
- **甘特HTML**:`KB\产出-数值设计\X3_7月排期_世界杯+深海节甘特.html`(两活动并到同一日历轴6/22-7/23·世界杯赛程锚策划案v0.22的6/28-7/19)。

## 当前进度 / 下一步
- ✅ 设计定稿(全模块+大富翁+周卡) · ✅ 对齐总览 · ✅ ID分配总表
- ✅ **美术换皮第一批(8张纯换皮背景/banner方向稿)已出**(2026-06-18)，详见下「美术换皮」段
- ⏳ 待做：B类纯配置 tsv 落地(依赖ID表) / C类程序(外部Jira) / i18n
- ⏳ 待做美术(非纯换皮·未做)：传说铭牌/史诗铭牌/深海头像框256²(🔧从零新出,有title/框格式锚) / 每日礼包15s视频(重制) / 转盘逐件外观+HUD icon / 大富翁24地块岛图+角色+弹脸特效 / 周卡三档卡面+banner
- 真源 tsv：`C:\x3\gdconfig\tsv\`（改tsv不碰xlsx，见 [[reference_x3_tsv_export_migration]]）

## 美术换皮（接管入口）
- **★详细清单看这份**：`C:\ADHD_agent\KB\产出-本地化与美术\X3\深海节\_深海节_换皮清单与复用说明.md`（复用投放物清单/模块换皮总表/复用资源三类/换皮三铁律/产物目录命名/工具链——换皮接手先读它，下面只留要点）。
- **✅ 深海活动bg已入库(2026-06-24·client dev_festival commit f18094c)·分两类**：① **透明banner(5张·540×500 RGBA下半透明)**=兑换/酒馆/BP/累充/许愿池;② **全屏背景(2张·540×960 RGB不透明)**=转盘/拜访(对齐尼罗Egypt_bg_10·**绝不透明**);③ visit_pack(368×260礼包小图·原图未改)。⚠️**两轮纠错沉淀**(见 [[X3活动HUD入口图标参考库]]「深海bg最终入库」):转盘/拜访不是banner不能做透明(已还原改动前版);透明蒙版要**上68%实心填满**(别太透);visit_bg(大背景540×960)≠visit_pack(礼包小图368×260)别混。
- **✅ 转盘界面"下半白带"修复(2026-06-24·commit 4063c9e)·假透明坑**：转盘界面背景**不走ActvOnline.ActvImg**，走另一张表 **`ActvLuckyWheel`**(`UIActvLuckyWheel.cs:133-135`)：col14 `DK_Turntable`=盘面/col15 `DK_TurntablePointer`=指针/**col16 `DK_BG`=底部背景图**(=`deepsea_bg_wheel` 1080×984)。**根因=`deepsea_bg_wheel`顶部40%被导出成白色不透明(alpha=255 RGB白)→盖住下层underwater ActvImg→界面中段一条白带**(用户报"下半空"、直觉"假透明"=对的)。修=顶部白区改回透明(只留珊瑚/石台·二值阈值sat>45保珊瑚·下半50%石台强制不透明)，对齐尼罗`Egypt_bg_11`的alpha剖面(上透明→渐入→底部石台不透明)。修复图`KB\...\深海节\01_转盘\img_Activity_deepsea_bg_wheel_FIXED.png`。详见 [[X3活动HUD入口图标参考库]]「转盘三层背景」。
- **✅ 拜访visit_bg重出(2026-06-24·commit 972b8e3)·门头+干净底板范式**：拜访(ActvType56)界面背景=`ActvOnline.ActvImg`=`deepsea_visit_bg`(540×960·`UIActvVisitPack.cs:115` SetActivityBaseInfo→mTFWImageBG)，**无独立底板DK**(pack图走另一字段ActvVisitPack.DKPackIcon→mTFWImagePackRewardBg=visit_pack 368×260)。**范式(查夏日VD_bg_13/尼罗Egypt_bg_7,二者最清晰)=上40%门头建筑浮岛(本期=海滨假日门头·热带小屋拱门+冲浪板+棕榈)+下60%干净渐变底板(UI奖励/按钮坐底板)**。原深海版下半是杂乱海洋底→重出成干净海蓝底板(GRFal·VD_bg_13当构图锚·cand0)。**visit_pack(368×260)用现成非透明版未动**(用户:pack用现在的非透明版即可)。重出脚本`scratchpad/gen_visit_bg.py`+FINAL`KB\...\07_海滨之约_拜访礼包\_入库FINAL\拜访活动背景_540x960_v2.png`。
- **产物目录**：根 `KB\产出-本地化与美术\X3\深海节\`，按模块分 `{编号}_{题材}_{功能}/`。文件名 `{功能}_选定/备选/版本n.png`；`复用_*`=从client拷入的现成投放物/贴图；`复用_{模块}_资源清单.txt`含3D原位路径。已出：01转盘bg(大/小潜艇**待挑定**)/02BP/03每日礼包/05累充/06装饰(banner+展示视频**已定稿**:vidu崩→改 **kling fflf** 重出·对标尼罗egypt格式标准化 810×1080,见下)/07拜访(背景+礼包图,真三件套)/09酒馆/04头像框(见下)。
- **06 装饰礼包展示视频（已定稿，2026-06-18）**：`装饰礼包展示视频.mp4`=banner氛围循环。**vidu 图生视频崩**(运动量47乱改画面+首尾差60不循环)→换 **kling fflf**(banner同图当首尾帧,首尾差2.3无缝/运动2~3只氛围动/忠实保banner)。**格式对标尼罗 egypt_sphinx**:810×1080(保banner原生3:4不裁·尼罗本身是9:16)/h264·yuv420p·24fps/-an去音轨/项目ffmpeg crf28→279KB。`_kling`=标准化前母片留底。recipe详见 [[reference_x3_hero_skin_video_production]]§一「不透明展示视频」。
- **★用户定调(覆盖美需表赛米拉锚)**：① 所有活动**背景一律不出现人物**(赛米拉立绘只作配色/主题参考不入画) ② 转盘核心主视觉=**深海猎手潜艇船皮**(非赛米拉)。
- **04 深海印记 头像框礼包（已出定稿，2026-06-18）**：两件 = ① `深海头像框_选定.png`（256² 透明，锚=client现有 mermaid 海洋框 restyle 深海；QA过=中心真透空/外圈透明，唯一小瑕疵内孔横向194略超标用户接受）② `头像框礼包弹窗背景_选定.png`（=v1，用户选；弹窗以**头像框本体当 hero 摆中心**、坐巨贝壳、下半渐隐留白）。⚠️**弹窗真格式=1016×980 RGBA**（详见 [[reference_x3_pack_panel_rendering]]「礼包弹窗背景标准格式」），现选定图是 gpt 出的 2048² RGB，**开配/DK入库前要降到 1016×980**。v1/v2 原图+头像框中间产物(`_v1_transparent`/`_v1b`)留底未清。**状态：美术定稿，待开配**（通用礼包模块需程序，banner槽位尺寸待程序定）。
- **04 配置备份表（草稿，2026-06-18）**：`KB\产出-数值设计\X3_深海节\配置备份表\04_深海印记_头像框礼包\`（KB配置备份=一个功能一个文件夹·非live tsv·依赖就绪后搬进tsv）。真ID分配:**框定义 PersonalizeAvatarFrameCfg=10076**(max10075+1,抄Egypt10026)+**道具 Item=80348**(max80347+1,抄Egypt框道具80110,param=`10076|-1`永久,DK_Bg_CM_Item4)+**Pack=211019**(Price档**107**=$9.99·已核PackPrice表/TC1830/BuyCount1)。头像框双表结构=框定义10xxx+Item80xxx包道具,见 [[reference_x3_cosmetic_resource_paths]]。**待补**:通用礼包模块需程序(PackType/Content写法)/头像框DK未入库/节日道具ID待建/Regained机制位置/MainBg是否自定义/i18n。
- **06 装饰阶梯礼包 配置备份表（草稿,2026-06-18,纯配置换皮无程序）**：同目录 `配置备份表\06_深海居所_装饰阶梯礼包\`(5文件)。复用夏日链整套 copy-swap：子包**211016/017/018**(抄210917-919,Price111=$19.99,PackType11/UIType5,Content=自身ID,限购1)+父**ChainPack677**(max676+1,PackList=211016\|017\|018,TC1830,**Video字段=展示视频挂点**夏日DK_video_summer_love_song→深海视频入库填这)+**PackTypeInfo211016**(tab,MallType9)+**Reward**(RewardID=子包ID,col0从25089续,每包椰风遮阳椅**151043**×1+抽奖券+钻石+VIP,DropPara必填10000)。⚠️**3处Icon**(ChainPack/PackTypeInfo/子包)易漏[[reference_x3_pack_tab_icon]];子包MainBg不显示(ChainPack prefab写死)[[reference_x3_pack_panel_rendering]]。待补:装饰icon+视频DK入库/节日抽奖券ID待建/**设计待确认:夏日3包3种不同家具vs深海写"每包同一椅"**/i18n。
- **★★转盘(ActvLuckyWheel)换皮继承坑清单（2026-06-23落地翻车补·克隆尼罗1023→深海必逐条换·同世界杯v0.37开箱继承坑）**：换皮只换了显眼的(背景/奖池)，漏了一堆"克隆继承的旧值"被用户骂"落地一坨"。必查：①ActvImg背景+ActvIcon HUD ②**col33 TopResource资源栏=`消耗券\|兑换币`(只配1201漏消耗券1200→玩家看不到券数)** ③ActvLuckyWheel.Item消耗道具(深海券1200) ④转盘皮3DK/RewardGroup奖池(深海专属321)/RankCfg(2000) ⑤**OtherRewardGroup阶段奖=必建深海新组发兑换币1201(别复用尼罗组号·内容是尼罗道具1001821-1827传奇手杖;深海建30920-26发1201递增)** ⑥**消耗券获取渠道(累充598 Reward发的券=克隆世界杯残留1146·必换1200;装饰211016-018已发1200)** ⑦券ItemObtain获取途径 ⑧col16残留名"尼罗之辉" ⑨**消耗/产出道具图标DK_Icon=克隆模板带的节日图残留**(深海1200抄情人节1134→DK_Icon`DK_icon_global_VD01`信封/1201抄1135→`VD02`玫瑰·漏换→游戏里券/宝珠显示情人节图=用户问"抽奖道具没出"真因)→必换Item.DK_Icon(col20)深海专属+出图 ⑩**背景尺寸别信memory预记·查模板ActvImg DK png实测**(转盘信memory"1080×1344"裁矮·实际尼罗Egypt_bg_10=540×960全屏)。**已修(2026-06-23)**:col33→`1200\|1201`、累充10档1146→1200、阶段奖3020→深海宝珠1201(新组30920-26·数量待核)、**消耗道具1200券→深海藏宝图(非券·世界杯券已占该概念·名+DK_Icon→`deepsea_treasuremap`+i18n·icon出图中)**、转盘背景重裁540×960。**转盘背景DK显示旧=客户端AB模式(盘面在旧AB/新turntable_bg没进AB)→切Editor模拟或重打AB,非配置**。
- **★分支状态(2026-06-23·用户切两仓到dev_festival·后续dev_festival干·不merge缺则重做)**：藏宝图/累充券/阶段奖/资源栏col33/i18n已合进dev_festival；feature最新2commit(宝珠1201图标+HUD统一5模块)**没赶上dev_festival那次merge→已在dev_festival直接重做**(宝珠DK_Icon→deepsea_orb·4d75d85;HUD兑换/转盘/拜访/许愿池/酒馆→hud_icon现8/8)。**教训:dev_festival merge feature=某时点快照,feature后续新commit不自动进→切dev_festival后必逐项核配置缺漏**。
- ✅**藏宝图+宝珠icon出图入库(client dev_festival·f0729708c16)**:藏宝图(航海卷轴·转盘消耗1200·deepsea_treasuremap)+宝珠(蓝漩涡·兑换币1201·deepsea_orb)·256透明·Path_Item+Display_Item双补。产物`01_深海罗盘..\深海藏宝图icon_256.png`/`深海宝珠icon_256.png`。**待重打AB/Reimport显示(feature新资源进包)**。⏳剩:阶段奖数量核。
- **01 转盘 配置备份表（草稿,2026-06-18,复用换皮·门槛提示需程序）**：同目录 `配置备份表\01_深海罗盘_转盘抽奖\`(5文件)。复用尼罗大转盘 copy-swap：**ActvOnline101025**(CID1025)+**ActvLuckyWheel1025**(RewardGroup=**321**/OtherRewardGroup=**3020**/转盘皮DK换深海)+**LuckyWheelReward Group321**(养成料复用·尼罗石币1129→深海代币待建)+**OtherReward Group3020**(进度x50~1500)。链路:ActvOnline→ContentID→ActvLuckyWheel(RewardGroup/OtherRewardGroup索引奖池,**不是按ContentID**)。✅**用户拍板(2026-06-18)**:转盘核心大奖=**深海猎手潜艇行军皮Item15065**(非海风旅者;奖池Group321已加SReward行32100权重10待核;海风旅者降级待定)。✅**节日代币已建**(见下_节日通用道具):**深海罗盘券1150**(转盘Consume)+**深海宝珠1151**(兑换币),奖池代币已换1151。⚠️余待确认:①新建1025vs原位1023(默认新建) ②05累充是否仍投同潜艇皮(避免与转盘重复) ③传说铭牌Title待建+出图 ④RankCfg186未配+门槛提示需程序 ⑤转盘皮/背景/道具图标DK入库 ⑥OtherReward的RewardID指向Reward表待按深海新建。
- **_节日通用道具 配置备份表（2026-06-18）**：`配置备份表\_节日通用道具\`。Type1计数货币,接112x-114x节日代币段(1143-1149被海妖转盘siren占,取1150+)。**1150深海罗盘券**(抄1134一封情书,转盘Consume/通用抽奖券)+**1151深海宝珠**(抄1135玫瑰花瓣,兑换商店货币/奖池产出)。喂:01转盘Consume+奖池✅/01兑换商店货币/11周卡奖池/04头像框·06装饰礼包节日道具——解了各处「节日道具待建」。待补:道具图标DK/获取渠道/数值/i18n。
- **01 传说铭牌「航者徽记」(2026-06-22,纯配置+美术+i18n,无程序·用户只要1个不做02史诗铭牌)**：配置备份 `配置备份表\01_传说铭牌_航者徽记\`(PlayerTitle_新增105.tsv + Text_新增105_i18n.tsv 16语言全译 + README)。**PlayerTitle表**(`PlayerTitle__PlayerTitle.tsv`,全表才35行)结构=`ID|Name|DK_Icon(头衔大图752×192)|PositionBuff(BUFF)|Reimburse(重复转钻100\|1000)|ObtainDesc|DK_SmallIcon(小图256²)|Quality(3=橙)|Order`;**新ID=105**(max104+1),**模板=104世界之巅**(传说·BUFF空·榜单获取=同款)。**用户定调铭牌无属性**→PositionBuff留空。i18n走`TXT_PlayerTitle_Name_105`+`_ObtainDesc_105`(16语言:cn3/en4/sp5/fr6/id7/de8/kr9/zh10/ru11/ua12/jp13/it14/pl15/po16/tr17/th18)。美术2张(大图reskin海皇nest_icon_title 752×192 + 小图reskin icon_global_nesticon_1 256²·锚+罗盘+浪花·金蓝传说·透明底)出图中→落 `01_深海罗盘_转盘抽奖+排行榜\传说铭牌_航者徽记_*`。待:美术挑定→透明化+裁尺寸→DK入库(`DK_deepsea_icon_title`+`DK_icon_global_deepseatitle`)→插表→过gate。**配置先备份·分支后续与深海节一起合并**。
- **08 许愿池 配置备份(2026-06-22,纯配置·仅换背景·无程序)**：`配置备份表\08_许愿池\`(ActvOnline_新增105013 + ActvWishingPool_新增5013 + README)。模板**105012**(26春节许愿池)→新**105013**(max+1);ActvOnline改CID5013/TC1830/GroupId140/ActvImg+ActvIcon深海DK;WishingPool5013复用奖励组(RewardGroup105/RewardGroup2103)+PackID1002001+Numble6,只换DK_PoolImg。⚠️深海许愿池背景美术**第一批漏了·待出**(全屏bg+水池图)+3DK入库。
- **09 最佳酒馆 配置备份(2026-06-22,纯配置·仅换背景·最简)**：`配置备份表\09_最佳酒馆\`(ActvOnline_新增10071704 + README)。**只一条ActvOnline行**:模板10071702为爱干杯→新10071704;**ContentID=717 + RankID=131 全系列共享复用**(最佳酒馆系列10071701/702/703都是CID717/Rank131,积分ActvScore一套不碰);改TC1830/GroupId140/ActvImg深海(美术已出)。⚠️别跟10071801蓝莲花宴(CID718另一套)混=ScoreID陷阱[[reference_x3_score_activity]]。
- **07 海滨之约拜访 配置备份(2026-06-22,复用换门头$99.99·无程序)**：`配置备份表\07_海滨之约_拜访礼包\`(4文件,核心三表骨架已配)。模板105603夏日柔情海湾→**AO105605/CID5606**(防撞已扫);ActvVisitPack5606(PackID=**门头礼包211020**/StageReward复用5/InvationItem暂1137);Pack211020($99.99抄210921,**MainBg必空**[[reference_x3_pack_panel_rendering]],Icon=拜访礼包图)。美术(拜访背景+礼包图)第一批已出真三件套。⛔**卡确认:门头礼包发哪个装扮道具**——夏日210921奖励发的是单个装扮道具81051(非设计案三件套ID 1001009/2001013/3001010),深海该发哪个海滨门头装扮8xxxx待查证/问策划,Reward211020内容留TODO。
- **★配置模板修正(2026-06-22·适用所有剩余配置模块)**：memory ID表/总览写的「夏日模板ID」部分**已被世界杯活动原地覆盖**(100597/102240现是世界杯累充/BP)。正确=在 **dev_festival** 按 **ActvType取最近同类节日行**当模板,新ID=该type现存**max+1**。实测真模板:许愿池Type50→105012 / 酒馆Type7→10071702为爱干杯 / 拜访Type56→105603夏日柔情海湾 / 兑换Type13→101337绽放之礼 / 转盘Type10→101023尼罗(已用)。02BP(Type22)/05累充(Type5)真模板待找(原槽被世界杯占)。
- **07门头道具已解(2026-06-22)**：设计案的1001009/2001013/3001010=**FurnitureSkin皮肤ID**(不可直接发);要发的解锁道具(Item Type9)=**152017横梁/152018地板/152019墙纸**(海滨假日,用后解锁对应皮肤)。夏日210921发的81051是「岛屿皮肤·柔情海湾」(另一种外显·标签串了)。深海门头礼包Reward211020=152017/18/19各×1+钻5万+VIP500(已配)。**追投放物链路必查Item表/FurnitureSkin表两层,别照抄夏日Reward字面ID**。
- **02 BP + 05 累充 配置备份(2026-06-22,按世界杯模板·用户同意·复用换奖励·数值待复盘)**：`配置备份表\02_远航日志_BP\`+`05_深海馈赠_累充\`(各ActvOnline+README)。⚠️**BP的ID撞了重分配**:memory ID表BP102242/CID2242现被夺宝通行证+世界杯通行证(102243/CID2242)占→重扫节日块取真free=**AO102244/CID2243**(模板世界杯通行证102243)。05累充**AO100598/CID598**(free·模板世界杯累充100597)。两者奖励数值待夏日复盘(BP复用210000系/累充10档ActvTask TaskType902);累充RechargePointPackWhitelist待填深海Pack块;✅**05顶档已定(用户拍板2026-06-22)=只投抽奖道具深海罗盘券1150·不投潜艇皮**(潜艇皮15065归01转盘大奖独占,消了重复)。02史诗铭牌不做(用户只要1铭牌)。
- **01 兑换商店 配置备份(2026-06-22,复用换皮)**：`配置备份表\01_深海罗盘_兑换商店\`(ActvOnline_新增101340 + ActvExchange_新增1340 15行 + README)。模板101337绽放之礼→AO101340/CID1340(free);ActvExchange抄1337的15行,**货币NeedItem 1135玫瑰花瓣→1151深海宝珠**,col0按1340xx惯例(134000-014),兑换品养成料/外显复用不变。
- **★防撞铁律(2026-06-22再次踩到)**:memory ID表/总览的预分配ID是2026-06-18快照,**世界杯/夺宝等并行活动后续会占槽**→每个模块落地前**必在dev_festival重扫该ActvType现存ID确认free**(BP就是没重扫差点撞102242)。按节日块取真free,不裸max+1(max常被离群ID带偏)。
- **★DK入库总清单(2026-06-22)**：`KB\产出-本地化与美术\X3\深海节\_深海节_DK入库清单.md`——全模块待入库DK逐条登记(DK名/对应图/尺寸/用在哪表字段/状态/入库前处理)。待美术挑定+HUD icon补齐后**一波统一入库**。⚠️10大富翁DK由另一agent负责不在此清单;11周卡已完成。
- **用户决策(2026-06-22)**：① 铭牌挑**v1=选定**(头衔标志+小图标·`_选定.png`,透明化+裁尺寸进DK清单批次) ② **03每日礼包走图片不做视频**(Pack.MainBg用弹窗背景图`每日礼包弹窗背景.png`,已出) ③ **兑换背景出图中**(深海宝藏集市,夏日兑换06当锚·无人物) ④ **10大富翁另一agent在做·本会话不碰** ⑤ 11周卡已配不改。
- **01转盘 3项更新(2026-06-22用户拍板)**：① **海风旅者英雄皮直接砍掉·只留潜艇**(奖池Group321已无海风旅者·全潜艇15065+深海宝珠+养成料;ActvOnline desc已改海风旅者→深海猎手潜艇) ② **★排行榜RankCfg修正**:memory的RankCfg186/RankType12错(186已被最佳酒馆占·RankType6/12的RankRewardSlotCfg都空)→转盘排行榜真模板=尼罗169(RankType6),已建**RankCfg1005**(max1004+1,抄169);**排名奖励走邮件**(NeedSendMailReward+MailID,不走slot表)→待建排名奖励邮件(传说铭牌Title105给Top段+养成档·档位+MailID待定);ActvLuckyWheel1025.ServerRank+ActvOnline101025.RankID应填1005(非186)。说明见`配置备份表\01_深海罗盘_转盘抽奖\RankCfg_排行榜_说明.md` ③ **转盘皮=3件DK**(尼罗1023实证):`DK_Turntable`盘面(Egypt_bg_12,1080×1344金框圆盘8扇格)/`DK_TurntablePointer`指针(Egypt_bg_13,112×188圣甲虫徽章)/`DK_BG`底台(Egypt_bg_11,1080×984)——非6icon;3件原图拷在`01_深海罗盘_转盘抽奖+排行榜\_转盘皮原资源_待确认\`待用户确认后reskin(逐件外观=转盘剩唯一大块美术)。
- **DK入库执行(2026-06-22)·6件透明DK已落仓注册+staged**：铭牌×2(DK_deepsea_icon_title→Path_Activity / DK_icon_global_deepseatitle→**Path_Item**)+HUD潜艇(DK_img_Activity_deepsea_hud_icon→Path_Activity,各模块ActvIcon共用)+转盘皮×3(DK_img_Activity_deepsea_turntable/_bg_wheel/_turntable_pointer→Path_Activity)。入库法=图进client/Res(文件名=DK去DK_)+抄同目录meta换guid+Path_*.asset单锚平行插再整体lower()重排(平行✓单调✓0丢键)+dev/Editor直读无需重打AB。详见 DK清单「入库执行状态」。⚠️**入库前处理**:gpt假棋盘格透明→PIL flood-fill扣连通灰白背景(保前景不穿洞)+裁目标尺寸。
- **★踩坑·x3-project commit 被 gdconfig 子模块钩子挡(2026-06-22)**：superproject 有钩子——**gdconfig 子模块有未提交改动时,阻止 x3-project commit**(报`uncommitted gdconfig content changes block x3-project commit`)。多agent并行时(我做client资源·他做gdconfig配置),client commit 会被对方gdconfig WIP 卡住。**不碰对方gdconfig改动**→ client文件staged等gdconfig干净再commit。我的DK入库14文件现staged待提。**✅已解(2026-06-22):用户拍板client先提→`git commit --no-verify`跳过该钩子(暂存集纯client/Assets·gdconfig未staged·不碰对方改动)→push dev_festival成功(commit 32b5da5b42e)**。即:多agent并行时client资源可--no-verify独立提(前提:确认暂存集无gdconfig)。
- **01转盘排名奖励 配置完成(2026-06-23·用户授权搞配置·live tsv `C:\x3\gdconfig`·dev)**：① 修转盘3处(AO101025.ActvImg→`DK_img_Activity_deepsea_turntable_bg`/ActvIcon→`DK_img_Activity_deepsea_hud_icon`/ActvLuckyWheel1025.ServerRank 169→**2000**) ② 建排名奖励:**Item82005 航者徽记头衔道具**(抄82004·Type9 UseEffect18 **UseParameter`105|-1`**永久·用后获Title105·铭牌就靠这种道具发,82001-04同理) + **8档Reward 30910-30917**(铭牌82005 Top3 + 深海宝珠1201 + 加速·镜像尼罗169梯度) + **RankRewardSlotCfg 8档(RankID=2000)**(1/2/3/4-5/6-10/11-20/21-50/51-100→30910-17) + RankCfg2000(NeedSendMailReward=1·MailID=1000018复用尼罗rank邮件·MailMaxRankNum3)。
  - **★排名奖励配置机制(通用)**：`RankRewardSlotCfg` 第2列名"RankType"实为 **RankID**(按名次档→RewardID);`RankCfg.NeedSendMailReward=1 + MailID` 走邮件发奖(设MailID必须NeedSend=1否则rankcfg_def报错);转盘本服榜=ActvLuckyWheel.ServerRank指RankCfg.ID。
- **★导表验证踩坑(2026-06-23·一串)**：① **csv.writer默认CRLF**→改tsv必转LF(`b.replace(b'\r\n',b'\n')`)否则verify报crlf abort ② **openpyxl重存xlsx污染同文件其他页签**(我直接改Rank.xlsx把mismatch 1→5·已git checkout还原·memory早警告过别再犯) ③ **sync_xlsx_tsv遇某表组xlsx/tsv双向都改且不一致→abort整个同步**(连累无关表同步不了);本地导表流程=`scripts/sync_xlsx_tsv.py`(改tsv后必跑·git变更检测)→`Tools/table_exporter/ExportTable.py`(先data逻辑校验·后verify_xlsx_tsv一致门)。
- **⛔当前卡点(2026-06-23·非我的问题)**：本地导表验证卡在**配置agent的ActvExchange冲突**(兑换1340纪念卡 xlsx=180080远航之歌/tsv=180077我对你的誓言·两边改不一·sync不敢猜→abort→我的Rank同步不上·verify mismatch=5)。我的转盘+排名tsv全对·数据逻辑校验已过。**待配置agent解ActvExchange纪念卡冲突→我再跑完整sync+导表验证→commit dev(都未commit)**。
- **★换皮三铁律**(详见清单§四)：① 双参考(老图=夏日/尼罗界面取构图框架·prompt明确ERASE旧配色UI + 新图=实际投放物) ② **投放物必须忠实入画**——卖具体物件的模块要把真实现成资源当主体陈列,禁止只喂贴图让模型自由再创作(拜访第一版画成海底金宫门=教训,已修;07现选定=真三件套陈列) ③ **礼包展示视频=动画化该模块已批准的方向稿,别套别人构图公式**(教训:把夏日"拱门框景"硬套装饰礼包被指背公式——拱门只适合卖门头/建筑的07拜访,装饰卖椅子直接animate批准banner即可;比例跟方向稿走,尼罗/夏日9:16仅供参考节奏不强制)。
- **复用资源不止icon**(详见清单§三)：家具类有 icon+贴图(Texter/Textures *.png)+3D(fbx/prefab/mat,留client原位拷出断引用,美术可直接Unity渲染);各模块文件夹归 `复用_*.png`+`复用_{模块}_资源清单.txt`。
- **工具链/踩坑**：x3-media异步派media-worker(图`general`+`gpt`/视频`general`+`vidu`+`image_to_video`)。坑:①绝对output_dir偶发当相对cwd→核对saved_to错位就mv回;②不覆盖同名、自增后缀→重出后手动cp成正式名+删落选。参 [[reference_x3_art_resource_spec]] + KB方法论 X3_AI出图工作流。

## 大富翁美术资源盘点（换皮接管入口·2026-06-18扒）
client 现成图全在 `C:\x3-project\client\Assets\Res\UI\Spirits\ActvVoyage\`（换皮=各图当格式锚）：
- **★可视化目录页(换皮先看这个)**：`KB\产出-本地化与美术\X3\深海节\10_大富翁\大富翁美术资源目录.html`(42张原图已拷入`_参考源_原航海之路\`+珍珠贝)。
- **地块图 island↔类型↔掉落(已核tsv真源 ActvVoyageIsland+ActvVoyageEvent Level=1,2026-06-22 终版)**：IslandType=1起始/2宝藏/3神秘/4钻石/5幸运。取消升级后只看Level=1的DKImg：
  - **island_4=起始岛**(EG99,灯塔)→掉「2个幸运/钻石岛奖励」。**用户定:改深海潜水艇包装**(潜艇/坞,呼应转盘潜艇)。
  - **island_1=钻石岛(EG100)+幸运岛(EG101船改/102加速/103英雄)共用**(光秃秃峭壁)。钻石掉钻石1002(500~3000);幸运掉养成料(船改55100/55101·加速11003-5·英雄)。⚠️幸运图问题已解=和钻石共用island_1,不用单出;但俩掉落不同,要不要视觉区分待用户定。
  - **island_2=宝藏岛**(EG104大/105小,金币+舵轮)→掉**海盗金币1060**(=兑换币,200~3000)。
  - **island_3=神秘岛**(EG106,主体+绿树丛)→随机(精准抽卡1058/海盗金币/后退·经验)。
  - **→取消升级后实际只需出4张岛图**(island_1/2/3/4),lv2-5不用。DKImg字段写在ActvVoyageEvent(值=DK名如`DK_img_Activity_icon_island_X`)。
- **★两种「贝/币」别混(用户2026-06-22问澄清)**：① **珍珠贝**=进度道具(棋盘捡4个开神秘宝箱,集齐计数器非货币),✅已出绿壳待落DK；② **兑换金币海盗金币1060**(`icon_Monopoly_currency`,宝藏/神秘掉,大富翁兑换商店101332货币)=真代币。**用户要新建的「深海代币」=②兑换金币的深海版,不是珍珠贝**(是否复用深海宝珠1151待定)。
- **★换皮逻辑(用户定2026-06-22)**：先改地图(`img_Activity_Monopoly_bg`俯视晴海→深海潜水视角·24格prefab写死不动·帆船可换潜艇;`navigation_bg_3`已是深海大贝壳可当色板锚)，再改岛：① 神秘岛只改周边环境**树林→珊瑚**(主体保留) ② 宝藏岛**加一个宝箱**(现成金宝箱`img_Activity_icon_chest`深海化) ③ 兑换金币→新深海代币(连`icon_Monopoly_currency`) ④ 钻石岛=光秃秃那个 ⑤ 起始岛改潜艇。
- **深海节大富翁新投放(vs原航海之路)**：主城皮肤「深海花园」≈300刀(最终大奖·现有皮肤不换皮) + 珍珠贝→神秘宝箱(新进度) + 成就礼包(跑15圈,搬X2) + 存钱罐(搬X2) + 新深海兑换代币(替1060)。
- **★岛屿终版出图方案(用户拍板2026-06-22·全换深海·不删任何岛)**：金币→新深海代币(纯换货币不删岛,放弃"删钻石岛"想法)。逐岛：起始岛=深海潜艇基地(ref island_4) / **钻石岛=♻️复用老高级图 island_2_lv5**(中央喷泉+蓝水晶·本就偏深海·不做新·只把EG100 Level=1 DKImg指到lv5) / 宝藏岛=陈列新代币(待代币出再出⏳) / 神秘岛=珊瑚+问号(ref island_3·原布局·符号换?·树林变珊瑚) / 幸运岛=珊瑚+深海宝箱(ref island_1+chest) / 地图底=深海潜水俯视(ref Monopoly_bg+navigation_bg_3·格子区留干净·可有小潜艇)。**2026-06-22已定稿5张(用户确认主变体)**:代币`大富翁_深海代币_256x256.png`(256²)+地图`大富翁_地图_深海_final.png`(540×960)+起始/神秘/幸运`..._final.png`(184×224),落`10_大富翁\`。宝藏岛(=代币岛·ref island_2金币岛+陈列新代币·EG104/105)出图中,待回来同样处理。⚠️**gpt"透明"=假透明(RGB画浅灰底)→必须GRFal remove_background扣真透明(单次)→本地PIL trim+按对应原图bbox位置/占比裁(底座对齐·不居中)**。原图布局基准(184×224):起始island_4=184×188上14下22/神秘island_3=178×151上53下20/幸运钻石island_1=168×127上71下26/钻石复用island_2_lv5=180×154上46下24/代币256²=175×177四边40。核验规则见[[reference_x3_art_resource_spec]]★出图后核验。**全8件已定稿**(代币/地图/起始/钻石复用/宝藏/神秘/幸运/珍珠贝v3_2[换掉无珍珠的旧版]),正式版`10_大富翁\_FINAL_正式版\`(8图+README·按岛号命名)。
- **★大富翁=纯换皮·布局不动(用户拍板2026-06-22从简)**。代码实现3层(查证):①**prefab写死位置**`Root/Animation/Middle/GridGroup/{1..24}`24格GameObject菱形环坐标全在prefab+地图底=独立BG Image节点(mTFWImageBG读活动ActvImg)+罗盘/角色/宝箱都是prefab固定节点;②**UIActvVoyage.cs:41-45只按path抓取**这24个填数据(不创建不定位),角色按index绕环走(GetActvVoyageModelRotation转朝向);③**GridItem.cs按DKImg渲染**单格(SetImageWithDisplayKey(mTFWImageImgIsland,DKImg))。→换岛样/地图=改配置DKImg/ActvImg(零代码零prefab);**只有改格子布局/数量才需动prefab(本期不做)**。ACTIVITY_VOYAGE_ISLAND_NUM=24(ActivityConst.cs:378)。这就是出图必须按原184×224尺寸/占比对齐的原因(prefab格子框写死)。
- **10 大富翁 配置备份(2026-06-22 v2·用户纠正=新建一套不复用原位)**：`配置备份表\10_大富翁\`(README+DK入库清单)。⚠️**推翻"复用2801原位+改1060"**→**整个活动新建一套+代币新建item**(不污染原航海之路·不改旧道具)。**新ID(已扫防撞)**:ContentID**2803**/AO**102803**/IslandGroup**2**/Island行**201-224**/EventGroup**199-206**/OtherRewardGroup**200**。换皮=克隆2801全套表(主表/Island×24/Event×N/OtherReward)改新ID+新深海DK(全新DK名不覆盖原·见DK入库清单)。**✅全部拍板(2026-06-22)**:新建4个item—代币**1152**(克隆1060)/深海罗盘普通骰**1153**(克隆1057)/珍珠贝**1154**(克隆1059·**走原神秘宝藏机制TreasureItemID·零程序**·进度条系统本期不做)/海神罗盘付费骰**1155**(克隆1058);**TC新建1833配0**(开始时间/计算方式=0·部署submit定起止·参考世界杯·不复用2702海域开放);**子活动全新建** 兑换**1341**(克隆金海浮市1332)/拼图**1810**(克隆美人鱼的梦境1809)/BP**2210**(克隆旅程记录册2209)。(1150/1151是转盘备份占的故代币取1152+)。**待程序(Jira)**:取消升级(钻石组200 Lv1指蓝水晶否则显示幸运图)/成就/存钱罐/弹脸/ROI=8。HUD icon+深海罗盘1153/海神罗盘1155道具图标+角色Spine 待美术。**✅GSheet「深海节-开发配置需求」已同步**(行17大富翁→2803新建/AO102803/TC1833 + 行29 TimeCycle大富翁→1833配0)。
- **主界面背景**(AI可出)：`img_Activity_Monopoly_bg`/`_1`/`_2`。**航海罗盘/骰子**：`img_Monopoly_compass_1~4`+`icon_Monopoly_compass_1/2`(海神罗盘=付费骰)。
- **图标**(AI可出·走双底差分透明)：`icon_Monopoly_currency`(海盗金币Item1060,弹脸特效也用它)/`icon_Monopoly_chest`(神秘宝箱)/入口`img_Activity_icon_Monopoly_6`。
- **AI出不了终稿**：角色模型 DKRoleMedel(阿米娜,Spine/3D,只能出概念)/海盗金币弹脸特效(Unity粒子序列帧)。珍珠贝图标✅已出·开箱动画✅复用。
- 管线分流：地块图/背景=gpt不透明场景图(同活动背景批)；图标类=transparify双底差分(ICON硬规则)。详见 [[reference_x3_voyage_art_chain]]。

## 其他模块待出美术(汇总)：铭牌×2(传说航者徽记01/史诗航徽02,752×192从零) · 深海头像框256²+礼包banner(04整模块未出) · **许愿池背景(08第一批漏了)** · 周卡三档卡面+banner+BUYALL(11) · ✅**怦然心动(03)已全干闭环(2026-06-24)**:克隆方向A新建**ActvOnline 102993**(进度礼包ActvType29·非动旧新手包102901)+ActvPack3002+Pack800005-809(全$4.99·ROI10)+Reward组40500/40600+TimeCycle**160100**(原160006撞dev已改·TC不能=0因ActvType29∈GIFT_TRIGGER强制要TC);5档全同(罗盘1057×10+藏宝图1200×20+钻石2500+VIP2500),买全部送藏宝图×100;16语言i18n全补;藏宝图弹窗背景DK入库(deepsea_schedule_bg 540×960·从3:4居中裁·双补);**jolt导表SUCCESS#1233**。不需要视频(无视频槽)。详见配置备份表`03_怦然心动_每日礼包\README`。**尾巴:HUD入口图标(ActvIcon)仍通用schedule图·深海专属待出**。 · 转盘逐件外观+HUD icon(01)

## 待确认(落地前点名,见ID表【8】)
1. 转盘新建CID1025 vs 原位改尼罗1023 2. 深海猎手归属(01排行榜 vs 05累充顶档两处都列) 3. 周卡是否需独立AO 4. 主TC1830起始日期 5. 成就礼包圈数+定价/累充档位数值/航迹皮肤ID/通行证礼包是否与BP高级档重复

参见 [[workflow_handover_assetization]] · [[reference_x3_voyage_art_chain]] · [[reference_x3_score_activity]]
