---
name: x2-art-requirement
description: Use when user needs to generate art requirement documents for X2 game features, including city special effects, march effects, UI elements, or visual assets. Triggers include: 美需、美术需求、出美需、主城特效、行军特效、特效需求、art requirement, city effect, march effect, visual asset spec, 节日包装, 出新方向.
---

# X2 美术需求生成

## 概述

为 X2 游戏功能生成「创意方向 + 参考图 + 美需文档 + 落表」的完整闭环。

| Step | 内容 | 说明 |
|------|------|------|
| 0 | 自主学习 | 查案例库 / P2 参考 |
| 1 | 理解用户输入 | 3种形态分类处理 |
| 2 | 创意发散 | 方向放空时给3-5候选 |
| 3 | 按类型产出美需 | 结构分类 + 范式填写 |
| 4 | 命名产出 | 字数格式硬约束 |
| 5 | 参考链接搜集 | Google 图片搜索链接 |
| 6 | 参考图生成 | x2-media / GRFal |
| 7 | 落 Google Sheet | 调脚本建 tab |
| 8 | 双产物输出 | Sheet 链接 + MD 速览 |

---

## Step 0 自主学习（必做，不跳过）

**两步都要做，顺序执行：**

**① 查 X2 案例库**（本 skill 底部）
- 找同类型已完成案例，确认 X2 已用方向
- X2 案例是重复判定的唯一依据

**② 读 P2 知识库**（无论 X2 案例多少，都要读）
- 路径：`C:\Users\linkang\.claude\skills\p2-festival-art-brief\knowledge\`
- 按节日读对应 MD，重点看：已用特效方向、视觉调性、命名样本
- **P2 仅供方向参考，不参与 X2 重复判定**：P2 做过极光、X2 也可以做极光，不算重复
- X2 没有机甲/手札，特效结构也与 P2 略有差异，创意借鉴即可

**③ 向用户汇报**（1-2 段）：X2 现有案例现状 + 从 P2 借鉴到的方向灵感，**等确认后再产出**

---

## Step 1 理解用户输入

用户输入分 3 种形态：

**A. 题材指定型**："做一个极光主题的行军特效"
→ 查案例确认无重复 → 直接按题材产出

**B. 方向放空型**："帮我想一个钓鱼节的主城特效新方向"
→ 进入 Step 2 发散 → 给候选 → 用户选定后产出

**C. 补写美需型**："给这个行军特效补完整美需描述"
→ 查已有框架 → 按范式补齐所有必填项

---

## Step 2 创意发散（方向放空型触发）

结合 3 类创意池，给 **3-5 个候选方向**，每个方向附：
- 一句定位：**[主题] [差异化切入点]**
- 与现有案例的差异点
- 3-5 个视觉关键词
- 命名示例 2-3 组

**3 类创意池：**
- **流行文化**：近 1 年热门影视/游戏/综艺题材
- **亚文化美学**：小众但有识别度（液态金属 / 生机符号学 / 大地色系…）
- **地域文化**：敦煌 / 和风 / 北欧 / 南美 / 东南亚…

**等用户选定后**再进入 Step 3。

---

## Step 3 按效果类型产出美需

### 主城特效

**外显位置**：城市岛屿底部地面，平铺于草地之上，城市模型正下方

**视觉结构分类**（先确认类型再填范式）：

| 类型 | 外显特征 | 代表感觉 |
|------|---------|---------|
| **A 圆环基础型** | 主圆环 + 内圈水纹/光效 + 点缀粒子 | 符文阵感、魔法感 |
| **B 圆环+光柱型** | 主圆环 + 向上光柱/光束 | 仪式感强、节日感 |
| **C 散点环绕型** | 无主圆环，散点粒子/图案围绕城市底盘 | 轻盈、自然感 |

**美需范式（必填项）：**
1. **主底面效果**：形状（圆/椭圆/不规则）、大小（相对城市底盘倍数）、纹样描述
2. **次级光效层**：内圈水纹 / 次圆环 / 散射光晕，层数与关系
3. **点缀元素**：粒子/图案类型、分布密度、是否随机
4. **可选：向上延伸**（B 型必填）：光柱数量、高度、粗细、颜色
5. **配色方案**：主色 HEX + 辅色 HEX + 高光描述
6. **≥2 个方向备选**（正文是方向 A，备选 B/C 供美术选）
7. **避坑项**：明确写"不做 XX""避免与 XX 撞型"
8. **动画脚本**（有动画必填，四节结构）：
   - **主题**：整体动画的情绪/故事感，一句话定性
   - **流程**：出现阶段 → 循环阶段的时序描述
   - **重点**：最核心的 2–3 个动画节拍，指导美术重点发力
   - **元素**：每个可动元素"做什么动作"，只写定性描述，不写参数

**风格硬约束：**
- 光效"发光"但不刺眼，整体低调烘托城市
- 特效不遮挡城市模型主体
- 与 X2 卡通蒸汽朋克风格一致
- 圆环/光弧必须是半透明发光线条，不做实体浮雕感

---

### 行军特效

**外显位置**：附着于行军队伍列阵上，跟随队伍在大地图移动

**前端主体分类**（决定整体气质，三选一）：

| 类型 | 外显特征 | 感觉 |
|------|---------|------|
| **A 包裹环型** | 椭圆光圈紧贴包裹整个队列，无具象主体 | 纯特效感、护盾感 |
| **B 装饰主体型** | 队伍前方有标志性物件（乐器/图腾/武器/神兽等） | 具象感强、叙事感 |
| **C 混合型** | 包裹环 + 前端标志性装饰物 | 层次丰富 |

**美需范式（必填项）：**
1. **前端主体**（选 A/B/C 并描述）：
   - A 型：光圈形态、厚度、发光方式
   - B 型：标志物具体描述（材质/大小/动作）
   - C 型：两者各自描述
2. **飘散元素**：粒子/物件种类、密度、运动方向
3. **路径拖尾**：形态（光带/纹样/粒子流）、宽度、渐隐方式
4. **可选：穹幕/向上延伸**：光幕形态、高度、透明度（建议 30-50%）
5. **配色方案**：主色 HEX + 辅色 HEX + 高光描述
6. **≥2 个方向备选**
7. **避坑项**

**风格硬约束：**
- 特效随队伍移动自然流畅，不显"贴图感"
- 不遮挡士兵轮廓和玩家名称文本
- 与 X2 卡通蒸汽朋克风格一致

---

## Step 4 命名产出

| 效果类型 | 格式 | 示例 |
|---------|------|------|
| 主城特效 | 4字主名 + 10-14字描述 | 鱼跃灵阵 · 金鲤绕城游转，带来好运与庇佑 |
| 行军特效 | 4字主名 + 10-14字描述（含动作词） | 极光远征 · 冰蓝光幕随军涌动，踏破极夜 |
| 行军表情 | 2-4字主名 + ≤10字描述 | — |
| 装饰物 | 可共用同名 + 描述增量 | — |

**命名原则：**
- 禁止直接照搬互联网命名，必须本土化 + 四字化
- 主名要有画面感，描述要含动词或动态意象
- 查案例库确认无重名

---

## Step 5 参考链接搜集（每个特效必做）

美术拿到美需后需要"一眼找到方向"，每个特效配搜索链接，美术点击直达 Google 图片挑图。

| 效果类型 | 建议条数 | 关键词策略 |
|---------|---------|-----------|
| 主城特效 | 3 条 | 主意象 + 特效/光效对照 + 配色氛围 |
| 行军特效 | 3 条 | 主意象 + 特效对照 + 配色氛围 |

**写法（落 Sheet 时用）：**
```json
{"label": "主图", "searchQuery": "magic rune circle koi fish glow game effect"}
{"label": "特效对照", "searchQuery": "ground light effect fantasy game art"}
{"label": "配色参考", "searchQuery": "blue teal gold bioluminescent color palette"}
```

**搜图关键词原则：**
- 英文 + 风格词（`concept art` / `game effect` / `artstation`）效果远好于中文
- 每条打标签：主图 / 特效 / 配色 / 避坑对照

---

## Step 6 参考图生成（x2-media / GRFal）

> **前置**：若 `/tmp/agent-skill` 不存在，先克隆：
> ```bash
> git clone --depth=1 https://git.tap4fun.com/skills/x2/agent-skill.git /tmp/agent-skill
> ```

### 通用：压缩参考图（必须 < 200KB）
```python
from PIL import Image
img = Image.open("原始截图.png").resize((600, 900), Image.LANCZOS)
img.save("/tmp/ref_small.jpg", "JPEG", quality=80)
```

### 通用：提交 + 轮询 + 下载
```bash
GRFAL_SCRIPT="/tmp/agent-skill/.cursor/skills/grfal-api/scripts/call_grfal.py"
ACCESS_TOKEN=$(python3 -c "import json; d=json.load(open('$HOME/.config/grfal-api/token_store.json')); print(d['access_token'])")

# 提交（⚠️ /api/mcp/call 已下线，必须用 --submit-only）
TASK=$(py "$GRFAL_SCRIPT" --tool generate_image --params "$PARAMS" \
  --file "reference_images=/tmp/ref_small.jpg" \
  --url "http://172.20.90.45:6018" --public-url none --submit-only 2>&1)
TASK_ID=$(echo "$TASK" | python3 -c "import json,sys; print(json.load(sys.stdin)['task_id'])")

# 轮询（每 15 秒，完成后 delete=true 只能取一次）
curl -s "http://172.20.90.45:6018/api/async/status/$TASK_ID" -H "Authorization: Bearer $ACCESS_TOKEN"
curl -s "http://172.20.90.45:6018/api/async/result/$TASK_ID?delete=true" -H "Authorization: Bearer $ACCESS_TOKEN"

# 下载
curl -s -o "output.png" -H "Authorization: Bearer $ACCESS_TOKEN" \
  "http://172.20.90.45:6018/api/output/image_generation_api/<日期>/<文件名>.png"
```

### 主城特效 Prompt 模板
```
Keep the UI layout exactly identical to the reference image.
Do NOT change any UI panels, buttons, text, icons, or layout structure.
ONLY add/replace the ground effect beneath the city island with:
[特效描述，英文]
flat on the ground beneath the island, subtle, consistent with cartoon game art style.
```

### 行军特效 Prompt 模板
```
Keep the game map layout and troop formation exactly identical to the reference image.
Do NOT change the checkered march path, the troop positions, the UI icons, or any layout structure.
ONLY add/replace the visual march effects around the marching troop column with:
[特效描述，英文]
wrapping around the troop formation as they march, dynamic and mobile feeling,
consistent with cartoon game art style, vibrant but not overwhelming.
```

---

## Step 7 落 Google Sheet

**X2 美需主表**：`1BND6XhvQkO7OPbAZg_yWLBThRwcVUuCExRO1F8lVqaI`

Tab 命名与插入规则同 P2（按年倒序+月正序，紧贴同年上月 tab 之后，禁止追加末尾）。

调脚本（复用 P2 的 `create_art_brief_tab.py`，有问题再调整）：
```bash
# spec JSON 参考 p2-festival-art-brief skill 的格式
python3 "C:/Users/linkang/.claude/skills/p2-festival-art-brief/scripts/create_art_brief_tab.py" \
  /tmp/art_brief_spec.json
```

spec JSON 结构（每行对应一个模块/特效档位）：
```json
{
  "spreadsheetId": "1BND6XhvQkO7OPbAZg_yWLBThRwcVUuCExRO1F8lVqaI",
  "newTabTitle": "2026 6月上线-深海节-主城特效",
  "insertAfterTabTitle": "2026 5月上线-拓荒节",
  "rows": [
    {
      "moduleGroup": "主城特效",
      "moduleName": "鱼跃灵阵",
      "functionDesc": "深海节主城地面特效，金鲤环绕符文圈",
      "copyNeed": "名称&描述",
      "copy": "名称：鱼跃灵阵\n描述：金鲤绕城游转，带来好运与庇佑。",
      "artBrief": "主圆环：金色符文圈+鱼鳞纹\n水纹：蓝绿内圈2-3层\n粒子：金色锦鲤沿圈游动\n避坑：不做龙纹（避春节撞型）",
      "refs": [
        {"label": "主图", "searchQuery": "magic rune circle koi fish glow game effect"},
        {"label": "特效", "searchQuery": "ground circular light effect fantasy game artstation"},
        {"label": "配色", "searchQuery": "blue teal gold bioluminescent palette"}
      ]
    }
  ]
}
```

---

## Step 8 三产物输出

**产物 1：Google Sheet tab 链接**（脚本执行后打印，直接发给美术）

**产物 2：对话 MD 速览**（便于飞书/钉钉转发）
```markdown
# X2 {特效类型} · {主题方向} · {名称}

## 主题定位
- 核心概念：
- 情绪关键词：
- 主色调：
- 与现有案例差异：

## 美需摘要
- 前端主体：{一句话}
- 飘散元素：{一句话}
- 路径拖尾：{一句话}
- 动效节奏：{一句话}

（详细美需 + 参考链接在 Sheet 里）
```

**产物 3：本地存档（必做）**

MD 速览同时写入本地：
```
路径：C:\ADHD_agent\KB\产出-本地化与美术\X2_{年份节日}_{特效类型}_美需.md
命名示例：X2_2026深海节_主城特效_美需.md、X2_2026音乐节_行军特效_美需.md
规则：同名覆盖，不保留草稿版本
```

GRFal 生成的参考图统一存入：
```
C:\ADHD_agent\KB\产出-本地化与美术\ref-images\{节日}\{图片名}.jpg
```

---

## 案例库

### 主城特效

| 名称 | 节日/主题 | 类型 | 参考图 | 日期 |
|------|---------|------|--------|------|
| 鱼跃灵阵 | 深海节 / 钓鱼 | A 圆环基础型 | `Downloads/x2_fish_effect_1.png` | 2026-04-23 |

**鱼跃灵阵 Prompt（可复用）：**
```
glowing circular rune with fish scale koi fish patterns, soft blue and teal water ripple rings
expanding outward, small golden glowing koi fish swimming along the rune circle, gentle bubbles
floating up near the city base, bioluminescent ocean glow in blue-green and gold,
flat on the ground beneath the island, subtle consistent with cartoon game art style
```

---

### 行军特效

| 名称 | 节日/主题 | 前端主体类型 | 参考图 | 日期 |
|------|---------|------------|--------|------|
| 极光远征 | 音乐节 / 北极光 | A 包裹环型 | `Downloads/march_aurora_2.png` | 2026-04-23 |

**极光远征 Prompt（可复用）：**
```
ethereal aurora borealis ribbon trails flowing along the march path in soft teal-green and violet hues,
translucent aurora curtains gently wrapping around the circular troop formation,
tiny ice crystal and snowflake particles drifting around the troops,
the march trail glowing with northern lights gradient colors (electric teal to soft purple),
aurora halos hovering above each soldier silhouette,
consistent with cartoon game art style, magical and premium feel, not too bright or overwhelming
```

---

## Step 9 沉淀回顾（每次必做，不跳过）

每次完成美需生成后，**主动发起沉淀对话**，询问用户以下 3 个问题，根据回答更新本 SKILL.md：

**① 这次新增了什么结构或设计位？**
> 例如：行军特效新发现了"脚底光晕"这个设计位；主城特效确认了"向上光柱"是独立类型
→ 更新 Step 3 的视觉结构分类表和美需范式必填项

**② 沟通过程中改了什么东西？**
> 例如：prompt 改了某个描述让生图更准；某个结构类型描述不清楚被用户纠正
→ 更新对应的 Prompt 模板 / 范式说明 / 类型描述

**③ 流程里有什么需要完善的新内容？**
> 例如：发现 Sheet 落表时有新的 tab 命名规则；发现某个节日有特殊的避坑项
→ 更新对应 Step 或案例库的避坑项

**沉淀操作清单（根据回答执行）：**
- [ ] 把本次案例追加到案例库（名称 / 节日 / 类型 / 参考图路径 / 日期）
- [ ] 把本次可复用 Prompt 存入案例记录
- [ ] 若有新结构 → 更新 Step 3 视觉结构分类
- [ ] 若有流程调整 → 更新对应 Step 描述
- [ ] 若有新踩坑 → 追加到「常见踩坑」表

---

## 常见踩坑（GRFal API）

| 问题 | 原因 | 解决 |
|------|------|------|
| `{"detail":"Not Found"}` | `/api/mcp/call` 已下线 | 改用 `--submit-only` + curl 轮询 |
| 结果取不到 | `delete=true` 只能取一次，被轮询脚本静默消费 | 改用 curl 直接轮询 `/api/async/status` |
| 参考图 → 404 | 原图 15-20MB，base64 超限 | 压缩到 < 200KB 的 JPG |
| UI 结构被改 | prompt 未明确保留 UI | 开头加 "Keep the UI layout exactly identical" |
| 图片下载失败 | 返回 URL 端口 80 不通 | 改用 `6018/api/output/...` + Bearer Token |
