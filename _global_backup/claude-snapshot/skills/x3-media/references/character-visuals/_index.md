# X3 角色立绘索引

本目录存放 X3 项目角色立绘（PNG）和对应 AI Prompt 关键词，供 x3-media skill 在生图时自动注入 `reference_images` + prompt，确保 AI 出图与角色官设一致。

## 用法（Agent 自动执行，不用人工查）

当用户生图请求中涉及 X3 角色时，Agent 按以下流程处理：

1. 按角色名（中文/英文）在下方表格匹配条目
2. 读取对应 PNG 文件 → base64 编码 → 注入 API 调用的 `reference_images` 参数
3. 把该角色的 **AI Prompt 关键词** 拼到 prompt 末尾，锚定外观

## 添加新角色（用户操作）

1. 把立绘 PNG 放到本目录（建议 1024×1024 或更大，透明底或纯色底）
2. 在下方表格新增一行：

```markdown
| <中文名> | <英文名> | <文件名.png> | <英文 prompt 关键词，逗号分隔> |
```

3. prompt 关键词应包含：种族/性别/年龄、发色发型、服装风格、配饰、表情等 AI 复现外观所需的全部要素

## 角色表

| 中文名 | 英文名 | 立绘文件 | AI Prompt 关键词 |
|---|---|---|---|
| 阿米娜（英雄20） | Amina | `Amina_20_official_fulllength.png` | mature confident female pirate captain, vivid crimson-red long wavy hair with a signature side braid, red headscarf/bandana, tanned olive skin, sharp almond eyes with dark lashes, full lips, athletic hourglass figure, gold jewelry (hoop earrings, layered gold necklaces, arm bangles), knowing half-smile |
| 阿米娜·马戏节皮肤稿 | Amina (Circus skin draft) | `Amina_20_circus_v1alt_ref.png` | same Amina character in circus performer costume, top hat with feather, tailcoat, corset, thigh-high stockings, tall boots — ⚠️**此稿配色(红黑金)已废弃**，仅供构图/姿势/服装形制参考，配色一律以任务 prompt 为准 |

### 使用注意
- **阿米娜的红发是不可改的核心识别符**，任何皮肤都保留；但**服装配色可以完全改**（2026-07-27 马戏节案：红黑金→深紫金，因与本体/春节剑姬/活动背景三重撞车）。
- 喂 `Amina_20_circus_v1alt_ref.png` 当参考时，**必须在 prompt 里显式压制红色服装**（如 `NO red or crimson in the costume, the red hair is the only red`），否则 AI 会继承废弃稿的红黑金。
- 官方本体立绘用于锁脸/发/身材/画风；皮肤稿仅用于锁构图与服装形制。
