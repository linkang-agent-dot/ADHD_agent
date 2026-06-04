# type: ui_extract_fine — 精细拆图（MXAI 同款 bbox-mask inpainting）

MXAI 工具的多图层提取效果（每层独立 PNG，像素 100% 对齐源图，可叠加还原）= **OpenAI gpt-image-2 inpainting + chroma key 去绿**。

grfal 自 2026-05-21 起暴露 `image_mask_edit` 端点（gpt-image-2 mask edit），这就是 MXAI 用的同款 inpainting。本流程基于此。

## 何时用此 type

| 适合 | 不适合 |
|---|---|
| UI 截图多图层拆分（底框 / 装饰 / 光晕 / Hero）| 完全无重叠的简单 sprite（用普通 `ui_extract`）|
| 要求像素 100% 对齐源图 | 速度优先时（每层 60-90s）|
| 要单层透明 PNG 可叠加还原 | 角色毛发抠图（mask 矩形不够细，需 SAM 或 alpha matting） |
| MXAI 风格多图层 PSD 还原 | 已经在 alpha PNG 里的素材（直接复用）|

## 核心原理

grfal `image_mask_edit` 语义（详见 `grfal-api/references/tool_catalog.md#image_mask_edit`）：

- **mask 是 RGBA PNG**，跟源图同尺寸
- **alpha > 0 的像素**：被 gpt-image-2 按 prompt 重画
- **alpha == 0 的像素**：服务端 composite，**100% 保留原图像素**

所以对每个图层，我们生成一个反向 mask：
- 该图层 bbox 内 alpha=0（保留目标层 100% 像素）
- bbox 外 alpha=255（被 gpt 重画为纯绿）

服务端返回的图 = 目标层完美对齐 + 其余纯绿 → 本地 chroma key 去绿 = 单层透明 PNG。

**优势**（对比旧的双底差分 / 风格迁移）：
- ✅ 像素 100% 对齐（mask 外完全不动）
- ✅ 单次 API 调用（不是双底两次）
- ✅ 边缘 feather=4px 自然过渡（不锐切）
- ⚠ 限制：bbox 是矩形（适合 UI 元素；不适合极不规则形状如毛发，需要更精细 mask）

## 两种跑法
- **DesignDeck 内**：勾「精细拆图」，mask + 去绿由主进程 jimp 跑（下文 4 步的 stdout 标记路径）。
- **脱离 DesignDeck（本地整机，2026-06 补）**：`scripts/ui_extract_fine.py` 把原来主进程那两步 jimp 补成了本地脚本（`make_bbox_mask.py` 画反向 mask + `chroma_key.py` 去绿），一条命令跑完整条。
  - 人工节点：先看图写 `manifest_layers.json`（层+bbox）→ `python ui_extract_fine.py --src 源图 --manifest m.json --preview`（画框确认，不烧 API）→ 框对了再去掉 `--preview` 开拆。

## 流程（4 步，每层串行）

### Step 1 — 准备输入 + 视觉分析

- 输入：源参考图（绝对路径）
- 用 Read tool 看源图，记录 `SRC_W` `SRC_H`（像素）
- 视觉识别 3-6 个主要图层（若用户已指明则按其拆）
- 每层估算包住所有像素的最小矩形 `[x, y, w, h]`（每边 +10~20px 缓冲）
- 落 `manifest_layers.json`：

```json
[
  { "id": "layer_1_baseframe", "desc": "底部主框架 / 金属边", "bbox": [40, 980, 1000, 80] },
  { "id": "layer_2_glow",      "desc": "中央水平光晕",        "bbox": [120, 500, 840, 200] },
  { "id": "layer_3_left_deco", "desc": "左侧电路装饰",        "bbox": [60, 300, 320, 600] },
  { "id": "layer_4_right_deco","desc": "右侧电路装饰",        "bbox": [700, 300, 320, 600] }
]
```

### Step 2 — 触发主进程生 mask（DesignDeck 路径）

DesignDeck spawn 主 claude 时，在 stdout 写一行标记，主进程会自动跑 jimp 画 mask：

```
MAKE_BBOX_MASK src=<源图> bboxes=[[40,980,1000,80]] out=<outDir>/<id>_mask.png
```

- bbox 是**二维数组**（即使只有一个 bbox 也要外层 `[[...]]`）
- 多 bbox 并集：`[[x1,y1,w1,h1],[x2,y2,w2,h2]]`（适用于跨多区域，如左右对称装饰共享一层）
- 主进程跑 jimp 画 RGBA mask：
  - 整图初始 alpha=255（可编辑）
  - bbox 内 alpha=0（保留），边缘 feather=4px 渐变
  - 输出到 `out=` 指定路径
- 等主进程 echo `[bbox_mask] done` 后再进 Step 3（用 `Test-Path` 轮询 mask 文件存在）

**CLI fallback**：若直接命令行跑 claude 没 DesignDeck → 自己用 Python PIL 画 mask（不推荐，用 DesignDeck）。

### Step 3 — 调 grfal image_mask_edit

```powershell
python C:\Users\caoxinying\.claude\skills\grfal-api\scripts\call_grfal.py --tool image_mask_edit `
  --params '{"multimodal":{"text":"Fill the masked editable region with a single uniform pure solid chroma key green color (#00FF00, RGB 0 255 0). Do not add any objects, shadows, gradients, text or texture. The whole non-preserved area must be one flat bright green.","files":[]},"model_type":"gpt","num_images":1}' `
  --file image_path=<源图绝对路径> `
  --file mask_path=<outDir>/<id>_mask.png `
  --download-dir <outDir> `
  --timeout 240
```

- **必须 `model_type=gpt`**（gpt-image-2 是唯一稳定 mask edit 后端）
- 下载文件名形如 `image_0.png` → **立即重命名**为 `<outDir>/<id>_inpaint.png`
- 单层失败（GPT 空 / 超时）→ 该层标 `status: failed`，跳到下一层

### Step 4 — 触发 chroma key 去绿

在 stdout 写：

```
READY_FOR_CHROMA_KEY input=<outDir>/<id>_inpaint.png out=<outDir>/<id>.png
```

DesignDeck 主进程检测到自动跑 jimp HSL chroma key：
- 绿色判定：hue 120° ±40° + saturation > 0.35
- Anti-spill：边缘溢绿像素把绿色分量压到 max(R,B)
- 输出最终 `<id>.png`（透明背景）

等 `[chroma_key] done` 再进下一层。

## 完整 stdout 序列（示意）

```
[主 claude 输出]
读取源图：1080x1920
识别 4 层：baseframe / glow / left_deco / right_deco
写 manifest_layers.json ✓

MAKE_BBOX_MASK src=<src> bboxes=[[40,980,1000,80]] out=layer_1_baseframe_mask.png
[主进程] [bbox_mask] done · 1080x1920 · preserved=80000 editable=2065600 · 12ms

调 grfal image_mask_edit (layer_1_baseframe)...
下载到 image_0.png → 重命名为 layer_1_baseframe_inpaint.png ✓

READY_FOR_CHROMA_KEY input=layer_1_baseframe_inpaint.png out=layer_1_baseframe.png
[主进程] [chroma_key] done · 1080x1920 · removed=72.4% · 28ms

（重复以上对 layer_2 / layer_3 / layer_4）

MEDIA_DONE type=ui_extract_fine status=success
```

## 校验

每层 chroma key 后看 stdout `removed%`：

- **50-80%**：好 — 目标层 bbox 占比合理
- **< 5%**：GPT 没听 prompt 没生绿（重画了别的内容），标 partial 提示用户
- **> 95%**：bbox 估算太小，目标层被切掉，重新估 bbox

## 失败 fallback 矩阵

| 错误 | 处理 |
|---|---|
| 视觉识别不到清晰图层 | 停下来问用户"想拆哪几层" |
| 某层 image_mask_edit 失败 | 标 failed 跳过；其他层继续 |
| 全部层失败 | 降级到普通 `ui_extract` individual 模式 |
| chroma key removed% < 5% | 标 partial；提示用户重试或调整 bbox |
| GPT 排队 > 240s | 超时退出该层；跳到下一层 |

## 完成输出

```
MEDIA_DONE type=ui_extract_fine status=<success|partial|failed>
```

fenced JSON：

```json
{
  "layers": [
    {"id":"layer_1_baseframe","path":"layer_1_baseframe.png","bbox":[40,980,1000,80],"chroma_removed_pct":72.4,"status":"success"},
    {"id":"layer_2_glow","path":"layer_2_glow.png","bbox":[120,500,840,200],"chroma_removed_pct":68.1,"status":"success"}
  ],
  "source_image": "<src>",
  "total_layers": 4
}
```

## 已知坑

1. **bbox 必须包住目标层全部像素** — 漏一点点边缘会被切掉 → 估算时每边加 10~20px 缓冲
2. **不规则形状（毛发 / 烟雾）矩形 mask 不够细** — 这种素材应该用旧的双底差分或外部 SAM；本流程主要适用于 UI 元素
3. **多层 bbox 重叠是允许的** — 不同层各自保留自己 bbox 内的像素，互不冲突
4. **不要用 `generate_image`** — 那是风格迁移，会漂移；本流程严格走 `image_mask_edit`
5. **不要并行多层** — grfal 排队会更长，且 stdout 标记乱序难调试
6. **gpt-image-2 偶尔不听 prompt 重画了别的** — 看 removed% 判定；< 5% 时重试或换 bbox

## 与其他 type 的关系

| Type | 适用 | API | 后处理 |
|---|---|---|---|
| `ui_extract`（普通）| UI 控件批量、单元素 | grfal `generate_image` + `remove_background` | `ui_extract_postprocess.py`（resize + pngquant）|
| `ui_extract_fine`（本流程）| 多图层拆分 + 像素 100% 对齐 | grfal `image_mask_edit`（gpt-image-2 inpaint）| `createBboxMask` + `chromaKey` (jimp, DesignDeck 内置) |

用户在 DesignDeck 的 `✂ 拆图` 面板里勾选「精细拆图」会切到本流程。
