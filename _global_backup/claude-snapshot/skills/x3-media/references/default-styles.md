# 默认风格

当用户要生成图片且**库中有该类型的默认风格**时：**若用户没有特殊指定风格，一律使用默认风格**（不询问）；仅当用户**明确说不使用默认风格**或**指定了其他风格**时，才不叠加默认风格。

## 使用规则

1. 用模糊/语义匹配判断用户意图是否在下表中有默认风格
2. **有默认风格且用户未指定其他**→ 直接使用，不询问
3. prompt = **default_prompt 全文（一字不差）** + 英文逗号 + 用户描述（英文）
4. **禁止**自拟、缩写或改写 default_prompt

## 默认风格列表

| 类型 | 类型 key | 默认风格提示词（default_prompt） | 备注 |
|------|----------|--------------------------------|------|
| 技能 | skill | game skill icon, magic effect, vibrant colors, clear silhouette, fantasy style, centered composition | — |
| 立绘 / 角色 | character | game character standing portrait, full body or upper body, clean lineart, anime game style, neutral background | — |
| 场景 | scene | clean stylized 3D cartoon render, smooth 3D geometry, crisp cel-shaded toon shading with clear gradient bands, plastic-smooth surfaces with stylized specular highlights, polished glossy materials, vibrant saturated colors, soft natural ambient lighting, clean minimal composition, sharp clean silhouettes, high-end 3D mobile game CG look, not painterly, not brush-stroke textured, not hand-painted, not anime-CG, no heavy light burst effects | 用户锁定风格：3D 卡通渲染 + 柔和自然光照，整体干净克制 |
| 海报 | poster | clean stylized 3D cartoon render, smooth 3D geometry, crisp cel-shaded toon shading with clear gradient bands, plastic-smooth surfaces with stylized specular highlights, polished glossy materials, vibrant saturated colors, soft natural ambient lighting, clean minimal composition with strong focal subject, sharp clean silhouettes, high-end 3D mobile game CG look, not painterly, not brush-stroke textured, not hand-painted, not anime-CG, no heavy light burst effects | 用户锁定风格：3D 卡通渲染 + 柔和自然光照，整体干净克制 |
| 道具 / 物品 | item | game item icon, clean edges, slight glow, inventory style, consistent lighting | — |
| 行军表情 | march_emoji | expressive in-game sticker emoji portrait, western-cartoon mobile game style, chibi proportions with oversized head and short upper torso, thick dark outline, rounded simplified shapes, clean two-step cel shading, warm saturated colors, large readable facial features, enlarged hands for gesture readability when needed, half-body close-up, centered composition, stable top padding, clear silhouette, transparent background, no frame, no card, no scene background, not realistic, not painterly, not regular UI icon | **需人物参考图**，产出 256×256；默认贴近游戏内现有表情包资产 |
| 技能图标 | skill_icon | ONE SINGLE circular game skill icon, transparent background (no white), do NOT generate multiple icons or a grid, just one single icon in the center, completely borderless, NO circular outline, NO drawn circle, NO edge line, NO stroke, shape formed naturally by content, The entire illustration MUST be strictly contained within a perfect circle with wide transparent padding around it. Nothing should extend beyond the circular edge, circular badge, vector 3D style, skill effect in dynamic composition, balanced circular composition, green and golden-orange palette, if character or creature appears: solid dark silhouette completely filled no hollow parts no internal transparency, single subject only one figure no multiple characters | 详见 `type-skill-icon.md` |
| 纪念品/收藏品图鉴 | card_gallery | STRICT STYLE LOCK — the attached reference image is the EXACT visual fingerprint to copy. Your output MUST look like it was painted by the SAME illustrator: warm hand-painted 2D cartoon trinket icon style, THICK BOLD BLACK OUTLINES clearly visible at every silhouette edge (pronounced dark ink stroke around each object), painterly cell-shading with vibrant warm mid-tones, clean fresh appearance, small soft brown contact shadow under each item. Match the reference's bold outline weight, paint texture, warm vibrant palette, and contact-shadow style. 2048x2048 SQUARE, PURE WHITE background #FFFFFF. EXACTLY 9 keepsake item icons in a clean 3x3 grid. No labels, no numbers, no captions, no text under items. No shelf, no frame, no domes, no ground line — items float with soft brown contact shadow only. Identical scale across all 9, equal spacing, warm upper-left key light. | **9 items 3×3 信物 grid sheet**（2048×2048 白底）— 粗黑描边 + 鲜亮暖色，不走旧物 / 乡愁 / sepia 风。用户描述只写 Theme + 9 items；REJECT 段由 `mediaTypes.ts.negativePrompt` 自动拼到末尾。详见 `type-card-gallery.md` |
| UI素材提取 | ui_extract | Extract and isolate all UI elements from the reference image, remove absolutely all text labels typography letters numbers and written content, place each UI element cleanly on a pure white solid background, preserve original colors and visual style of each element, clear separation between elements, no overlapping, clean crisp edges, game UI asset sheet style, extract only UI components such as buttons icons panels progress bars frames decorations badges tabs sliders | 需UI参考图，支持 grid/individual 模式，详见 `type-ui-extract.md` |
| 按钮 | button | game UI button, polished 3D cartoon render, vibrant saturated color, beveled edge with subtle inner highlight and bottom shadow, slight glow rim, rounded rectangle or pill shape, transparent background, no text label inside button (label area shown as colored stripe if needed), single button centered, designed for 9-patch slicing with preserved corner detail, normal state | 透明底，9-patch 兼容；详见 `type-button.md` |
| UI 框 / 背景 | uiframe | game UI frame or background panel, polished 3D cartoon render, warm-toned medieval/fantasy palette, decorative ornate border with golden metallic accents, subtle inner gradient, transparent area outside the frame for compositing, no text labels inside, designed for 9-patch slicing with preserved corner detail, fixed-size composition | 头像框/弹窗背景/标题装饰条/列表项背景，详见 `type-uiframe.md` |

## 参考图喂入规则（所有 type 通用，硬约束）

每次调 grfal `generate_image` 时，**第一张 `reference_images` 必须是该 type 的风格模板大图**：

```
references/<type>_style_template.png
```

**例**：跑 `skill_icon` 时第一张 ref = `references/skill_icon_style_template.png`。

**为什么**：这张图是该 type 的「美术基准」，含多变体 + 调色板 + 排布范例，喂进去能让 GPT 收敛到 X3 项目实际风格（之前不喂模板时各种风格漂移）。

**追加规则**：
- 若该 type 还需要**内容参考图**（如 character 立绘 / 用户传的源图）→ 追加为第 2-4 张 ref
- 单次调用 `reference_images` 总数 **不超过 4 张**（再多 GPT 容易混淆）
- 若 `<type>_style_template.png` 不存在 → 跳过这条规则（不强报错），直接用 default_prompt + 内容 ref

**当前已有的 9 张风格模板**（2026-05-22 落地）：
`skill_icon` / `march_emoji` / `white_icon` / `achievement_badge` / `resource_icon` / `item_icon` / `herofragment_icon` / `button` / `uiframe`

其他 type（如 `activity_icon` / `effect_texture` / `card_gallery` / `dynamic_march_emoji` / `small_icon` / `game_video` / `ui_extract` / `general`）暂无模板，按原 default_prompt 走。

---

## 维护说明

- 新增类型：在本表增加一行
- 修改风格：直接改对应行的 default_prompt
- 类型 key 用于在 Router 中快速匹配
- 加新 style template：跑一次 reference sheet 生图 → 落到 `references/<type>_style_template.png` → 上面的规则自动生效
