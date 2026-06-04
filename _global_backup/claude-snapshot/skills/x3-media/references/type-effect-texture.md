# 特效贴图（effect_texture）完整流程

本文件自包含 Unity 粒子/特效贴图生成的全部规则：原理、prompt 构造、后处理、命名。

参考样本（技能仓库内）：`references/effect_texture_samples/common_icon_CrossServer_Wonder2.png`
（源自项目 Unity 客户端 `client/Assets/x3/Res/Effect/Textures/obj/`，首次使用时用来理解 RGB=白 + Alpha=形状 的格式）

---

## 核心原理（务必先理解再动手）

Unity 特效贴图 ≠ 普通图标。它是**纯剪影蒙版**，运行时靠粒子/Shader 着色：

- **尺寸**：`2^N` 正方形（默认 256×256；允许 128/512）
- **RGBA**：**RGB 恒为 (255, 255, 255)，所有形状信息只在 Alpha 通道**
- **边缘**：清晰锐利，无柔边羽化（接近二值化；Alpha 只在边缘做 1 px 抗锯齿过渡）
- **构图**：单一主体居中，四周留透明 padding
- **禁止**：颜色、渐变、阴影、发光、高光、文字、边框、任何灰度色块

**关键**：AI 模型几乎无法直接产出"透明底 + RGB 全白"的贴图。策略是：
1. 让模型画「**纯黑底 + 纯白实心剪影**」（这一步可靠）
2. 本地后处理脚本：**亮度 → Alpha**，**RGB 强制全白 (255,255,255)**，正方形归一化到 2^N

跳过后处理 = 不合格贴图。

---

## 流程（必须按序执行）

1. **索要/确认主题**：与用户确认主体（例：王冠奖杯、翅膀、星星、剑、符文、图腾、拳头…）；若有同系列参考，向用户索要参考图
2. **确认尺寸**：默认 256×256；若用户需要更精细/更省显存，问清 128 或 512
3. **模型**：未指定且 config 无偏好 → **必须先询问**；推荐 `gpt`（对"纯黑白无灰度"依从性最好）；其次 `gemini`
4. **构造 prompt**：default 约束（下方）+ 用户主题（英文化、审美化）
5. **调用 API**：见 `api-calling.md`，参数 `transparent_background: false`（我们要黑底白图，不是透明底）
6. **下载**：保存到下载目录
7. **后处理**：运行 `scripts/effect_texture_postprocess.py`（亮度→Alpha + RGB 全白 + 正方形缩放）
8. **自检**：脚本输出后，读 RGB 均值应为 255、Alpha 可见像素占比在 10%–60% 合理区间
9. **产出**：按命名规则保存到目标目录；有同系列时追加序号后缀
10. **临时文件清理**：删除 `_params_*.json` 与中间黑底版本

---

## Prompt 通用约束（拼到用户描述前）

英文原文按以下模板逐字拼接，**不得改写**：

```
Pure solid white silhouette of {SUBJECT}, flat filled shape, no internal details,
no shading, no gradient, no highlights, no shadow, no glow, no rim light,
hard crisp edge, sharp clean vector-like outline, centered composition with
generous transparent padding around the shape, single subject only, no text,
no letters, no border, no frame, no background pattern.
PURE BLACK background (#000000), absolutely uniform, no texture, no noise,
no atmospheric fog, no particles. The silhouette must be PURE WHITE
(#FFFFFF, R=G=B=255) with NO grayscale, NO anti-aliasing gradient except
a single pixel of edge smoothing. Square 1:1 aspect ratio. ONE SINGLE shape,
do NOT generate multiple shapes or a grid.
```

**用户主题转英文**：只描述形状轮廓特征（剪影看得见的），不要描述颜色/材质/光影。
- 好：`a crown trophy: tall royal crown on top with five cross-tipped spires, narrow neck, wide tiered pedestal base with two steps`
- 差：`a golden crown trophy with glowing gems and metallic shine`（颜色/光影会污染剪影）

---

## 参数文件模板

```json
{
  "prompt": "<上方通用约束全文> + <主题英文>",
  "model": "gpt",
  "num_images": 1,
  "aspect_ratio": "1:1",
  "image_size": "square_hd",
  "output_format": "png",
  "transparent_background": false
}
```

**注意**：`aspect_ratio: 1:1` 是硬约束，决不能输出非正方形。

---

## 后处理（必须执行）

运行脚本：

```powershell
py "<x3-media>/scripts/effect_texture_postprocess.py" <AI原图路径> `
   --output <目标路径> --size 256
```

脚本做的事（固定顺序）：
1. 转灰度；**如背景偏亮/主体偏暗自动反相**（保证"主体=白"）
2. 阈值/对比度增强 → 可选轻度二值化（默认 `--threshold 0` 不强制二值，仅做对比度拉伸）
3. 缩放到 `--size × --size`（默认 256，允许 128/512；正方形裁切居中）
4. 组装 RGBA：**R=G=B=255 常量**，**A=灰度值**
5. 可选 `--trim` 去掉外围多余透明边后重新按 `padding_ratio` 居中（默认关闭，保持原构图）
6. 覆盖输出；打印统计（RGB 均值、alpha 可见占比）

**自检通过标准**：
- `mode == 'RGBA'`
- `R == G == B == 255` 恒成立
- `alpha > 10 的像素占比在 5% ~ 70%`（太低=主体太细，太高=图填满了，均需重做）

---

## 文件命名

贴图文件名遵循同目录约定，**由用户确定最终名**。常见前缀：

| 用途 | 前缀示例 | 说明 |
|------|---------|------|
| 通用 Obj 贴图 | `Obj_001.png` ~ `Obj_NNN.png` | 粒子素材 |
| 图标类（功能关联） | `common_icon_<Feature>_<Name>N.png` | 如 `common_icon_CrossServer_Wonder2.png` |
| Mask 类 | `Mask_NNNN_kd.png` | 配合 Shader 遮罩 |

默认产出先保存到 `$env:USERPROFILE\Downloads\<name>.png`，用户确认后再拷入项目 Unity 客户端 `client/Assets/x3/Res/Effect/Textures/obj/`（具体绝对路径由用户在 `config.json` 中提供 `project_path` 后拼接）。

---

## Gotchas — 特效贴图专属踩坑

1. **灰度过渡** — 模型容易在白色剪影内加高光/阴影造成灰度，后处理脚本的"亮度→Alpha"会把灰度当半透明，导致贴图发灰。prompt 一定要写 `no shading, no gradient, no highlights, no shadow`。

2. **多色/描边** — 模型常自作主张加彩色描边、外发光。脚本不做去色（假设输入已是黑白），所以 prompt 必须守住黑白二值底线。如果输出有彩色污染，脚本需加 `--desaturate` 再跑一次。

3. **非正方形** — 模型如果输出 16:9 或 4:3，脚本会裁中间正方形，但主体可能被裁掉或留大量空白。一律强制 `1:1 / square_hd`。

4. **形状贴边过满** — 和普通图标不同，特效贴图需要 padding（约 10%~20%）。如果 AI 输出太满，脚本加 `--padding 0.15` 二次居中。

5. **分辨率误区** — Unity 特效贴图 99% 是 2^N（128/256/512/1024），非 2^N 会触发 mipmap 重采样导致显存浪费。输出务必是 2^N。

6. **反相判断** — 少数时候模型会输出白底黑图（正好反了）。脚本靠"背景角落像素亮度"自动判断并反相，但用户用奇特 prompt 可能失败，此时加 `--invert` 手动反转。

7. **边缘粗糙** — AI 输出的边可能带低频噪波。脚本加 `--smooth 1` 做 1 px 中值滤波可改善；但过度会破坏细节。
