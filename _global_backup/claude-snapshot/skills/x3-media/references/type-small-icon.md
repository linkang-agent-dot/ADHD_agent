# 小图标（small_icon）完整流程

游戏内小尺寸功能标签/分类标记图标，用于熔炉标签、功能入口小图、筛选器标记、数值说明等位置。尺寸极小，要求极简可辨识。

---

## 何时匹配

用户说：小图标、标签图标、tag 图标、small icon、功能小图标、分类标记、筛选图标 等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 58×58 像素（或按需 58×51） |
| **背景** | 透明底（alpha = 0） |
| **风格** | 极简扁平或微 3D，色彩鲜明，蒸汽朋克奇幻质感，一眼可辨识 |
| **主体** | 单一符号/标记居中，笔画粗壮清晰（小尺寸下仍可辨认） |
| **禁止** | 复杂细节、渐变过多、文字、多物品拼接 |

---

## 流程（必须按序执行）

1. **确认用途**：与用户确认图标用于什么场景（如：熔炉标签、联盟股票、功能分类、筛选器等）
2. **确认含义**：确认图标要表达的语义（如：卷轴、武器、防具、材料等）
3. **模型**：未指定模型且 config 无偏好 → **必须先询问**
4. **传入参考图**：从 `references/icon-ref-small/` 中选参考图作为 `reference_images`（用于风格锚定，非内容参考）
5. **构造 prompt**：default_prompt（从 `default-styles.md` 的 `small_icon` 行逐字复制）+ 英文逗号 + 语义描述（英文）
6. **调用 API**：见 `api-calling.md`，`aspect_ratio: "1:1"`
7. **后处理**：
   - 调用 `remove_background` 抠背景 → 得到 RGBA 透明底
   - 缩放至目标尺寸 58×58（或 58×51）（Lanczos）
   - **必须在实际尺寸下预览**，确认缩小后仍可辨识；若模糊则简化 prompt 重新生成
8. **保存**：按命名规则保存到下载目录

---

## 命名规则

参考项目 UI 素材命名规范（`L2_asset_export/references/naming-conventions.md`，X3 项目 asset_export skill 路径待确认）：

`{Module}_Icon_{Tag}.png`

示例：
- `Furnace_Icon_Tag01.png`（熔炉标签）
- `Alliance_Icon_StockScroll.png`（联盟股契卷轴）
- `Filter_Icon_Weapon.png`（筛选器武器标签）

> `{Module}` 取所属功能模块英文名（PascalCase），`{Tag}` 取图标语义英文名。

---

## 参考图目录

`references/icon-ref-small/` — 风格参考（现有小图标），用于提炼视觉风格，不作为内容模板。
