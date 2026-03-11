---
name: sprite-reskin
description: |
  Generate AI replacement images for Unity UI sprites and apply the original alpha mask to preserve shape.
  No stretching — AI images are generated at the correct aspect ratio, cover-cropped, and masked.
  Supports single file, batch folder, and catalog poster card composition.
  Use when: (1) replacing sprite artwork while preserving alpha/shape,
  (2) batch reskinning a folder of UI sprites with AI-generated art,
  (3) creating color/theme variants of existing game UI backgrounds,
  (4) composing catalog poster cards with Figma-style border + inner stroke,
  (5) user mentions "换皮", "reskin", "替换贴图", "替换素材", "批量替换图片",
  "生成新素材", "重新生成图片", "sprite替换", "蒙版", "alpha mask",
  "目录海报", "catalog poster", "海报卡片", "compose poster".
---

# Sprite Reskin

Replace Unity UI sprite artwork with AI-generated images. **No stretching or distortion.**

Style presets are in `references/styles.md`（包含 `catalog_poster` 目录页海报等类型）。

---

## Workflow A: Basic Reskin（基础换皮）

适用于：直接替换 sprite 图片，仅需 alpha mask，无额外边框效果。

### Phase 1: Analyze Reference

```bash
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py --analyze <reference.png>
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py --analyze-dir <folder>
```

Output includes orientation, pixel size, and **exact prompt phrases to copy into Phase 2**.

### Phase 2: Generate AI Images

Use `GenerateImage`. **The analyze output gives you three mandatory prompt phrases — copy them exactly.**

**CRITICAL — Orientation controls whether the AI produces portrait or landscape:**

| Reference | Analyze output says | You MUST put in prompt |
|-----------|--------------------|-----------------------|
| 306x404 (tall) | `"tall portrait orientation, vertical composition"` | exactly that phrase |
| 800x400 (wide) | `"wide landscape orientation, horizontal composition"` | exactly that phrase |
| 512x512 | `"square composition"` | exactly that phrase |

**Prompt template** (fill in the blanks, keep the structure):

> "[subject description], [orientation phrase from analyze], [WxH pixels from analyze], main subject centered in frame, [style description]. No text, no borders."

**Rules:**
1. Copy the orientation phrase from analyze output verbatim — this is the #1 factor for correct aspect ratio
2. Include pixel dimensions so the AI generates at the right scale
3. Say `"main subject centered in frame"` so cover-crop preserves content
4. Pass the reference image via `reference_image_paths`

### Phase 3: Apply Mask (Cover-Crop, No Stretch)

```bash
# Single file
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py \
  --ref <reference.png> --input <ai_generated.png> --output <output.png>

# Batch folder
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py \
  --ref-dir <ref_folder> --input-dir <gen_folder> --output-dir <out_folder> \
  --suffix "_Red"
```

**Batch matching rules:**
1. Exact filename: `ref/Foo.png` ↔ `input/Foo.png`
2. Prefix match: `ref/Foo.png` ↔ `input/Foo_Red.png`
3. Single input fallback: one input file applies to all references

### Phase 4: Verify

```bash
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py --analyze-dir <output_folder>
```

---

## Workflow B: Catalog Poster（目录页海报）

适用于：游戏目录/分类页面的海报卡片，需要叠加 Figma 组件样式（圆角边框 + 内描边高光）。

**完整流程：Phase 1 → Phase 2 → Phase 3 → Phase 3.5（compose-poster）→ Phase 4**

Phase 1–3 与 Workflow A 完全相同，在 Phase 3 输出 masked 图片后，再执行 Phase 3.5：

### Phase 3.5: Compose Poster Card（叠加边框效果）

将 Phase 3 的输出叠加 Figma 组件样式：

- **外层**：黑色圆角边框（2px border, corner radius 8px）
- **内层**：内容图 + 亮色内描边高光（corner radius 6px, 2px stroke with blur）

```bash
# Single file
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py \
  --compose-poster --input <masked.png> --output <poster.png>

# Batch folder
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py \
  --compose-poster --input-dir <masked_folder> --output-dir <poster_folder>

# Custom parameters
python .cursor/skills/ui-sprite-reskin/scripts/sprite_reskin.py \
  --compose-poster --input <masked.png> --output <poster.png> \
  --border 2 --corner-outer 8 --corner-inner 6
```

**参数说明：**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--border` | 2 | 边框宽度（px） |
| `--corner-outer` | 8 | 外圆角半径 |
| `--corner-inner` | 6 | 内圆角半径 |

**Figma 组件对照：**

```
Frame (WxH)
├── image_outer (WxH)      ← 黑色圆角底框
└── image_inner ((W-4)x(H-4) at (2,2))  ← 内容 + 内描边高光
```
