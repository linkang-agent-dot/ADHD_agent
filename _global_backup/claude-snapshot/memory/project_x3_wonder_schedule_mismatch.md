---
name: project-x3-wonder-schedule-mismatch
description: "X3奇观(巢穴研究/永恒之岛)排期错配案——X3NEW-792把岛挪到D30但D23锚点配套没跟,空跑结算全员并列第一;修复进度+遗留缺口101209"
metadata: 
  node_type: memory
  type: project
  originSessionId: e2f9dbeb-e282-4be0-8bb0-cf07f2db3546
  modified: 2026-07-24T08:09:47.469Z
---

# X3 奇观排期错配（巢穴研究提前发奖·全员第一名）

## ✅✅ 最终收口（2026-07-23 晚，决策反转后的真实终态）
下面「修复方案=IsOn=1+TC=0」是**过程态，已被推翻**。真实终态：
- ⏰**部署/热更时间 = 昨(07-23)~22:00**（不是 16:30，用户更正）→ 105501 消耗补偿截点应=22:00（我 CSV 初版用 16:30，漏算 2280-2310 的 16:30-22:00 段共 ~9M 金币/60人，只金币无钻石阅历，待修）。
- **105501 = IsOn=0 退休**（MR !158 待合，dev d62a890a/qa 45a40661 已同步）。**为什么反转**：数据丢失已在 ~22:00 部署时既成事实（见下），IsOn=1+TC=0「保配置防 purge」已无意义 → 用户拍板回退成标准 IsOn=0 退休（105501 已被 105502 替代），顺带甩掉导表器 type55 skip 依赖(留着无害)。prod 现状本就是 IsOn=0，此回退使 master 与 prod 一致。⚠️安全前提=无残留 105501 实例(2280-2350 已全 purge、其他服无 live)。
- **105502 = IsOn=1 + CloseServerList(2240-2330) 屏蔽双开**（MR !157 已合）。仍需 prod 热更 `ReloadGameServer` 重载 ActvOnline 生效。
- **双开实例(105502)清除 = 逐服 `ForceRemoveServerActivity <雪花activityId>` 强删**（非 GMRemoveServerActivityByCfgId——按 cfgId 对残留无效；机制/雪花来源见 [[reference_igame_gm_send]]）。实例存在服=105502窗口(服龄25-31)=**2240-2310(8服,各count=1)**；2320-2350没到D26无实例。prod GM 走审批→分两批(GMPrint拿雪花 opid3734-3741 / ForceRemove opid3742-3749)。8服105502雪花+opid存 scratchpad `champ_snowflakes.json`/`forceremove_opids.json`。CloseServerList 未上 prod 前，删完重启会被 TimeCycle 重建，屏蔽才治本。
- **数据补偿 = 邮件 mailId 4761341（待审待放行，554人）**：按逐人 105501 消耗退还（金币123M/阅历56.43M/钻石5.14M等），产物全在 `KB\产出-补发邮件\X3\20260723_冠军之路105501数据丢失补偿\`（CSV+content.json含"因技术原因下线"+审核单HTML）。**纯邮件补偿、不 GM 重开活动**。
  - **🔄补偿方案二次调整（2026-07-24 用户拍板）**：邮件 4761341（逐人精确补偿）**已发出**→改为**统一每人 15,000 钻($30)**，故需**先回收已发的精确补偿**。回收走 **DebtRecycle 表**（非 GM，GM 扣不到负数；机制/GM工具见 [[reference_igame_gm_send]]）：554 行(ID 1391001-1391554,VersionID=1,逐人 AssetList=各自4761341发放量,Arg1=0)→dev(35c8dbf9)/qa(623e75ea)/**master MR !160 待合**→jolt→prod热更→玩家登录扣回。统一补偿=邮件批量。
  - **✅进展(2026-07-24)**：①统一补偿定为**每人 2,000 钻($4)**(非15000),560人(全量参与者·非554),邮件 **mailId 4762127 待审**(含"回收此前补偿+致歉"文案,旧4762122已撤回作废);产物=`统一补偿2000钻_批量导入.csv`+`content_2000.json`。②**master 全就位**:MR!157(105502屏蔽)/!158(105501 IsOn=0)/!160(DebtRecycle回收554行) **全已合** + master jolt #2102 SUCCESS 导出,就差 prod 热更(gen_hotplugin gold+ReloadGameServer 重载 ActvOnline+DebtRecycle)。③**GM vs DebtRecycle 判定=查余额定案走DebtRecycle**:⚠️余额必用**快照表 `dl_active_user_asset_balance_d`**(ods_user_asset 的 balance 字段稀疏→假"无记录/不足",一度误判468/554不足)。准确:**多数够扣**(钻355/391、金币469/486、阅历375/378=90-99%),仅**123人有资产不足**(且多是美酒/金属/行动微量缺口;三大货币缺口金币261万/阅历122万/钻40万)。GM 能扣掉多数、少数不干净;**DebtRecycle 单配置全扣+不够记欠账兜住那123人→仍定用导表**(且已合master就绪)。④本地服3080验:**扣负数核心机制已证**(GMAddDebt日志:扣光余额+记欠账+未来抵扣),但 **config-read(ApplyConfig读表)本地没复现应用**(appliedCount=0,反常)→**prod热更后必须验回收真生效**(日志`DebtRecycleMgr.ApplyConfigToAllOnline count>0`或抽查玩家debt),否则回收落空玩家超补。⑤**🔄最终改用 GM 批量扣回、弃 DebtRecycle（2026-07-24 用户"直接GM扣吧"拍板）**：不走导表热更，改 `GMReduceItems` 逐人 prod 直扣，理由=避开本地 appliedCount=0 的不确定性 + 零导表环节；代价=**floor到0扣不到负数→写掉 813,318 钻值≈$1,627（123人扣不满）**，用户接受。扣回源=**已发补偿CSV**（严格等于发出去的，非重算数仓）→ 生成批次 `scratchpad/reclaim_gm_batch.json`（554条各 `1001,量;1008,量;1002,量;7001,量;...`）。floor账（快照余额算）:实扣≈93%(11.65M钻值)/写掉7%。**金丝雀双路径验通**:op3750扣1金币(res路径)+op3751扣1英雄美酒(item/storage路径)到自己号1930/1730557,用户确认"扣上了"。**正式批次554条 prod 发送中**(工具 `~/.claude/skills/igame-gm-send/scripts/batch_reduce_items.py --env prod`,op id存 `scratchpad/reclaim_ops.json`)。⚠️**554条各一个 prod 待审单,需 iGame 逐条/批量放行才真扣**;放行后逐条 `gm-operate/detail` 抽查 errCode0。⑥**🔄再修正为「GM+DebtRecycle 混合」，不是纯GM（2026-07-24 用户"debt按剩余数量写一版"）**：GM 扣主体(能扣的93%,扣到0)，**DebtRecycle 只兜 GM 扣不满的缺口**(123人·缺口=应扣−当前余额)→全额追回、不写掉$1,627、不双扣。故 DebtRecycle 表从「554全额行」**改写为「123缺口行」**(ID1391001~1391123,VersionID=1,AssetList=各自缺口;缺口合计=钻396,195/金币2,613,546/阅历1,219,358/美酒92/金属661/行动525,与写掉账一致)。生成器已产 `scratchpad/debt_shortfall_rows.tsv`(123行,格式合规)。**🔴硬顺序约束(违反=少扣)：必须先放行+执行554条GM(op3752-4305)把余额扣到0，再 prod 热更这版DebtRecycle**；反了(debt先于GM应用)debt会从未被GM扣的余额里扣、GM再扣已到0→总扣回<应扣。**554全额行(!160已合master/origin dev·qa·master均598行)需替换为123缺口行**:dev提交→qa→master(MR,如!160路径)→jolt。⚠️本地dev旧(仍44行·无554),动前先同步 origin/dev。GMReduceItems res+item通吃机制/工具见 [[reference_igame_gm_send]]。⑦**缺口版已全推(2026-07-24)**:dev f80dec36 / qa 073678c2 直推、master **MR !163 待合**(分支 debtrecycle-shortfall-master),三分支文件哈希一致 ea09bcb(44表头+123缺口行)。**qa jolt #2110 SUCCESS**(缺口版prod路径干净导出,`转换合并 DebtRecycle表 共123条`)。⚠️**dev jolt #2108 FAILURE=无关的预存坑**:`ActvOnline TimeCycleID不存在 timeCycleId:625 activityIds:{105502}`——dev 上 105502 指了 dev 不存在的 TC625(wangjuanhan 海妖机甲 X3NEW-2194 的 TC624/625 分叉遗留),**非本次DebtRecycle改动**(我只碰 DebtRecycle__DebtRecycle.tsv,该表123条已成功导出);dev 因此导不出表,需 wangjuanhan 修 dev 的 105502→TC 引用。qa/master 用 TC624(存在)不踩此坑。⑧**554 GM 已放行执行完(2026-07-24)**:op3752-4305 抽样12条全 errCode0、真扣(金丝雀3750金币115→114/3751美酒22→21;正式批各服真降),floor 行为符合(无货资产`removeNum:0`留DebtRecycle兜)。**硬顺序前置(GM扣到0)已满足**→可进 MR!163 合→master jolt→prod 热更缺口 DebtRecycle。核验法/全量脚本见 [[reference_igame_gm_send]]。⑨**缺口版按GM实扣量重算123→113(2026-07-24)**:快照缺口偏大(会多扣~10万钻),用554条 `gm-operate/detail` 逐玩家实扣量重算真实剩余缺口(应扣−GM实扣)=**113人**(比快照少10人=那10人余额涨了被GM全扣)。真实剩余 钻291,550/金币2,375,604/阅历1,204,858/美酒96/金属579/行动415。dev bbd252a7/qa 4b5a2f01 已推113版(文件哈希e49eb519)。数据:`scratchpad/reclaim_actual_deducted.json`(每玩家实扣)+重算器inline。⚠️**MR!163(123偏大版·sha1d01d2ba)已被approver合进master(15:13)**→master暂为123偏大版(167行);**prod尚未热更(无玩家影响)**,已开**MR!164(113实扣版→master)纠正**,合!164后再热更才不多扣。**剩余待办**:合MR!164 / master jolt / prod热更(ActvOnline+DebtRecycle) / 邮件4762127(2000钻×560)放行 / 热更后验 `DebtRecycleMgr.ApplyConfigToAllOnline count>0`+抽查debt。
  - **补偿钻石价值拉通（2026-07-24，口径 500钻=$1）**：道具→钻石单价查 X3道具价值表 GSheet `1gOCYBTtnxUiviDNiGwIX1vMAGRgQIyv76Nmd7ngBDF0`「道具表」(列=Name/ID/钻石价值)：**金币1001=0.04 / 冒险阅历1008=0.03 / 钻石1002=1 / 英雄美酒7001=3000(贵!237个折71万钻别漏) / 金属55101·行动次数57003=无估值略去**。拉通=钻石5.14M+金币4.92M+阅历1.69M+美酒0.71M=**12.46M 钻 ≈ $24,928**；单人平均22,498钻($45)/中位13,700钻($27)/最高632,700钻($1,265);554人,主体(344)在5k-2w钻。⚠️此为16:30截点值,22:00截点+~36万钻(+$720)量级不变。
- ⚠️导表机今晚多次 jolt FAILURE 皆 **infra**（robot 竞态 / client_master `.git/index.lock` 残留），非配置——重跑即过，别赖到改动上。

## 🔴🔴 下游二次事故：冠军之路排期迁移用错「下线姿势」→ IsOn=0 清实例(丢数据) + 跨服龄双开（2026-07-23，上线 master 后暴露）
排期修复用「只增不改」把冠军之路 105501(TC619,D22开7天,活跃**age21–27**)**改 IsOn=0** 下线、新建 105502(TC624,D26开7天,活跃**age25–31**)。今天合入 master+部署后 leader 服「老的刚结束、新的又开」。**表层是双开，真根因是下线姿势用错**：
- **★真根因（用户 2026-07-23 点破，已核实代码）：下线用 `IsOn=0` 而非 `TC=0`，会清掉现有实例=丢数据。**
  - `IsOn` 是**导表阶段过滤列**（生成的 `client/.../CfgProtos/ActvOnline.cs` 里根本没这个字段；tsv col7=bool）→ IsOn=0 的行**不导入配置** → 运行时 `CActvOnline.I(105501)` **返回 null**。
  - `ActivityMgr.OnLoadActivity`(ActivityMgr.cs:963-967) 在**服启动 `LoadAllEntitiesAsync` 全量 load 实例**时，遇 `cfg==null` 就把该 ServerActivity 加进 `mRemoveActivityIds`→`DeleteActivity`（日志「cfgId is off, remove activityId」）。→ **跑过/在跑老活动的服一重启，105501 实例被当"配置没了"删掉，玩家名次/结算/奖励丢失**。
  - **purge 只在重启(OnLoadActivity)触发，配置热更本身不触发**（其它 `cfg==null` 处 274/695 只 continue/return 不删）。→ **没重启过的服，105501 实例还在内存+Mongo，可救**。
  - ✅**正确迁移姿势=老 `IsOn=1` 保留 + `TimeController(TC)=0`**（配置行在→cfg 非 null→实例不被清、照常结算；TC=0→无触发不再开新实例）。对齐船只手册迁移范式「老TC=0」。**通用铁律见下游 [[reference_x3_timecycle]]。**
- **✅修复方案已落地并验证（2026-07-23）**：改动=**两文件配套**（缺一不可）：① `tsv/ActvOnline__ActvOnline.tsv` 105501 `IsOn 0→1`+`TimeController 619→0`；② `Tools/table_exporter/PostProcessData.py` 把 `ACTV_TYPE_HERO_CHAMPION_ROAD`(55) 加进 `SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE`（否则 TC=0 卡导表校验 :1804，详见 [[reference_x3_timecycle]] 铁律）。
  - **本地服 3080 实测通过**：修复版导表 exit0→cp bytes+manifest→ReloadGameServer→GMAdd 105501 从`1017001`变`created`（证 IsOn=1 让 cfg 回来）→**重启后 105501 实例存活、日志无 is off、仍 1 条(TC=0 不重开)**；同一次重启里 **IsOn=0 的活动(101027/101028/103101/108201)被 `OnLoadActivity: cfgId X is off, remove` 清掉=根因活体复现**（同框对照铁证）。
  - **三分支同步状态**：dev(a35aff7a)✅ **jolt #2077 SUCCESS** / qa(69ef89e4)✅ **jolt SUCCESS** / **master MR !155 ✅已合入(2026-07-23)** — 105501 修复已上 master。
  - **prod 热更（救没重启的服，时间敏感）依赖链**：MR!155 merge→master jolt导表 SUCCESS→`server/scripts/gen_hotplugin_x3.py --env gold --apply`取 Game script_md5→iGame gold 工具箱 `ReloadGameServer`(先单服后 allServer，见 E:\333\服务器_服务器热更_igame实操.md)。热更下的是修复版 bytes→ReloadGameServer 不触发 purge(实测)、能救没重启过的服；已重启过实例已删的救不回。
  - ℹ️**jolt导表机脏树 blocker（已消解）**：dev jolt 首次 #2073 FAILURE 根因=导表机 `git checkout dev` 被 `client/UIHelper.*.cs` 未提交改动 abort（**非配置问题**）；重跑 #2077 已 SUCCESS（脏树被清），qa 亦 SUCCESS。若 master 导表再遇同类 abort=导表机脏树复发，非本改动问题。
- **动手前必查 prod 运行时（本次兼容没测透的补课）**：①受影响服自 07-23 部署后有没有重启过 ②105501/105502 实例现在在不在 `ServerActivity`（含 leader 台,age25-26 老活动本不该"结束",没了=已被 purge=已重启）。查法=prod Mongo ServerActivity filter cfgId 105501/105502。⚠️prod Mongo 访问通道待确认(memory 只跑通过 beta)。
- **双开(105502)是另一条线**：修好 105501 后，跑过老的服会保住老实例，但 105502 仍在其身上多开一轮。**优先级：先热更止损 105501，再处理 105502 双开。**
- **✅105502 双开处置=CloseServerList 屏蔽 + GM 下线（2026-07-23，用户拍板）**：
  - **配置屏蔽（防未来重开/重建）**：给 105502 配 `CloseServerList`=`2240\|2250\|2260\|2270\|2280\|2290\|2300\|2310\|2320\|2330`（管道分隔服号列表，非区间）。运行时 `ActivityMgr.CreateNewServerActivity`(:817-833) 非 ark 创建时 `CloseServerList.Contains(本服)→return null` 不开；对**单服 TimeCycle 自动开生效**、ark 手动部署不受限。**列定位**：ActvOnline tsv **物理 col37=OpenServerList(白名单,只在这些开·别放错!) / col38=CloseServerList(黑名单) / col39=GroupId**（tsv_edit 0-index 分别 36/37/38；生成代码反序列化序 Open→Close→Group 定性，KVK 102001 col37=`1170\|1270\|1310` 印证）。**导表不拦**（「必须为空」校验仅对 `ACTV_TYPE_KVK_REVIVE_SOLDIER`=type23，非本 type55；无需再改导表脚本）。改动 commit=3e2fb3f7，走 dev→qa→新 MR(≠!155,!155已合)。
  - **GM 下线（清已开出的现有实例，CloseServerList 只防未来不删现有）**：已开的 8 台 **2240-2310** 逐服 `GMRemoveServerActivityByCfgId 105502`（iGame prod operateType=3 内层 `{"serverIds":"2240","cmd":"GMRemoveServerActivityByCfgId","args":["105502"]}`，服务器级不带 playerIds，查 detail 出 `removed N/N`）。2320/2330 没开出实例不用 GM（CloseServerList 拦其 D26 不开）。
  - ⚠️**顺序**：先让 CloseServerList 上 prod（防重建）→ 再 GM 下线；否则单下线后遇重启被 TimeCycle 重建。2340/2350(age21)未跑老→单开正确→**不屏蔽**。
  - **同步状态(2026-07-23)**：dev(b9c5a31e)/qa(c1513566) 已推，**master 新 MR !157 待合**(≠已合的!155)。GM 下线命令 TXT=`C:\Users\linkang\冠军之路105502下线_GM命令.txt`(8服 iGame JSON+核实+顺序铁律)。
  - 🔴**跨分支 TimeController 编号分叉坑(碰105502必看)**：105502 的 TC **dev=625 / qa/master=624**，两边都指"冠军之路新排期D26"——因 **dev 的 TC624 被海妖机甲推关(X3NEW-2194 wangjuanhan)占用**，冠军路在 dev 被 renumber 到 625。**别跨分支假设同 TC 号**；cherry-pick 靠 tsv3way 各自保留本分支 TC 号（我的 CloseServerList 改只碰 col38，TC 不动，所以三分支各自 TC 都对）。**dev jolt 一度报「TimeCycleID不存在 625」= robot 回写瞬时竞态（#2082 FAILURE→#2085 重跑 SUCCESS，TC625 本身没问题）**，非本 CloseServerList 改动；qa/master 的 624 有效、导表正常，prod 走 master 不受影响。
  - 🔴🔴**遗留真隐患（知会 wangjuanhan）**：dev `TC624=海妖机甲推关`(X3NEW-2194,wangjuanhan,commit 9e973b4c) vs qa/master `TC624=冠军之路`——**同一 TC624 号两分支是不同活动**。海妖机甲往 qa/master 发版时 TC624 会跟冠军之路**撞号**（冲突/静默覆盖），海妖机甲须改用别的空 TC 号。此分叉是 dev 冠军路被挤到 625 的根。
  - **MR 合并**：!155(105501)+!157(105502) 均由 changxiaoyun 于 2026-07-23 合入 master。
- **🔴数据确实丢了（2026-07-23 定案，deploy=今天16:00）**：IsOn=0 是**今天下午 16:00 才部署到 prod**（不是 06:02 合 master 即生效），部署即触发 purge。**服归类必须按服龄周期反推、不靠数仓**（reason_id `item_op_activity_hero_champion_road_item_cost` **105501/105502 共用拆不开**）：
  - 105501(老TC619)窗=服龄21-27；105502(新TC624/625)窗=服龄25-31；按部署时刻服龄分：
    - **跑5501·16:00被清·丢数据 = 服龄21-27 = `2280 2290 2300 2310 2320 2330 2340 2350`(8服)**（其中2320-2350纯5501；2280-2310是5501被清+5502双开重叠区）
    - **纯5502·没丢（老活动早结算）= 服龄28-31 = `2240 2250 2260 2270`**
  - **数仓印证**（非判据）：这8服105501消耗**今天16:00戛然而止**（小时级created_at），2240-2270只有16:00后消耗(=纯105502)。⚠️**按天粒度会看漏16:00断点**（我一度误判"没丢"）——查purge必用小时级。
  - **算5501损失消耗**：排除今天16:00之后的消耗（那是105502）；即 07-13~今天16:00 前 = 纯105501。
- **⏳待办：数据恢复补偿（丢了就重开补资源）**：
  - **判据（缩小范围）**：purge 只在**重启**(OnLoadActivity)发生、**配置热更(ReloadTable)不删实例**（实测）→ 只有「105501 IsOn=0 在 prod runtime 期间 + 该服重启过」才真丢；纯热更吃到 IsOn=0 的服实例只是 cfg 变 null 没删=数据还在，热更修复(IsOn=1)即恢复。正式服少重启→真丢的大概率少数/无。
  - **at-risk 服（有 105501 数据可丢）**=服龄 21-27（老 TC619 活跃期）=**2280 2290 2300 2310 2320 2330 2340 2350**；age28+ 老活动已结算完不受影响。
  - **核查缺 prod Mongo**：脚本只有 beta 连接串(`x3-beta-nlb.a3games.com:27017`)，**prod/gold Mongo 通道未知**→要么找运维要 prod 只读 Mongo/重启日志，要么走**数仓兜底**（查这批服冠军之路排名结算邮件有没有在预期时点发；没发=purge 在结算前=真丢要补）。
  - **恢复动作**：丢了的服 GM 重开 105501（`GMAddServerActivityByCfgId 105501 <分钟>`，注意它现 TC=0 但 GM 带显式时长可开）+ 按排名补发结算奖励（走 iGame 批量补发 [[reference_x3_igame_mail_import]]）。
  - **✅已解析玩家消耗资产（补偿依据，2026-07-23 数仓）**：reason_id=`item_op_activity_hero_champion_road_item_cost` change_type='2'（查法+道具速查见 [[reference_x3_datain_asset_query]]「查某活动玩家消耗资产」段）。8 服(2280-2350)07-13起 **556 参与玩家**，消耗合计：金币1001≈1.28亿 / 冒险阅历1008(=英雄经验)≈5643万 / **钻石1002≈514万(391人·人均13,146,鲸线2290人均24.7k·地板5000=一次冠军秘籍溢价选项)** / 金属55101≈2400 / 7001·57003零星。消耗随服龄递减(2280/2290重·2340/2350仅几千金币)。⚠️**这是已成功扣费的账，与是否purge无关**；真补偿要**按 user_id 逐人退实际消耗**(拉逐人清单喂 iGame 批量补发)，别用人均一刀切。**逐人清单待确认丢数据的服后再拉**(prod Mongo/重启那步)。
  - **prod GM 只读探针受阻**：想用 iGame prod `GMPrintServerActivityByCfgId` 直查实例，但 **prod webgw-cn 的 gm-operate operateType=3 路由格式与 dev/beta 不同**（add 收单 id 但 detail serverId/playerId/returnInfo 全 null=没路由执行；send_gm.py 只在 dev/beta 验过）。要解=在 iGame prod UI 真点一次 GM→F12 Copy as cURL 拿 prod 正确 body 格式。
- 双开机制（表层）：endTime 是绝对值(open+32d)，截图剩余天数可反推服龄(6D15h→open+32d≈07-29→开服06-27/28→age25–26)。不是同服重复实例(那是 [[reference_x3_server_activity_duplicate]] 的 no-dedup)。
- **判受影响服 = 服龄带交集**：`老已开(age≥老offset)` ∩ `新在窗(age∈新窗口)`。2026-07-23 实测(数仓 [[reference_x3_server_coverage_query]] 服龄SQL)：
  - 🔴正在双开(age25–31,开服06-22~06-28)：**2240 2250 2260 2270 2280 2290 2300 2310**
  - ⚠️1–4天内将双开(age21–24,开服06-30~07-02)：**2320 2330**(age23,已跑老)+边界 **2340 2350**(age21,老今天才到点待确认)
  - ✅不涉及：≥2360(age≤19,老关闭时没到D22→单开=本意) / ≤2230(age≥33,新窗口已过 Init 不再建)
- **处置**（GM 命令已核实，2026-07-23）：冠军之路 **ActvType=55=TRIGGER_TYPE_HERO_CHAMPION_ROAD，在 `SingleServerActivityTypes`**（不在跨服集/Center托管集）→ 纯单服本地直删。逐服执行 GM：**`GMRemoveServerActivityByCfgId 105502`**（这才是注册的 GMHandler 名,自动识别个人/服务器/跨服;服务器级内部转 `GMTakedownServerOrCrossActivityByCfgIdAsync`→`ForceEndAndDeleteServerActivity`=先广播 OnSeaAreaActivityEnd 通知在线玩家撤界面再删,不残留)。**服务器级下线不带 playerIds**;iGame gm-operate/add(operateType=3)内层=`{"serverIds":"2240","cmd":"GMRemoveServerActivityByCfgId","args":["105502"]}`逐服换 serverIds;核实查 `gm-operate/detail?id=<opid>` returnInfo 出 `removed N/N`。⚠️三坑：①**只对已开出实例的服有效**——未到 D26 的服(2320/2330/2340/2350)现在下返 `no server activity found`,等各自 D26 再下；②正式服走 prod 通道 `webgw-cn.tap4fun.com`+prod token(`.igame-auth.json` systemId=101,到09-06)——**`send_gm.py` 只支持 dev/beta 没 prod endpoint**,prod 要手拼调用或给脚本加 prod；③**TC624 仍 IsOn=1**,服龄仍在 25–31 窗内的服维护重启会被 `Init` 重建 → 盯这几天或配 per-server 屏蔽。
- **通用规律(排期迁移必查)**：用「只增不改」改活动**开启时机**时，除了配对锚点(见下"排期配对锚点审计法")，还要查**老活动关闭时点 vs 新窗口的服龄交集**——若「老关前已有服开过」且「新窗口覆盖同批服」→ 必双开。迁移前先跑服龄SQL圈出交集带，随配置一起给运营预备 takedown 清单，别等上线后 leader 撞见。

**🚀接管摘要**：X3NEW-792(06-03)把 3 级奇观永恒之岛首次报名 TC10301 从 20d→29d（天下大势 V2 阶段 357 世界主宰 D30 解锁），但挂老争夺日 D23 锚点的配套排期没同步 → 结算类活动在岛开放前空跑结算，**全员 0 分/同分 → RankDetail.viewRank 并列名次 → 人人第 1 名邮件**。完整审计+甘特图=`KB\产出-数值设计\X3_奇观排期错配\X3奇观排期错配_巢穴研究提前发奖审计_20260721.html`（唯一入口）。

## 修复状态（2026-07-21 深夜批次后：dev/dev_festival 双线除 11000 外全修完）
- ✅ dev 收尾 commit `fd69ae8d`（jolt #1989 SUCCESS）：101209→101213（新 TC1213 第10周周二/21d循环，旧行 IsOn=0，Text 补键）+ 展示/商店 5 条（2007/9000/10601→32d；9001→第8周周一 TT6；9002→第11周周一 TT6；2008 仅注释）
- ✅ dev_festival 全家桶同步 commit `f6709852`：5 新 TC(608/624/1211/1212/1213)+5 新 AO(克隆 festival 原生行仅换 TC)+5 旧行 IsOn=0+10501→32d+展示商店类+Text 键。**跨分支同步手法=克隆本分支源行，绝不 verbatim 搬 dev 行（两分支 ActvOnline 列数 56 vs 53 不同！）**；TimeCycle 12 列两分支一致可照搬
- ✅ 本地服(3080, dev_festival线)已部署验证：手术式 checkout ProtoGen（robot 提交 c5b1e2ba——注意我的 #1994 build 报"没有可提交改动"是因为改动被上一班车 #1993 顺带导出，**判 robot 回写别只等自己 build 号的提交**）→ ReloadGameServer 26表 → @28240 GM 开 100201/101211/100608/101213 全部 count=1（窗口 8/20 起，服有 +30d 时间偏移）
- ✅ **全链跳时验证通过（07-21 下午，本地服 3080 时间线已烧到游戏日 9/7）**：①KE/赛季1/赛季3 三活动到期结算=**空榜零邮件**（rank109/114/116 SendRankRewards 被调但 SendRankRewardMails=0 封；同窗对照 rank142 有分正常发）②永恒之岛 9/4 00:00 整点 Protected→SignUp、9/6 开打+跑马灯、9/7 Battle→Protected（无人参战 SetWinner=0 无异常）③10502 赛季更新 9/7 00:00 准点 fire ④老 TC1209 仍 fire 但 AO IsOn=0 不建活动=只增不改按设计工作。桥上验证：客户端配置热加载齐全（TC1213/10501=32d）、4 活动实例同步、Text 键全解析（繁中）。⚠️跳时手法：过期活动结算在大跳落地时即触发（不一定等午夜）；带奖励的排行结算仍需跨午夜 day-update。
- ⏳ 仅剩：11000 全服地图入口（23d，需服务端确认跨服依赖，故意不动）；制盾人 9002 上架属客户端懒计算窗口无服务端日志，留肉眼（本地服现已在 9/7 之后，重登即可见）
- 🔧 批量 tsv 行级编辑手法：csv.reader/writer + QUOTE_MINIMAL + **改前先验全文件无损往返** + 原子写(tmp+os.replace)；QUOTE_NONE 会在多行单元格上炸。克隆活动必须同步补 Text 键组（往源活动同键组行尾 `|TXT_ActvOnline_ActvName_<新id>` 追加，仅 col0）
- 报告生成器已归档：KB 同目录 `_报告生成器_wonder_audit_gen.py`（tap4fun 壳+静态SVG甘特，改 ROWS 数据重跑即可刷新 HTML）；实机测试对照清单=同目录 `X3奇观新排期_本地服实测清单_20260721.html`（4 活动逐条断言+可选结算闭环加测）

## 修复状态明细（dev，2026-07-21 白天）
- ✅ 赛季1/2积分活动：101207/101208 IsOn=0，新 101211(TC1211=26d起6天)/101212(TC1212=第7周周二) — zoe e13db23+dd0e1887
- ✅ 王座KE永恒之主：100607→100608(TC608=31d/24h=争夺日) — e637449b
- ✅ 冠军之路：105501→105502(TC624,D26) — e637449b
- ✅ **赛季更新锚点 TC10501：23d→32d — 我 07-21 c0064370，jolt #1984 SUCCESS**（截图"距赛季结束18分钟"的来源）
- 🔴 **101209 赛季3活动未修**：仍 IsOn=1 挂 TC1209(47d起6天/15d循环)，与新第3场(第10周周五报名/21d节奏)错位，D48-54 会再次空跑全员第一。修法=同款只增不改（5578e75 原计划：第10周周二起/21d循环）
- ⏳ 展示/商店类 6 条交策划：TC2007/10601/9000(23d→32d 直改)、9001(38d→第8周周一,TT2→6)、9002(53d→第11周周一)、11000 全服地图入口(23d→32d,**功能解锁须服务端确认**)；2008/10602 已对齐不用动
- ⏳ dev_festival 全套未同步（只有 10301=29d），走 dev→festival 官方合并
- ⏳ 线上暴露面未确认（V2 若已上 beta/正式服，窗口内开服的服都发过错奖）

## 关键机制（可复用）
- **全员第一名成因**：排行榜同分共享并列名次（`RankDetail.API.cs GetRank→viewRank+1`；地图侧 `RankSystem`/服务端 `ServerRank.SendRankRewards` 按 slot 发奖）。任何"结算窗口内玩法没开/没人产分"的排名活动都会全员并列第 1 发奖——**排期错配的标准事故形态**。
- **排期配对锚点审计法**：改某玩法解锁时间（TimeCycle/WorldTrend 阶段）时，grep TimeCycle 全表注释里同锚点天数（如"第23天"）+ 反查消费方（ActvOnline.TimeController / Hero.ShowTimecycleID / ShopItemCfg col24 / DailyPack / FunctionUnlockTask.Parameter1 / ConstCfg 指针如 WonderSeasonStartTime=10501），配套一起挪。X3NEW-792 就是只挪了本体漏了全家。
- 奇观时间链：UnitConfigWonder(243001 永恒之岛).TimeSignUp=10301/TimeSignUpAfter=10302，BattleStartTime=0(报名结束即战)+TimeBattle≈24h；赛季切换=Const WonderSeasonStartTime(10501首次)/After(10502循环)→WonderSystem.OnTimeStartEvent→WonderComp.OnWonderSeasonTimeStart(只 bump 赛季号,有幂等守卫)。客户端"距赛季结束"=UIActvWonderMain 取 10501/10502 的 start。
- 改在用 TimeCycle=双开风险 → 只增不改，见 [[X3 TimeCycle 配置知识]]（reference_x3_timecycle）。

## 涉案 ID 速查
巢穴研究主活动=ActvOnline 100201(type3 WONDER_TASK,TC401 开服常驻)；王座KE=100607/608(type6,RankID109)；永恒之岛积分=101207-09/101211-12(type12,RankID114-116)；中心奇观=UnitConfigWonder 243001(Rank173,ActvID105901)；海皇=KingOfSeas* Const；赛季表=UnitWonder__WonderSeason(每季HeroID+首占奖励)。
