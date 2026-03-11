# Sprite Reskin — Style Presets

Pre-defined style prompts for common sprite categories. When using `sprite-reskin`, pick the matching style type and **append** the style snippet to your prompt.

## How to Use

1. Run `--analyze` to get orientation/size phrases.
2. Pick a style type below.
3. Build your prompt:

> "[subject], [orientation phrase], [WxH pixels], main subject centered in frame, [style snippet]. No text, no borders."

---

## Style Types

### catalog_poster（目录页海报）

游戏内目录/分类页面的海报卡片，通常带圆角边框 + 内描边高光效果。典型尺寸 306x404。

**Figma 组件结构：**

| 图层 | 尺寸 | 说明 |
|------|------|------|
| Frame 外框 | WxH（如 306x404） | 最终画布 |
| image 外框底图 | WxH | 黑色圆角边框（border=2px, radius≈8px） |
| image 内容图 | (W-4)x(H-4) at (2,2) | 内容 + 内描边高光（radius≈6px, stroke=2px） |

**生图后需要额外执行 `--compose-poster` 来叠加边框和描边效果。**

**Style snippet:**

```
3D cartoon semi-realistic render style with rich material textures, volumetric lighting,
warm subsurface glow, painterly quality similar to stylized mobile game character art,
dramatic cinematic lighting with strong contrast
```

**Example prompts:**

| Subject | Full prompt (fill in orientation/size from analyze) |
|---------|-----------------------------------------------------|
| 陨石坠落 | "A dramatic red meteor crashing into the ground with a powerful impact explosion, [orientation], [WxH pixels], main subject centered in frame, scattered debris rock fragments and smaller meteor shards across the ground surface, dark dramatic sky with smoke and dust clouds, 3D cartoon semi-realistic render style with rich material textures, volumetric lighting, warm subsurface glow, painterly quality, dramatic cinematic lighting with strong contrast. No text, no borders." |
| 冰霜场景 | "A frozen ice landscape with crystalline frost formations and swirling snowstorm, [orientation], [WxH pixels], main subject centered in frame, glowing blue ice shards and frozen terrain, cold atmospheric fog, 3D cartoon semi-realistic render style with rich material textures, volumetric lighting, cool subsurface glow, painterly quality, dramatic cinematic lighting with strong contrast. No text, no borders." |
| 火焰场景 | "Raging fire erupting from cracked volcanic ground with lava flows, [orientation], [WxH pixels], main subject centered in frame, embers and ash particles floating upward, intense heat haze, 3D cartoon semi-realistic render style with rich material textures, volumetric lighting, warm subsurface glow, painterly quality, dramatic cinematic lighting with strong contrast. No text, no borders." |

---

<!-- Add new style types below this line -->
