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
| 场景 | scene | game environment, atmospheric lighting, detailed background, fantasy or modern setting, wide composition | — |
| 道具 / 物品 | item | game item icon, clean edges, slight glow, inventory style, consistent lighting | — |
| 动态行军表情 | march_emoji | 2D game UI icon, vector illustration style, flat color, sticker texture, dynamic emoji pack first frame, half-body close-up, thick line outline, pure white background | **需人物参考图**，产出 256×256 |
| 技能图标 | skill_icon | ONE SINGLE circular game skill icon, transparent background (no white), do NOT generate multiple icons or a grid, just one single icon in the center, completely borderless, NO circular outline, NO drawn circle, NO edge line, NO stroke, shape formed naturally by content, The entire illustration MUST be strictly contained within a perfect circle with wide transparent padding around it. Nothing should extend beyond the circular edge, circular badge, vector 3D style, skill effect in dynamic composition, balanced circular composition, green and golden-orange palette, if character or creature appears: solid dark silhouette completely filled no hollow parts no internal transparency, single subject only one figure no multiple characters | 详见 `type-skill-icon.md` |
| 集卡册卡片 | card_gallery | game collectible card, vertical card format, no border no card frame no decorative frame, 3D rendered stylized cartoon, character full body or half-body centered, fantasy game character design, rich costume and prop details, themed background with soft environmental or dramatic lighting, rich color palette optional gold or metallic accents, avoid overwhelming bokeh or confetti particles keep effects subtle, clear silhouette and expressive face, album card illustration, consistent game UI asset style, full body visible in frame adequate margin no severe cropping, character centered with safe zone on all sides do not place subject at frame edge, face and expression consistent with reference character design | 需确认人物与模型，产出 640×900，详见 `type-card-gallery.md` |
| UI素材提取 | ui_extract | Extract and isolate all UI elements from the reference image, remove absolutely all text labels typography letters numbers and written content, place each UI element cleanly on a pure white solid background, preserve original colors and visual style of each element, clear separation between elements, no overlapping, clean crisp edges, game UI asset sheet style, extract only UI components such as buttons icons panels progress bars frames decorations badges tabs sliders | 需UI参考图，支持 grid/individual 模式，详见 `type-ui-extract.md` |
| 活动图标 | activity_icon | single 3D game item icon, completely transparent background, no frame no border no circle, 3D rendered stylized cartoon, steampunk mechanical aesthetic with gears rivets and metal pipes, vibrant saturated colors, warm golden and metallic tones, clean crisp edges, subtle soft shadow underneath, game UI asset style, no text no labels no numbers no letters, single centered object | 需节日参考元素，产出 256×256 透明底，详见 `type-activity-icon.md` |

## 维护说明

- 新增类型：在本表增加一行
- 修改风格：直接改对应行的 default_prompt
- 类型 key 用于在 Router 中快速匹配
