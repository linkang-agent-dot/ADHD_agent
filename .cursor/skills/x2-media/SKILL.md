---
name: x2-media
description: |
  X2 项目统一媒体生成入口 — 所有图片、视频、3D 及媒体处理请求的唯一 skill。
  GRFal 为主后端，art-skills 为自动 fallback，双后端互备。
  覆盖 8 种专属类型（技能图标、集卡册卡片、行军表情、成就徽章、游戏视频、UI素材提取、活动图标、通用生图/修图/生视频）
  及 17+ 种工具能力（抠图、超分、换背景、扩图、3D、虚拟试穿、LoRA 等）。
  确保在用户提到任何视觉资产生成或媒体处理需求时使用此技能，
  即使用户没有明确说"生图"——如描述角色外观、要求做素材、讨论 UI 切图风格、
  或提到 grfal/art-skills 等关键词时，都应主动触发。
  触发词(中): 生图、画图、做图、文生图、图生图、立绘、场景、道具、技能图标、
  集卡、行军表情、成就徽章、做视频、制作游戏视频、视频集成、视频代码、
  抠图、超分、换背景、扩图、放大图片、去背景、修图、P图、AI画画、
  3D、虚拟试穿、CardGallary、SBS导出、行军表情包、
  切图、拆UI、拆图素、提取UI素材、UI元素提取、UI拆解、
  活动图标、活动ICON、活动小图标、节日图标。
  触发词(en): generate image, generate video, skill icon, card gallery,
  march emoji, achievement badge, game video, remove background,
  upscale, grfal, art-skills, media processing, LoRA,
  UI extract, extract UI elements, UI teardown.
alwaysApply: false
---

# x2-media：X2 统一媒体生成

所有图片、视频、3D 及媒体处理请求的**唯一入口**。

## 依赖 Skill（引用，不复制）

- **grfal-api** — 提供 `call_grfal.py` 脚本（主后端）
- **art-skills** — 提供 `generate_2d.py` / `generate_video.py` / `generate_3d.py`（fallback 后端）

## 目录约定

- `references/` — 按需加载的详细文档（类型流程、API 规范、模型列表等）
- `scripts/` — 可执行脚本（Cookie 获取、图标后处理等）
- `templates/` — 输出用代码模板（如 `BubbleVideoPlayer.cs.template`），不加载到上下文
- `rules/` — **Cursor 项目规则模板**（`.mdc`），见下「分享给同事」

---

## 分享给同事：启用 Cursor Rule（推荐）

**Skill 不会自动注册为 Rule。** 每个要用 x2-media 的**业务项目仓库**需装一次项目级规则（安装到该仓库的 `.cursor/rules/`，非 skill 仓库本身）。

### 方式 A：安装脚本（推荐，初始配置）

在**目标项目根目录**（如 Unity 工程 `E:\X2`）下执行：

```bash
python "<x2-media_skill绝对路径>/scripts/install_cursor_rule.py" --project .
```

或显式指定路径：

```bash
python "<x2-media_skill绝对路径>/scripts/install_cursor_rule.py" --project "E:/X2"
```

- 会创建 `.cursor/rules/`（若不存在）并写入 `x2-media.mdc`；重复执行会**覆盖**同名文件。
- 预览：`--dry-run`

**首次配置时**：Agent 应在用户确认「要绑定的项目根」后，**直接代为执行**上述命令（把 `<x2-media_skill绝对路径>` 换成本机 x2-media 目录），无需让用户手抄 `.mdc`。

### 方式 B：手动复制

将 `rules/x2-media.mdc` 复制到目标项目的 **`.cursor/rules/x2-media.mdc`**。

### 生效说明

- 重启对话或重新打开项目后，Cursor 按 `description` 匹配规则（`alwaysApply: false`）；若希望**每条对话都带**，把 `x2-media.mdc`  frontmatter 里 `alwaysApply` 改为 `true`。
- `call_grfal.py` 路径以本机 **grfal-api** skill 为准（见 grfal-api 的 SKILL.md）。
- Monorepo 可将 `.cursor/rules/` 提交进 Git，全员拉代码即生效。

> **说明**：本脚本只支持**项目级** `.cursor/rules/`。Cursor「用户级」规则目录因版本而异，需同事自行在设置里添加时，仍可用方式 B 复制同一份 `.mdc`。

---

## Type Router — 根据用户意图分类后按需读取

| 用户意图 | 类型 key | 读取文件 | 说明 |
|---------|---------|---------|------|
| 技能图标 | skill_icon | `references/type-skill-icon.md` | 需图2 + 技能表查询 + 后处理贴边 |
| 集卡册/图鉴 | card_gallery | `references/type-card-gallery.md` | 确认人物 + 模型 + 640×900 |
| 行军表情 | march_emoji | `references/type-march-emoji.md` | 需人物参考图 + 256×256 |
| 成就徽章 | achievement_badge | `references/type-achievement-badge.md` | 1中央+5底板 + 128×128 |
| 游戏视频制作 | game_video | `references/type-game-video.md` | 视频生成+处理+Unity保存+C#代码 |
| UI素材提取 | ui_extract | `references/type-ui-extract.md` | 从参考图提取UI元素，去文字，白底平铺/九宫格 |
| 活动图标 | activity_icon | `references/type-activity-icon.md` | 256×256 透明底 3D 物件，需节日参考元素 |
| 通用生图/生视频/修图 | general | 直接按下方通用工作流 | 查 `references/default-styles.md` |

**匹配方式**：模糊 / 语义匹配。用户说法与类型含义相近即匹配，不要求完全一致。

**未明确类型时**：如果用户只说「我要生图」「帮我做个图」等泛化请求，Agent 应弹出欢迎引导卡片（见「配置完成 → 欢迎引导卡片」）让用户选择，而非直接假设 general 类型。

**读取顺序**（渐进式披露）：
1. 本文件（始终加载）→ Router 表 + 通用规则 + Gotchas
2. 匹配到的 `references/type-xxx.md`（按需加载，仅 1 个）
3. `references/api-calling.md`（调用 API 时按需加载）

---

## 通用工作流（适用于所有类型）

### Prompt 转换

- 中文 → 英文，补全构图 / 光线 / 氛围细节，不改变用户本意
- 不是逐句翻译，而是理解后写出具象、可出图的英文提示词

### X2 角色参考图（自动查找并注入）

当用户描述中涉及 X2 游戏角色（主角、铁匠、机械师、特蕾莎、镇长等任何角色），**必须自动执行以下流程，无需用户提醒**：

1. **查找参考图索引**：读取 `x2-narrative-design` skill 的 `references/character-visuals/_index.md`，按角色名（中文或英文）匹配对应条目，获取图片文件名和 AI Prompt 关键词。
   - 索引路径（仓库相对）：`gd/x2-narrative-design/references/character-visuals/_index.md`
   - 图片目录（仓库相对）：`gd/x2-narrative-design/references/character-visuals/`

2. **注入参考图**：将找到的角色图片以 base64 编码后放入 API 调用的 `reference_images` 参数，告知模型以这些图片的角色外观为准。

3. **注入角色描述**：将 `_index.md` 中该角色的 AI Prompt 关键词段落完整拼入 prompt，作为角色外观的精确描述锚定。

4. **风格默认对齐参考图**：若用户**未额外指定画风**，则在 prompt 开头加入：`same art style as the reference images: cartoon steampunk fantasy style, vibrant colors, clean outlines, cel-shaded, colorful game character design`，确保风格与官方立绘一致。用户明确指定其他风格时，跳过此条。

> **示例**：用户说「画主角和铁匠」→ 自动读取 `protagonist-full.png` + `bob-full.png`，base64 编码后作为 `reference_images`，同时把两个角色的 prompt 关键词拼入 prompt。

### 模型选择

- 已指定 → 直接用，不再询问
- 未指定 → **必须先问**（列表见 `references/available-models.md`）
- 若 `config.json` 中 `preferred_image_model` 非空，可跳过询问直接使用偏好模型

### 默认风格

- 查 `references/default-styles.md`，有则自动使用（用户明确拒绝除外）
- prompt = default_prompt **全文原样** + 英文逗号 + 用户描述（英文）
- 改写 default_prompt 会导致风格偏移，因此务必逐字复制，不要缩写或重写

### 多张图并行

- N 张图 = N 个 `Start-Job` 并行执行，避免串行（串行等待时间是 N 倍）
- 直接调用 `call_grfal.py` 即可，不要额外封装批量脚本（增加维护负担且容易引入 bug）

### API 调用

- 见 `references/api-calling.md`（含 GRFal 主后端 + art-skills fallback）

### 下载与保存

- 默认保存到「下载」目录（Windows: `$env:USERPROFILE\Downloads`）
- **必须**在调用 `call_grfal.py` 时加 `--download-dir <目录>`，由脚本在返回成功后立即用同一 Cookie 下载结果 URL（勿只把 trycloudflare/内网 URL 丢给用户）
- 按类型命名（各 type reference 中有具体规则；`call_grfal` 按 URL 路径命名，可在下载后按需重命名）
- 每次生成成功后追加一行到 `state/history.jsonl`（时间、类型、模型、结果路径、后端）
- 下载完成后告知用户「已保存到：<完整路径>」

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
   - 若当前工作区根下**尚未存在** `.cursor/rules/x2-media.mdc`，询问用户是否将 x2-media 规则装到**本工作区**（或用户指定的游戏项目根）。  
   - 用户同意则执行：  
     `python "<x2-media>/scripts/install_cursor_rule.py" --project "<工作区或项目根>"`  
   - 已存在则跳过，避免重复打扰。

2. **`GRFAL_COOKIE`**  
   - **已设置** → 跳过认证说明，进入欢迎引导  
   - **未设置** → 引导运行 `scripts/get_grfal_cookie.py` 并配置环境变量

配置完成后（或用户意图不明确时），弹出 AskQuestion 欢迎卡片让用户选择能力类型或新增类型。

---

## State（跨会话持久化）

`state/` 目录存储运行时数据：
- `history.jsonl` — 每次生成的记录（时间、类型、prompt、模型、结果URL、后端）
- `session_prefs.json` — 本次会话临时偏好（如「本轮对话都用 gemini」）

用途：同角色色调统一、重复请求检测（5 分钟内相同 prompt 不重复生成）、Fallback 成功率统计。

---

## Memory Protocol（跨会话记忆）

**依赖同事自行配置** 带 `memory_search` / `memory_write` 的 MCP（如团队自建的 agent-memory）后才会出现对应工具；**非 Cursor 默认行为**，与 `rules/x2-media.mdc` 一并说明即可。

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

11. **角色参考图缺失** — 用户描述涉及 X2 角色但未主动提供参考图时，**不要直接生图**，必须先从 `x2-narrative-design` skill 的 `character-visuals/` 目录查找对应图片并注入 `reference_images`。跳过此步骤会导致角色形象严重偏差（种族、服饰、配色全错）。
