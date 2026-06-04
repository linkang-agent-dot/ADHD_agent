# UI 框 / 背景（uiframe）完整流程

游戏 UI 框 / 背景面板：**头像框 / 弹窗背景 / 标题装饰条 / 列表项背景**。透明底 PNG，**9-patch 兼容**（拉伸时四角不变形）。

---

## 何时匹配

用户说：UI 框、头像框、touxiangkuang、弹窗背景、tanchu、标题框、biaoti、列表背景、taizhangliebiao、9-patch 背景、装饰边等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 头像框 256×256，弹窗背景 1024×768 或 512×384，标题条 768×128，列表项 512×96 |
| **背景** | 透明底（alpha = 0），框/背景外完全透明 |
| **风格** | 3D 卡通：warm parchment / medieval 色调，装饰边带金属高光，inner subtle gradient |
| **细节** | ornate border + 四角强化装饰（用于 9-patch 保 corner） |
| **文字** | **不出现文字**（标题 / 内容由前端 overlay） |
| **9-patch** | 中段单色可拉伸；四角细节须保留 |
| **禁止** | Pixar 风、厚涂、深色背景、文字水印、有内容图标 |

---

## 形状 / 用途变体

- **头像框（avatar frame）**：圆形或方形，外加品质边（金 = epic / 蓝 = rare / 灰 = common）
- **弹窗背景（popup bg）**：parchment 主体 + 角落卷轴装饰
- **列表项背景（list row bg）**：横向长条，左右收窄圆角
- **标题装饰条（title banner）**：横向 banner，两端羽化或卷轴尾
- **Tab 选中/未选**：tab 形状 + 选中状态高亮 vs 未选灰化
- **信息板（info panel）**：装饰边 + 内嵌分隔线

---

## 流程（必须按序执行）

1. **确认框类型**：与用户确认要做什么框（用途 + 尺寸 + 品质等级）
2. **模型**：未指定模型且 config 无偏好 → **必须先询问**（gpt / gemini）
3. **传入参考图**：从 `references/uiframe/` 中选 2-4 张作为 `reference_images`（X3 真实 UI 框：touxiangkuang 头像框 / tanchu 弹窗 / biaoti 标题 / taizhangliebiao 列表），用于风格锚定
4. **构造 prompt**：从 `default-styles.md` 的 `uiframe` 行复制 default_prompt + 英文逗号 + 用户描述（含用途 + 尺寸 + 品质等级）
5. **首次 prompt 三件套**（CLAUDE.md 硬要求）：
   - 宽高比：头像框 1:1，弹窗 4:3，列表项 16:3，标题条 6:1
   - 艺术风格：polished 3D cartoon render, warm parchment / medieval palette, decorative ornate border with golden metallic accents, subtle inner gradient
   - reject list：no Pixar, no painterly, no realistic photo, no anime CG, no flat minimal design, no text labels, no internal icons, no scene background, no neon, preserve corner detail for 9-patch
6. **GPT 空返回 → 自动 fallback `model=gemini` 重试同 prompt**
7. **调用 API**：见 `api-calling.md`，aspect_ratio 按上面变体表
8. **后处理**：
   - 调用 `remove_background` 抠掉框外区域 → 得到 RGBA 透明底（**保留框内的内部装饰**，只去框外）
   - 保留尺寸（让前端按 9-patch 拉伸）
9. **保存**：按命名规则

---

## 命名规则

`{Module}_frame_{purpose}_{quality_or_state}.png`（snake_case）

示例：
- `Common_frame_avatar_common.png`
- `Common_frame_avatar_epic.png`
- `Common_frame_popup_default.png`
- `Common_frame_list_row.png`
- `Common_frame_title_banner.png`
- `Common_frame_tab_selected.png` / `Common_frame_tab_unselected.png`

> 模块前缀按调用语境决定，用户未指定时默认 `Common`

---

## 参考图目录

`references/uiframe/` — X3 真实 UI 框（头像框 1-2 / 弹窗背景 / 标题框 / 列表背景），用于提炼视觉风格

---

## 风格模板大图

`references/uiframe_style_template.png` — 3×3 网格示范图，含 9 个 frame 变体（3 头像框品质 + 3 背景类型 + 3 装饰条/Tab）+ 调色板。生图前先 Read 这张图建立"该长什么样"的视觉锚。
