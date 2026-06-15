# UI 素材提取（ui_extract）完整流程

从 UI 参考图（游戏截图、界面设计稿、效果图、素材合集等）中提取 UI 元素（按钮、图标、面板、进度条、装饰框等）。

## 核心：按源图类型选路径

拆图分两条路径，**先判断源图是哪种**：

### 路径 A · 像素级复刻（默认，源图是干净素材表 / 元素已可分离）
源图本身就是排好的素材表、或元素背景干净可分离时——**严禁** `generate_image` 重画（会改造型/配色，跟原图差异巨大）：
- ✅ 对源图本身 `remove_background` → 连通域/image_split 切元素 → autocrop → 去白边 → 量化。全程真实像素。

### 路径 B · 平铺生成（源图是密集场景 / mockup，元素相邻重叠共背景）
完整界面 mockup 里元素挤在一起，直接连通域切不干净——这时**允许**先重画成平铺表再切：
- ✅ 让 `generate_image` 把 mockup 上**可复用的独立元素**（图标/按钮/品质框/单品）**重画成一张白底元素平铺表**（asset sheet：互不重叠、间距清晰、保留各自造型配色）→ 对平铺表 `remove_background` → image_split 切 → autocrop → 去白边 → 量化。
- ⚠ 平铺是 AI 重画，造型/配色会有**微漂移**——这是为换"干净切割"有意接受的代价。**只重画独立小元素，不要重画整屏布局**；整块布局靠组件/原型还原。
- ❌ 仍禁止：在 mockup 上叠坐标网格、肉眼估坐标手动 PIL 裁（必然错位）。

## 何时匹配

用户说：切图、拆 UI、拆图素、提取 UI 素材、UI 元素拆解、UI 拆解、把界面元素拆出来、UI extract、extract UI elements 等。

---

## 流程（全程操作源图真实像素）

1. **索要参考图（必须）**：未提供则提示「请提供要拆解的 UI 参考图」
2. **确认输出模式**：grid（整图）/ individual（逐元素），默认 individual
3. **⭐ 超分放大源图（先做，防糊）**：`call_grfal.py --tool upscale --file reference_images=<源参考图>`（2x/4x）→ 高清源图 `<name>_hd.png`
   - **为什么先超分**：源图元素往往偏小，后面直接 PIL resize 放大会糊；先用超分模型把整张源图放大，后续切出来的元素自带高分辨率，清晰锐利
   - **为什么放在 removebg 之前**：此时源图还是不透明的，超分模型不会破坏 alpha 边缘；先 removebg 再超分会把透明边缘搞脏
4. **对高清源图 removebg**：`call_grfal.py --tool remove_background --file reference_images=<name>_hd.png` → **源图的透明底真实像素**（不是 AI 重画）。命名 `<name>_nobg.png`
   - 源图背景是纯色（白/单色）且 removebg 效果不佳时，可改本地阈值抠底
5. **切元素（对高清真实像素）**：
   - 优先 grfal `image_split`（传 `<name>_nobg.png`，按元素切）；
   - 或本地 cv2 连通域：对 `<name>_nobg.png` 的 alpha 做连通域 → 每个元素 bbox → **从高清透明底真实像素裁剪** → autocrop
6. **边缘净化（关键，对应"二分法"的清边效果）**：每个裁出的元素跑白边去污染（white-fringe decontaminate），消除 removebg 残留的白描边/半透明杂边，得到干净 alpha
7. **后处理**：individual 模式按分档跑 `ui_extract_postprocess.py`（此时元素已是高清，resize 只会缩小不会放大 → 不糊 + 量化）
8. **写运行记录**：追加一行到 `state/history.jsonl`
9. **告知用户**：回复「已保存到：<完整路径>」

---

## 输出模式（都是从源图切真实像素，不生图）

### Individual 模式（逐元素，默认）

把源图里识别到的每个 UI 元素**各裁成一张透明底 PNG**。

**执行方式**：
1. 对源图 removebg → 透明底真实像素
2. 连通域 / image_split 切出每个元素 bbox → 从真实像素裁剪 → autocrop → 边缘净化
3. 先告知用户识别到的元素列表（可让用户挑要哪些）

**适用场景**：入 Unity 的单个素材、后续二次编辑

### Grid 模式（整表总览）

不切分，直接把源图 removebg + autocrop 成**一张透明底总表**，留作素材盘点 / 风格参考。

---

## ⚠ 不涉及任何生成 prompt

本类型**不调 generate_image**，所以没有"prompt 追加约束 / 风格关键词 / 去文字 prompt"这些东西——那些是生图才有的。源图里有什么文字就保留什么（拆图是 1:1 复刻像素）。若用户确实要去掉元素上的文字，那是另一个"局部重绘(mask edit)"需求，不在 ui_extract 范围。

---

## Reference Images

- **源参考图就是要拆的图本身**，直接对它 removebg + 切元素
- 不传给 generate_image，不需要任何模板参考图

---

## 文件命名

| 阶段 | 后缀 | 说明 |
|------|------|------|
| 高清源图 | `<name>_hd.png` | 对源参考图先超分放大（防糊），仍是不透明真实像素 |
| 源图透明底 | `<name>_nobg.png` | 对**高清源图**做 remove_background（真实像素，非 AI 重画）|
| 抠图 | `<id>_nobg.png` | 从高清源透明底切出的单个元素，全尺寸透明底 |
| 裁剪 | `<id>_nobg_trimmed.png` | bbox 裁掉透明边缘（中间产物，**保留**用于排查） |
| Resize | `<id>_resized.png` | 等比缩放到分档目标像素（中间产物，**保留**） |
| **最终** | `<id>_final.png` | **入 Unity 用这个**，已 resize + 量化 |

grid 模式输出名不变：`ui_extract_grid_YYYYMMDD_HHMMSS.png`（grid 模式不走分档/量化流程）。

---

## 元素类型分档（individual 模式必须）

X3 项目分两大类，决定 final 输出规范：

### 图标类（ICON_CLASSES）→ 256×256 透明画布 + 20px padding

| element_class | 输出尺寸 | 文件大小目标 | 量化色数 | 典型 id 示例 |
|---|---|---|---|---|
| micro_icon  | **256×256** | ≤20 KB | 256 | heart_broken, heart_full, single_dot, radio_btn, star, btn_close 内的 × |
| small_icon  | **256×256** | ≤25 KB | 256 | icon_speed, icon_time, icon_order, icon_appraise |
| button      | **256×256** | ≤30 KB | 256 | btn_minus, btn_plus, toggle_on, toggle_off, btn_confirm |
| tab         | **256×256** | ≤35 KB | 256 | tab_quality_*, tab_blueprint_* |

所有 ICON 类一律放进 **256×256 透明画布**，元素居中，**边缘留 20px padding**（内接框 216×216 内最长边等比缩放）。这是 X3 项目的统一图标裁图规范。

### 非图标类（NON_ICON_CLASSES）→ 保留 trimmed 原尺寸，不缩放

| element_class | 输出尺寸 | 文件大小目标 | 量化色数 | 典型 id 示例 |
|---|---|---|---|---|
| slider      | nobg+trimmed 原尺寸 | ≤50 KB  | 256 | slider_full, slider_handle_* |
| title_frame | nobg+trimmed 原尺寸 | ≤80 KB  | 256 | title_frame, big_banner |
| panel       | nobg+trimmed 原尺寸 | ≤150 KB | 256 | panel_main, panel_decoration |

非图标类**只做 nobg + autocrop trimmed**，**不再 resize**（保留原始细节给精修 / 复用）。最终 final 仅做无损量化（pngquant / optipng）压体积。

**自动归类规则**（用户没显式指定时）：
- 含 `slider` / `bar` → `slider`
- 含 `tab` / `badge` / `quality_` / `blueprint_` → `tab`
- 含 `btn_` / `button` / `toggle` → `button`
- 含 `panel` / `_bg` 末尾 → `panel`
- 含 `title` / `frame` / `banner` → `title_frame`
- 含 `heart` / `star` / `dot` / `check` / `radio` → `micro_icon`
- 其余默认 `small_icon`

用户显式覆盖优先于自动规则。

---

## 抠图（removebg 源参考图）

直接对**源参考图**去背景，得到源图的透明底真实像素，再从里面切元素。

**完整流程**：
1. **源参考图** → removebg → 透明底真实像素（不是 AI 重画的图）
2. 切元素 → 每个元素 autocrop → **边缘净化（去白边）** → 量化

**执行方式**：
```powershell
# art-skills removebg（推荐，GRFal 不可用时的唯一选择）
py "<art-skills>/scripts/generate_2d.py" --service removebg --images "<白底UI元素图路径>" --host "https://ai-art-api.tap4fun.com/v2" --token "$ART_TOKEN" --timeout 120

# GRFal removebg
py "<grfal>/scripts/call_grfal.py" --tool remove_background --params "{\"prompt\":\"remove background\"}" --file "reference_images=<白底UI元素图路径>" --url $GRFAL_URL --public-url none --timeout 60
```

**注意**：
- 生图和抠图是两步，不要跳过抠图直接交付白底图
- 抠图后的文件命名加 `_nobg` 后缀，如 `ui_extract_panel_nobg.png`
- 若用户明确说要白底图则跳过此步

### Autocrop（去除透明空白，必须）

removebg 输出的图片尺寸与原图相同，主体周围有大量透明空白区域，**必须裁掉**。

```python
from PIL import Image
img = Image.open("<抠图结果路径>").convert("RGBA")
bbox = img.getbbox()  # 获取非透明像素的边界框
if bbox:
    img.crop(bbox).save("<最终输出路径>")
```

- 在 removebg 之后**立即执行**，不要交付未裁剪的大空白图
- 最终文件命名加 `_trimmed` 后缀，如 `ui_extract_panel_nobg_trimmed.png`
- 这一步用 Python PIL 本地执行，不需要调用 API

### Step 8: Resize + 量化压缩（individual 模式必须）

trimmed 后再做两件事，把每个元素压到项目标准（1-80 KB 区间，按分档表）。**跳过这步会让资源比标准大 10-100 倍。**

直接调用本 skill 的封装脚本（路径相对 skill 根目录）：

```bash
python "<x3-media>/scripts/ui_extract_postprocess.py" \
  --input-dir "<DLDIR>" \
  --manifest "<DLDIR>/manifest.json"
```

**manifest.json 格式**（id → element_class）：
```json
{
  "slider_full": "slider",
  "btn_minus": "button",
  "btn_plus": "button",
  "heart_broken": "micro_icon",
  "heart_full": "micro_icon",
  "icon_speed": "small_icon",
  "icon_time": "small_icon",
  "icon_order": "small_icon",
  "icon_appraise": "small_icon",
  "tab_quality_rare": "tab",
  "tab_quality_epic": "tab",
  "toggle_on": "button"
}
```

脚本会对 `<DLDIR>/<id>_nobg_trimmed.png` 依次做：

1. **规范化**：
   - ICON_CLASSES（micro_icon/small_icon/button/tab）→ 放进 **256×256 透明画布，20px padding，居中**
   - NON_ICON_CLASSES（slider/title_frame/panel）→ 保留 trimmed 原始尺寸（不 resize）
2. **量化**：优先 `pngquant`（256 色）→ 降级 `oxipng` → `optipng` → PIL `optimize=True`
3. **校验**：实际文件大小超过分档目标 ×1.5 时打 warning（不阻塞），写入 `oversize:true`
4. **history.jsonl 追加**：每个元素一行，含 `element_class` / `icon_canvas`（图标）/ `final_size_kb` / `oversize`

> 实现细节见 `scripts/ui_extract_postprocess.py`。Agent 不要手写 PIL/pngquant 调用，直接调脚本。

---

## 关键规则

1. **按源图选路径**：干净素材表/可分离元素 → 路径 A 像素级复刻（**禁** generate_image 重画）；密集场景/mockup → 路径 B 先平铺生成再切（**允许**重画独立元素成白底平铺表，接受微漂移）。两种都**禁止**肉眼估坐标手动裁。
2. **⭐ 先超分再切，防糊**：切图前先对**整张源图**跑 grfal `upscale`（在 removebg 之前，源图不透明超分安全）；元素自带高清，后处理只缩不放，不会糊。绝不用 PIL 直接放大小图当终态。
3. **参考图必须**：没有源参考图无法工作，必须先获取
4. **对（高清）源图 removebg → 切元素**：全程操作源图真实像素；removebg 对高清源图，不是对 AI 重画图
4. **边缘净化（清边）**：每个裁出的元素要去白边/半透明杂边（white-fringe decontaminate），保证 alpha 干净——这是"之前二分法那种干净抠图"的关键步骤，不能省
5. **保留文字**：拆图 1:1 复刻像素，源图有文字就保留（要去文字是另一个 mask edit 需求）
6. **individual 模式先确认**：列出识别到的元素让用户确认
7. **不甩脚本给用户**：直接执行 `call_grfal.py`（可加 `--download-dir`）
8. **必须做后处理**：trimmed 不是终态，individual 模式跑 `ui_extract_postprocess.py`（resize + 量化），只有 `<id>_final.png` 才是入 Unity 的版本
9. **类型归类必须显式**：individual 模式为每个 id 生成 `manifest.json`（id → element_class）
10. **⭐ 抠"图中某一块"必须附裁片参考（2026-06-12 三连返工教训）**：只给整图 reference + 文字描述，模型自己挑区域极易错位/配色看走眼（世界杯队伍板：v1 脑补成月桂横幅、v2 配色切成深绿深蓝，实际是亮黄绿/浅蓝，返工三次）。正解=主 agent/worker 先用 PIL 按比例 bbox 把目标区域裁出来，作为**第二张 reference** 与整图一起传（整图=上下文，裁片=精确目标），prompt 注明"extract exactly the element shown in the second reference"。
11. **⭐ 几何规整件（板/条/框）双保险打法（2026-06-12 定版）**：这类件 AI 默认手抖（波浪边/不对称/透视），prompt 必须钉死「perfectly axis-aligned rounded rectangle + 精确颜色 + 列出此前错误版本当反面清单」——钉死后 AI 能出"又正又华丽"的成品（世界杯队伍板 v3 翻盘实证）。同时用 `C:\ADHD_agent\scripts\draw_ui_panel.py` 程序绘制一版当保底（秒出/参数可调/绝对规整但偏素），两版对比择优：AI 正了用 AI（质感赢），AI 还歪用程序版。
