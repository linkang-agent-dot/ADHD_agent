# 动态行军表情（dynamic_march_emoji）完整流程

## 何时匹配

用户说：动态行军表情、逐帧图、sprite sheet、4x4、九宫格表情、16 宫格表情、逐帧行军表情 等。

## 输出模式

### A. 严格网格逐帧图

用于：用户明确要求 `4x4 / 16宫格 / 九宫格 / 逐帧 / sprite sheet`。

- 构图统一使用：**half-body close-up in every frame**
- 必须保持：**same character**, **same crop ratio**, **same scale**, **same camera angle**
- 必须强调：**ONE SINGLE sprite sheet**, **STRICT 4x4 grid**, **exactly 16 equal cells**, **left-to-right, top-to-bottom**
- **16 格每格固定为 `256×256`**
- **必须是透明底**
- **最终交付尺寸固定为 `1024×1024`**
- **首尾帧必须可循环衔接**

## 流程

1. **索要人物参考图**：必须先拿到人物参考图；未提供则先要图
2. **确认规格**：
   - 动态行军表情统一输出严格 `4×4`
   - 16 格**每格固定 `256×256`**
   - 即使用户提到 `3x3`，也要按当前规范改为 `4×4` 执行
   - 动作编排必须保证最后一帧能自然回接第一帧
3. **模型**：未指定则先询问；如果用户已指定，直接使用
4. **先出首帧预览**：
   - 如果用户提供的是**立绘/全身像/非表情包画风**参考图，不要直接出动态表
   - 必须先按 `march_emoji` 流程生成一张**行军表情首帧预览图**
   - 首帧职责是：把原始立绘转换成表情包画风，并确认脸型、五官、半身裁切、表情强度
   - 首帧给用户确认通过后，才能开始做动态逐帧表
   - 如果用户已经给了通过确认的静态行军表情首帧，后续动态表必须以这张首帧为**绝对锚点**，不要重新发散风格或重新理解半身比例
5. **构造 prompt**：必须使用下面“逐帧表 prompt 规则”
6. **调用 API**：`generate_image`，人物图用 `--file reference_images=<路径>`
7. **检查版式**：
   - 若生成结果不是严格 `4×4`
   - 或者出现 `5上4下`、错位、角色大小不一致、某些格为空
   - 则必须使用 `scripts/rearrange_sprite_sheet.py` 后处理重排
8. **检查规格**：
   - 背景必须为透明底，不能交付白底
   - 最终输出必须缩放或重排到 `1024×1024`
9. **检查一致性**：
   - 16 张图中的人物必须在各自 `256×256` 格子内居中，不能有明显左右或上下漂移
   - 人物顶部到格子上边缘的距离必须基本一致，不能有的贴边、有的下沉
   - 16 张图的露出范围必须稳定，统一为半身像；默认应看到**头、颈、肩、胸口到上腰**，不能退化成胸像，也不能裁断头顶或下巴
   - 人物在每格中的主体占比必须接近游戏内现有表情包参考，不要缩得太小；经验目标可按**主体可见包围框约占单格宽度 0.88-0.94、高度 0.84-0.90** 自检
   - 若原始生成稿的半身构图已经正确，只是存在棋盘伪透明底、格线残影或脏边，优先使用 `scripts/fix_dynamic_march_sheet.py --preserve-layout` 做**保留原构图的清底**
   - 只有当原始生成稿本身出现露出范围漂移、人物忽大忽小、胸像/半身不一致时，才使用 `scripts/fix_dynamic_march_sheet.py` 做统一半身窗口校正，再复检
10. **保存到下载目录**

## 逐帧表 prompt 规则

逐帧表 prompt 中必须出现以下约束，缺一不可：

- `ONE SINGLE sprite sheet`
- `STRICT 4x4 grid`
- `exactly 16 equal cells`
- `each cell is exactly 256x256`
- `left-to-right and top-to-bottom`
- `half-body close-up in every frame`
- `same character design`
- `consistent crop ratio`
- `consistent scale`
- `consistent camera angle`
- `centered in each cell`
- `full head, neck, shoulders, chest, and upper waist visible in every frame`
- `subject size similar to in-game march emoji sample, not too small inside each 256x256 cell`
- `clear spacing between cells`
- `no staggered layout`
- `not separate images`
- `transparent background`
- `no checkerboard background`
- `no panel borders`
- `no divider lines`
- `no horizontal or vertical separator strokes`
- `1024x1024 canvas`
- `loopable sequence`
- `frame 16 transitions seamlessly back to frame 1`

## 推荐动作组织

### 4x4 循环动作

固定使用 16 帧，并按循环动画组织：

1. 待机起始
2. 轻微预备
3. 抬手开始
4. 抬手继续
5. 手势接近成型
6. 比心成型
7. 心形出现
8. 心形增强
9. 表情强化
10. 保持动作
11. 轻微回收
12. 回收到过渡姿态
13. 接近初始姿态
14. 循环过渡
15. 回到起始前一瞬
16. 与第 1 帧自然衔接

## 可选交付：透明底循环 GIF（2026-07-08 新增·柴犬案实证）

用户要「GIF 动图」时，逐帧表出好后**多交付一个 GIF**，用固化脚本：

```bash
py scripts/sheet_to_gif.py --src <sheet.png> --out <out.gif>   # 默认 4x4、110ms/帧、alpha阈值128
```

- GIF 只有 1-bit 透明：alpha 二值化后毛边会硬化，属正常；要细腻半透明边缘改交付 WebP/APNG。
- 关键参数：`disposal=2`（防上一帧拖影）、`loop=0`（无限循环）、每帧 100-120ms 手感适中。
- sheet 和 gif **都写进 saved_to**，用户既能用动图也能自己挑单帧。
- 真实宠物/真人照片来源的动态表：先按 type-march-emoji.md 的「图转表情 likeness-first」出静态锚点帧并让用户确认，再以它为绝对锚点出 sheet。

## 后处理脚本

当模型输出构图不守规矩时，不要反复赌模型；直接重排：

- 脚本：`scripts/rearrange_sprite_sheet.py`
- 半身一致性校正：`scripts/fix_dynamic_march_sheet.py`
- 如果原稿构图正确但只是底不干净：优先 `scripts/fix_dynamic_march_sheet.py --preserve-layout`
- 典型用法：

```bash
py scripts/rearrange_sprite_sheet.py --src input.png --out output.png --src-cols 5 --src-rows 2 --dst-cols 4 --dst-rows 4
py scripts/fix_dynamic_march_sheet.py --src input.png --out output.png --crop-width-ratio 0.64 --crop-height-ratio 0.84 --top-lock
py scripts/fix_dynamic_march_sheet.py --src input.png --out output.png --preserve-layout
```

脚本内置了：

- `5x2 -> 4x4` 的默认补帧/停顿帧

## 关键规则

- `reference_images` 参数名必须是 `reference_images`，不是 `image_paths`
- 必须用 `--file reference_images=<路径>` 传人物参考图
- 动态行军表情**统一交付透明底**
- 动态行军表情**统一交付 `1024×1024`**
- 动态行军表情**16 格每格固定 `256×256`**
- 动态行军表情**统一使用半身像，不要生成全身**
- 动态行军表情**人物占比必须接近游戏内样例，不能缩成小人贴在格子中央**
- 动态行军表情**统一只生成 `4×4`，不要再出 `3×3`**
- 动态行军表情**首尾帧必须形成循环，最后一帧要能回接第一帧**
- 用户提供立绘时，**必须先出行军表情首帧图给用户确认，确认后再开始动态**
- 用户若已提供通过确认的静态首帧，**必须把它当成动态表的绝对人物锚点**
- 动态表中，**人物居中与顶部边距必须自检，不通过就继续修正**
- 动态表中，**若出现棋盘伪透明底、格线、横线残影，优先整表去底或 preserve-layout 清理，不要先把正确半身又裁坏**
- 逐帧表场景下，**排版正确性优先于一次生成**；版式不对就重排，不要让用户自己裁
