# UI 素材提取（ui_extract）完整流程

从 UI 参考图（游戏截图、界面设计稿、效果图等）中提取 UI 元素（按钮、图标、面板、进度条、装饰框等），去除所有文字后平铺在白色背景上输出。

## 何时匹配

用户说：切图、拆 UI、拆图素、提取 UI 素材、UI 元素拆解、UI 拆解、把界面元素拆出来、UI extract、extract UI elements 等。

---

## 流程

1. **索要参考图（必须）**：向用户索要 UI 参考图；未提供则提示「请提供要拆解的 UI 参考图（界面截图、设计稿等）」
2. **确认输出模式**：询问用户选择九宫格（grid）还是逐个输出（individual）
   - 用户未指定 → 默认 **grid 模式**
   - 用户明确要「每个元素单独一张」→ individual 模式
3. **确认模型**：未指定模型且 config 无偏好 → **必须先询问**
4. **分析参考图**：识别参考图中的主要 UI 元素类型（按钮、图标、面板、进度条、标签、装饰等）
5. **构造 prompt**：default_prompt 全文 + 模式特定约束 + 用户补充描述（英文）
6. **调用 API**：`call_grfal.py` + `reference_images`；**必须**加 `--download-dir` 指向用户下载目录（与 API 同进程、自动带 Cookie 落盘 PNG，勿只打印 URL 让用户自己下）
7. **写运行记录**：每次成功生成后追加一行到 `state/history.jsonl`（时间、类型 `ui_extract`、模型、元素 id、本地保存路径或 URL、后端）
8. **告知用户**：回复「已保存到：<完整路径>」，并说明若 Agent 运行环境无法解析结果域名，需用户在本机终端用同一命令重跑一次 `--download-dir`

---

## 输出模式

### Grid 模式（九宫格）

所有 UI 元素压缩排列在**一张图**上，白色背景，网格布局。

**prompt 追加约束**：
```
neatly arranged in a grid layout on pure white background, evenly spaced rows and columns, all UI elements visible at similar scale, no overlap between elements, clean spacing between each element, asset sheet style layout
```

**适用场景**：快速总览、素材盘点、风格参考

### Individual 模式（逐个输出）

Agent 分析参考图，列出识别到的主要 UI 元素，每个元素**单独生成一张图**。

**prompt 追加约束**：
```
single UI element centered on pure white background, isolated, clean edges, no other elements visible, zoomed in on this one element only
```

**执行方式**：
1. 先告知用户识别到的元素列表，确认要提取哪些
2. 每个元素一次 API 调用，N 个元素用 `Start-Job` 并行（禁止串行）
3. prompt 中具体描述该元素的外观特征以确保准确提取

**适用场景**：需要单个高清素材、后续二次编辑

---

## Prompt 通用约束

以下约束在两种模式下**均必须包含**：

- **去除文字**：`absolutely no text, no labels, no typography, no letters, no numbers, no words, no characters, remove all written content`
- **白色背景**：`pure white background, solid #FFFFFF background`
- **保留原始风格**：`preserve original visual style, colors, and design language of each UI element`
- **清晰边缘**：`clean crisp edges on every element, no blur, no feathering`
- **仅提取 UI 元素**：`extract only the UI components such as buttons, icons, panels, progress bars, frames, decorations, badges, tabs, sliders — ignore background scene and text`

---

## Reference Images

- 传入**用户提供的 UI 参考图**作为 reference_images
- 不需要额外的模板参考图

---

## 文件命名

| 模式 | 文件名格式 | 示例 |
|------|-----------|------|
| grid | `ui_extract_grid_YYYYMMDD_HHMMSS.png` | ui_extract_grid_20260320_143025.png |
| individual | `ui_extract_元素描述_NN.png` | ui_extract_button_01.png, ui_extract_panel_02.png |

---

## 关键规则

1. **参考图必须**：没有参考图无法工作，必须先获取
2. **文字必须去除**：这是核心需求，prompt 中务必强调 no text 相关约束
3. **白底必须**：所有输出统一纯白背景，方便后续使用
4. **individual 模式先确认**：列出识别到的元素让用户确认，避免生成不需要的素材
5. **并行生成**：individual 模式多张图用 Start-Job 并行，禁止串行循环
6. **不甩脚本给用户**：直接执行 `call_grfal.py`（可加 `--download-dir`），不要把「请你运行某某 .py」当交付物；批量并行仍用多次 `call_grfal` 调用，每次带 `--download-dir`
