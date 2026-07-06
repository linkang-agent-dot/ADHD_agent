---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 04 深海印记 头像框礼包 — 配置备份表（草稿）

> **性质**：KB 配置备份表（一个功能一个文件夹），**非 live tsv**。这里把要配的行按真实表结构排好，待依赖项就绪后搬进 `C:\x3\gdconfig\tsv\`。
> **真源**：X3 配置真源 = tsv（改 tsv 不碰 xlsx）。本备份表只是落地前的暂存草稿。
> **来源**：ID 分配来自策划案 GSheet「深海节-开发配置需求」页签【4】【7】；设计见对齐总览 HTML 模块04。

## 这个礼包是什么
$9.99 通用礼包，购买得 **深海头像框 + 深海节节日道具**。挂礼包墙直售，无独立 ActvOnline，绑深海主时间 TC1830。

## 双表结构（头像框 = 框定义 + 包成道具）
| 表 | 新增 ID | 文件 | 说明 |
|---|---|---|---|
| `Personalize__PersonalizeAvatarFrameCfg.tsv` | **10076** | `PersonalizeAvatarFrameCfg_新增10076.tsv` | 框定义(图/buff/名)，max 10075→10076，抄 Egypt 10026 |
| `Item__Item.tsv` | **80348** | `Item_Item_新增80348.tsv` | 把框包成可售道具(param=`10076\|-1`永久)，max 80347→80348，抄 Egypt 框道具 80110 |
| `Pack__Pack.tsv` | **211019** | `Pack_Pack_新增211019.tsv` | 礼包本体 $9.99(价格档107)，PackType 待程序 |

## 已定字段（可直接用）
- 框定义 10076：DK=`DK_Img_Player_AvatarFrame_DeepSea`(待入库)、buff 沿用 Egypt(220010 防御/150/虚战力20000)、Name=深海印记、SourceDesc=深海印记礼包获取、Unlock=1。
- 道具 80348：Type9/UseType1/UseEffect4、UseParameter=`10076|-1`(永久)、DK_Icon=同框DK、DK_Background=`DK_Bg_CM_Item4`、ObtainTips=通过深海印记礼包获得。
- Pack 211019：Price=**107**($9.99，已核 PackPrice 表)、TimeCycleID=**1830**、BuyCount=**1**(限购1)。

## ⚠️ 落地前待补（依赖外部，未就绪）
1. **通用礼包模块需程序** → `Pack.PackType / UIType / Content写法 / OpenActv(礼包墙)` 待程序定型后才能拼整行。
2. **深海头像框 DK 未入库** → `深海头像框_选定.png`（在 `KB\产出-本地化与美术\X3\深海节\04_深海印记_头像框礼包\`）需拷进 client + 注册成 `DK_Img_Player_AvatarFrame_DeepSea`（走 DK 资源流程 [[feedback_dk_resource_workflow]]）。
3. **节日道具 ID 待建** → 礼包里的「深海节抽奖券/兑换代币」ID 尚未建（见周卡页签同款待建道具），Content 里先占位。
4. **Regained（重复转钻补偿）** → GSheet 标「带 Regained」，但 Item 表无 Regained 列，机制位置待确认（外显通用补偿，见 [[reference_x3_monetization_mechanics]]）。
5. **弹窗背景** → 通用礼包默认走模板、MainBg 一般留空；若程序支持自定义，再把「头像框礼包弹窗背景_v1.png」入库填 MainBg（见 [[reference_x3_pack_panel_rendering]]）。
6. **本地化** → Name/Desc/SourceDesc 的 TXT key 走 x3-translation-automatic。

## 落地顺序（依赖就绪后）
DK 入库 → 框定义 10076 → 道具 80348 → 节日道具建好 → 程序给通用礼包模块定型 → Pack 211019 拼整行进 tsv → i18n → 导表验证。

_生成 2026-06-18；分支 dev_festival。_
