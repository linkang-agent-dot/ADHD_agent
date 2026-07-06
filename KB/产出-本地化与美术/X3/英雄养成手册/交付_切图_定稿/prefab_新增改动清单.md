---
tags: [kind/产出, domain/美术媒体, proj/X3, year/2026]
---

# UIActvLoginChoice.prefab · 新增/改动清单（切分支后照这个拼）

> 目标 prefab：`client/Assets/Res/UI/Prefab/Activity/UIActvLoginChoice.prefab`
> 豪华列节点根：`Root/Animation/Packs/ColLuxury`（基础列 `ColBasic` 保持不动做反衬）
> 前置：先把定稿 4 张 PNG 拷进 `client/Assets/Res/UI/Spirits/ActvLoginChoice/`，Unity 里选中→Inspector 设 **Texture Type = Sprite (2D and UI)** → Apply。

## 改动 1：换豪华 panel 背板
- 找 `ColLuxury` 的**列背板 Image**（当前指向旧 `panel_luxury_final`）
- Inspector → Image 组件 → **Source Image 换成 `panel_luxury_v2`**
- 底边完整、9-patch 可拉伸（如设了 Image Type=Sliced 记得配 border）

## 新增 2：×2 BONUS 勋章（静态装饰·无代码）
- 在 `ColLuxury` 下新建 Image 节点，命名 `badge_x2`
- **Source Image = `badge_x2_bonus`**
- 锚点/位置：**ColLuxury 右上角**（锚点右上，往外探出一点压在 panel 边角，参考效果图）
- 尺寸 ~180×180（按观感调）；**Raycast Target 取消勾**（纯展示不挡点击）

## 新增 3：-17% 折扣角标（静态装饰·无代码）
- 在 `ColLuxury` 下新建 Image 节点，命名 `tag_discount`
- **Source Image = `tag_discount_-17`**
- 位置：豪华 **`UIBtnPurchase`（$49.99 按钮）右端**，压住按钮右上角
- 尺寸 ~120×120；**Raycast Target 取消勾**

## 新增 4：2X 标语丝带 + 文字（丝带静态·文字走 i18n）
- 在 `ColLuxury` 下新建 Image 节点，命名 `ribbon_tagline`
- **Source Image = `tagline_ribbon_2x_luxury`**
- 位置：豪华列**奖励格上方/空白处**横铺；宽度按列宽拉伸；**Raycast Target 取消勾**
- 在 `ribbon_tagline` 下加子节点 **TFWText**，命名 `txt_tagline`：
  - 文本内容填 i18n key **`TXT_ActvLogin_Luxury_Tagline`**（cn=「每日奖励X2！」，翻译已在 `i18n_translation_staging.tsv`）
  - 居中、字色描边跟丝带协调
  - **若 TFWText 设 key 后没自动本地化** → 在 `UIActvLoginChoice.cs` 的 `RefreshView()` 里加一行 `mTextTagline.text = "TXT_ActvLogin_Luxury_Tagline";`（需在 Auto 绑 `mTextTagline`）；能自动本地化就纯 prefab 搞定、不动代码。

## 要不要动代码？
- 勋章/角标/丝带 = **纯静态装饰**，UIActvLoginChoice 只给双档活动开，豪华列永远显示这些 → **默认全部纯 prefab、不改代码**。
- 唯一可能的一行代码 = 丝带 TFWText 本地化触发（见新增 4 备选）。

## 拼完自检
- [ ] 4 张图都设成 Sprite 类型
- [ ] 豪华 panel 换成 v2、底边完整不裁
- [ ] 勋章/角标/丝带 Raycast Target 都关（别挡购买键点击）
- [ ] 丝带文字显示为「每日奖励X2！」（i18n key 生效）
- [ ] 基础列没被误动
