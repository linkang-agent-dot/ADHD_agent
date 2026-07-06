---
name: project-x3-hero-handbook
description: X3 英雄养成手册双版本扩展（新一期3活动之第1个）——ActvType=27机制+双档互斥设计+策划案落点
metadata:
  node_type: memory
  type: project
  originSessionId: hero-handbook-2026-06-18
---

# X3 英雄养成手册（双版本）— 新一期3活动之第1个

2026-06-18 立项。这批共3个活动：①英雄养成手册双版本(本条) ②[[project-x3-piggybank-foreign-wine]]异国美酒储蓄罐改造 ③(待定)。

## 需求
现有「英雄养成手册」只有 $29.99 单档，付费天花板被压。**加一个 $49.99 豪华版**，结合现有界面 Prefab 改、**新增页签**。

## 现有原型（要改的就是它）
- **ActvType=27**（养成手册，独立类型，**不走** BattlePass）
- 入口 ActvOnline **102701** / ContentID **2701**
- 机制：**付费登录制**——一次性买 → 30 天每天登录领一份奖励（无任务/无等级）
- 配置链：`ActvOnline 102701` → `ActvLoginPurchase__ActvLoginPurchase`(2701行: Pack=220001 / Group=100) → `ActvLoginPurchase__ActvLoginRewardGroup`(Group=100, 30行=30天, 奖励列指向 Reward__Reward 的 RewardID 4100101~4100130) → `Reward__Reward`(col2=RewardID分组,col4=ItemID)
- 基础版 day1=万能传奇信物(52003)×10、day30=英雄装备材料袋(165905)×100，每天单道具
- Pack 220001：$29.99(价格点112)，PackType=16
- **价格点**：112=$29.99，116=$49.99
- 界面：单页签 `UIActvLogin.prefab` + `UIActvLogin.cs`（单购买按钮+单奖励轨；`CActvLoginPurchase.I(ContentID).Pack/.Group` 各取一个；`GetGiftPurchaseNum>0`=已购隐藏按钮）

## ★机制关键结论
**ActvType=27 是单档死结构**：每个 ContentID 只挂一个 Pack + 一个 RewardGroup。「双档互斥+新页签」**原生不支持，必须改程序**。

## 设计定稿
- 双档**并列、二选一互斥**购买（买任一版→另一版购买按钮置灰锁定+提示）
- 豪华版每日奖励=基础版同槽道具 **×2.0**（向上取整，种类不变只放大数量）
- 豪华版**第30天满勤封顶**追加**专属大奖**（纯复用现成养成道具：52003传奇信物×30+高阶技能书等，无新道具图）
- **程序方案A**：扩展 ActvType=27（`ActvLoginPurchase` 加 Pack2/Group2 列 + 服务端互斥校验+大奖发放 + `UIActvLogin` 加页签栏/双购买按钮/双奖励轨/封顶位强调）
- 美术：界面改动有新美术（双页签按钮选中/未选中态、豪华版banner换色、锁定遮罩、第30天封顶强调）；大奖道具复用无新图
- 豪华 PackID ~~220002~~ → **实定 220003**（⚠️2026-06-30 预研发现 220002 已被"建筑激活属性加成"$99.99占用，改用 2200xx 下个空闲 220003；克隆220001，价格点116=$49.99已存在✓）；豪华奖励组 **Group=101**(空闲✓)；豪华 day奖励 Reward **4100201~4100230**(克隆基础4100101~4100130·数量×2.0,空闲✓)；满勤大奖建议 Reward 4100231(数值待策划案③确认,发放靠程序)

## 产物清单（接管入口）
- **策划案**：GSheet SID=`15NKt8gF5H5fbPTKYkciYL-yFpmkY31VFIivZgyh6EcA`（X3_英雄养成手册_双版本_策划案）。10页签：变更记录/①活动模块/②开发配置需求/③数值设计/④活动配置改动(含schema 4行横铺)/⑤本地化/⑥美术需求/⑦验收Checklist/⑧打点事件/⑨日志需求。已过 task-checker 验收(2 blocker 修完)。奖励=用现有 X3 数值(不新增技能书ID)。
- **交互原型(出界面·讲交互)**：`KB\产出-交互原型\X3_英雄养成手册\英雄养成手册_双版本_交互原型_v1.html`（活原型+实时说明，演示双页签/购买/互斥锁/封顶位）。
- **效果图(给美术目标图)**：`KB\产出-本地化与美术\X3\英雄养成手册\`。v1_a/v1_b=AI整张生成(方向对但底飘,弃)；v2_真底加页签=真底img2img忠实复刻+成功拼入双页签栏。
- **★真素材拼装版(零AI·还原prefab真实模板·最终选定方向)**：`KB\产出-交互原型\X3_英雄养成手册\英雄养成手册_双版本_真素材拼装_v1.html` + `_assets\`(真实PNG)。用 UIActvLogin.prefab 实际sprite拼，保真=prefab本身，每块=独立真实组件。**含完整交互**(购买→已拥有/二选一互斥锁+提示/达成天点格领取盖✓/未到天🔒/状态条+重置)，对齐首版交互原型。
- **★改造版日历底板美术(给美术/程序)**：`KB\产出-本地化与美术\X3\英雄养成手册\日历底板_带切换按钮位_nourish3_v1.png`(2048²)=以 nourish_3 为模板img2img出的新面板，顶部加一条**放切换按钮的header凹槽带**(金线分隔·留空)。已 copy 进原型 `_assets\panel_with_header.png` 替换原面板——**切换按钮挂在这条header带里**(非独立页签·非压格阵)。

## ★真实组件清单(prefab库sprite·美术/程序拆组件直接用)
从 `UIActvLogin.prefab` m_Sprite GUID 反查(方法见 [[reference_x3_client_new_ui_workflow]]/GUI知识)，"nourish"=养成手册专属美术：
| 部件 | sprite路径(Assets/Res/UI/Spirits/) |
|---|---|
| 羊皮纸活页夹大面板 | Activity/img_Activity_bg_nourish_3.png (1060×1092) |
| 每日格 解锁态(金)/锁定态(棕) | Activity/img_Activity_bg_nourish_2.png(188×228) / _1.png(186×225) |
| 宝箱主视觉 | Activity/img_Activity_bg_nourish.png (568×584) |
| 9600%角标 / 倒计时沙漏 | Pack/img_gift_bg_Discount.png / Pack/img_gift_time.png |
| 锁 / 勾(已领) | Intelligence/img_cm_lock.png / WorldTend/img_TXDS_icon_gou.png |
| 规则按钮 / 金按钮 | CommonNew/img_cm_anniu_guize.png / CommonNew/img_cm_anniu1_gold.png |
**新增页签栏**：现复用 img_cm_anniu1_gold 拼；豪华版金紫皮=真要新出的美术(列美术需求)。
**★UX习惯约束(别违反)**：购买按钮**保持原界面位置=右上角·宝箱下方**(非底部)，双版本下「价格随当前选中页签变」(基础$29.99/豪华$49.99)；双页签栏=版本选择器(放奖励格阵正上方)。改造现有界面通则=不挪动原有控件位置习惯。生成脚本=task json(`x3-media\state\tasks\`)。
- **★真实基础界面截图(最权威底)**：`C:\Users\linkang\Pictures\X3验收\养成手册新增二选一高档位\主界面.png`（现版养成手册真容：羊皮纸活页夹+5列每日格带🔒锁标+右上宝箱主视觉+9600%角标+$29.99按钮+底部页签）。同族参考=`...\世界杯\世界杯登录活动.png`(ActvType=27,封顶宽格清晰)、`...\BP新增档位\节日BP模板.png`(分档/页签视觉)。

## ★Leader 设计转向（2026-06-18·覆盖早期"主面板挂双档切换栏"方案）
- **双档不再挂在主面板**（早期切换栏挂日历底板的方案作废，对齐痛点也随之消失）。
- **主界面**：只改日历区，其余全保持真实养成手册；**购买按钮保留但删掉所有价格**。
- **购买逻辑改**：点购买 → **弹出 BP 式「二选一」选择弹窗**（在弹窗里选基础版/豪华版再付）。
- **二选一弹窗** = 本期唯一新界面（需新美术）；参考范式**待用户给竞品图**（库里 A周卡顶部档位页签/B猎杀时刻BP多档 均被否，等竞品）。
- 效果图定稿方向 = **真组件拼装→AI reskin 五步法**（见 [[x3]]出图工作流§12），成品 `...\效果图_AI合成v1_reskin.png` 获认可("就是这个味道")。
- **切图交付**：主界面 `KB\产出-本地化与美术\X3\英雄养成手册\切图交付_主界面_v1.md`（13组件全真实sprite·直接取·S6四层归类；每日宝箱入口候选=ItemIcons/Chest_daily.png 256²）。

## 当前阶段（程序按 出界面→定交互→写代码 走）
- ✅ 出界面：真素材拼装原型 + AI reskin 成品效果图（定稿方向）
- ✅ 主界面切图清单（真实sprite直接取，无需AI切）
- ✅ 二选一弹窗选版(2026-06-30)：**用户选定 alt1**(`KB\产出-本地化与美术\X3\英雄养成手册\二选一弹窗_X3风格设计稿_v1_alt1.jpg`)——木纹底·圆形书本icon+标题条·仅豪华版挂角标丝带·真实风格道具图(罗盘/奖杯/金币/红包/卷轴/头像);v1(紫调酒馆+双丝带+彩色星星占位)弃。竞品参考=高级/豪华通行证(横屏BP二选一,`Pictures\X3验收\养成手册新增二选一高档位\通行证购买界面参考.png`)。方法=横竖转换→reskin两段式(见[[x3]]出图工作流§12b)。**alt1 定稿前仍需微调2处**:①底部"解锁任意版本达到45级将返还💎300"是竞品文案口径,养成手册=登录天数制无等级,"45级"不适用→改我方口径(如"满勤返还"或删);②奖励图标占位→换真道具(基础版day槽真实养成道具)。改完再拆弹窗切图。弹窗含:左基础版/右豪华版二选一·各自购买键(删价格,只显"购买")·标题下二选一描述行·关闭键/货币/底部说明。
- ✅ 弹窗切图交付清单(2026-06-30,2026-07-01更正)：`KB\产出-本地化与美术\X3\英雄养成手册\切图交付_二选一弹窗_v1.md`——**0新美术·全复用现成真实sprite**(早期以为要3项书本徽章/丝带,实际_assets真素材已齐:书本icon复用`icon_Skill_Book_1_3`、豪华角标复用折扣角标`img_gift_bg_Discount`;教训=生成新美术前先查_assets,项目惯例100%复用)。字号+金渐变规格见`客户端prefab拼装指南.html`「🎨文字规格」节(米色档位面板字Gradient2改深棕7A4F1D→5A3A12)。
- ✅ 配置落地草稿(2026-06-30·**不push,待开分支执行**)：`KB\产出-数值设计\X3_英雄养成手册\配置落地草稿_待开分支执行.md`——含4块改动(Pack220003克隆/Group101克隆/Reward4100201~230×2.0全表/满勤大奖)+真实基础版30天奖励表(已从tsv捞出)+执行顺序。
- 🔄 写代码(2026-06-30开工)：**两 feature 分支都叫 `X3NEW-hero-handbook-deluxe`**——配置仓 `C:\x3\gdconfig`(基dev_festival)/代码仓 `C:\x3-project`(server+client单仓,基origin/dev_festival)。⚠️x3-project拉分支前清过一堆ProtoGen生成物残留(含UU冲突)+删4个未跟踪HeroClub.bytes;嵌入gdconfig子模块post-checkout hook会切到dev(正常)。
  - **★实现范式(代码调查实证)=套用世界杯竞猜 ActvType=71 二选一互斥**：互斥放**客户端表现层**(买一边Hide另一边购买键),服务端存两档购买状态(权威)。参考 server `ActivityMeta.WorldCupGuess.cs`(packA/packB各purchased) + client `UIActvWorldCupGuess.cs` RefreshPurchaseState/RefreshSideState(lockedByOther→Hide)。
  - 二选一弹窗 prefab 的拼法（索引回写补充 2026-07-03）：客户端 .cs 已写、待 Unity 拼 prefab，做法=**复制世界杯弹窗（UIActvWorldCupGuess 的弹窗 prefab）改名**当底子改造。
  - **schema改动**:ActvLoginPurchase表加 **Pack2/Group2** 两列(proto字段5/6)→走加tsv列+导表自动重生成CfgProtos,别手编生成proto。生成类 `client\Assets\Scripts\CSShared\Common\Cfg\CfgProtos\ActvLoginPurchase.cs`(现仅ID/Pack/Group)。
  - **服务端4处**:①ActivityMeta.cs ActivityItem加双档购买bool(purchasedBasic/Luxury,仿worldCupGuessData) ②ActivityMeta.Msg.cs:910-916 CheckCanReceiveActivityReward的isPurchased改"购任一档" ③GiftMeta.Activity.cs购买事件按PackID判档置位 ④序列化自动。ActvType=27常量=ActivityConst.TRIGGER_TYPE_PAY_SIGN。
  - **客户端**:UIActvLogin.cs 39-47(OnShown读Pack+Pack2)/59-70(ShowBtnPurchase互斥)/72-112(ShowSignInfos读Group2第二轨)+UIActvLogin.prefab布局+新二选一弹窗(需Unity)。
- ★**范式拍板(2026-06-30,覆盖早期Pack2/Group2方案)**：①**新开独立活动·老活动2701一行不动**(用户定);②**豪华日奖=基础×2「发奖翻倍」**(服务端把同RewardID再发一次,不建Group2/不克隆×2 Reward,零新增奖励行·翻倍永远整);③**满勤大奖=新增FinalReward列**(豪华满勤最后一天追加);④二选一=双礼包(基础giftId==activityId旧逻辑+豪华独立giftId)+客户端互斥(同世界杯ActvType=71)。表级Pack2/FinalReward对老活动默认空=单档,向下兼容。
- ✅**服务端代码已写入分支**(未编译未测,待构建)：发奖唯一chokepoint=`ActivityPaySignCondition.GetReward`(client\...\CSSharedHotfix\Game\Activity\ActivityTriggerConditions\),`#if _SERVERLOGIC_`+IsLuxuryPurchased+Pack2>0三重闸门注入×2+满勤大奖。改动4处:①ActivityPaySignCondition.cs(OnAddActivity建双礼包/OnRemoveActivity删双/GetReward翻倍+满勤/IsLuxuryPurchased/IsLastSignDay) ②GiftMeta.Activity.cs(CreateActivityPaySignLuxuryGift+GetActivityPaySignLuxuryGiftId+TryFindActivityGiftByCfgId,豪华独立giftId+重登复用) ③ActivityMeta.cs OnBuyGiftForGiftId加PaySignOnBuyGift(豪华giftId≠activityId,购买路由标记活动) ④ActivityMeta.cs ClearActivityGiftPurchasedOnRefund(豪华退款反查清标记)。判档不新增proto(从GiftMeta购买数推导)。
- ✅**配置schema已加**(gdconfig分支)：ActvLoginPurchase__ActvLoginPurchase.tsv加Pack2(依赖Pack)+FinalReward(依赖Reward)两列,老行2701留空=0;csv-aware脚本加列(多行注释cell完好,git diff 7±7干净)。
- ✅**弹窗美术已切好进工程**(2026-07-01,走Morphix元素拆分ui_extract路径B从alt1切,gpt灰底雪碧图→removebg→切)：`client/Assets/Res/UI/Spirits/ActvLoginChoice/` 4张FINAL=panel_basic/panel_luxury(顶带金header条=豪华区分)/bookicon_basic/bookicon_luxury;**ribbon豪华角标弃用**(用户定不做,豪华区分靠panel header+华丽书icon+txt_name描金);已压缩达标(panel 133/143KB≤150·bookicon 各23KB≤35;透明尺寸保留)——⚠️实测**GRFal无PNG压缩器,art-skills兜底做的**(下次要压PNG别指望GRFal)。原图KB`切图_从alt1\`。挂法panel→Col*/Panel·bookicon→Col*/BookIcon,导入设Sprite(2D and UI)。弹窗框/奖励格/购买键/关闭/道具货币仍复用现成sprite(路径见切图交付_二选一弹窗_v1.md)。
- ⬜**配置新独立活动待建**(部分待满勤数值)：ActvOnline+ActvLoginPurchase新行(Pack/Group新基础+Pack2新豪华+FinalReward)+克隆基础Pack($29.99点112)/豪华Pack($49.99点116已存在)各BuyCount=1/基础Group30行/基础Reward一套+满勤大奖1行。豪华原计划220002已被占→用新空闲id。
- ✅**客户端 Auto 已手写落仓**(2026-06-30,免跑生成器)：`client\Assets\Scripts\UI\Gen\Auto_UIActvLoginChoice.cs`(新建)+`Auto_UIActvLogin.cs`(加mBtnChoice/OnBtnChoiceTrigger)→C1/C2编译阻塞清。**prefab 必须摆成的确切节点路径**(Auto按此Find,对不上=运行时找不到非编译错)见拼装指南HTML第9步;弹窗存 `Assets/Res/UI/Prefab/Activity/UIActvLoginChoice.prefab`。监听方法名规律=`OnBtn{节点名}Trigger`(节点`close`→OnBtnCloseTrigger/节点`choice`→mBtnChoice+OnBtnChoiceTrigger),详见[[X3客户端GUI知识]]。
- ★**绑定=路径匹配(手写Auto,非拖拽)**：Auto用`FindByFullPath("字符串")`,场景节点路径对上即自动绑,Inspector不用配引用。**11个必存在路径**:Top下txt_title/txt_desc/close,Packs/**ColBasic**/{txt_name,txt_state,RewardList,UIBtnPurchase},Packs/**ColLuxury**/同。⚠️两栏节点名必须`ColBasic`/`ColLuxury`(Ctrl+D复制的ColLuxury(1)要改名+去子节点(1)后缀);**Panel/BookIcon不绑**(纯美术·名字随意)。**col的txt_desc已按需求删**(2选栏不做副描述)→代码RefreshView+Auto已去mTextDescBasic/Luxury引用(否则null崩);顶部txt_desc(副标题)保留。
- ⬜**客户端待Unity**：UIActvLogin.cs+prefab(读Pack2/购买弹二选一窗去价格/互斥/豪华轨×2显示+满勤大奖位)+新二选一弹窗prefab(alt1定稿,切图见`切图交付_二选一弹窗_v1.md`·0新美术全复用)。生成类`CfgProtos/ActvLoginPurchase.cs`的Pack2/FinalReward属性**已手加**(2026-07-01·field5/6 tag40/48·让client+server先编译过·真导表会覆盖,tag与真导表对齐);col的txt_desc已删代码去引用。
- ✅**客户端代码已push feature分支**(2026-07-01·commit 5b341d8·11文件574行=服务端3+客户端6+2新meta)到 `X3NEW-hero-handbook-deluxe`(x3-project)。⚠️**本地分支track的是origin/dev_festival→push必须显式`git push origin X3NEW-hero-handbook-deluxe`,别用裸`git push`(会污染共享dev_festival)**。**未传(故意)**:①prefab+sprites(弹窗prefab残留`_RefOverlay`描图纸节点引用`_RefMockup_TEMP`,待用户Unity删该节点+清描图纸再传)②100个Club/mask/*.meta无关噪音(Unity重导序列化·非本功能·别提交)③描图纸临时图。走MR不直合dev_festival。**②prefab+4切图+Auto+生成器SaveData已推(2026-07-01·commit e73c1a4)**——客户端代码+prefab+美术全在分支。⚠️**坑:点正规生成器但prefab节点没配绑定标记→生成空Auto+建冲突空logic stub(base UIBase vs UIBase<T>·方法重复→编译错)**;解=git checkout恢复手写Auto+删空stub+Auto的Identifier改成生成器ID(2039220338),详见[[X3客户端GUI知识]]。手写Auto按路径找不吃标记,策划侧用它即可,正规生成器要产出得先配标记(问负责程序)。
- ✅**配置全建完(2026-07-01·gdconfig commit 47cc996 push feature分支)**：ActvOnline 102702/ContentID 2702/type27/MailID 101109/TimeCycle 2701模板 + ActvLoginPurchase 2702(Pack220003基础/Group101/Pack2 220004豪华/FinalReward 4100231) + Pack 220003·220004 + Group101(30行) + Reward 4100201~230基础+4100231满勤(信物52003×30+材料袋165905×100)。引用链5环验通。dev jolt导表已触发(队列76972·结果走钉钉)。
- ✅**本地服已部署102702**(x3_local_redeploy Sid3080·PlayService started无报错·没撞世界杯64坑)。GenCSharp重生成CfgProtos的Pack2/FinalReward=tag40/48与手加一致。GM开活动=`GMAddServerActivityByCfgId 102702 43200`(GM菜单"[活动_活动]通过配置ID开启服务器活动"·别填0会查TimeCycle报错)。
- **🚀推送状态(2026-07-01·已全推完)**：origin/X3NEW-hero-handbook-deluxe **完整全套**=服务端`5b341d8`+prefab/切图`e73c1a4`+配置robot`ae8edab`+i18n`1cb34b9`+客户端UI迭代`d7262278`(rebase成`a808908190f`已推·当时pull--rebase无冲突)。**验收人直接拉此分支即全套**。⚠️gdconfig两clone同远程:`C:\x3\gdconfig`本地还挂2个**无关**提交(深海节RuleTips/怦然心动102993)非手册·别误推。
- **✅TimeCycle改0已推+导表(2026-07-01)**：102702 TimeCycle 从 2701→0(`ActvOnline` field[7]·**脱离固定时间轮=只能后台iGame触发**·用`x3-config-export/scripts/tsv_edit.py set`改·工具列号0-based·xlsx已出git只改tsv)。配置仓 pull--rebase 整合 origin(无冲突)后 **push成功**(提交`a5fd5e1`·连带把当时本地掺的4个深海节i18n/累充提交291dd0f等一起推了·用户确认都推)，已触发 jolt 导表编进 ProtoGen。⚠️经验：`C:\x3\gdconfig`的X3NEW-hero-handbook-deluxe是**多功能共用配置分支**，push前必查有没有别人未推提交(可能连带推)。
- **📋验收/接管路径清单(2026-07-01·全在分支 `X3NEW-hero-handbook-deluxe`)**：3 代码提交(x3-project) `5b341d8`(服务端+客户端逻辑) `e73c1a4`(prefab+切图) `d7262278`(迭代:合并数量/×2/proto字段) + gdconfig嵌入仓 `1cb34b9`(i18n) + **配置表在标准仓 `C:\x3\gdconfig` commit `47cc996`**(ActvOnline102702/ActvLoginPurchase2702/Pack220003·220004/Group101 30行/Reward4100201~230+4100231满勤)。
  - **服务端**(`server/GameServer.Hotfix/`)：`PlayerMeta/Gift/GiftMeta.Activity.cs`(双档礼包创建L251/反查L270/二选一硬拦截CheckPaySignExclusive L277) `PlayerMeta/Gift/GiftMeta.cs`(CheckCanBuyGift拦截) `PlayerMeta/Activity/ActivityMeta.cs`(购买路由/退款清标记)
  - ⚠️**验收易误判「没服务端代码」**：发奖翻倍×2+满勤大奖的**核心服务端发奖逻辑在共享文件** `client/Assets/Scripts/CSSharedHotfix/Game/Activity/ActivityTriggerConditions/ActivityPaySignCondition.cs` 的 `#if _SERVERLOGIC_` 块(L137 IsLuxuryPurchased/L142 FinalReward)——X3 共享代码放 client/CSSharedHotfix 靠 _SERVERLOGIC_/_CLIENTLOGIC_ 宏分编进服务端/客户端；**只扫 server/ 目录会漏看误判成"只做了客户端"**。验收要同时看 server/GameServer.Hotfix/ + CSSharedHotfix 的 _SERVERLOGIC_ 块。(2026-07-01 大哥就这么误判过一次)
  - **客户端逻辑**(`client/Assets/Scripts/`)：`UI/Actv/UIActvLoginChoice.cs`(二选一弹窗) `UI/Actv/UIActvLogin.cs`(主界面choice键) `UI/Actv/UIActvLogin.UIActvLoginSlotItem.cs`(日历×2) `UI/Gen/Auto_UIActvLoginChoice.cs`+`Auto_UIActvLogin.cs`(手写绑定) `CSSharedHotfix/Game/Activity/ActivityTriggerConditions/ActivityPaySignCondition.cs`(发奖翻倍+满勤) `CSShared/Common/Cfg/CfgProtos/ActvLoginPurchase.cs`
  - **proto/prefab/素材**：`Res/Config/Proto/ActvLoginPurchase.proto`(Pack2/FinalReward) `Res/UI/Prefab/Activity/UIActvLoginChoice.prefab`+`UIActvLogin.prefab` `Res/UI/Spirits/ActvLoginChoice/*`
  - **落地方案HTML**(唯一入口)：`KB\产出-数值设计\X3_英雄养成手册\英雄养成手册_双版本_落地方案.html`；拼装指南**两版**：v1建弹窗(已完成) `客户端prefab拼装指南.html`+**v2 UI强化(2026-07-02·当前用)** `客户端prefab拼装指南_v2_UI强化.html`(换panel_v2+挂勋章/角标/丝带·全在ColLuxury·基础列不动·含2X强化四方向后两项可选:文案条/默认推荐锚点)；**切图交付定稿目录(唯一入口·2026-07-01)= `KB\产出-本地化与美术\X3\英雄养成手册\交付_切图_定稿\`**(旧`交付_切图\`含废弃候选作废)：4张切图(badge_x2_bonus勋章=真实版切+BONUS·X3风/panel_luxury_v2华丽版底边完整/tag_discount_-17/tagline_ribbon_2x)+`i18n_translation_staging.tsv`(12key×15语言译好·含新增TXT_ActvLogin_Luxury_Tagline「每日奖励X2！」)+`prefab_新增改动清单.md`(换panel+加勋章/角标/丝带·纯静态装饰默认不改代码·基础列不动)+交付说明.md。全grfal抠透明。**剩两件**:①切回X3NEW-hero-handbook-deluxe(gdconfig)把staging填进Text__Text.tsv传i18n ②Unity按prefab清单拼。**⚠️切图已定稿(2026-07-01)=5项**：`badge_x2_bonus.png`(华丽星芒版·用户否掉了简洁clean版)/`panel_luxury_v2.png`(华丽豪华panel·无alt1)/`tag_discount_-17.png`/`tagline_ribbon_2x_luxury.png`(文案「每日奖励X2！」空底叠字走i18n)/交付说明.md。**全部 grfal remove_background 抠(非双底差分)+过透明验证**；基础panel保持朴素不动；还没拼进prefab(拼装需切回手册分支+Unity拖图·当前客户端仓在guide分支)。透明抠图默认已全局改grfal remove见[[project_quality_gate_and_interaction_module]]
- **⚠️奖励构成澄清+UI强化方向(2026-07-01)**：本手册**无英雄**！奖励全是异国美酒/信物/资源/技能书等消耗道具(标题里"霍普金斯·兔耳魅影"是测试占位文本·不当真)。UI强化方向(用户拍板)=①基础/豪华panel拉开代差(基础朴素反衬·豪华深金紫+宝石+发光+更大上浮)②疯狂强化「2X」当豪华视觉主题(巨型×2光爆+双倍飘带+每格标×2)③用2X文案条填panel空白(全部奖励×2/每日双倍/满勤专享大奖/一份价两份货)④价值锚点法参考[[project_x3_hero_handbook]]世界杯至尊BP复盘(显性锚点+默认推荐>光加徽章)。效果图产出`效果图/`(真实界面精修版f7a8 + 豪华强化2X版d4e2)。
- **弹窗UI迭代(2026-07-01·未commit)**：①**RewardList 改竖排**(prefab UIActvLoginChoice：ScrollRect m_Horizontal0/m_Vertical1 + LoopScrollRect direction1；Viewport sizeDelta.y 1150→0 去横排溢出残留；RewardList sizeDelta.y 403→1000 加高填栏。改法见[[X3客户端GUI知识]])②**奖励预览=全合并(最终决策)**：`GetPreviewEndowItemsAndMerge(...true)` 每道具一条+数量累加(豪华×2+满勤大奖)——本活动30天只4种ItemID(52003/7001/19003/165905)，不合并会重复堆叠丑&看不清数量；合并只剩4条icon是正常(不是bug)③**两个新美术已出**(KB`英雄养成手册/badges/`)：`badge_reward_x2_luxury.png`(×2翻倍徽章挂豪华列)+`tag_discount_17off.png`(-17%折扣角标挂价格旁·透明已验)；**-17%口径=相比买两份普通版($59.98)买豪华版($49.99)省16.7%**；拖进`Spirits/ActvLoginChoice/`即用。整体效果图`效果图/…效果图_a.png`/`_b.png`两变体给客户端照着摆位。④**合并数量走loop会丢showNum坑已修**：`GetPreviewEndowItemsAndMerge`累加写showNum，但RefreshLoopReward循环经IDValView只拷num丢showNum→格子显首日单量像"没合并"；修法=合并后`it.num=(int)it.showNum`(新增`CarryMergedNumToVal`)。日历slot直连ItemUnitView.Refresh不受影响。详见[[X3客户端GUI知识]]。
- ✅**客户端手册改动已提交(本地·未push·2026-07-01)**：分支`X3NEW-hero-handbook-deluxe`两仓——超级仓`d7262278c0f`(11文件:ActvLoginPurchase.proto加Pack2/FinalReward+对应CfgProtos.cs+ProtoGen.bytes一套、合并数量修复showNum→num、日历×2、choice购买键、cspb修复、badge_chaozhi素材、两prefab)+gdconfig`1cb34b9`(i18n 11key)。**只commit没push**(推要显式`git push origin X3NEW-hero-handbook-deluxe`防污染dev_festival)。提交后已切到新分支`dev-guide-jump-fix`(从dev_festival干净建·guide无关任务)。⚠️2X强化版UI(panel重出/2X主题)是后续迭代·还没做进prefab。
- ⚠️**(历史)客户端一批改动**(2026-07-01)：①3编译坑=UIActvLoginChoice.cs加`using GameCommon.Endow`+`Hide()`→`CloseSelf()`、Auto删`using UnityEngine.EventSystems`(EventTriggerType歧义)②choice购买按钮已加进UIActvLogin.prefab(Root/Animation/Top/choice·复制btn_info·raycast+Auto已wire)③**日历×2显示已实现**(P1待办完成·豪华买家日历每格×2:slot BindData加isLuxury→`GetPreviewEndowItemsAndMerge(rewardId重复2次,空list,needMergeNum=true)`合并翻倍·跟服务端发奖一致;ProviderData传mIsLuxury)。**无"切换按钮"=设计如此(二选一一次性锁定,买豪华主界面自动显×2)**。详见[[X3客户端GUI知识]]。
- 🔄**本地验收进行中(2026-07-01)**：GM `GMAddServerActivityByCfgId 102702 43200` 已开活动(GMPrintServerActivity确认count=1·7/1-7/31运行);主界面日历+30天奖励显示OK;**i18n补了11个cn key**(活动名/弹窗UI/礼包名·两仓tsv都加·状态"新增"·未commit·16语后面走x3-translation-automatic)→本地轻量导表(ExportTable+cp ProtoGen/i18n+GM `ReloadGameServer`·数据改动不重编)→活动名"英雄养成手册"已显示。**缺:主界面UIActvLogin.prefab的choice购买按钮**(用户加中·复制btn_info→改名choice·Auto已wire `Root/Animation/Top/choice`→OnBtnChoiceTrigger)。加完点购买→弹二选一窗验收买档/互斥/发奖。
- ⬜ 收尾:choice按钮补完验收买档→i18n补16语+commit→回推客户端3编译修复→dev部署(基础×1/豪华×2+满勤/互斥/退款/老活动回归)→i18n→jolt_verify
- ★**本地化处理**(走[[reference_x3_i18n_workflow]]):两块——①**代码7个自定义UI key**(TXT_ActvLogin_Choice_Title/_Desc/Basic_Name/Basic_Desc/Luxury_Name/Luxury_Desc/Owned;⚠️i18n扫描器只扫配置表**不扫.cs**,这7个必须手动补进Text表,可现在就补·不依赖ID) ②**配置侧自动key**(TXT_ActvOnline_ActvName/_ActvDesc_{活动ID}·TXT_Pack_Name/_Desc_{基础&豪华礼包ID}·满勤大奖邮件,建表后按ID拼)。**做法=精准append到`tsv/i18n/Text__Text.tsv`(16语cn/en/sp/fr/id/de/kr/zh繁/ru/ua/jp/it/pl/po/tr/th),别在dev_festival跑全局CompositeI18n扫描(卷别人待译+噪音)**。⚠️**头号坑=新活动/新礼包的新ID没建i18n key→客户端标题/礼包名空白(导表不报错)**,收尾必审计`i18n_leak_audit.py`。
- ★**价格口径(2026-07-01定)**:**第一界面**(主界面UIActvLogin那个开窗"购买"键)=**去价格**(只弹窗);**第二界面**(二选一弹窗两个UIBtnPurchase)=**显价格**($29.99/$49.99,玩家看价选档)。代码本就对(Show(giftId)自带价);别隐藏弹窗价格文本。
- ⬜ **待拍决策**:满勤大奖数值(策划案③,建议52003×30+技能书)。弹窗底部"45级返还"文案=已定**删**(养成手册无等级)。美术=已定**0新美术全复用**(书本icon复用icon_Skill_Book_1_3/豪华角标复用折扣角标)。
- **★sub-agent审代码结论(2026-06-30,已处理)**：①**L1真bug已修**=买豪华(giftId≠activityId)主界面不刷新→UIActvLogin.OnBuyGiftSuccess加豪华giftId比对；②**P2已修**=CheckPaySignExclusive加ActvType==PAY_SIGN闸门(防ContentID跨表撞号误伤)；③**P4已修**=TryFindActivityGiftByCfgId改用Data.GetGiftCfgID(更idiomatic)。**配置必满足(P3)**：豪华Pack必须克隆220001→PackType=PACK_TYPE_ACTIVITY,否则退款不走ClearActivityGiftPurchasedOnRefund→退款后仍能领×2。**已知v1缺口(P1,非阻塞)**：主界面日历轨对豪华买家仍显基础数量(实领×2服务端已对·弹窗预览已×2),mIsLuxury字段已留;要日历也显×2=给slot加倍率(视觉精修)。核心无双发(subItem.received守卫)/老活动Pack2==0零影响=审核确认通过。C1/C2编译阻塞=prefab/Auto未生成(Unity前置非bug)。
- **★落地方案HTML(交接唯一入口)**：`KB\产出-数值设计\X3_英雄养成手册\英雄养成手册_双版本_落地方案.html`(范式决策+服务端已写详情+配置/客户端spec+执行验证步骤+风险)
> ⚠️ 策划案 GSheet(`15NKt8gF...`)的界面交互/规则段仍是早期"主面板双页签"写法，待二选一弹窗定稿后回改对齐本转向。

机制参考 [[reference_x3_monetization_mechanics]]、写策划案模板 [[x3]]、出图工作流见 KB\方法论\X3_AI出图工作流。

- ✅**TC=0导表缺口已堵(2026-07-02)**：导表工具`PostProcessData.py` SKIP_TIMECYCLE_CHECK豁免名单加 **ActvType 27**(同世界杯64/签到14先例)，本地导表带102702 TC=0全绿实测过；已推 dev_festival(794da04) + cherry-pick到手册分支。**102702正式方案=TC0只走iGame触发**，上线合分支时导表不再拦。
