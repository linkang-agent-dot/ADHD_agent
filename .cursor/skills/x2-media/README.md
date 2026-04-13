# x2-media

X2 项目统一媒体生成 Skill — 所有图片、视频、3D 及媒体处理请求的唯一入口。

## 适用场景

- 生成游戏美术资源：技能图标、集卡册卡片、行军表情、成就徽章、英雄立绘、场景背景
- 游戏视频制作与 Unity 集成（含 C# 播放代码自动生成）
- 通用媒体处理：抠图、超分、换背景、扩图、3D 生成、虚拟试穿、LoRA 训练

## 安装步骤

1. 确保本目录存在于 `.cursor/skills/` 下
2. 安装依赖：`pip install Pillow playwright && playwright install chromium`
3. 确认 `grfal-api` skill 目录存在（主后端）
4. 首次触发 skill 时，Agent 自动引导配置 `config.json` 和 GRFal Cookie

## 核心能力

| 类型 | 说明 |
|------|------|
| 技能图标 (skill_icon) | 圆形 256×256 技能图标，含后处理贴边 |
| 集卡册 (card_gallery) | 图鉴/集卡册卡片，640×900 |
| 行军表情 (march_emoji) | 动态行军表情包，256×256 |
| 成就徽章 (achievement_badge) | 成就图标，1 中央 + 5 底板，128×128 |
| 游戏视频 (game_video) | 文生视频 + 处理 + Unity 保存 + C# 代码 |
| 通用 (general) | 文生图/图生图/抠图/超分/换背景/扩图/3D/LoRA 等 17+ 工具 |

## 目录结构

```
x2-media/
├── SKILL.md              # AI 指令（Agent 读取）
├── README.md             # 人类文档（Skill Hub 展示）
├── config.example.json   # 配置模板
├── .gitignore
├── references/           # 按需加载的详细文档
│   ├── api-calling.md        # API 调用规范（GRFal + art-skills）
│   ├── available-models.md   # 可用模型列表
│   ├── default-styles.md     # 默认风格 prompt
│   ├── onboarding.md         # 首次使用引导
│   ├── memory-protocol.md    # 跨会话记忆协议
│   ├── type-skill-icon.md    # 技能图标流程
│   ├── type-card-gallery.md  # 集卡册流程
│   ├── type-march-emoji.md   # 行军表情流程
│   ├── type-achievement-badge.md  # 成就徽章流程
│   ├── type-game-video.md    # 游戏视频流程
│   ├── video-code-patterns.md    # C# 代码模板
│   └── video-naming.md       # 视频命名规范
├── scripts/              # 可执行脚本
│   ├── get_grfal_cookie.py       # Cookie 自动获取
│   ├── skill_icon_postprocess.py # 技能图标后处理
│   └── skill_icon_reference/     # 技能图标参考图
└── templates/            # Unity 代码模板
    └── BubbleVideoPlayer.cs.template
```

## 后端架构

- **主后端**: GRFal（内网 AI 生图/视频服务），通过 `call_grfal.py` 调用
- **Fallback**: art-skills（备用 AI 美术系统），GRFal 失败时自动切换

## 相关技能

- `grfal-api` — GRFal 脚本库（主后端依赖）
- `art-skills` — AI 美术系统（fallback 后端）
- `agent-memory` — 跨会话记忆 MCP（可选）
