# L1_game_ux ARCHITECTURE

## 三层架构

```
L1_game_ux (主 skill, 项目无关协议)
    │
    │ 启动时 Preamble 读
    ▼
config/projects.json (项目注册表)
    │
    │ 解析当前 project, 拿到 design_system_path + harness_config
    ▼
<project>/Design System/harness.config.json (项目自描述)
    │
    │ 提供 canvas / tokens / 组件 / regex / 风格关键词 / 加载顺序 / ...
    ▼
质检 agent (l1-game-ux-checker) + 主 Claude 按读到的规则做事
```

**主 skill / 质检 agent**：只持有协议（阶段名、产物契约结构、status 枚举、Completion Status Protocol、AskUserQuestion 5 件套）。
**projects.json**：把项目名映射到 work_root / design_system_dir / harness_config 等路径。`default` 字段定义未指定项目时用哪个。
**harness.config.json**：每个项目自带一份，描述该项目所有可契约化字段（颜色 token 列表 / 字号梯级 / 必含组件 / 资源 regex / 媒体生成关键词 / reject_list / easing 白名单 / 按钮状态契约 / icon 调色板 / html 加载顺序 / ...）。

## state.json schema 设计取舍

- **顶层 `project` 字段**绑定固定项目。即便用户中途"切到 X3"，新功能在新 state.json，老功能不会被错误地按 X3 规则质检。
- **每阶段独立 status**：todo / in_progress / blocked / done / done_with_concerns。Block 失败 ≠ done；warn 失败 = done_with_concerns。
- **`auto_checks` 由主 Claude 写**：质检 agent 物理无 Edit，只能 stdout 输出 JSON 报告，主 Claude 解析后写回 state.json。这是 ETHOS 原则 2 的工程实现。
- **`approved_version` 阶段 3 闸口**：未设置 → 阶段 4 准入失败。这是 harness 的唯一"用户拍板"硬闸口，其他都自动化。
- **`blockers` 数组用于断点续接**：阶段中途停 → 写 blockers → 重启时 Preamble 朗读。

## 质检 agent 沙箱隔离机制

| 切割维度 | 做法 |
|---|---|
| **工具权限** | frontmatter `tools: Read, Grep, Glob, Bash`（Bash 仅 Test-Path / 文件大小读取）。无 Edit / Write |
| **上下文** | 主 Claude 调用时只传 `PHASE=<N\|icon> FEATURE_DIR=<absolute path>`，无对话历史 |
| **结果写入** | agent stdout 输出 fenced JSON + `CHECK_DONE phase=N passed=K/N` 单行。主 Claude 解析后写 state.json |
| **规则源头** | agent 自己读 state.json → project → projects.json → harness.config.json，**不**从主 Claude 接收任何规则参数 |
| **作弊防护** | 即便主 Claude 把伪造的 state.json 传给 agent，agent 跑出来的也是基于该 state.json 的客观结果。主 Claude 想"作弊"必须伪造产物本身——而产物本身就是用户要看的东西 |

## 多项目扩展（X3 上线步骤）

1. 准备 `E:\AIProgram\A-X3Gxd\X3 Design System\` 目录（X3 自己的设计系统资产 + SKILL.md）
2. 新建 `X3 Design System\harness.config.json`，填入 X3 的 canvas / 颜色 / 字号 / 组件 / 风格关键词 / 加载顺序 等
3. 修改 `L1_game_ux/config/projects.json`：把 X3 项的 `design_system_dir` / `harness_config` 等路径从占位改成实际
4. 启动新会话：`项目=X3 做一个 xxx 功能`
5. 主 skill **一行不改**，质检 agent **一行不改**

## 自检：跑一遍

任何修改主 skill / 质检 agent 后，跑：
- `grep -E '(X2|X3|1080|1920|#[0-9A-Fa-f]{6}|OPlusSans|Fredoka|--x2-|SceneBackdrop)' SKILL.md` 应当 0 命中（"附录：实例参考"段除外）
- `grep -E '(X2|--x2-|OPlusSans)' .claude/agents/l1-game-ux-checker.md` 应当 0 命中

## 不借鉴的 gstack 范式

- SKILL.md.tmpl 生成器（过度工程，小 harness 不需要）
- Contributor Mode（无外部贡献者）
- Boil the Lake 哲学表（保持简短）
- Repo Ownership Mode（不是 npm 包）
- Eureka jsonl（暂不需要）
- 自动更新检查 / bun 工具链（无 build pipeline）

## 借鉴的 gstack 范式

- Preamble 启动块（每次进 skill 必跑健康检查）
- Completion Status Protocol（DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT）
- AskUserQuestion 5 件套（Re-ground / Simplify / Recommend + Completeness X/10 / Options / 一次一个决定）
- Telemetry jsonl（不阻塞，后台落盘）
- 文档分层（SKILL.md / ARCHITECTURE.md / ETHOS.md）
- Plan Status Footer（state.json `phases.<N>.review_summary`）
