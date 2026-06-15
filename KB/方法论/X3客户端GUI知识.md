---
tags: [kind/方法论, domain/前端, proj/X3]
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

## 待补（这里随项目积累继续加控件模式）
- 价格购买按钮 / 倒计时 / 道具格 等**业务级可复用组件**清单已在 memory `reference_x3_client_new_ui_workflow`。
- 后续遇到新控件模式（弹窗 / 红点 / Tab 页签 / LoopScroll 大列表虚拟化 等）往本文「控件模式库」追加。
