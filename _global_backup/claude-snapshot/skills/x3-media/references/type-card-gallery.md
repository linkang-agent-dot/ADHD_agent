# 纪念品 / 收藏品图鉴（card_gallery）完整流程

## 何时匹配

用户说：纪念品图鉴、收藏品图鉴、信物图鉴、物件图鉴、回忆图鉴、CardGallery / CardGallary、信物 grid sheet、9 items 3×3 等。

> ⚠ 注意：本类型已从「人物图鉴卡」**重定向为「9 items 3×3 信物 grid sheet」**。
> 一张 2048×2048 白底图里 9 个收藏品 3×3 平铺，统一风格、统一缩放、纯白底、无文字。
> 若用户实际要的是英雄人物图鉴卡，先与用户确认 —— 当前默认风格不再走人物。

## prompt 结构（**重要：用户只写中间部分**）

完整 prompt = 三段拼接，**头/尾固化在 mediaTypes.ts**，用户只填中间：

```
[STRICT STYLE LOCK 段]   ← mediaTypes.ts.defaultPrompt （固定不变）
[Theme + 9 items 列表]   ← 用户写的 description
[REJECT 段]              ← mediaTypes.ts.negativePrompt（固定不变，永远在最后）
```

主进程 `MediaRunner.prepareTaskInputs` 按顺序拼接 → 写 `prompt.txt` + `_call.ps1`，
所以你做新主题时**只需在 description 框写 Theme + 9 个 items**。

## 用户填写格式（description 字段）

```
Theme: <中文名> (<English Name>). Render exactly these 9 items in 3x3 order, top-left to bottom-right:
(1) <item1> — <description>
(2) <item2> — <description>
(3) <item3> — <description>
(4) <item4> — <description>
(5) <item5> — <description>
(6) <item6> — <description>
(7) <item7> — <description>
(8) <item8> — <description>
(9) <item9> — <description>
```

完整示例库见 `E:/x3git/x3-project/_assets/xinwu_tujian/all_prompts.md`，
里面有 16 个主题（童年/友情/爱情/亲情/师恩/旅伴/战友/故乡/求学/梦想/离别/重逢/信仰/邻里/传承/异乡），
按需复制 Theme + 9 items 块进 description 即可。

## 流程

1. **确认主题**：与用户确认信物主题名（中文 + 英文）+ 9 个 items 清单（若用户没给完整 9 项，按 `all_prompts.md` 配方或主题语义自由发挥补齐）
2. **生成 prompt**：用户描述填进 description → 主进程自动拼 STYLE 头 + REJECT 尾
3. **参数**：params 须带 `"aspect_ratio": "1:1"`（2048×2048 正方形）
4. **风格模板（必须）**：主进程自动注入 `<media_skill_root>/references/card_gallery_style_template.png` 作为第一张 reference_image（STRICT STYLE LOCK 段就是指它）
5. **调用 API**：见 `api-calling.md`
6. **下载 + 后处理**：保留 2048×2048 grid sheet 原图，按需切单 item（用 ui_extract 流程）
7. **清理**：完成后删除当次一次性临时文件

## 关键规则

- **9 items 3×3 grid**：一张图固定 9 个 item，不要 6 / 12 / 16 个，不要单 item
- **纯白底 #FFFFFF**：背景必须纯白，无场景、无木板、无陈列架
- **统一缩放**：9 个 item 视觉大小一致，等间距
- **无文字**：图里**严禁**任何 caption / label / 编号 / 商标
- **无人物**：画面里**严禁**出现人物 / 角色 / 半身像 / 头像
- **鲜亮暖色调**：金 / 红 / 橙 / 棕 / 木质 / 暖色辅以小量蓝绿点缀，clean fresh appearance（**不走** sepia / aged / desaturated 旧物风）
- **粗黑描边 + 半写实手绘**：THICK BOLD BLACK OUTLINES clearly visible at every silhouette edge + 手绘笔触 + 微立体感 + contact shadow，**不是**纯 3D 渲染 / 不是 Pixar 风 / **不是**细笔淡描
- **质感优先**：纸张纤维、金属反光、织物针脚、皮革磨痕、玻璃透光 —— 体现"被使用过"的细节
- **warm upper-left key light**：主光源来自左上方，物件下方有小柔棕色接触阴影

## 风格模板参考

`<media_skill_root>/references/card_gallery_style_template.png` —— 当前是 3×3 童年信物 grid（玻璃弹珠 / 折纸鹤 / 奖状卷轴 / 布娃娃 / 铁皮青蛙 / 木陀螺 / 贴纸册 / 玩具小汽车 / 彩色粉笔）。
要换标杆 → 在 DesignDeck 资源生成面板，历史批次卡片右上角点「🎯 设为标杆」一键替换。

## 完整 16 主题配方

见 `E:/x3git/x3-project/_assets/xinwu_tujian/all_prompts.md`，已含：
童年 / 友情 / 爱情 / 亲情 / 师恩 / 旅伴 / 战友 / 故乡 / 求学 / 梦想 / 离别 / 重逢 / 信仰 / 邻里 / 传承 / 异乡。
