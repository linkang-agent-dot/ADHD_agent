---
name: x3-actvvoyage
description: X3 航海之路大富翁式活动的地块美术配置+渲染全链路，换皮/配活动时查每个地块图怎么写进去
metadata: 
  node_type: memory
  type: reference
  originSessionId: 490ce72b-3baa-4614-9fe0-430f6331e079
---

X3 **航海之路 = 大富翁式棋盘活动**（ActvType=28，全表唯一；主活动图标用 Monopoly_* 模板）。配/换皮时查这条链路，不用再追代码。

## 配置表（`C:\x3\gdconfig\tsv\ActvVoyage__*.tsv`）
- **ActvVoyage**：主活动。ContentID 2801；字段 IslandGroup / LotteryItemID1(普通抽卡1057) / LotteryItemID2(精准抽卡1058) / TreasureItemID(神秘宝藏1059) / OtherReward(阶段奖励组) / **DKRoleMedel(角色模型,如 DK_Role_Bunny)**。
- **ActvVoyageIsland**：24 个地块（IslandID 1~24，对应界面 1~24 号岛）。每行 = IslandType + ExpGroup(等级组) + IslandName/Story(TXT_) + **EventGroupID**(指向 Event 表)。**Island 表本身没有美术字段**。
  - IslandType：1=起始岛 / 2=宝藏岛 / 3=神秘岛 / 4=钻石岛 / 5=幸运岛。
- **ActvVoyageEvent**：地块事件 + **`DKImg`(地块图，美术就在这)**。按 **(EventGroup × Level)** 给图。EventType 1=奖励道具(EventParameter1=道具)，2/3=神秘岛随机事件。
- **ActvVoyageLevel**：ExpGroup=1，地块可 lv1→5，升级经验 2/3/7/15（满级 5）。

## 🎨 地块美术 = ActvVoyageEvent.DKImg（核心）
**地块图不写在 Island 表，写在 ActvVoyageEvent.DKImg，且按等级换图**（岛屿升级 → 换更高级的图）。
图集约 **4 套基础岛图**（命名 `DK_img_Activity_icon_island_{变体}_lv{等级}`）：
- `..._island_4` 起始岛（单图）
- `..._island_1_lv1~lv5` 幸运岛/部分钻石岛（5 级）
- `..._island_2_lv2~lv5` 钻石岛高级（多级）
- `..._island_3` 神秘岛（随机事件 EventType 2/3，单图）

## 代码渲染链（`client\Assets\Scripts\UI\Actv\`）
- 棋盘 24 格**位置写死在 prefab**：`UIActvVoyage.cs:41` 按固定路径 `Root/Animation/Middle/GridGroup/{1..24}` 找 GameObject。**布局/移动动画不是配置驱动，是美术摆在 prefab 里的**（`UIActvVoyage.prefab`）。
- 每格取图链（`GridItem.cs:84-94`）：
  ```
  格子 mIndex(1-24)
   → ActivityUtils.GetActvVoyageIsLandCfgId(contentId, mIndex)        → islandId
   → CActvVoyageIsland.I(islandId)                                    → islandCfg
   → IslandType ∈ ACTIVITY_VOYAGE_CAN_LEVEL_UP_LAND_TYPE ? 当前level : 0
   → ActivityUtils.GetActvVoyageEventGroupFirstId(EventGroupID, level)→ eventId
   → CActvVoyageEvent.I(eventId).DKImg                                → DK_ 字符串
   → UIHelper.SetImageWithDisplayKey(mTFWImageImgIsland, DKImg)       → DisplayKey→贴图
  ```
- 其他美术挂点：角色模型 `ActvVoyage.DKRoleMedel`(UIActvVoyage.cs:87)；抽卡道具图标走 `Item.DKIcon`；UI 特效 prefab 写死(`Fx_Ui_UIActvVoyage_WaterPattern/_Wind`、`Fx_Box_voyage`)。
- DK→贴图统一走 `UIHelper.SetImageWithDisplayKey`，DisplayKey(DK_名)→GUID 资产（注册见 [[reference_x3_client_resources]]）。

## 换皮要改什么（7月用它做主题时）
1. 出新主题约 **4 套岛图**（island_1 lv1-5 / island_2 / island_3 神秘 / island_4 起始）+ 角色模型；
2. 客户端注册新 DK→GUID 资产；
3. 改 `ActvVoyageEvent.DKImg` 指向新 DK_ 名（若复用同名 DK，直接换贴图、配置不动）；
4. **24 格棋盘位置/移动动画 prefab 现成，零改动**。

## 🔁 新增 UI（进度条/特效）优先复用现成件（2026-06-04 珍珠贝进度系统沉淀）
"航海之路新增寻宝进度条+流动填充+珍珠贝飞入"——三件全部复用现成，**零新美术**：
- **通用进度条 9-slice**：底框 `Common/Bg_CM_Keji_jinduantiao_Zhihui.png`(灰槽) + 填充 `Common/Bg_CM_Keji_jinduantiao1.png`(32×32，Image.color 可 tint 任意色)。Filled+Horizontal 控 fillAmount。全局通用，放哪不违和。
- **填充流光特效**：`Effect/Prefabs/UI/Common/Fx_Ui_FillArea.prefab`（内 `liuguang` 粒子+UV滚动，即填充区域流光）。
- **飞入拖尾**：`FX_Trail_Long.prefab`；**到达吸入光**：`FX_Sparkle_Long.prefab` / `FX_ui_icon_circle11.prefab`（均在 UI/Common）。
- 珍珠贝图标已出：`KB\产出-本地化与美术\_process\绿壳\green_shell_nobg_full.png`。
- 教训：**新增 UI 特效/进度条先翻 `UI/Spirits/Common` + `Effect/Prefabs/UI/Common`**，多半有现成；AI 生图/特效美术是兜底不是首选。程序落地需求见 `KB\产出-交互原型\X3_2026深海节\珍珠贝进度系统_程序落地需求.md`。

## 开启链路（排期）
ActvOnline 102801「航海之路」(Type28) → TimeController=TimeCycle **2702**「海域开放第13天开，持续5天」(TriggerType=4 海域开放，X3 中期活动主时钟)。子活动兑换101332/拼图1018091/BP1022091 TimeController 为空（疑似随主活动容器开，待确认服务端 Type28 逻辑）。详见 [[reference_x3_timecycle]]。
