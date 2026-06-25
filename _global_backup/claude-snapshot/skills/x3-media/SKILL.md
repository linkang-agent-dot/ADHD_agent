---
name: x3-media
description: |
  X3 项目统一媒体生成入口 — 所有图片、视频、3D 及媒体处理请求的唯一 skill。
  GRFal 为主后端，art-skills 为自动 fallback，双后端互备。
  覆盖 14 种专属类型（技能图标、集卡册卡片、行军表情、成就徽章、游戏视频、改造界面出效果图、UI素材提取、活动图标、白图图标、资源图标、道具图标、小图标、英雄碎片图标、通用生图/修图/生视频）
  及 17+ 种工具能力（抠图、超分、换背景、扩图、3D、虚拟试穿、LoRA 等）。
  确保在用户提到任何视觉资产生成或媒体处理需求时使用此技能，
  即使用户没有明确说"生图"——如描述角色外观、要求做素材、讨论 UI 切图风格、
  或提到 grfal/art-skills 等关键词时，都应主动触发。
  触发词(中): 生图、画图、做图、文生图、图生图、立绘、场景、道具、技能图标、
  集卡、行军表情、成就徽章、做视频、制作游戏视频、视频集成、视频代码、
  抠图、超分、换背景、扩图、放大图片、去背景、修图、P图、AI画画、
  3D、虚拟试穿、CardGallary、SBS导出、行军表情包、
  切图、拆UI、拆图素、提取UI素材、UI元素提取、UI拆解、活动图标、活动ICON、
  改造界面、改界面出效果图、界面加档位、界面加页签、界面加格子、UI换皮、reskin界面、真组件拼装、AI reskin、横竖转换、竞品界面改我方风格、出整张界面效果图、
  特效贴图、粒子贴图、特效Alpha贴图、白模贴图、剪影贴图、Unity特效图、Obj贴图。
  触发词(en): generate image, generate video, skill icon, card gallery,
  march emoji, achievement badge, game video, remove background,
  upscale, grfal, art-skills, media processing, LoRA,
  UI extract, extract UI elements, UI teardown, activity icon,
  UI reskin, redesign existing UI, restyle screen, assemble-then-reskin,
  white icon, resource icon, item icon, small icon, hero fragment.
---

# x3-media：X3 统一媒体生成

所有图片、视频、3D 及媒体处理请求的**唯一入口**。

## 依赖 Skill（引用，不复制）

- **grfal-api** — 提供 `call_grfal.py` 脚本（主后端）
- **art-skills** — 提供 `generate_2d.py` / `generate_video.py` / `generate_3d.py`（fallback 后端）

## 目录约定

- `references/` — 按需加载的详细文档（类型流程、API 规范、模型列表等）
- `scripts/` — 可执行脚本（Cookie 获取、图标后处理等）
- `templates/` — 输出用代码模板（如 `BubbleVideoPlayer.cs.template`），不加载到上下文
- `rules/` — **Cursor 项目规则模板**（`.mdc`），见下「分享给同事」
- `state/tasks/` — 异步任务状态文件（每个 task_id 一个 JSON，见「执行模式」）

---

## 执行模式：异步子 agent（强制）

**所有**媒体生成任务一律派发到 `media-worker` 通用子 agent **后台异步**执行（x2-media / x3-media / 未来其他媒体 skill 共用同一个 worker，通过 SKILL_ROOT 参数指明上下文）。
主 agent **不得**直接调用 `call_grfal.py` / `generate_2d.py` / `generate_video.py` / `generate_3d.py` 或任何后端脚本——这些只能在 worker 内部跑。

> 设计动机：长任务（视频 8-15 分钟、gpt 图生图 20 分钟）会阻塞主对话，用户无法在同一会话推进其他需求；同时长 API 输出会污染主上下文。改为派后台 worker 后，主 agent 立即回到对话，用户可继续提需求；worker 完成后通过 task-notification 触达，主 agent 1-2 句播报结果。

### 派发流程

1. 主 agent 完成意图澄清：type、模型、参考图、输出目录、其他参数
2. 主 agent 为**每个原子任务**生成 `task_id`：`yyyyMMdd-HHmmss-<4 字符随机十六进制>`
3. 主 agent 写入 `state/tasks/<task_id>.json`（`status=pending`，schema 见 [references/dispatch-protocol.md](references/dispatch-protocol.md)）
4. 主 agent 调用 Agent 工具：
   - `subagent_type: "media-worker"`
   - `run_in_background: true` ← **必须**
   - `model: "sonnet"` ← **强烈建议显式指定**（2026-06-13 实证：不指定则 worker 继承主 agent 的 session model，若当前是 fable 等子 agent 不可用的模型，**整批 worker 全挂在"model may not exist"**，已提交的生成任务白费。media-worker 是工具型 agent，sonnet 足够且快又省）
   - `prompt`: 两行 —
     ```
     TASK_ID=<task_id>
     SKILL_ROOT=C:\Users\caoxinying\.claude\skills\x3-media
     ```
     （SKILL_ROOT 让通用 worker 知道去 x3-media skill 的 state/tasks/ 读 task）
   - `description: "x3-media <type> <task_id>"`
5. 主 agent 立即在对话里告知用户：「已派发 N 个任务（task_id 列表），完成后通知。继续提需求？」
6. 用户继续提需求时，重复步骤 1-5；多个任务并发执行互不阻塞

### 派发粒度（关键）

**一次原子 GRFal 调用 = 1 个独立 worker**：

| 用户请求 | 派发数量 |
|---|---|
| "给铁匠画 1 个火焰锤击的技能图标" | 1 个 worker |
| "给铁匠画 3 个技能图标" | **3 个** worker（并发） |
| "做 1 个战斗演示视频 + 1 个活动图标" | 2 个 worker（并发） |
| "拆解这张 UI（individual 模式）" | 1 个 worker（一次 GRFal 调用产多元素，含全部后处理） |

> 不要在 1 个 worker 内循环跑多张——失去隔离粒度，单张失败拖累全批，进度不可见。

### 进度查询

用户问"现在有几个任务在跑？" / "活跃任务" / "list tasks"：

1. `glob state/tasks/*.json`
2. 过滤 `status in (pending, running)`
3. 按 `started_at` 排序后输出表格：

```
进行中 2 个：
| task_id              | type        | 描述              | 状态     | 已耗时   |
|----------------------|-------------|-------------------|----------|----------|
| 20260509-143022-a7f3 | skill_icon  | 铁匠/火焰锤击     | running  | 2分15秒  |
| 20260509-143108-b1c2 | game_video  | 战斗演示          | running  | 8分02秒  |
```

### 完成通知处理

worker 完成 → task-notification 触达主 agent → 主 agent：

1. 读 `state/tasks/<task_id>.json`
2. 按 `status` 1-2 句播报：
   - `success`：`✅ 任务 <id> 完成（<type>）。已保存：<saved_to[0]>`（多文件列前 3 个）
   - `failed`：`❌ 任务 <id> 失败（<error.step>）：<error.message>。重试 / 改参数 / 跳过？`
   - `needs_auth`：⚠️**先别让用户刷 Cookie**（2026-06-13 实证：GRFal 已迁 token 认证 device flow，refresh token 在 `~/.config/grfal-api`；部分 worker 仍按旧 GRFAL_COOKIE env 误判 needs_auth——同批其他 worker success 即为铁证）。主 agent 先跑 `python <grfal-api skill>/scripts/call_grfal.py --list-tools` 验真：**通 = 认证活着 → 直接按 resume 协议重派同 task_id**；真不通才走 `call_grfal.py --auth-bootstrap` / device flow（get_grfal_cookie.py 的 Cookie 法已过时）。
3. 完成的 task json 保留 7 天供回查
4. **不要**重新读 SKILL.md 或 type-*.md 来"二次校验"——worker 已写好结果

### 重派（resume）

用户刷新 Cookie 后说"Cookie 已刷新，重派 a7f3"：

1. 主 agent 读 `state/tasks/a7f3.json`，确认 `status == needs_auth`
2. 主 agent 改写：`status="pending"`、清空 `started_at` / `finished_at` / `error`、`retry_count=0`、`created_by="resume"`
3. 主 agent 用**同一个 task_id** 派新 worker：`Agent(subagent_type="media-worker", run_in_background=True, prompt="TASK_ID=a7f3\nSKILL_ROOT=C:\\Users\\caoxinying\\.claude\\skills\\x3-media")`

> 不要新生成 task_id——保持原任务 + 重派的连续性，便于历史追溯。

---

## 分享给同事：启用 Cursor Rule（推荐）

**Skill 不会自动注册为 Rule。** 每个要用 x3-media 的**业务项目仓库**需装一次项目级规则（安装到该仓库的 `.cursor/rules/`，非 skill 仓库本身）。

### 方式 A：安装脚本（推荐，初始配置）

在**目标项目根目录**（Unity 工程根，由用户指定）下执行：

```bash
python "<x3-media_skill绝对路径>/scripts/install_cursor_rule.py" --project .
```

或显式指定路径：

```bash
python "<x3-media_skill绝对路径>/scripts/install_cursor_rule.py" --project "<unity_project_root>"
```

- 会创建 `.cursor/rules/`（若不存在）并写入 `x3-media.mdc`；重复执行会**覆盖**同名文件。
- 预览：`--dry-run`

**首次配置时**：Agent 应在用户确认「要绑定的项目根」后，**直接代为执行**上述命令（把 `<x3-media_skill绝对路径>` 换成本机 x3-media 目录），无需让用户手抄 `.mdc`。

### 方式 B：手动复制

将 `rules/x3-media.mdc` 复制到目标项目的 **`.cursor/rules/x3-media.mdc`**。

### 生效说明

- 重启对话或重新打开项目后，Cursor 按 `description` 匹配规则（`alwaysApply: false`）；若希望**每条对话都带**，把 `x3-media.mdc`  frontmatter 里 `alwaysApply` 改为 `true`。
- `call_grfal.py` **统一走项目 vendored 副本**：相对项目 skill 根目录的 `vendor/grfal-api/scripts/call_grfal.py`。⚠️ 不要用 grfal-api 全局副本——协议可能超前升级（如切成 Bearer Token）与项目 Cookie 认证不兼容，会返回 `Not Found`。项目 skill 根由用户环境决定（Cursor 下通常是 `~/.cursor/skills/<project>/`），Agent 按以下优先级查找：① 当前工作区向上查找 `<project>/vendor/grfal-api/scripts/call_grfal.py` ② `<USERPROFILE>/.cursor/skills/<project>/vendor/...` 最终用 `which python` 等效方式定位。
- Monorepo 可将 `.cursor/rules/` 提交进 Git，全员拉代码即生效。

> **说明**：本脚本只支持**项目级** `.cursor/rules/`。Cursor「用户级」规则目录因版本而异，需同事自行在设置里添加时，仍可用方式 B 复制同一份 `.mdc`。

---

## Type Router — 根据用户意图分类后按需读取

| 用户意图 | 类型 key | 读取文件 | 说明 |
|---------|---------|---------|------|
| 技能图标 | skill_icon | `references/type-skill-icon.md` | 需图2 + 技能表查询 + 后处理贴边 |
| 集卡册/图鉴 | card_gallery | `references/type-card-gallery.md` | 确认人物 + 模型 + 640×900 |
| 行军表情 | march_emoji | `references/type-march-emoji.md` | 需人物参考图 + 贴纸式表情包 + 透明底 `256×256` |
| 动态行军表情 | dynamic_march_emoji | `references/type-dynamic-march-emoji.md` | 需人物参考图 + 先首帧确认 + 4×4 半身循环逐帧（每格 `256×256`）+ 透明底 `1024×1024` |
| 成就徽章 | achievement_badge | `references/type-achievement-badge.md` | 1中央+5底板 + 128×128 |
| 游戏视频制作 | game_video | `references/type-game-video.md` | 视频生成+处理+Unity保存+C#代码 |
| 改造现有界面出效果图 | ui_reskin | `references/type-ui-reskin.md` | 真组件拼装→AI reskin 五步法（prefab反查sprite→拼装图#1→图#2真实界面→reskin→拆槽）；含竞品横竖转换 variant。**出整张改造后界面效果图**（区别于 ui_extract 的拆元素） |
| UI素材提取 | ui_extract | `references/type-ui-extract.md` | 从参考图提取UI元素，去文字，按类型分档 resize + pngquant 量化（成品对齐项目标准 1-80KB） |
| 精细拆图（毛发/光晕/无白边） | ui_extract_fine | `references/type-ui-extract-fine.md` | gpt-image-1 双背景差分法（白底+黑底各画一次 → transparify_dual_bg.py 反推 alpha），适合角色 / 特效 / 半透明边缘 |
| 活动图标 | activity_icon | `references/type-activity-icon.md` | 活动入口/奖励图标，透明底 256×256，需节日参考元素 |
| 特效贴图 | effect_texture | `references/type-effect-texture.md` | Unity 粒子/特效用剪影贴图，RGB 全白 + Alpha 蒙版，2^N 正方形（128/256/512） |
| 按钮 | button | `references/type-button.md` | 游戏 UI 按钮（多色/多状态/多形状），透明底 PNG，9-patch 兼容 |
| UI 框 / 背景 | uiframe | `references/type-uiframe.md` | 头像框 / 弹窗背景 / 标题装饰条 / 列表项背景，9-patch 兼容 |
| 通用生图/生视频/修图 | general | 直接按下方通用工作流 | 查 `references/default-styles.md` |

**匹配方式**：模糊 / 语义匹配。用户说法与类型含义相近即匹配，不要求完全一致。

**未明确类型时**：如果用户只说「我要生图」「帮我做个图」等泛化请求，Agent 应弹出欢迎引导卡片（见「配置完成 → 欢迎引导卡片」）让用户选择，而非直接假设 general 类型。

### ★透明化硬规则（生成类透明资产，默认走双底差分）
下列类型产物**必须透明底**，生图后**默认用 `scripts/transparify_asset.py`（双底差分一条龙：生白底→生黑底→反推 alpha）**出透明 PNG，**禁止**用 `generate transparent` 参数 / `remove_background`（会白边、穿洞、吃毛发）：
- **行军表情** march_emoji / dynamic_march_emoji
- **各种 ICON**：skill_icon / activity_icon / 资源图标 / 道具图标 / 小图标 / 英雄碎片图标
- **道具相关 DK 资产**（投放进客户端的道具/图标类）

用法（全自动）：`python scripts/transparify_asset.py --prompt "<元素描述，不带背景词>" --out x.png [--trim] [--resize 256]`
已有白/黑两图时：`--white W.png --black B.png --out x.png`
> 双底差分硬要求：两次生图除背景外 prompt 一字不差 + 强调 keep pixel-aligned；漂移就重跑。
> **例外**（不走双底差分）：`effect_texture` 走自己的 Alpha 蒙版后处理；`ui_extract*` 是从现成图拆元素、不是生成；`card_gallery` 带框非透明。

**读取顺序**（渐进式披露）：
1. 本文件（始终加载）→ Router 表 + 通用规则 + Gotchas
2. 匹配到的 `references/type-xxx.md`（按需加载，仅 1 个）
3. `references/api-calling.md`（调用 API 时按需加载）

---

## 通用工作流（适用于所有类型）

### Prompt 转换

- 中文 → 英文，补全构图 / 光线 / 氛围细节，不改变用户本意
- 不是逐句翻译，而是理解后写出具象、可出图的英文提示词

### X3 角色参考图（自动查找并注入）

当用户描述中涉及 X3 游戏角色，**必须自动执行以下流程，无需用户提醒**：

1. **查找参考图索引**：读取本 skill 的 `references/character-visuals/_index.md`，按角色名（中文或英文）匹配对应条目，获取图片文件名和 AI Prompt 关键词。
   - 索引路径（skill 内相对）：`references/character-visuals/_index.md`
   - 图片目录（skill 内相对）：`references/character-visuals/`

2. **注入参考图**：将找到的角色图片以 base64 编码后放入 API 调用的 `reference_images` 参数，告知模型以这些图片的角色外观为准。

3. **注入角色描述**：将 `_index.md` 中该角色的 AI Prompt 关键词段落完整拼入 prompt，作为角色外观的精确描述锚定。

4. **风格默认对齐参考图**：若用户**未额外指定画风**，则在 prompt 开头加入：`same art style as the reference images: 2D illustration, cartoon semi-painted rendering, light steampunk fantasy, vibrant colors, clean outlines, colorful game character design`，确保风格与官方立绘一致。用户明确指定其他风格时，跳过此条。

> **示例**：用户说「画角色 A 和角色 B」→ 自动读取对应角色立绘 PNG，base64 编码后作为 `reference_images`，同时把两个角色的 prompt 关键词拼入 prompt。

### 模型选择

- 已指定 → 直接用，不再询问
- 未指定 → **必须先问**（列表见 `references/available-models.md`）
- 若 `config.json` 中 `preferred_image_model` 非空，可跳过询问直接使用偏好模型

### 超时设置

- 调用 `gpt` 模型（图生图耗时较长、易超时）时，`--timeout` 取 `config.json` 的 `gpt_timeout` 字段（目前配置为 `1200` 秒，20 分钟；若字段缺失，回退到 600s）
- 其他图像模型保持默认 180s；视频 600s；LoRA 1200s

### 默认风格

- 查 `references/default-styles.md`，有则自动使用（用户明确拒绝除外）
- prompt = default_prompt **全文原样** + 英文逗号 + 用户描述（英文）
- 改写 default_prompt 会导致风格偏移，因此务必逐字复制，不要缩写或重写

### 多张图并行

- **N 张图 = N 个独立 task_id = N 个并发 background worker**
- 主 agent 顺次写 N 个 pending task json，再连发 N 次 `Agent(run_in_background=true)` 即可；之后立刻回到对话告诉用户"已派发 N 个"
- ❌ 不要在 1 个 worker 内 `Start-Job` 循环跑多张：失去隔离粒度，单张失败拖累全批，进度不可见
- ❌ 不要额外封装批量脚本：派发协议已经处理批量并发

### 任务派发（取代主 agent 直调 API）

主 agent 收集到全部参数后，**不要直接调用 `call_grfal.py` 或任何后端脚本**：

1. 按「执行模式」流程派发 `media-worker`
2. worker 内部按 `references/type-<type>.md` 完整工作流执行（含后端选择、fallback、下载、后处理、history 写入）
3. 详细 API 规范见 `references/api-calling.md`（worker 加载，主 agent 不需要）

### 下载与保存（worker 职责）

worker 在执行 type 工作流时必须遵守（主 agent 在 task json 的 `params.output_dir` 里指定目录，下面是 worker 的执行规范）：

- 默认保存到「下载」目录（Windows: `$env:USERPROFILE\Downloads`）
- **必须**在调用 `call_grfal.py` 时加 `--download-dir <task.params.output_dir>`，由脚本在返回成功后立即用同一 Cookie 下载结果 URL（勿只把 trycloudflare/内网 URL 写进 task json）
- 按类型命名（各 type reference 中有具体规则；`call_grfal` 按 URL 路径命名，可在下载后按需重命名）
- 每次生成成功后追加一行到 `state/history.jsonl`（时间、类型、模型、结果路径、后端、task_id）
- 把完整本地路径写入 `task.result.saved_to`，主 agent 在通知里播报

---

## 工具能力

17+ 种工具覆盖生图、生视频、修图、3D、LoRA 等。运行 `call_grfal.py --list-tools` 查看完整列表和参数。
常用超时参考：生图 180s | 生视频/视频处理 600s | LoRA 1200s | 其余 60-300s。

---

## 认证与 Cookie

GRFal 所有 API 调用均需认证（Tap4Fun 统一账号 OAuth，通过钉钉登录）。

### 认证优先级

`call_grfal.py` 按以下顺序查找 Cookie：
1. `--cookie` 命令行参数（最高优先级）
2. `GRFAL_COOKIE` 环境变量 ← **推荐方式**
3. 无 Cookie → API 返回 `未认证` 错误

### 获取 Cookie

运行 `scripts/get_grfal_cookie.py`，自动打开 Chrome → 钉扫码登录 → CDP 提取 Cookie → 存入 `config.json`。

### 设置环境变量（持久化）

```powershell
# 从 config.json 读取并写入 Windows 用户级环境变量（重启终端后仍生效）
$cookie = (py -c "import json; print(json.load(open('config.json'))['grfal_cookie'])")
[System.Environment]::SetEnvironmentVariable('GRFAL_COOKIE', $cookie, 'User')
$env:GRFAL_COOKIE = $cookie
```

设置后所有终端自动可用，无需每次传 `--cookie`。

### Cookie 过期

Cookie 通常在服务端会话超时后失效。症状：API 返回 `未认证，请提供有效的 Bearer token 或登录 session`。
处理：重新运行 `get_grfal_cookie.py` 获取新 Cookie，再更新环境变量。

---

## 首次使用与配置

首次触发时，Agent 按顺序处理：

1. **Cursor Rule（项目级）**  
   - 若当前工作区根下**尚未存在** `.cursor/rules/x3-media.mdc`，询问用户是否将 x3-media 规则装到**本工作区**（或用户指定的游戏项目根）。  
   - 用户同意则执行：  
     `python "<x3-media>/scripts/install_cursor_rule.py" --project "<工作区或项目根>"`  
   - 已存在则跳过，避免重复打扰。

2. **`GRFAL_COOKIE`**  
   - **已设置** → 跳过认证说明，进入欢迎引导  
   - **未设置** → 引导运行 `scripts/get_grfal_cookie.py` 并配置环境变量

配置完成后（或用户意图不明确时），弹出 AskQuestion 欢迎卡片让用户选择能力类型或新增类型。

---

## State（跨会话持久化）

`state/` 目录存储运行时数据：
- `history.jsonl` — 每次生成的记录（时间、类型、prompt、模型、结果路径、后端、task_id）
- `session_prefs.json` — 本次会话临时偏好（如「本轮对话都用 gemini」）
- `tasks/<task_id>.json` — **异步任务状态文件**（每个派发的任务一份，schema 见 [references/dispatch-protocol.md](references/dispatch-protocol.md)）；活跃任务（pending/running）由主 agent glob 查询，完成后保留 7 天供回查

用途：同角色色调统一、重复请求检测（5 分钟内相同 prompt 不重复生成）、Fallback 成功率统计、异步任务状态追踪。

---

## Memory Protocol（跨会话记忆）

**依赖同事自行配置** 带 `memory_search` / `memory_write` 的 MCP（如团队自建的 agent-memory）后才会出现对应工具；**非 Cursor 默认行为**，与 `rules/x3-media.mdc` 一并说明即可。

- **任务开始**（有 MCP 时）：`memory_search` → 应用历史经验；可创建 `state/.media_session.json` 标记
- **任务结束**（有 MCP 时）：`memory_write` → 删除标记文件

简要字段约定见 `references/memory-protocol.md`（与 Rule 第 5 条一致）。

---

## Gotchas — 常见踩坑与原因

1. **九宫格问题** — 多数模型在不明确约束时会输出多图拼接。prompt 中加 "ONE SINGLE icon, do NOT generate multiple icons or a grid" 可有效避免。

2. **串行 vs 并行** — N 张图用 `Start-Job` 并行发起，串行等待时间是 N 倍。也不要额外封装批量脚本，直接多次调用 `call_grfal.py` 更简单可靠。

3. **模型选择** — 不同模型风格差异很大，未指定时先问用户（除非 config 中有 `preferred_image_model`），避免用户不满意后重新生成浪费时间。

4. **默认风格完整性** — default_prompt 是经过调优的完整提示词，任何缩写或改写都会导致风格偏移。逐字从 `default-styles.md` 复制，再拼接用户描述。

5. **技能描述 ≠ prompt** — 技能表中的文字描述是功能说明，不是视觉描述。需要理解语义后提炼出具象的视觉元素，用审美化的英文重新组织。

6. **视频传 URL 不传文件** — 视频体积大，用 `--file` 上传会超时。改用 `video_path=URL` 传参，只在最终保存到 Unity 目录时才下载到本地。

7. **Cookie 过期** — API 调用或下载失败且返回 `未认证` 时，第一步检查 `GRFAL_COOKIE` 是否过期。引导用户重新运行 `scripts/get_grfal_cookie.py` 并更新环境变量，不要重复重试同一个失败请求。

8. **技能图标后处理** — 模型输出通常是 1024×1024，游戏需要 256×256 并贴边。跳过 `skill_icon_postprocess.py` 会导致图标在游戏中显示异常。

9. **双后端 fallback** — GRFal 返回 `success:false` 或超时时，按 `references/api-calling.md` 切换到 art-skills，不要让用户空手而归。

10. **视频工作流前置配置** — 游戏视频需要 `project_path` 指向 Unity 项目，没有这个路径无法保存到正确位置，因此需在开始前确认配置。

11. **角色参考图缺失** — 用户描述涉及 X3 角色但未主动提供参考图时，**不要直接生图**，必须先从本 skill 的 `references/character-visuals/` 目录查找对应图片并注入 `reference_images`。若 `_index.md` 中无对应角色，提示用户先到该目录贴立绘并登记到索引，不可跳过。跳过此步骤会导致角色形象严重偏差（种族、服饰、配色全错）。

12. **UI 拆图未做后处理 = 资源超大** — AI 生图默认 1024×1024，trim bbox 后 PNG-32 直存往往 100KB-600KB；项目标准是 1-80KB（按元素类型分档）。`type-ui-extract.md` 的 Step 8（resize+pngquant 量化）必跑，封装在 `scripts/ui_extract_postprocess.py`，individual 模式调用时由 Agent 自动调用。

13. **绝不在主 agent 直调 call_grfal** — 所有任务必须派 `media-worker` 后台执行（见「执行模式」）。直调会阻塞对话且污染主上下文；用户连续提多个生成需求时无法并发。task_id 是单一事实来源，主 agent 只读 `state/tasks/<id>.json` 不接受子 agent 长文本输出。

14. **worker prompt 只传 task_id** — 调用 Agent 工具派 worker 时，prompt **只**包含 `TASK_ID=<id>` 一行，所有参数在 task json 里。塞参数副本进 prompt 会造成两份数据不一致，且浪费 token。
