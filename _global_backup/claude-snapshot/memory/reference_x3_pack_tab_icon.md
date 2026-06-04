---
name: x3-pack-tab-icon-source
description: X3 装饰阶梯礼包底部商城页签 tab 图来自 PackTypeInfo.Icon 而非 ChainPack.Icon，节日换皮要分两处改
metadata: 
  node_type: memory
  type: reference
  originSessionId: b1d54617-ced7-46ea-8de4-1270c217b1a4
---

## 装饰阶梯礼包的 3 处 Icon 字段

X3 装饰阶梯礼包（ChainPack 形态，1 个父 + 3 档子 Pack）涉及 3 个独立的 Icon 字段，节日换皮容易只改 1-2 个：

| 表 / 字段 | 控制的 UI 元素 | 例（26 尼罗装饰） |
|---------|--------------|-----------------|
| `Pack.xlsx` → `Pack` sheet → `Icon` 列（每档子 pack）| 礼包卡片本体 icon（弹窗内大图）| 210630/631/632 各自的 Icon |
| `Pack.xlsx` → `ChainPack` sheet → `Icon` 列（父 ChainPack ID） | 礼包面板内部头像（弹窗顶部的总图）| ChainPack 648 Icon |
| **`Pack.xlsx` → `PackTypeInfo` sheet → `Icon` 列** | **底部商城页签 tab 按钮图**（用户最先看到的入口图）| PackTypeInfo row 126 (ID=210630) Icon |

PackTypeInfo 表注释明确写"控制商城页签按钮上显示的图片icon"，是 tab 唯一来源。

## 关联记录与坑

- 26 尼罗 + 26 夏日装饰礼包多次"修复"都失败，原因：commit `e034a3a` 只改了 ChainPack.Icon，**没动 PackTypeInfo.Icon**，客户端 tab 仍显示旧值（猫咪 / 玫瑰手）
- 修复 commit：`fix/festival-pack-tab-icons` 分支
  - PackTypeInfo 210630 尼罗装饰特惠: `DK_img_Activity_Egypt_icon_10`(巴斯特猫) → `DK_img_Activity_Egypt_icon_12`(狮身人面像)
  - PackTypeInfo 210917 夏日装饰礼包: `DK_img_Activity_VD_icon_7`(玫瑰手) → `DK_img_Activity_VD_icon_10`(花拱门)

## 下次换皮 checklist（装饰阶梯礼包专用）

换 PackType=ChainPack 的装饰阶梯礼包时，节日图标必须同时确认 3 处都换：

1. ✅ `Pack` sheet 子 pack Icon × N 档
2. ✅ `ChainPack` sheet 父 pack Icon
3. ✅ **`PackTypeInfo` sheet 对应 ID 的 Icon**（最容易漏，因为这张表不在常规 Pack 关联检查里）

关联：[[reference_x3_pack_panel_rendering]] 弹窗背景由 Pack.MainBg 覆盖 ActvOnline.ActvImg；[[reference_reskin_workflow]] 节日换皮工作流；[[feedback_reskin_round2_lessons]] 换皮第二轮踩坑（含其他类似遗漏）。
