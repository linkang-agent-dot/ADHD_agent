---
name: project-x3-piggybank-hud
description: X3 异国美酒储蓄罐触达改造(HUD挂件+登录弹窗+BI打点)，超哥需求；分支/代码锚点/设计要点，接手先读
metadata: 
  node_type: memory
  type: project
  originSessionId: 1a88ad9c-2a66-4b0c-bc39-1d37c122fae1
---

# X3 异国美酒储蓄罐触达改造（2026-07-07 立项，超哥上周五提）

**需求**：①抽卡界面下方挂储蓄罐 HUD（图标+均CD时倒计时/可买时红点·每日刷新）②点击进获取途径 ③进界面检测"有档可买&&无美酒7002"→自动弹获取途径（每登录一次）④BI打点。背景=超哥指触达两缺口：没弹窗、没专属按钮。

**分支**：x3-project `feature/x3-piggybank-hud`（dev 基底，2026-07-07 从 origin/dev 切）。纯客户端，服务端/配置零改动，完成走 MR 进 dev。

## 代码锚点（勘探已完成，别重挖）
- **"异国美酒界面" = 限定英雄抽卡界面 `UI/Gacha/UIHeroLottery.cs`**（prefab `Assets/Res/UI/Prefab/Gacha/UIHeroLottery.prefab`，全屏Window）。美酒7002=DrawCards 限定池消耗（`gachaCfg.CostType`，凌霜/夜玫瑰/爱莉希雅等全部限定池）。缺酒时已有 `UIHelper.ShowItemObtain(gachaCfg.CostType, buyNum)`（:361/:392）——触达缺口=只有点抽卡才触发。
- **获取途径入口** = `UIHelper.ShowItemObtain(7002, 1)`（UIHelper.ItemObtain.cs，内部 WndMgr.Show<UIItemObtain>，含储蓄罐卡 UIPiggyBankContent）。
- **每登录弹一次范式** = `UIHelper.TryPushRedPackLoginPopup`（UIHelper.Update.cs:483 一掷千金红包，调用点 GuideModule.cs:56；含跳过原因日志结构可借鉴）。
- **BI打点 API** = `TgsHelper.Instance.TraceUserClick(controlId)` / `TraceApplicationLog(eventName, attrs)`（Sdk/TGS/TgsHelper.BI.cs，字符串ID+BIConst常量，用法样例 UiActivityCommonRules.cs:138）。
- **红点系统**已有 `RedPointType.ActivityMonopolyPiggyBank`（那是大富翁储蓄罐，别混）；美酒HUD红点=新做或本地per-day点击记录。
- **储蓄罐"储蓄"真相**（详见 KB 策划案⚠️实装差异节）：无积累状态，可买判定=有档今日(UTC)未购；均CD倒计时=到明日UTC0点（口径同 `UIPiggyBankContent.IsDailyResetPiggy` / 服务端 GiftMeta isExoticWineDailyPiggy，常量 `GiftConst.DAILY_RESET_PIGGY_RES_ID=7002`）。

## 实现进度（2026-07-07 代码全部落地·终审通过·待用户Unity自测）
- 设计doc+实现计划在 `KB\产出-数值设计\X3_异国美酒储蓄罐\`（`储蓄罐触达改造_*_2026-07-07.md`）。子代理+双审执行，全部通过。
- **分支6个commit（origin/dev基底,未push）**：`f6a491b3b78` BI常量 / `96b2e39c833` 挂件类UIPiggyBankHudEntry / `597542652bb` meta / `06f6f7fe07c` 质量修复(OnHide兜底停表+节点缺失报错) / `aca84d76e7d` prefab节点组(YAML手术,PiggyBankHud@Faded下,占位图ui_Howtogetit_piggybank_1+红点img_cm_hongdian) / `a5811a03cb1` 宿主接线(Auto绑定+UIHeroLottery五处)。
- **✅端到端自测已由agent全自动跑完(2026-07-07,本地服3080+GM推时间,配方=x3-feature-test recipes配方6)**：7项全过——美酒池显示/非美酒池隐藏/均CD倒计时(17:49:11到明日UTC0点)/**界面开着跨0点自动切回红点**/弹窗(重进弹+每登录一次+均CD不弹负例)/点击(熄红点+记日+跳获取途径)/跨天红点重亮/BI三事件留痕(click明文,show+popup=pb_client_application_log)。未测：低等级隐藏(需新号,逻辑复用)/重登弹窗复弹(双审过)/真机BI上报。环境改动=服务器时间又+2天(现2026-09-08,重置需重启GameServer)。
- **视觉已改情缘商店同款圆形制式(2026-07-07用户看图后要求)**：二轮prefab手术`1ebe8d981a6`(Shop的圆底sprite/点击助手/TFWButton/描边Txt制式逐字段克隆,根节点隐形raycast接收器方案,节点名RedPoint/TxtCd未动)+可买态横幅常显储蓄罐名(复用PiggyBank.Name i18n,均CD倒计时替换;commit见分支)+位置实机校准左移94px避让情缘商店文字(755→660.76,commit见分支)。改后回归全过(含重登弹窗复弹=上轮未测项)。验证报告HTML(3截图)=KB案子目录`report_X3NEW-piggybank-hud.html`。
- **✅弹窗口径已拍板(2026-07-07用户)**："抽卡耗到0也弹+每登录一次"=现实现原样,零改动定案。
- **✅MR已开(2026-07-07)**：**!668** → dev（can_be_merged无冲突,remove_source_branch）。!667 已关（其版本有BUG）。分支 13 commits,tip=`1c00a8260cd`。
- **BUG复盘(用户测出,修复=1c00a8260cd)**：切非美酒卡池时未清 `mVisiblePackIDs` + 未取消已排的延时弹窗 → 1s门控窗口内可能用过期档位/旧mCostNum在错误卡池弹美酒获取途径。修复=切池分支清列表+取消未弹延时窗。教训：**带延时/门控的弹窗,宿主状态切换(切池/OnHide)每个出口都要取消pending并清缓存**。后续新增 commit：37c862fdd2e 弹窗1s节拍门控避让抽卡动画(MMF/UIHeroLotteryShow/UIHero10LotteryEnd在播则再等+弹前重验)+prefab横幅Btn/Icon图集引用；afb0fa92523 补StreamedAssetsRollback.cs.meta。
- **待办**：①等MR !668 review合并 ②美需正式小图标替占位(合并后换prefab单个sprite引用即可)。
- **MR姿势更正**：Chinese标题/描述 API 可用——UTF8 bytes body + `charset=utf-8` header 即可（此前"必须ASCII"是编码姿势问题,不是GitLab限制）。
- **feval坑两条(改运行时时用)**：不吃`120f`float后缀(写120);lint禁分号(多语句拆多条--command,同run会话变量共享)。
- **新知**：①UIWidget(TFWCore/Script/UIBase/UIWidget.cs)非MonoBehaviour,挂件=WidgetContainer.AddSingle运行时挂,prefab不引用脚本GUID,但.cs仍需.meta(手写=抄同目录meta换uuid4 guid) ②TimeUpdateText被禁用不停表(OnDisable只置mText null,FrameUpdateRegistry继续跑到endTime)→挂件必须OnHide兜底StopTiming ③G.Player每登录重建(ClientPlayer.InitFromData赋值/OnDestroy置null),static引用ReferenceEquals可判"每登录一次" ④UIWidget事件只在Shown态注册,Refresh首行要Show()。

## 设计定稿要点（用户已答3问）
HUD挂抽卡界面内部下方（非主城）；非CD态=红点(每日刷新)；日志=BI打点(非诊断日志)。方案=独立 UIPart `UIPiggyBankHudEntry`（UIBtnPurchase同款 WidgetContainer.AddSingle 模式），美酒池(CostType==7002)才显示。弹窗"每登录一次"=静态会话标记。**待用户批设计**（2026-07-07 已呈现，等回复）；批后设计doc落 `KB\产出-数值设计\X3_异国美酒储蓄罐\`。

## 线上BUG（2026-07-13实锤，玩家2137817/2330服，周日"显示可买点击弹等待存钱罐复原中"）
**根因=6-25日重置改造漏改客户端购买前置校验**：`client\Assets\Scripts\Entity\Player\Gift\GiftMeta.cs:900-909` CheckCanBuyGift 的 CD 判定仍是通用滚动 ColdTime(24h)，没加 7002 UTC日重置特例；而显示层 `UIPiggyBankContent.cs:179-191` 和服务端 `server GiftMeta.cs:1644-1652` 都有特例。→ 凡"距上次购买<24h但已跨UTC0"时段：按钮亮但点击被本地拦（请求根本没发服务端，IAP 未拉起），弹 `ErrCodeBuyingGiftInCd`(1010027)→`Text_ErrCodeBuyingGiftInCd`=「等待存钱罐复原中」(Text__Text.tsv:4211)。链路：UIBtnPurchase.cs:384/399 DoBuy→ReqBuyGift(GiftMeta.cs:102):104本地校验→:207-210 PopTips。影响=压制每日复购收入（买得越晚次日被拦越久），06-25 起带病在线。教训：**改限购口径要三处同步——显示层/客户端前置校验/服务端校验，客户端 CheckCanBuyGift 是镜像服务端的独立副本，最易漏**。
**修复已落地=MR !718**（2026-07-13，feature/x3-piggybank-daily-cd-fix→dev，can_be_merged）：没改校验逻辑，改**共享层写入口径**——CSShared `GiftData.ChangeGiftBuyInfo` 里 7002 每日储蓄罐的购买时间戳取整写 UTC 当日 0 点，通用滚动 24h 校验数学上恰好等价于"次日 UTC0 解锁"，三层口径一次对齐；老客户端不用发版即被修（buyingTimes 是服务端权威数据重登同步）。⚠️部署：GiftData 经 `server/GameServer/CSSharedGame@` 软链编进 **GameServer 主程序集，须随服务端完整发布，不能只热部 Hotfix dll**。已核实 Pack Group 8/11 两档独占无跨礼包影响；本地 dotnet build GameServer 0 错误。手法沉淀：零接触 plumbing 提交（工作树在 feature/skin-moment 脏着没动）。

## 关联
- [[reference_x3_client_new_ui_workflow]]（UIPart/prefab四件套）· 储蓄逻辑=KB `X3_异国美酒储蓄罐\异国美酒储蓄罐_可重复购买改造_策划案.md` ⚠️实装差异节
- 美术：HUD储蓄罐小图标待出（参考活动入口124×136透明底），临时可裁获取途径卡现图
