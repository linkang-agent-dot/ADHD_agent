# UX Assistant · X3 游戏交互设计助手

X3 游戏专属 UX 设计小助手，具备完整的 4 阶段设计工作流、玩家画像数据库和交互自查标准。

## 适用场景

- 功能交互流程设计（新系统 / 优化迭代）
- 生成功能交互流程分析报告
- 生成可运行交互原型（含 X3 视觉规范）
- 设计自测：WCAG 2.2 + 启发式评估 + 多玩家视角反馈

## 核心能力

| 能力 | 说明 |
|------|------|
| 引导式需求挖掘 | 苏格拉底式提问，逐步厘清状态机和边界情况 |
| 功能设计分析报告 | Markdown Canvas，结构清晰可预览 |
| 交互原型生成 | 可运行 HTML，符合 X3 UIKit 规范（1080×1920 竖屏）|
| 交互自测报告 | 按优先级分类问题 + 多层级玩家犀利意见 |
| 玩家画像库 | 15 个真实玩家画像（大R/中R/小R/零氪）|

## 触发方式

说以下任意关键词即可激活：

> 设计交互 · 做原型 · UI 设计 · 交互需求 · 做个界面 · 交互流程 · UX 助手 · 自测 · 启发式评估 · ux assistant

或在对话中直接输入阶段关键词：**设计** / **构建** / **自测**

## 安装

```bash
git clone git@git.tap4fun.com:skills/x3/agent_skill.git
```

仓库内本 skill 路径：`UX/L1_game_ux/`。落地位置：

```
Windows: C:\Users\{用户名}\.claude\skills\X3\UX\L1_game_ux\
Mac:     ~/.claude/skills/X3/UX/L1_game_ux/
```

## 目录结构

```
L1_game_ux/
├── SKILL.md                    # AI 指令（核心）
├── README.md                   # 本文件
└── references/
    ├── ui-kit.md               # 视觉规范
    ├── users-map.md            # 15个玩家画像
    └── check-self.md           # 交互自查验收标准
```

> ⚠️ references/ 下 8 个 md（design-docs/users-map/unity-mapping/ui-layouts/ui-kit/module-patterns/design-spec/ux-spec）目前仍含较多 X2 历史内容，X3 适配待补。

## 相关技能

- `L1_figma_screen` — X3 沿用 X2 组件库的 Figma 界面生成
- `L1_flow_doc` — 从截图生成交互文档网页
- `L0_user-research` — 体验诊断（四维鸿沟）
- `L0_simulator` — 玩家视角反馈模拟
