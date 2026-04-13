# GRFal AI 媒体工具（grfal-api）

通过 HTTP API 直接调用 GRFal 服务，生成图片、视频、3D 模型，以及处理媒体文件（超分、抠图、扩图等）。

## 适用场景

- **图片生成**：AI 画图、游戏素材、插画
- **视频生成**：文生视频、图生视频
- **图片处理**：超分辨率、去背景、扩图、调光
- **视频处理**：超分、口型同步、变速、去背景
- **3D 模型**：文本/图片转 3D
- **其他**：虚拟试穿、LoRA 训练、PPT 生成

## 触发关键词

`"画图"` `"生成图片"` `"做视频"` `"抠图"` `"超分"` `"放大图片"` `"去背景"` `"图生视频"` `"grfal"`

## 安装

```bash
git clone git@git.tap4fun.com:x2/agent_skill.git
```

将 `UX/grfal-api/` 复制到 Cursor skills 目录：

```
Windows: C:\Users\{用户名}\.cursor\skills\grfal-api\
Mac:     ~/.cursor/skills/grfal-api/
```

## 特点

- 无需 MCP，直接 HTTP 调用
- 支持多种 AI 模型和处理管线
- 自动处理任务轮询和结果下载

## 目录结构

```
grfal-api/
├── SKILL.md    # Cursor Skill 定义
└── README.md   # 本文件
```
