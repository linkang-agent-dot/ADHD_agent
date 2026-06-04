---
name: X3 主城皮肤 = 岛屿皮肤（非三件套）
description: X3项目"主城皮肤"的正确术语和ID对应，避免与主城装饰三件套混淆
type: feedback
originSessionId: 7f1d10e6-76c8-46b3-b30d-957a641cda96
---

在 X3 项目中，"主城皮肤"指的是**岛屿皮肤**，不是主城装饰三件套。

**Why:** 初次接触X3时把"主城皮肤"理解成了 FurnitureSkin 三件套（地板/墙纸/横梁），用户纠正："不是三件套，就是主城皮肤"。两者是完全不同的品类。

**How to apply:**
- X3 主城皮肤 = 岛屿皮肤，Item ID 格式为 `Item_81xxx`，定义在 `Skin.xlsx`（SkinType=1）
- 主城装饰三件套 = 地板/墙纸/横梁，asset_id 格式为 `FurnitureDecorateSkinID_XXXX`，定义在 `FurnitureSkin.xlsx`
- 岛屿皮肤的 Item_81xxx 在数据库中直接以 `Item_81xxx` 格式存储，**不是** `FurnitureDecorateSkinID_` 前缀
- 每次讨论X3皮肤类道具时，先确认是"岛屿皮肤"（整个主城换肤）还是"主城装饰三件套"（地板/墙纸/横梁分件）
