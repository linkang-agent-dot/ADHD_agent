# 首次使用与欢迎引导

## 前置依赖

| 依赖 | 安装方式 | 是否必须 |
|------|---------|---------|
| Python 3 | [python.org](https://python.org) 或 `winget install Python.Python.3` | 必须 |
| Pillow | `pip install Pillow` | 技能图标后处理必须 |
| playwright | `pip install playwright && playwright install chromium` | Cookie 自动获取推荐 |
| grfal-api skill | 确认 `.cursor/skills/grfal-api/` 目录存在 | 必须（主后端） |
| art-skills skill | 确认 art-skills skill 目录存在 | 可选（fallback 后端） |
| agent-memory MCP | Cursor 设置中配置 `user-agent-memory` MCP server | 可选（跨会话记忆） |

## 首次配置（Agent 自动引导）

首次触发本 skill 时，Agent 按以下流程自动引导，用户无需手动编辑文件：

1. **创建 config.json** — 自动从 `config.example.json` 复制
2. **获取 GRFal Cookie** — 运行 `scripts/get_grfal_cookie.py`，自动打开浏览器让用户登录，登录后自动提取 Cookie 写入 config
3. **按需补充** — game_video 类型会要求填写 `project_path`（Unity 项目路径）

```powershell
# Agent 执行的首次引导命令（用户无需手动运行）
python "<skill路径>/scripts/get_grfal_cookie.py" --config "<skill路径>/config.json"
```

## Config 字段说明

配置文件：本 skill 目录下的 `config.json`（首次使用时自动从 `config.example.json` 创建）。

| 字段 | 用途 | 何时需要 |
|------|------|---------|
| `grfal_url` | GRFal 服务地址 | 默认 `http://172.20.90.45:6018`，通常无需修改 |
| `project_path` | Unity 项目路径 | game_video 类型必须 |
| `preferred_image_model` | 偏好生图模型 | 可选，设置后生图不再每次询问 |
| `preferred_video_model` | 偏好视频模型（默认 vidu） | 可选 |
| `grfal_cookie` | GRFal Cookie 缓存 | 内网下载时需要（自动获取） |
| `art_token` | AI 美术系统 Token | fallback 时需要 |

按需最小配置（不需要一次性填完）：
- 生图请求 → Agent 自动运行 Cookie 获取脚本
- 视频工作流 → Agent 会要求配置 `project_path` + Cookie
- Cookie 过期 → Agent 自动检测并重新引导获取

## 欢迎引导卡片

首次配置完成后（或用户意图不明确时），Agent 使用 `AskQuestion` 工具展示可用能力，让用户点选：

```
AskQuestion 参数：
  title: "x2-media 媒体工作台"
  questions:
    - id: "media_type"
      prompt: "选择你要使用的能力（或添加新类型）："
      options:
        - id: "skill_icon"    label: "技能图标 — 圆形游戏技能图标，256×256，需英雄形象图"
        - id: "card_gallery"  label: "集卡册卡片 — 图鉴/集卡册卡片，640×900"
        - id: "march_emoji"   label: "行军表情 — 动态行军表情包，256×256"
        - id: "achievement"   label: "成就徽章 — 成就图标，1中央+5底板，128×128"
        - id: "game_video"    label: "游戏视频 — 视频生成+处理+Unity集成+C#代码"
        - id: "general"       label: "通用生图/生视频/修图 — 文生图、图生图、抠图、超分、换背景等"
        - id: "add_new"       label: "新增类型 — 添加一种新的媒体生成类型"
      allow_multiple: false
```

### 用户选择后的处理

| 用户选择 | Agent 行为 |
|---------|-----------|
| 已有类型（skill_icon / card_gallery / ...） | 读取对应 `references/type-xxx.md`，按该类型流程执行 |
| `general` | 直接按通用工作流执行，询问用户具体需求 |
| `add_new` | 进入下方「新增类型引导」流程 |

## 新增类型引导（用户选择 add_new 时）

**Step 1 — 收集信息**（用 AskQuestion 或对话）：

```
AskQuestion 参数：
  title: "新增媒体类型"
  questions:
    - id: "type_name"
      prompt: "新类型的名称（英文 key，如 hero_portrait）："
      options:
        - id: "hero_portrait"    label: "hero_portrait — 英雄立绘/半身像"
        - id: "scene_bg"         label: "scene_bg — 场景背景图"
        - id: "item_icon"        label: "item_icon — 道具/物品图标"
        - id: "loading_screen"   label: "loading_screen — 加载图/闪屏"
        - id: "custom"           label: "自定义 — 我来输入类型名称"
```

**Step 2 — 对话补充细节**：
- 输出尺寸是多少？（如 512×512、1024×1024、自定义）
- 是否需要参考图（reference_images）？
- 是否有特定的默认风格 prompt？
- 是否需要后处理（缩放、贴边、去背景等）？
- 命名规则是什么？（如 `hero_xxx_portrait.png`）

**Step 3 — 自动创建文件**：
1. 在 `references/` 下创建 `type-<type_name>.md`，内容参照已有 type reference 的结构
2. 在 `references/default-styles.md` 中追加该类型的 default_prompt 行（如有）
3. 创建完后提示用户：「新类型已创建，建议将以下行添加到 SKILL.md 的 Type Router 表中：」并给出表格行

**Step 4 — 确认并试用**：
- 告知用户新类型文件路径
- 询问是否立即用这个新类型生成一张测试图
