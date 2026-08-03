# 资源图标（resource_icon）完整流程

游戏内资源/货币/道具材料的彩色图标，用于 HUD 资源栏、背包、商店、奖励展示等位置。2D 卡通半厚涂渲染风格，与 X3 奇幻轻蒸汽美术一致。

---

## 何时匹配

用户说：资源图标、货币图标、材料图标、resource icon、做个资源图、HUD 图标、道具材料图标 等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 256×256 像素 |
| **背景** | 透明底（alpha = 0），无边框 |
| **风格** | 2D 美术，卡通半厚涂渲染，奇幻轻蒸汽风，色彩饱和鲜明 |
| **主体** | 单一资源/材料居中，视觉紧凑，不留大面积空白 |
| **质感** | 金属光泽、宝石折射、木纹纹理等材质细节丰富 |
| **禁止** | 多个物品拼接、九宫格、文字标签 |

---

## 流程（必须按序执行）

1. **确认资源类型**：与用户确认要生成什么资源（如：食物、铁矿、木材、宝石、金币、联盟币、体力等）
2. **模型**：未指定模型且 config 无偏好 → **必须先询问**
3. **传入参考图**：从 `references/icon-ref-resource/` 中选 2-3 张作为 `reference_images`（用于风格锚定，非内容参考）
4. **构造 prompt**：default_prompt（从 `default-styles.md` 的 `resource_icon` 行逐字复制）+ 英文逗号 + 资源描述（英文）
5. **调用 API**：见 `api-calling.md`，`aspect_ratio: "1:1"`
6. **后处理**：
   - 调用 `remove_background` 抠背景 → 得到 RGBA 透明底
   - 缩放至 256×256（Lanczos）
7. **保存**：按命名规则保存到下载目录

---

## 命名规则

参考项目 UI 素材命名规范（`L2_asset_export/references/naming-conventions.md`，X3 项目 asset_export skill 路径待确认）：

- 全局资源：`icon-global-resource-{小写名}.png`（如 `icon-global-resource-iron.png`）
- 道具材料：`Icon_Item_{PascalCase名}.png`（如 `Icon_Item_GoblinCoin.png`）
- HUD 资源：`HudIconRss{PascalCase名}.png`（如 `HudIconRssFood.png`）

> 优先匹配项目中已有的同类资源命名前缀，保持一致。

---

## 参考图目录

`references/icon-ref-resource/` — 风格参考（44 张现有资源图标），用于提炼视觉风格，不作为内容模板。
