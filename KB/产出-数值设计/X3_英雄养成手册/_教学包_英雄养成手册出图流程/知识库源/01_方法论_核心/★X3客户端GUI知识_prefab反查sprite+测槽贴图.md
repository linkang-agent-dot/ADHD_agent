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

## 待补（这里随项目积累继续加控件模式）
- 价格购买按钮 / 倒计时 / 道具格 等**业务级可复用组件**清单已在 memory `reference_x3_client_new_ui_workflow`。
- 后续遇到新控件模式（弹窗 / 红点 / Tab 页签 / LoopScroll 大列表虚拟化 等）往本文「控件模式库」追加。
