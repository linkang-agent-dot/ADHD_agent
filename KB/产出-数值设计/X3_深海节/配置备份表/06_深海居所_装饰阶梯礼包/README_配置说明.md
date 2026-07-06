---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 06 深海居所 装饰阶梯礼包 — 配置备份表

> **性质**：KB 配置备份表（一个功能一个文件夹），非 live tsv，依赖就绪后搬进 `C:\x3\gdconfig\tsv\`。
> **真源**：X3 配置真源=tsv。**本模块=纯配置·复用换皮（无程序依赖）**，比头像框礼包(04)完整得多。
> **复用源**：夏日恋语装饰阶梯礼包（ChainPack 647 / 子包 210917-919 / PackTypeInfo 210917），整体 copy-and-swap。
> **ID 来源**：GSheet「深海节-开发配置需求」【4】。

## 这个礼包是什么
$19.99 × 3 链式装饰礼包（ChainPack，PackType=11/UIType=5）。每包给**椰风遮阳椅**（家具，带坐下动画，复用现成 Item151043）+ 深海节抽奖券 + 钻石 + VIP点数。

## 表清单（4 张，照此搬进 tsv）
| 表 | 新增 | 文件 | 模板 |
|---|---|---|---|
| `Pack__Pack.tsv` | 子包 **211016/211017/211018** | `Pack_Pack_新增211016-211018.tsv` | 夏日 210917-919 |
| `Pack__ChainPack.tsv` | 父链 **677**（max676+1） | `Pack_ChainPack_新增677.tsv` | 夏日 647 |
| `Pack__PackTypeInfo.tsv` | tab **211016** | `Pack_PackTypeInfo_新增211016.tsv` | 夏日 210917 |
| `Reward__Reward.tsv` | RewardID **211016/017/018**（col0 从 25089 续） | `Reward_Reward_新增.tsv` | 夏日 210917-919 |

## 已配好（真 ID + 真模板，可直接用）
- 3 子包：Price=**111**($19.99)、PackType=11、UIType=5、Content=自身ID、BuyCount=1、名「深海居所特惠」。
- 父 ChainPack 677：PackList=`211016\|211017\|211018`、TimeCycle=**1830**、CustomParameters=4。
- Reward：每包 = 椰风遮阳椅 **151043**×1 + 深海节抽奖券×(40/60/80递增) + 钻石1002×10000 + VIP 2022×100；DropType=1/DropPara=10000；同 RewardID 内 col0 连续（守 [[reference_x3_reward_table_rules]]）。
- PackTypeInfo 211016：MallType=9、Content=211016。

## 🎬 展示视频挂点（重要）
**视频已在 KB 做完**：`KB\产出-本地化与美术\X3\深海节\06_深海居所_装饰礼包\装饰礼包展示视频.mp4`（kling fflf 无缝循环、已对标尼罗格式标准化 810×1080/279KB）。
→ 挂在 **`ChainPack.Video` 字段**（夏日是 `DK_video_summer_love_song`）。本备份表填的是占位 DK `DK_video_deepsea_decoration`，待视频入库注册成该 DK 后生效。

## 🖼️ 3 处 Icon（[[reference_x3_pack_tab_icon]] 必查，换皮易漏）
夏日用 `DK_img_Activity_VD_icon_10`，深海全换占位 `DK_img_Activity_deepsea_icon_decor`（待入库，用装饰 banner 派生）：
1. `ChainPack.Icon`（父链 677）✅ 已填占位
2. `PackTypeInfo.Icon`（211016）✅ 已填占位
3. 子包 `Pack.Icon`：夏日为空（不靠它），深海也留空。
- **子包 MainBg 不显示**：装饰阶梯礼包(ChainPack)弹窗背景 prefab 写死，子包 MainBg 填什么都不渲染（见 [[reference_x3_pack_panel_rendering]]）——夏日填了 `DK_img_gift_bg_28` 是无害冗余，深海备份表沿用，不用纠结。

## ⚠️ 待补 / 待确认
1. **DK 入库**：① 装饰 icon（banner 派生）→ `DK_img_Activity_deepsea_icon_decor` ② 展示视频 → `DK_video_deepsea_decoration`。art 都在 KB，待拷进 client 注册。
2. **深海节抽奖券 ID 待建**（Reward 里占位 `<深海节抽奖券·待建>`，与周卡/头像框礼包同款待建道具）。
3. **设计待确认**：夏日 3 子包给**不同**家具（永恒长椅/爱之廊玫瑰/誓言之门）；深海设计写「每包椰风遮阳椅×1」=3 包同一把椅子。是否如此 or 应给 3 件不同家具？落地前点名。
4. **本地化**：子包名/Desc 的 TXT key 走 x3-translation-automatic。
5. **TimeCycle 1830 起始日期**待整体排期。

## 落地顺序（依赖就绪 + 仓库干净时）
DK 入库(icon+video) → Reward 行 → 3 子包 → ChainPack 677 → PackTypeInfo → i18n → xlsx+tsv 一起改保持一致(过 gate) → commit dev_festival → 导表 jolt_verify。

_生成 2026-06-18；分支 dev_festival；纯配置换皮无程序依赖。_
