---
name: reference-x3-voyage-piggybank
description: X3 大富翁(Voyage)存钱罐实现机制+复购化(加档$49.99/$99.99+UTC0日刷)评估结论；动这个模块先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4cf1282b-7643-418f-9527-24446c5a16c2
  modified: 2026-07-27T11:56:55.818Z
---

# X3 大富翁（Voyage）存钱罐 · 复购化全案（2026-07-27 一天内评估→实现→用户实测收官✅）

> **🚀接管摘要（冷启动看这段就够）**：复购化=三档($19.99/$49.99/$99.99·独立阈值10/20/30个6·各档UTC0日刷·"买完才算"跨天清储蓄)已全量落 dev_festival 并经用户 Editor 实测通过（买→切档→跨天清零→重攒→复购全闭环）。x3-project 提交链=bfe6718→ec82be5→(v3)→cde5510(v4收官)；gdconfig=f5594333+1cba0669+v3 Text。**遗留3件**：①新档产出数值=档1等比×2.5/×5占位,上线前策划复核 ②新增文案/礼包名的完整 i18n 跑 x3-translation-automatic ③正式上线随完整发版(CSShared+proto 改动,禁只热更)+马戏 2803 侧仅配置就绪未实测。测试环境=worktree 本地服3080(时间持久在9-29,恢复用GMClearServerTimeOffset不可靠→drop_db)。奖励条横滑最终版=**张力正修 `3cca31512d6`**(弃 ChildGroupController 改 UIWidgetList+关格子图形 raycast 穿透到热区,替代我的 SRFilter 运行时接线;我的 content 定宽/BoxScroll 结构/Auto 路径全保留,弹窗与跨天逻辑未动——丢失审计已做,零丢失);两方案对比与 ChildGroupController 深坑已归口 GUI KB。

⚠️ 与异国美酒储蓄罐（Gift/PiggyBank 表系统，[[project-x3-piggybank-hud]]）是**两套系统**，别混。

## 现状机制（代码核实）
- **配置**：`ActvVoyage` 表三字段 = `PiggyBankPackID`（单档，只有一个）/ `PiggyBankTriggerStep` / `PiggyBankNeedCount`。
- **服务端** `server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.Voyage.cs`（~:536）：走步出指定点数 → `voyageData.piggyBankCount++`，**只累计不拦截、不设 bought、购买不消耗 count**；购买判定全在客户端。
- **购买** = 普通 Pack 走 gift 系统；限购靠 `Pack.BuyCount` vs `giftInfo.purchaseNum`（客户端 `ActivityMeta.Voyage.cs CheckCanShowVoyagePiggyBankRedPoint` :92-128）。现状单档 $19.99 单笔买断。
- **UI**：`UI\Actv\UIActvVoyage.cs`（存钱罐段 ~:956）。

## 复购化需求评估（8-10月需求点4：加 $49.99/$99.99 档 + 各档 UTC0 日刷复购）
**结论=能搞，3-5 人天**（配置 0.5-1 / CSShared 日重置泛化 0.5 / 客户端多档 UI+红点 1-2 / 测试 1；服务端计数逻辑不分档=零改）。
- 多档 = ActvVoyage 加字段 + Pack 克隆新档（各档独立 Group，抄美酒双档先例）。
- UTC0 日刷 = 泛化 MR!718「购买时间戳取整到 UTC 当日 0 点」机制（现只对 ResourceID 7002 生效，改成按 Group/标记字段触发），一处改三层口径自动对齐。
- ⚠️ **排期硬约束**：取整改动在 CSShared → GameServer 主程序集，**必须随服务端完整发版，禁只热更 Hotfix**（美酒罐 MR!718 已踩实）→ 需求要挂正式版本（0.3x）。
- **✅UI 已拍板（2026-07-27 用户）**：单卡自动切档 + **手动切档按钮**（循环切三档，可跳看/买任意档）。自动切规则默认=显示第一个今日未买档（美酒罐同款）；已买档显示该档 UTC0 倒计时。
- 余 1 点待拍：储蓄进度三档共用（现状天然成立·已按此实现）vs 各档独立阈值（要再加配置字段）。

## ✅代码已落地并合入 dev_festival（2026-07-27，commit `bfe6718bb2f`，合入=merge `c0eec2214b9` 已验 origin ancestor）
- 合并期间撞两次竞态（机器人/其他工作推 dev_festival），按 SOP「合origin进feature→ff推」重合两轮成功；`git merge` 超时被杀会留 stale MERGE_HEAD（commit 已成、双parent+difftree干净即真完成，删 `$gitdir/MERGE_HEAD` 即可）。
- 用户告知：美酒 MR!718 早已合过，dev_festival 上 GiftData 无取整实现≠冲突隐患（勿再预警）。
- worktree=`C:\x3-wt-piggybank`（sparse：server+Scripts+Protobuf+依赖4路径+scripts+.githooks；junction 20条已建）。基于 origin/dev_festival。
- 6文件+307行：①CfgProto ActvVoyage 加 `PiggyBankPackID2/3`（字段13/14=tag104/112，手写照生成物样式）②新建 CSShared `VoyagePiggyBankPacks`（DataModel命名空间；从CActvVoyage收集档位礼包ID，Cache按Instance引用失效防热重载stale；RoundToUtcDayStart）③`GiftData.ChangeGiftBuyInfo` 购买时间戳对存钱罐档取整UTC0（MR!718机制泛化，注意 **dev_festival 上没有 MR!718 原实现**——美酒那套在此分支仍是三层特例，将来 dev 合入时 ChangeGiftBuyInfo 会撞小冲突，union即可）④客户端 ActivityMeta.Voyage 红点改"任一档可买"+`IsVoyagePiggyTierBuyable`/`GetVoyagePiggyTierCdEndTime` ⑤UIMonopolyPigBanck 自动选档+切档按钮+CD倒计时（`BtnSwitchTier`/`TxtTierCd` 节点缺省兼容=退化单档现状）。
- **验证状态**：dotnet 三 Hotfix 0错误✅；客户端 Unity 编译**未验**（客户端文件 dotnet 不碰）；端到端未测。
- **待做**：①gdconfig 配置（ActvVoyage 加两列+TableProtoGen 重生成；新档 Pack 克隆=价格$49.99/$99.99+各档独立Group+ColdTime24h+BuyCount清空；**现有档280001/280003 也要同改** BuyCount1→空+ColdTime+Group；现状 Pack=PackType16/Price111/限购1/无CD无组）②新档产出数值待策划 ③prefab 拼 BtnSwitchTier+TxtTierCd ④本地服+GM推时间端到端 ⑤验完合回 dev_festival（非保护，自助合并）。
- sparse worktree 踩坑复证：.githooks 被截断（checkout --还原）；pre-commit 要 scripts/ 在 cone（报"未找到 check_video_assets.py"→sparse add scripts 即过）。

## ✅配置+prefab+本地服全链落地（2026-07-27 下午）
- **gdconfig**（worktree=`C:\X3\gdconfig-piggybank`，feature/piggybank-tiers，commit `f5594333` 已合 dev_festival）：①ActvVoyage 表尾加 PiggyBankPackID2/3 两列（proto 字段 13/14=tag104/112，**已用本地 ExportTable 生成的 .proto 比对手写 CfgProto 一致**）②**马戏 2803 挂 280004($49.99)/280005($99.99)，常驻 2804 挂 280006/280007**（深海 2802 已结束不动）③280002/280003 改日刷=限购空+CD`24h`+组；**6 档独立 Group=1010-1015** ④Reward 新组 1028037(113罗盘/25000钻/125VIP点=×2.5)/1028038(225/50000/250=×5)共享给两活动，seq 16001132-137，**数值占位待策划复核** ⑤Text 补 TXT_Pack_Name_280002/04/05(马戏珍宝罐)+280006/07(克隆280003全语种)。
- **Pack 列速查（本案实测）**：[6]美元备注 [7]PackPrice id($19.99=111/$49.99=116/$99.99=115) [9]PackType [13]Content=RewardID [20]BuyCount [24]ColdTime(格式`24h`) [35]Name [43]Group。ActvVoyage=6 行表头 13→15 列。
- **jolt**：触发失败（Jenkins 172.20.110.29 周日不通）；本地 ExportTable EXIT=0 等价验证。**⚠️Jenkins 恢复后补 `jolt_verify.py dev_festival`** 让 robot 回写 bytes（在那之前主仓 client ProtoGen 的 3 张手动 cp bytes 别被 pull 还原——robot 回写后自然覆盖）。
- **prefab 手术已合入**（x3-project commit `4556234e9f8`）：BtnSwitchTier=CloseButton 同款隐形热区(240x80@-350,-600)+描边文字"切换档位"子节点；TxtTierCd=TFWText(620x54@0,-700)。占位样式，美术可调。
- **本地服已起并验过**（worktree `C:\x3-wt-piggybank\server` 起的 3080/3081，全表预载零 proto 异常）：GM 已开 **102804**（30天窗口）、测试号 **28297**（库里唯一号）已发精准骰 1058×30+普通骰 1057×50。游戏内时间 2026-09-26（旧 offset 持久化）。
## ✅v2 四反馈修复+桥测全通（2026-07-27 晚,全部合入 dev_festival）
- **用户 4 反馈全修**（x3-project `ec82be54504`+gdconfig `1cba0669`，均已合 dev_festival）：①切档按钮加金色九宫底板(BG(1) sprite d2e47f81,Type=Sliced) ②**档位独立阈值** ActvVoyage 加 PiggyBankNeedCount2/3 列(字段15/16=tag120/128)=10/20/30 个6,`VoyagePiggyBankPacks.GetTierNeedCounts`(空回落档1)+红点/弹窗逐档判定 ③自动探索开局解锁=ConstCfg `ActvVoyageAutoUnlockCondition` 30→0(X2 倍率本就无锁,同一常量只锁自动) ④额外奖励条改横滑=BoxScroll 包裹(ScrollRect `0f4296fa`+RectMask2D `3312d773`+content CSF `3245ec92` HorizontalFit=Preferred+Item 宽0→120+HLG MiddleLeft/ForceExpand=0)。
- **桥测实录（DebugUtils 全自动,截图在会话 scratchpad v4_*）**：三档循环 3/10→3/20→3/30→绕回✓·切档按钮点击✓·自动无锁✓·X2✓·奖励条图标+数字原尺寸横滑✓·10/10 满储蓄可买态(锤子动画+红点)✓。**购买/IAP/日刷跨天未实测**（要真买,留用户）。
- **拖不动终极根因（v4 代码铁证,GUI KB 已归口）**：EventTriggerListener 实现拖拽接口+转发只认显式 SRFilter 字段,格子 Item 模板 prefab 自带 Listener 且序列化 SRFilter={fileID:0}（⚠️早期记录误写"运行时挂载"——是跨块正则解析 bug 漏扫了模板组件,prefab 组件归属映射必须逐文档切块解析别用 re.S 跨块）→吞掉全部拖拽。修=RefreshChildCount 后遍历 content 内 listener 统一指到 ScrollRectFilter（UIActvVoyage.cs 定宽代码旁）。症状三分法:完全没反应=事件层/回弹=尺寸/单向=方向初始位。
- **滚动组件鉴别（拖不动两轮排查的终局）**：`0f4296fa`=**LoopScrollRect**(虚拟化循环列表,要 totalCount/数据源,裸配完全拖不动)≠普通滚动;普通滚动=**TFWScrollRect `93998fea`**(ScrollRect子类,+handleDrag/scrollable 两字段);`ca6dfd03`=ScrollRectFilter。guid 反查真身姿势=`git ls-files <目录> | grep meta` 逐个 `git show HEAD:file | grep guid`（工作树 sparse 没铺时）。另:**i18n 多语列空→客户端直接显 key**（用户语言=繁中 col10,新 key 至少填 cn/en/tw 三列）。
- **桥测纪律（2026-07-27 违反过一次,用户 Play 中被我 recompile 冻成"服卡了"）**：触发 `recompile`/`AssetDatabase.Refresh` 前**必查 `Application.isPlaying`**——用户在 Play 时一律不动编译（domain reload 会把运行中的游戏冻住,现象酷似服务器卡死;判"服卡"三件套=日志mtime推进+端口LISTENING+无持续stuck,先排除客户端侧再动服）。
- **桥测三坑**（详见下节+GUI知识库归口）：①Play 中 pull 不重编,退 Play+`AssetDatabase.Refresh`+recompile 才吃到磁盘改动 ②recompile 返回 hasErrors:true 可能是 domain reload 竞态**误报**——判真伪=Editor.log 无新 error CS 行+桥拒连后恢复+eval 新符号可用 ③**reparent 手术必同步 Auto_ 全路径绑定**(断了=OnLoad NRE=界面半初始化:锁不刷/列表不生成,症状分散但同根因)；RectMask2D 会裁掉原设计溢出 rect 的图标(viewport 扩高+content 反向偏移保位)。
- **合并竞态实录**：dev_festival 高频推进(robot 导表回写+他人大合并),ff 推被拒就回炉重合,本地未提交的部署 bytes/占位补丁挡 merge 时 `git checkout --` 丢弃(robot bytes 已上 origin=手动版使命完成;上游已正修 NumericComp=补丁弃用)。**Jenkins 当天恢复,robot-20891 已导第一轮配置**。
- 主仓(Editor)残留:我镜像的 7 文件+3 bytes 为未提交 M(内容=已合并版),robot 二轮 bytes 推上后 `checkout -- + pull --ff-only` 清理对齐。

## 「买完才算」跨天规则（2026-07-27 深夜用户新增设计,已实现待验）
- **规则**：有档位购买后跨过 UTC0 → 储蓄进度清零重攒；没买过的积累跨天保留（"买过的那轮储蓄才被消耗"）。
- **实现（一次性清零状态机,双端同口径）**：①proto `ActivityVoyageData` 加字段13 `piggyBankLastBuyTime`(tag104,int64,UTC0取整;Scripts/Protos/activityVoyage.cs 双端共享一份经 junction) ②服务端登记=订阅 `TEventType.OnBuyGiftForGiftId`(三处fire全入口覆盖,签名 `(long giftId,int cfgId)`)→VoyagePiggyBankPacks.Contains→遍历 Data.activityDict 找含该pack的voyage活动→标记=RoundToUtcDayStart(now)；注册行在 ActivityMeta.cs :65 注册块 ③清零=lazy `NormalizeVoyagePiggyBank`(走步 OnStartActivityVoyageReq 入口):标记>0 且 now-标记≥MS_PER_DAY→count=0+标记归零(防重复清,新攒不再被误清) ④客户端镜像:`GetVoyagePiggyEffectiveCount`=**与服务端同款一次性清零状态机(本地 count=0+标记归零),不能只读判定**——走步回包(StartActivityVoyageAck)只带计数不带标记,客户端旧标记不归零会把跨天后新攒的计数也恒判成0(实翻:用户"投6没计数",服务端数据其实全对);只信同步/本地登记的标记,不做gift时间戳兜底(兜底会在服务端清零后误判)+弹窗买成功本地即时登记标记(UIMonopolyPigBanck.OnBuyGiftSuccess,与服务端同口径取整)。红点/弹窗计数全走 effective。
- ⚠️proto 字段变更=GameServer 主程序集,须停服重编重启(已做);正式上线同样随完整发版。**测跨天类功能推时间一律用 `GMSetServerTimeOffset`(持久化)别用 ByDHM**——中途还要重启服(改代码)时 ByDHM 的推进会被抹掉,跨天测试态丢失(本案实翻一次,时间从9-27弹回9-26被用户当"服卡了")。本地服现持久在 2026-09-27。

## 客户端桥测进行中（2026-07-27 傍晚）
- **DebugUtils 桥可跨会话直用**（client.py 不依赖 MCP 注册）；Editor 曾在 Play(旧程序集)——**Play 中 pull 代码 Unity 不重编，退 Play 才编**，验新代码前必须退 Play+recompile。
- **踩坑① 我的 bug（已修主仓工作副本，待从 worktree 正式提交）**：UIMonopolyPigBanck.cs 加 `using TFW;`(为 TgsHelper) 与原 `using UnityEngine.EventSystems;` 撞出 `EventTriggerType` 歧义 CS0104——**Auto_ 生成文件没 using EventSystems 所以没事，手写文件两个都要就得全限定 `TFW.EventTriggerType`**。教训：给带 AddListener 的 UI 文件加 using TFW 必查歧义。
- **踩坑③ 桥改磁盘源码后 recompile 不生效**：后台 Unity 不 auto-refresh，`recompile` 用的还是旧导入源（报错行列号纹丝不动=铁证）→ 必须先 `invoke UnityEditor.AssetDatabase.Refresh` 再 recompile；Refresh 带出 domain reload 期间桥 10061 拒连是正常窗口（~1min 后恢复），别当故障。
- **踩坑② 他人雷（本地占位补丁勿提交,待海妖侧张力真修）**：dev_festival 既成编译坏——`NumericComp.Data.cs:119 public long MechaDamagePctAdd => NumericData.MechaDamagePctAdd;`(海妖commit) vs 生成码 `NumericValueDictionary.API.cs:671 float MechaDamagePctAdd(GetAsFloat)` → CS0266。本地导表重生成的数值文件也仍是 float=生成码没错，是手写侧类型错。**波及面=客户端 Unity 编译 + 服务端 MapServer.Hotfix（CSSharedHotfix/Map 经 junction 同源）双挂，dev_festival 全线**。本地补丁=`(long)` 强转+注释勿提交（主仓+x3-wt-piggybank 两处都打了）。**须报张力正修**。
- **看效果姿势**：Unity Editor(主仓,已含代码+prefab+3张bytes) Play→登本地服→常驻航海之路→精准骰选 6 点×10 攒满储蓄→开存钱罐弹窗：档1 $19.99 可买→买后自动切 $49.99→切档按钮循环三档→已买档显示 UTC0 倒计时。**未验项=Unity 编译+实机 UI**（unity-mcp 属别的会话接不进）。
