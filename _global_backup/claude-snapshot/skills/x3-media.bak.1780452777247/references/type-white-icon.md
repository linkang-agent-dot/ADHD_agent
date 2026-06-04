# 白图图标（white_icon）完整流程

纯白色扁平剪影图标，用于装备/物品分类标识、UI 功能按钮底图等场景。无色彩、无渐变、纯轮廓识别。

---

## 何时匹配

用户说：白图、白稿、白色图标、装备白图、white icon、纯白图标、单色图标、剪影图标 等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 128×128 像素 |
| **背景** | 透明底（alpha = 0） |
| **颜色** | 纯白色（#FFFFFF），无渐变、无阴影、无灰度变化 |
| **风格** | 扁平剪影，线条简洁，一眼可辨识物品类型 |
| **主体** | 单一物品居中，留适当边距（约 10% padding） |
| **禁止** | 任何色彩、渐变、描边粗细变化、3D 效果、光影 |

---

## 流程（必须按序执行）

1. **确认物品类型**：与用户确认要生成什么物品的白图（如：剑、盾、头盔、药水、戒指等）
2. **模型**：未指定模型且 config 无偏好 → **必须先询问**
3. **传入参考图**：从 `references/icon-ref-white/` 中选 2-3 张作为 `reference_images`（用于风格锚定，非内容参考）
4. **构造 prompt**：default_prompt（从 `default-styles.md` 的 `white_icon` 行逐字复制）+ 英文逗号 + 物品描述（英文）
5. **调用 API**：见 `api-calling.md`，`aspect_ratio: "1:1"`
6. **后处理**：
   - 调用 `remove_background` 抠背景 → 得到 RGBA 透明底
   - 缩放至 128×128（Lanczos）
7. **保存**：按命名规则保存到下载目录

---

## 命名规则

参考项目 UI 素材命名规范（`L2_asset_export/references/naming-conventions.md`，X3 项目 asset_export skill 路径待确认）：

`Common_WhiteImg_{物品英文名}.png`（PascalCase）

示例：`Common_WhiteImg_Sword.png`、`Common_WhiteImg_Shield.png`、`Common_WhiteImg_MagicianHat.png`

> 若用户指定了功能模块前缀（如 `Furnace`），则用 `{Module}_WhiteImg_{名称}.png`

---

## 参考图目录

`references/icon-ref-white/` — 风格参考（20 张现有白图：武器、防具、饰品、药水等），用于提炼视觉风格，不作为内容模板。
