# 英雄碎片图标（hero_fragment_icon）完整流程

英雄碎片/灵魂石图标，用于英雄召唤、碎片合成、商店兑换等界面。以英雄半身像为主体，带碎片化视觉效果。

---

## 何时匹配

用户说：英雄碎片、碎片图标、灵魂石、hero fragment、英雄碎片图标、召唤碎片 等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 256×256 像素 |
| **背景** | 透明底（alpha = 0） |
| **风格** | 与 X3 项目英雄立绘一致的 2D 卡通半厚涂渲染、奇幻轻蒸汽风 |
| **主体** | 英雄半身像/头像为核心，带碎片化/晶体化边缘效果 |
| **角色一致性** | **必须**注入对应英雄的参考图和 prompt 关键词（见下方流程） |
| **禁止** | 九宫格、多角色拼接、与角色原设不符的外观 |

---

## 流程（必须按序执行）

1. **确认英雄**：与用户确认要生成哪个英雄的碎片图标（中文名或英文名）
2. **自动查找角色参考图**：
   - 读取本 skill 的 `references/character-visuals/_index.md`
   - 按角色名匹配，获取图片文件名和 AI Prompt 关键词
   - 将角色立绘 base64 编码后注入 `reference_images`
   - 将角色 prompt 关键词拼入 prompt
   - **若索引中无此角色**：提示用户先到 `references/character-visuals/` 贴立绘并登记到 `_index.md`，不可跳过
3. **传入碎片风格参考**：从 `references/icon-ref-herofragment/` 中选参考图一并注入 `reference_images`（用于风格锚定）
4. **模型**：未指定模型且 config 无偏好 → **必须先询问**
5. **构造 prompt**：default_prompt（从 `default-styles.md` 的 `hero_fragment_icon` 行逐字复制）+ 英文逗号 + 角色 prompt 关键词
6. **调用 API**：见 `api-calling.md`，`aspect_ratio: "1:1"`
7. **后处理**：
   - 调用 `remove_background` 抠背景 → 得到 RGBA 透明底
   - 缩放至 256×256（Lanczos）
8. **保存**：按命名规则保存到下载目录

---

## 命名规则

参考项目 UI 素材命名规范（`L2_asset_export/references/naming-conventions.md`，X3 项目 asset_export skill 路径待确认）：

`Icon_HeroFragment_{英雄英文名}.png`

示例：`Icon_HeroFragment_Alice.png`、`Icon_HeroFragment_Bob.png`

---

## 角色参考图来源

1. **优先**：本 skill 的 `references/character-visuals/` 目录（角色立绘 + prompt 关键词，用户自行维护）
2. **兜底**：用户手动提供参考图

---

## 参考图目录

`references/icon-ref-herofragment/` — 风格参考（现有英雄碎片图标），用于提炼碎片化视觉效果风格。
