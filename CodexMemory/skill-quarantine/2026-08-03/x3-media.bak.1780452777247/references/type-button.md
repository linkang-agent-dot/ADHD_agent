# 按钮（button）完整流程

游戏 UI 按钮（多色 / 多状态 / 多形状），透明底 PNG，**9-patch 兼容**（拉伸时四角不变形）。

---

## 何时匹配

用户说：按钮、anniu、button、确定按钮、取消按钮、关闭按钮、返回按钮、9-patch 按钮、UI 按钮等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 默认 512×128（长方形 / pill），圆形小按钮 128×128 |
| **背景** | 透明底（alpha = 0），按钮外完全透明 |
| **颜色** | 单色饱和（blue / green / orange / red / yellow / gold / purple / grey-disabled） |
| **风格** | 3D 卡通渲染：beveled edge + 内高光 + 底部投影 + 轻微 glow rim |
| **文字** | **不出现文字**（label 区域留空 / 显示为纯色描边带，让前端套文字） |
| **9-patch** | 圆角对称，中段可拉伸；四角细节须保留 |
| **禁止** | Pixar 风、厚涂、写实摄影、深色背景、文字水印 |

---

## 状态变体

- **Normal**：常规色 + 完整高光投影
- **Pressed**：色调暗 5-10%，去掉底部投影
- **Disabled**：去饱和（saturation 30%）+ 灰色 overlay
- **Loading**：保持 normal 色 + 不画 spinner（spinner 由前端 overlay）

---

## 形状变体

- **长方形 / Pill**：512×128，圆角 ~30% 高度
- **圆形小按钮**：128×128（用于 close X / back 箭头 / +/- 等）
- **方形小按钮**：128×128 圆角 ~15%

---

## 流程（必须按序执行）

1. **确认按钮类型**：与用户确认要做什么按钮（颜色 + 形状 + 状态）。若用户给参考图片优先尊重原图。
2. **模型**：未指定模型且 config 无偏好 → **必须先询问**（gpt / gemini）
3. **传入参考图**：从 `references/button/` 中选 2-4 张作为 `reference_images`（X3 真实按钮：anniu3 多色 / delete / 改名 / jianding / shilian 等），用于风格锚定
4. **构造 prompt**：从 `default-styles.md` 的 `button` 行复制 default_prompt + 英文逗号 + 用户描述（含颜色 + 形状 + 状态）
5. **首次 prompt 三件套**（CLAUDE.md 硬要求）：
   - 宽高比：长方形 4:1，pill 4:1，圆形 1:1，方形 1:1
   - 艺术风格：polished 3D cartoon render with cel shading, warm-toned palette, beveled edge highlight
   - reject list：no Pixar, no painterly, no realistic photo, no anime CG, no flat material design, no text inside button, no scene background, no neon
6. **GPT 空返回 → 自动 fallback `model=gemini` 重试同 prompt**
7. **调用 API**：见 `api-calling.md`，长方形 `aspect_ratio: "4:1"`，圆形/方形 `aspect_ratio: "1:1"`
8. **后处理**：
   - 调用 `remove_background` 抠掉按钮外的白底 → 得到 RGBA 透明底
   - 保留尺寸（不缩放，让前端按 9-patch 拉伸）
9. **保存**：按命名规则

---

## 命名规则

`{Module}_btn_{color}_{shape}_{state}.png`（snake_case）

示例：
- `Common_btn_green_pill_normal.png`
- `Shop_btn_orange_pill_pressed.png`
- `Common_btn_close_circle_normal.png`
- `Common_btn_back_circle_normal.png`

> 模块前缀（如 `Common`、`Shop`、`Battle`）按调用语境决定，用户未指定时默认 `Common`

---

## 参考图目录

`references/button/` — X3 真实按钮（anniu3 多色系列 + delete / 改名 / jianding / shilian 等），用于提炼视觉风格

---

## 风格模板大图

`references/button_style_template.png` — 4×3 网格示范图，含 12 个按钮变体（4 主色 + 4 特殊态 + 4 形状）+ 调色板。生图前先 Read 这张图建立"该长什么样"的视觉锚。
