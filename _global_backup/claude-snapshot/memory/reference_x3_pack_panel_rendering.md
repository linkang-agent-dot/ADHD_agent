---
name: x3
description: X3 礼包/活动弹窗背景图来源链路 — Pack.MainBg 优先级高于 ActvOnline.ActvImg；拜访礼包 MainBg 历史都是空，新配千万别填通用模板
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 核心规律

**`Pack.MainBg` 一旦填值，会覆盖弹窗主视觉**，包括节日主背景的渲染。拜访礼包/家具礼包这类挂在活动里的礼包，MainBg **必须保持空**，让客户端走默认渲染（用 ActvOnline 的 ActvImg / 默认主视觉）。

## 弹窗背景的字段来源（按渲染优先级）

| 渲染对象 | 来源字段 | 客户端代码 |
|---------|---------|-----------|
| 拜访礼包面板主背景 | `Pack.MainBg`（如配了）+ `ActvOnline.ActvImg`（默认）| `UIActvVisitPack.cs:101` → `UIHelper.SetActivityBaseInfo` → `UIHelper.Activity.cs:236-239` `cfg.ActvImg` |
| 礼包行后面的小背景 | `ActvVisitPack.DK_PackIcon` | `UIActvVisitPack.cs:122-125` 直接用 `visitPackCfg.DKPackIcon` |
| 礼包入口图标 | `Pack.Icon` / `Pack.Head` | Pack 列表展示用 |
| 礼包面板底部 | `Pack.BottomBg` | 渲染面板下半部 |

## 拜访礼包 MainBg 历史值（对照表）

| Pack ID | 节日 | MainBg | 状态 |
|---------|------|--------|------|
| 210417 | 圣诞拜访 | **None** | ✅ 标准 |
| 210617 | 尼罗拜访 | **None** | ✅ 标准 |
| 210717 | 情人节拜访 | **None** | ✅ 标准 |
| 210816 | 新春拜访 | **None** | ✅ 标准 |
| 210921 | 夏日拜访 | 曾错填 `DK_img_gift_bg_28`，2026-05-26 commit `dfb3e41` 清空 | ✅ 已修 |

`DK_img_gift_bg_28` 是 X3 通用礼包模板（粉/蓝/绿三色 + 手枪/斧/三叉戟），跟节日无关。一旦填上，弹窗就显示这张通用图，节日主视觉就被顶替。

## 实战 BUG 经验

**2026-05-26 X3 夏日柔情海湾拜访礼包弹窗显示紫色三武器图**
- 截图看：弹窗背景=粉/蓝/绿三色+三武器（X3 通用礼包模板）
- 排查：以为是 `ActvOnline.105603.ActvImg = DK_img_Activity_VD_bg_13`（情人节复用），打开实际图发现是粉色樱花小屋——不是截图那张
- 真正来源：`Pack.210921.MainBg = DK_img_gift_bg_28`
- 修法：清空 MainBg（commit dfb3e41）

## ⚠️ 链式/装饰阶梯礼包（ChainPack）根本不读 Pack.MainBg（2026-06-05 验证）

上面"MainBg 覆盖弹窗背景"只对**单包**成立。**装饰阶梯礼包（ChainPack 形态，1父+3档子，UIType=5）的弹窗背景是 prefab 写死的，代码完全不读子包 MainBg**：
- `UIPackCommonPop.cs:158-164` — `isChainGift` 分支走 `RefreshChainPackContentView` 后直接 `return`，**跳过**了非链式分支里那几个 `SetPackBasicInfo(mainBgImage: mImageMainBg)`
- `RefreshChainPackContentView`（268-333）只设 title + 子包列表，**不碰 mImageMainBg**
- `UIChainPack.cs` 全文无任何 MainBg/BG/Img 渲染

→ 所以装饰阶梯礼包子包的 MainBg 填什么都不显示（尼罗 210630-632 填 `Egypt_bg_19`、夏日 210917-919 填 `gift_bg_28` 都是**无害冗余字段**，不用纠结、不用改）。诊断装饰阶梯礼包弹窗背景错误时，别查 Pack.MainBg，要查 prefab 或 ChainPack 渲染。

## 新增节日礼包 checklist

1. **Pack.MainBg** — **单包**拜访礼包/家具礼包类 → **必须空**（会顶替）；链式/装饰阶梯礼包 → 不读此字段，随意；定制弹窗背景的特殊单包（VIP/周卡/特殊活动）才填
2. **Pack.Head / Icon** — 用节日定制 DK，不要复用上一节日（如 `DK_icon_jiaju_ValentinesDay_2` 是情人节专属）
3. **Pack.BottomBg / Icon** — 跨节日通用图（如 `DK_img_gift_bg_8`）可以复用

## 相关

- 客户端实际资源位置：[[reference_x3_client_resources]]
- DK 资源接入流程：[[feedback_dk_resource_workflow]]
- ActvOnline.ActvImg 等字段：[[reference_x3_config]]
