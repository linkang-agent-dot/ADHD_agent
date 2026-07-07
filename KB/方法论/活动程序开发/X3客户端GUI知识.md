---
tags: [kind/方法论, domain/前端, proj/X3, year/2026-06]
---

# X3 客户端 GUI 知识

> X3 客户端 UI 的可复用做法与控件模式集合。技术栈 = **纯 UGUI + prefab + 代码生成绑定**（无 UI Toolkit / FairyGUI；X2 试过 UI Builder 没落地，别引入）。
> 配套：新增一个完整活动界面的链路（4 件套 / 路由分流 / 暗坑）见 memory `reference_x3_client_new_ui_workflow`；本文专收**控件级模式**。

---

## 控件模式库

### 1. 可滑动 + 居中的列表（奖励 / 道具列表）

**场景**：一列奖励/道具，数量不定——多了要能滑动看，少了要居中不靠边。
**反面教材**：把整列 `localScale` 死缩硬塞进框（静态、多了挤、少了靠左堆）——❌ 别这么做。
**专业做法**（2026-06-15 莫琪 GUI 做世界杯竞猜界面 `UIActvWorldCupGuess` 验证）= **三件套**：

| 件 | 挂在哪 | 关键设置 | 作用 |
|----|--------|----------|------|
| **① 滑动** | `RewardList` 节点挂 `ScrollRect` | `m_Horizontal:1` `m_Vertical:0`（只横滑锁竖滑）；`m_MovementType:1`(Elastic 弹性回弹) + Elasticity 0.1 / Inertia 1 / DecelerationRate 0.135（手感）；连 `m_Viewport` + `m_Content` | 物品多能滑 |
| **② 居中** | `Content` 节点挂 `GridLayoutGroup` | **`m_ChildAlignment: 4`（=MiddleCenter，命门！）** 物品没填满时整体居中不靠左；配 `m_CellSize`(如 180×180) / `m_Spacing`(如 12×4) / `m_Constraint:1`(FixedColumnCount) + `m_ConstraintCount` 控行列 | 物品少则居中 |
| **③ 内容自适应** | `Content` 节点同时挂 `ContentSizeFitter` | `m_HorizontalFit: 2`(PreferredSize) | 内容宽度随物品数自动撑开，**ScrollRect 才知道能滑多远**（漏了=滑不动/滑过头） |

**节点层级**：`RewardList(ScrollRect)` → `Viewport(Mask/RectMask2D 裁溢出)` → `Content(GridLayoutGroup + ContentSizeFitter)` → 各物品格。
**多列**：左右两列（`ColumnL` / `ColumnR`）各自独立一套同样结构。

**一句话心法**：**滑动容器(ScrollRect) + 居中布局(GridLayout MiddleCenter) + 内容自适应(ContentSizeFitter)，永远别用缩放硬塞。**

**枚举速查**（手编 prefab YAML 时对照）：
- `ChildAlignment`(TextAnchor)：0 UpperLeft / 1 UpperCenter / 2 UpperRight / 3 MiddleLeft / **4 MiddleCenter** / 5 MiddleRight / 6 LowerLeft …
- `Constraint`(GridLayoutGroup)：0 Flexible / 1 FixedColumnCount / 2 FixedRowCount
- `MovementType`(ScrollRect)：0 Unrestricted / 1 Elastic / 2 Clamped
- `ContentSizeFitter.Fit`：0 Unconstrained / 1 MinSize / 2 PreferredSize

---

### 2. 从 prefab 反查真实 sprite → 纯真素材还原界面模板（零AI拼装·2026-06-18 养成手册案）
要"还原某个现有界面的真实模板"做交互原型/效果图（保真=prefab本身、且每块=独立真实组件，天然好拆）：
1. **抽 GUID**：`grep -oE "m_Sprite: \{fileID: [0-9]+, guid: [a-f0-9]{32}" <prefab> | grep -oE "[a-f0-9]{32}" | sort -u`
2. **GUID→PNG 反查**：扫 `Assets/` 下 .meta 文件头部 `guid:`，命中即 `路径[:-5]`（py: os.walk + 读前400字节正则 `guid:\s*([a-f0-9]{32})`）。
3. **拷进原型同目录 `_assets/`**（素材化自包含，零绝对路径），HTML 用 `background:url(./_assets/x.png) center/100% 100%` 拼，9-patch 框用 `100% 100%` 拉伸。
4. **截图自检**：`chrome --headless --disable-gpu --screenshot="<绝对路径>" --window-size=W,H --hide-scrollbars file:///<url编码路径>`（⚠️ 截图输出必须**绝对路径**否则"拒绝访问"；中文路径要 URL 编码）。
> 命名线索：sprite 名常带活动语义（养成手册=`*_nourish*`，nourish=养成）；一套活动美术通常同前缀邻近放（Activity/ 下 nourish/_1/_2/_3 = 主视觉/锁格/解锁格/大面板）。新页签等原界面没有的件，复用同风格真实件(如金按钮 `img_cm_anniu1_gold`)拼，或去带该控件的 prefab(BP/Tab类)抠。范例：`KB\产出-交互原型\X3_英雄养成手册\*_真素材拼装_v1.html`。

### 3. 活DOM元素叠"烤死的图槽"对齐痛点 → 测槽坐标精准贴(2026-06-18 养成手册案)
**症状**：把活控件(切换按钮/页签)叠在一张"已画好凹槽/槽位"的底图上时，控件总跟画死的槽对不齐(box-in-box、留白不均、偏上/偏下)。**根因**：活元素位置靠手调、烤死的槽靠像素，两套坐标系，手调必飘。**反例参照**：纯CSS自洽原型(无烤死槽)永远不会有此问题——所以能全CSS就别烤槽。
**若必须用烤槽底图，解法=测量槽的真实像素坐标再贴**：
1. PIL沿底图中线竖扫每行亮度，找"亮带(凹槽)"上下edge + "暗线(金线分隔)"y → 算出槽的 y%/高度%（横向同理扫一行找左右edge）。
2. 活元素按**百分比**定位贴进槽中心(`top/height` 用算出的%；底图 `background-size:100% 100%` 时 x/y% 直接对应)。
3. **去掉活元素自身的背景框**(border/bg)——否则槽里再套一个框=box-in-box；让活元素"住进"画好的槽，不自带容器。
> 养成手册实测：切换按钮原 top:78(掉到分隔线上)→错位；竖扫测出凹槽在 y5.3%~14.6%(中心~10%)→改 top:28/height:52 居中贴入 + 去掉 .switch 背景 → 对齐。范例 `KB\产出-交互原型\X3_英雄养成手册\*_真素材拼装_v1.html`。

- **★动 AI 生成"新美术"前先查 `_assets`/主界面切图清单（2026-07-01 养成手册踩坑）**：X3 活动界面惯例是**结构件 100% 复用游戏真实 sprite**，别一看设计稿有个"书本徽章/丝带"就派 GRFal 生成——项目 `_assets` 里真素材通常已齐（书本有 `icon_Skill_Book_1_3`、角标有 `img_gift_bg_Discount`、面板/框/按钮/关闭全现成）。先查再决定出不出新图，多数是 0 新美术全 copy-and-swap。字号+金渐变规格照世界杯：米色羊皮纸面板上的字 `Gradient2` 两端改深棕 `7A4F1D→5A3A12`+保描边，深色底字保模板金渐变，Best Fit 勾着填 Max Size。

### 4. 两栏 / N选一购买弹窗 = 复制世界杯 UIActvWorldCupGuess 改名（2026-06-30 养成手册双版本案）
- 任何「两栏 / 多选一购买」弹窗（二选一档位 / 竞猜 / 对比礼包）别从零搭：**复制 `UIActvWorldCupGuess.prefab` 改名**，删竞猜专属（Match 对阵 / ApprovalRating / BonusTips / LockTips / 装饰 TicketHero·GiftBox·BonusBar），两栏 ColumnL/R 改名重绑即可。它自带「每栏 RewardList 道具格 + UIBtnPurchase 购买键 + txt_state 已购态 + 客户端互斥」= 直接复用的内脏。
- **RewardList / UIBtnPurchase 是"内脏"**（前者 LoopScrollRect+道具模板，后者价格/支付/限购总成），删了要去别 prefab 偷，复制整栏连带保留最省。
- **★RewardList 横排↔竖排切换（2026-07-01 养成手册实证）**：世界杯那套 RewardList 是 **SG `LoopScrollRect` 单行 loop**（`ItemUnitLoopLine` 只喂数据、真正排布靠它包的 LoopScrollRect），**不是** 上面「三件套」的 GridLayoutGroup 静态网格——两套并存别混。改方向 = 每栏 prefab 改两处：① 该 `RewardList` 节点的 **`ScrollRect`**：`m_Horizontal`/`m_Vertical` 对调（横=1/0，竖=0/1）；② 同节点的 **`LoopScrollRect`**：`direction` 字段（**0=横 1=竖**）。`ScrollRectFilter.bVertical` 会在 OnEnable 自动 `= scrollRect.vertical`，**不用手改**。Content 锚点 top-center(0.5,1)+pivot top(0.5,1) 即竖排从顶往下排（世界杯原始 content 已是这锚点，切竖无需再调）。**portrait 竖栏必竖排**——横排单行填不满高栏子。
  - **★★改 prefab 文本前先确认 Unity 没开着这个 prefab（2026-07-01 血泪）**：Unity 打开着某 prefab 时，它持有内存版；一旦保存/切焦点/reimport 就用**内存版覆盖磁盘**——你在文本里改的 direction/anchor 全被静默还原（实测竖排改完被打回横排）。**规避**：① 要么关掉 Unity 里那个 prefab 再改文本；② 要么直接在 **Inspector 里改**（Unity 开着时 Inspector 才是权威）。方向/尺寸这种在 Inspector 点几下就好，别跟开着的 Unity 抢文本。
  - **★UI 显示空/旧 = 先看 Console 有没有编译错误（2026-07-01）**：有 CS error 时 Unity 进 play 跑的是**上一次成功编译的旧程序集**，你的新代码（如奖励合并）根本没生效 → 界面空白或还是旧样子，容易误判成布局 bug。**排查第一步永远是确认 Console 全绿**，再谈布局。
  - **★奖励只有几种道具时横排就够，别硬上竖排（2026-07-01）**：合并后 icon 数 = distinct ItemID 数；养成手册只 4 种 → 4 个 icon 横排一行正好，不用竖排。**先看合并后到底几个 icon 再决定横竖**，别为想象中的"很多"提前改竖排。
  - **★横→竖后必查 RewardList 框尺寸 + Viewport 溢出残留（2026-07-01 血泪，改完 direction 只是第一步）**：世界杯横排的 RewardList 是**又矮又宽的横条**（实测 sizeDelta 611×403 + `LocalScale 0.6` 缩到视觉 ~242 高），直接切竖排 → 只露 1-2 行、下面全裁掉，用户报"显示不全"。**两处必改**：① **RewardList RectTransform 加高**（sizeDelta.y 403→~1000，注意有 scale 0.6 要除回来算视觉高；宽度 ×scale 别超栏宽，611×0.6=366<栏500 才不溢）；② **Viewport 的 sizeDelta 归零**——横排残留常给 Viewport 叠一个诡异的 `sizeDelta.y:1150`（stretch 锚点下 = 比框高 1150，遮罩范围溢出框外，item 渲染到弹窗外被上层裁），改成 `{x:0,y:0}` 让遮罩=框本身。改完 Pos Y 可能顶到栏里 BookIcon/名字/购买键，Inspector 拖 Pos Y 落中段空档。图标偏小的根源常是那个 `LocalScale 0.6`，想放大把 scale 调回接近 1（守住 宽×scale<栏宽）。
- **★奖励预览：合并 vs 铺全 = 看横竖排 + 道具品类数（2026-07-01 养成手册实证，含踩坑）**：`EndowHelper.GetPreviewEndowItemsAndMerge(gids, itemIDs, needMergeNum:true)`（签名在 `EndowHelper.Client.cs`）会**按 ItemID 把相同道具跨条目合并累加**。**关键坑**：合并后 icon 数 = **distinct ItemID 数**，不是天数！养成手册 30 天翻花样其实只用 4 种 ItemID（52003/7001/19003/165905，每天数量不同），一 merge 就**塌成 4 个 icon**，用户嫌"少了/没匹配全"。**正确判据**：① **横排单行放不下** → 用 merge 折叠成几类（省地方）；② **竖排 loop 能滚** → 直接 `GetPreviewEndowItems(gids)` **铺全**（30 天 30 条、豪华 60+满勤），滚动看全才有"奖励很多"的观感。翻倍档铺全 = 把同 rewardId 塞两遍（60 条成对出现）；翻倍档要显 ×2 数量又只想 30 条则用 merge（但会塌成品类数，二选一）。范例 `UIActvLoginChoice.RefreshPreview`（竖排=铺全）+ `UIActvLogin.UIActvLoginSlotItem.BindData` isLuxury 分支（单天=doubled+merge 显 ×2 数量）。
  - **★★合并数量走 loop 会丢失(2026-07-01 硬核坑·排查1h)**：`GetPreviewEndowItemsAndMerge` 把累加总量写在 **`showNum`**(非 num)；`ItemUnitView.Refresh(EndowItemData)` 显示时**优先读 showNum**——所以**直接调 `ItemUnitView.Refresh(mergedData)` 的路径(如日历 slot `mItemUnitViewXxx.Refresh(...)`)合并数量正常**。但**走 `ItemUnitHelper.RefreshLoopReward(go, list)` 循环渲染的路径会丢 showNum**：中间 `ItemUnitLoopLine.Refresh<T>`→`TypIdValHelper.Create` 把每个道具重包成 `new IDValView(cur)`，IDValView 只按 `IIDVal` 接口拷 type/id/**num(Val)**，**拷不到 showNum**(不在接口上)→ 格子退回显示**首日单量**，看着像"没合并"(其实 icon 已去重、只是数字没累加)。**修法**：合并后把 showNum 落回 num——`foreach(it in merged) if(it.showNum>0) it.num=(int)it.showNum;` 再传给 RefreshLoopReward(EndowItemData.num 是 `int` 可写；showNum 是 long)。范例 `UIActvLoginChoice.CarryMergedNumToVal`。**判据**：合并数量对不对 = 看该界面走的是 ItemUnitView.Refresh 直连(OK) 还是 RefreshLoopReward 循环(要落 num)。
  - **附**：Reward 表(`Reward__Reward.tsv`)每行 = RewardID(col2)+seq(col3)+**ItemID(col4)**+名字(col5)+数量(col6)。**名字列是非权威显示标签**，克隆残留常与 ItemID 对不上（同一 165905 写"传奇技能书/钻石/蓝图"多种名）——**客户端预览按 ItemID 查真 Item 表显示，不受错名影响**；诊断"奖励种类少"要看 distinct ItemID(col4)，别被 col5 花名骗。
- **互斥范式**：服务端存各档购买态（权威），客户端 `RefreshSideState`（买一档 → 另一档购买键 `Hide`）。代码见 `UIActvWorldCupGuess.cs`；养成手册 `UIActvLoginChoice.cs` 照此写。
- **绑定字段名是硬约定**：`Auto_*.cs` 由 prefab 绑定配置生成，字段名必须与业务 `.cs` 一字不差，对不上 = 编译失败。出拼装指南必给「节点路径 → 绑定字段名 → 类型」表（同路径在不同 prefab 字段名可不同，作者手设）。
- **交互式拼装指南范式**（给 Unity 人手把手）：带勾选进度条 + localStorage 的 HTML，每步「复制现成 → 改名 → 换图」+ why/warn/翻车点 + 名字终检 path 清单。范式 = `世界杯竞猜界面\prefab拼装指南.html`、`英雄养成手册\客户端prefab拼装指南.html`。
- **★UI 生成器命名约定（2026-06-30 实证，拼 prefab 必懂）**：`Auto_*.cs` 由 prefab 绑定生成，两类绑定命名规则不同——① **点击监听**：方法名与字段名**按节点名自动派生** = 方法 `OnBtn{节点名PascalCase}Trigger`、字段 `mBtn{节点名}`（证据：节点 `Info`→`OnBtnInfoTrigger`/`mBtnInfo`；节点 `btn_info`→`OnBtnBtnInfoTrigger`/`mBtnBtnInfo`）→ 想要业务代码里的 `OnBtnCloseTrigger` 就把节点命名为 `close`（不是 btn_close，否则多一截 Btn）。② **GameObject/组件绑定**（mTextXxx/mGoXxx）：字段名在绑定面板**手动设**，可不随节点名（如 `txt_state`@ColumnL 设成 `mTextStateL`）。**结论**：业务 .cs 先定字段/方法名 → 反推「监听节点取名、组件字段手填」，出拼装指南务必给「节点→字段名/方法名」对照表。
  - **★没有/不该自己跑 UI 生成器时（数值/策划手里没那套客户端构建工具）= 手写 `Auto_*.cs` 救急让代码先编译**（世界杯当初的 Auto 也是手写的，后续客户端跑生成器覆盖无碍）。手写模板：`namespace UI { [GameCommon.Identifier(任意唯一int)] [UIDescribe(assetPath:"…prefab", layer:nameof(UILayer.Window), label:UILabel.Stack)] public partial class UIXxx { private void OnAutoLoad(){ mGoX=GameObject.FindByFullPath("路径"); mTextY=GameObject.GetComponent<TFWText>("路径"); UIHelper.AddListener(EventTriggerType.Click, GameObject, "路径", OnBtnZTrigger, out mBtnZ);} protected GameObject mGoX; protected TFWText mTextY; protected GameObject mBtnZ; } }`。`[UIDescribe]` 的 assetPath 即 WndMgr.Show 加载 prefab 的依据，prefab 必须存到该路径。**手写 Auto 后路径对不上=运行时 Find 返 null(控件点不动/不显)，不是编译错**——故拼装指南要把「prefab 必须有的确切节点路径」单列清单。范例：`Auto_UIActvLoginChoice.cs`（养成手册二选一弹窗，手写）。
  - **★点了正规生成器(UIGeneratorSaveWnd「保存并生成」)但 prefab 节点没配"绑定标记"→生成空 Auto(OnAutoLoad空/无字段)+ 在生成器窗口路径处新建一个空 logic stub(2026-07-01养成手册实证)**。空 stub 有 OnLoad/OnShown/... 且 base 写成 `UIBase`(非你的 `UIBase<TData>`)→ 与你手写 logic **同名 partial 类方法/base 冲突→编译报错**。**解**：① `git checkout HEAD -- Auto_xxx.cs` 恢复手写 Auto(按路径找·不吃标记) ② **删掉生成器新建的空 stub**(它在生成器"窗口路径"对应的目录·非你 logic 目录) ③ 把手写 Auto 的 `[Identifier]` 改成生成器注册的那个 ID(SaveWnd 里显示·如 2039220338)对齐注册。**正规生成器要真产出必须先给 prefab 节点配绑定标记(客户端框架的事·问负责程序)**;策划/美术侧走手写 Auto 即可。生成器的 SaveData(`Editor/UITools/SaveData/<窗口>.asset`)记录窗口 ID/模板,可一并提交。
- **★X3 UI 逻辑代码 3 个常见编译坑(2026-07-01 养成手册弹窗实证)**：① **弹窗自关闭用 `CloseSelf()`,不是 `Hide()`**(`Hide` 不存在于 UIBase<T>;`WndMgr.Show<T>` 打开的窗自关也用 CloseSelf;范例 HeroChampionReward/UIIdleDefeat)。② **`EndowHelper` 在 `using GameCommon.Endow`**(奖励预览 GetPreviewEndowItems 靠它)。③ **手写 Auto 里别加 `using UnityEngine.EventSystems`**——会和 `TFW.EventTriggerType` 歧义(CS0104);`UIHelper.AddListener` 用的是 `TFW.EventTriggerType`(由 `using TFW` 提供),官方生成的 Auto 都不加 EventSystems using(logic 文件为 PointerEventData 可加,不冲突因不引用 EventTriggerType)。④ **`EndowItemData` 在 `cspb` 命名空间，裸名不可见(CS0246/CS0266)**——`EndowHelper.GetPreviewEndowItems*` 返回 `IReadOnlyList<cspb.EndowItemData>`。**内联传参没事**(`Refresh(GetPreviewEndowItems(...)[0])`)，一旦想**显式声明变量**(如 ×2 分支要 if/else 赋值)就得写全限定 `IReadOnlyList<cspb.EndowItemData> x;` 或加 `using cspb;`（`using GameCommon.Endow` 只给 EndowHelper 不给 EndowItemData）。
- **★多档活动 giftId≠activityId 的两个坑（2026-06-30 养成手册审代码实证）**：单档活动惯例 giftId==activityId，但「一活动挂多礼包」时副档 giftId 由服务端 IdGenerater 生成 ≠ activityId，连带两处必处理：① **客户端购买成功事件**（OnBuyGiftSuccess）默认 `if(giftID!=activityId)return` 会漏掉副档购买→主界面不刷新（购买键不消失/不可领），必须额外比对副档 giftId（`GetGiftIdByPackCfgId(activityId, 副Pack)`）；② **服务端购买标记/退款清标记** `SetActivityGiftPurchased`/`ClearActivityGiftPurchasedOnRefund` 入参是 giftId、内部 `GetActivityData(giftId)` 只认 activityId，副档要先 `GetActivityIdByGiftId` 反查再设；③ 服务端二选一拦截按 ContentID 找配置时要带 `ActvType==目标类型` 闸门，防 ContentID 跨表撞号误伤别的活动礼包。

### 5. UIWidget 挂件模式 + 纯手写 prefab YAML 加节点组（2026-07-07 储蓄罐HUD案·全流程无Unity验证通过）
**适用**：给现有界面加一个小挂件（入口按钮/角标/状态牌），不想动界面主逻辑、无 Unity 在手也能落代码。
- **UIWidget 挂件范式**（范例 `UI/Public/UIBtnGift.cs` + 本案 `UI/Gacha/UIPiggyBankHudEntry.cs`）：类继承 `UIWidget`（TFWCore/Script/UIBase/UIWidget.cs，**非 MonoBehaviour**，prefab 不引用脚本 guid，但 .cs 仍要 .meta——手写=抄同目录 meta 换 uuid4 guid）；宿主 prefab 里放一个节点组，宿主 OnLoad `mUIXxx = WidgetContainer.AddSingle<UIXxx>(mGoXxx)`（**AddSingle 对 null GO 会抛 ArgumentNullException，节点可能缺就先判空**）；挂件内 `mGo` = 被挂节点，子节点 `mGo.transform.Find("名字")` 拿（找不到 `D.I?.Error` 报警别静默）。
- **挂件生命周期 4 坑**：① 事件只在 Shown 态注册 → Refresh 首行 `if(!IsActive) Show()`（UIBtnGift 同款）；② `TimeUpdateText` 被禁用**不停表**（FrameUpdateRegistry 跑到 endTime，onEnd 会在隐藏态触发）→ **必须 override `OnHide()` 兜底 `UIHelper.StopTiming`**（Hide/Destroy/Show重入三路径全覆盖）；③ 宿主接线四件套 = OnLoad挂载/OnShown转发(去重标记先重置)/RefreshView转发(含判空分支 Refresh(null))/OnHidden转发；④ "每登录一次"判定 = `static object` 与 `G.Player` ReferenceEquals（ClientPlayer 每登录 new、登出置 null，已核实）。
- **手写 prefab YAML 加节点组方法论**（本案 235 行纯增、12 项结构审查全绿）：① 模板块**从同 prefab 内抄**（GameObject/RectTransform/CanvasRenderer/TFWImage/TFWText 整块，字段集不脑补，TFWText 连字体材质抄现成倒计时文本）；② 新 fileID 用统一前缀大数（如 88990011223344550xx），写前 grep 全文件零碰撞；③ **父子接线三处缺一不可**：新 GO 的 m_Component 表 / 新 RT 的 m_Father+m_Children / **父节点 RT 的 m_Children 追加**；④ sprite 引用 `{fileID: 21300000, guid: <png.meta的guid>, type: 3}`（单 sprite 默认 21300000，meta textureType:8 确认）；⑤ 新块全放文件末尾（YAML 文档顺序无关），保持原行尾（X3 prefab 纯 LF）；⑥ 自检 = `python C:\ADHD_agent\scripts\unity_prefab_tree.py <prefab> 5` 看到新节点 + fileID 引用闭合 + `git diff --numstat` 纯增。改前备份；**Unity 开着该 prefab 时禁改文本**（内存版覆盖磁盘，见 §4 血泪）。
- **审查清单可复用**（给审查 agent 的 8 条：组件表回指/父子闭环/fileID唯一/sprite guid对meta/m_Script guid同文件一致/classID匹配(1=GO,224=RT,222=CR,114=Mono)/行尾BOM文件尾/惯例字段齐）——本案审查 prompt 见 memory `project_x3_piggybank_hud` 关联会话。

## 待补（这里随项目积累继续加控件模式）
- 价格购买按钮 / 倒计时 / 道具格 等**业务级可复用组件**清单已在 memory `reference_x3_client_new_ui_workflow`。
- 后续遇到新控件模式（弹窗 / 红点 / Tab 页签 / LoopScroll 大列表虚拟化 等）往本文「控件模式库」追加。
