# 活动图标（activity_icon）完整流程

活动内用的 256×256 透明底 3D 物件图标，用于活动界面内的功能入口、奖励展示、主题标识等位置。

---

## 何时匹配

用户说：活动图标、活动 ICON、活动小图标、节日图标、activity icon、做个活动入口图标 等。

---

## 视觉规范

| 属性 | 要求 |
|------|------|
| **尺寸** | 256×256 像素 |
| **背景** | 透明底（四角 alpha = 0），无边框、无圆形外框 |
| **形状** | 非固定形状，由物件本身轮廓决定 |
| **风格** | 3D 卡通渲染，蒸汽朋克/末日机械游戏美术风格，与 X2 项目一致 |
| **主体** | 单一物件居中，视觉元素紧凑，不留大面积空白 |
| **质感** | 金属铆钉、齿轮、管道等蒸汽朋克元素，色彩饱和鲜明 |

---

## 流程（必须按序执行）

1. **获取活动主题**：确认用户要做什么活动的图标（如：周卡、每日礼包、限时折扣、节日活动等）
2. **获取节日参考元素（必须）**：用户需提供节日相关的参考元素，可以是：
   - 参考图片（已有活动素材、节日主视觉、主题色板等）
   - 文字描述（节日名称、主题元素、色调偏好等）
   - 若用户未提供，提示「请提供节日相关的参考元素（图片或文字描述均可），如主题色、节日元素、风格方向等」
3. **确认模型**：未指定模型且 config 无偏好 → **必须先询问**
4. **构造 prompt**：default_prompt 全文 + 活动主题描述（英文） + 节日元素描述（英文）
5. **传入参考图**：从 `references/activity-icon-ref/` 中选 2-3 张风格最接近的作为 `reference_images`
6. **调用 API**：见 `api-calling.md`，`aspect_ratio: "1:1"`
7. **后处理**：缩放至 256×256（使用 `scripts/skill_icon_postprocess.py`）
8. **保存**：按命名规则保存到下载目录

---

## Prompt 通用约束

以下约束**必须包含**在每次生成的 prompt 中：

- **透明底**：`completely transparent background, no background color, no circle frame, no border`
- **单一物件**：`single centered 3D object, no multiple items scattered`
- **无文字**：`no text, no labels, no numbers, no letters, no typography`
- **3D 卡通风格**：`3D rendered stylized cartoon, game item icon style, steampunk mechanical aesthetic`
- **清晰边缘**：`clean crisp edges, no blur, no feathering, subtle soft shadow underneath`
- **色彩鲜明**：`vibrant saturated colors, warm golden and metallic tones`

---

## Default Prompt

```
single 3D game item icon, completely transparent background, no frame no border no circle, 3D rendered stylized cartoon, steampunk mechanical aesthetic with gears rivets and metal pipes, vibrant saturated colors, warm golden and metallic tones, clean crisp edges, subtle soft shadow underneath, game UI asset style, no text no labels no numbers no letters, single centered object
```

**拼接规则**：prompt = default_prompt 全文 + 英文逗号 + 活动主题描述（英文） + 英文逗号 + 节日元素描述（英文）

---

## Reference Images（选 2-3 张）

从 `references/activity-icon-ref/` 目录中，根据活动主题选取风格最接近的参考图：

| 活动类型 | 建议参考图 |
|---------|-----------|
| 礼包/礼盒类 | `RedEnvelop__IconRedEn*.png` |
| 商店/兑换类 | `Alliance__AllianceShop2.png` |
| 道具/物品类 | `ItemIcon__*.png`, `BattlePass__daoju*.png` |
| 机械/科技类 | `BossRush__*.png`, `Underground__Icon_Science.png` |
| 活动入口/通用 | `ActivityKvK__*.png`, `Other__Icon*.png` |
| 人物/NPC 类 | `NPC__*.png` |

---

## 后处理

1. 将生成图片缩放到 **256×256**
2. 运行 `scripts/skill_icon_postprocess.py <图片路径>`
3. 确认输出通过合规检测（256×256，有效内容面积足够）

---

## 文件命名

```
activity_icon_<活动主题英文简写>.png
```

| 示例活动 | 文件名 |
|---------|--------|
| 周卡 | `activity_icon_weekly_card.png` |
| 每日礼包 | `activity_icon_daily_gift.png` |
| 限时折扣 | `activity_icon_limited_discount.png` |
| 春节活动 | `activity_icon_spring_festival.png` |
| 复活节活动 | `activity_icon_easter.png` |

---

## 关键规则

1. **节日参考元素必须**：没有主题参考无法生成，必须先获取
2. **透明底必须**：不能有任何背景色、边框、圆形外框
3. **风格一致性**：必须和 `activity-icon-ref/` 中的参考图保持同一游戏美术风格
4. **多张并行**：N 张图用 `Start-Job` 并行，禁止串行循环
5. **不甩脚本给用户**：直接执行生成和后处理流程
