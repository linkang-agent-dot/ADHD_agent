# L1_game_ux ETHOS

本 harness 的三条根原则。设计上有冲突时优先以这里为准。

## 1. 减少人工判断（客观才设 block）

只有 grep / 文件存在性 / JSON 解析 / 尺寸读取 等**机器可判定**的项目才能进 block 级规则。
主观判断（"美感是否合格" / "情感节奏是否合适" / "玩家是否能理解"）**永远不进 block**，最多进 warn 或留给用户决定。

**Why**：harness 的价值在于把可程序化的检查自动化，把人的注意力留给真正需要判断的事。一旦 block 含主观项，质检 agent 就会卡死，用户被迫绕过它，harness 就垮了。

**How to apply**：写规则时问自己——"如果两个不同的 Claude 实例独立跑这条规则，会不会给出完全一致的结果"。不能 → 降级 warn 或删掉。

## 2. 执行 / 质检物理切割（不作弊）

质检 agent (`l1-game-ux-checker`) 物理上只有只读工具（Read / Grep / Glob / Bash 仅 Test-Path 与文件大小读取），**没有 Edit / Write 权限**。state.json `auto_checks` 字段由**主 Claude 写**，agent 只能把 JSON 报告输出到 stdout。

**Why**：让同一个 agent 既改产物又给自己打分 = 作弊的最大可能。物理切割能在工具层面把这条路堵死。参考 `x2-media-worker.md` 的沙箱模式。

**How to apply**：质检 agent 的 frontmatter 必须只声明只读 tools。若将来质检规则需要"修复建议"，由质检 agent 输出**文字建议**到 JSON，主 Claude 决定是否采纳并修改，**不允许**质检 agent 自己改。

## 3. 项目无关（多项目可移植）

主 SKILL.md 和质检 agent 文件中**不得**出现项目特定字面量：
- 项目名（X2 / X3 / ...）
- 资源路径（E:\AIProgram\A-X2Gxd / 任何具体盘符目录）
- 颜色 hex（#0D1520 / #F9CB64 / ...）
- canvas 尺寸（1080 / 1920 / ...）
- 字号特定值（22 / 28 / ... 数字）
- 字体名（OPlusSans / Fredoka / ...）
- 组件名（SceneBackdrop / Header / ...）
- 风格关键词（"medieval-fantasy" / "navy backdrop" / ...）

例外：**唯一**允许出现的位置是 SKILL.md 的"附录：实例参考"段（如有），并明确标注"此处为示例，实际值从 harness.config.json 读"。

**Why**：用户已经声明 X2 之后立刻做 X3，再后面可能还会有更多。每次新项目都改主 skill 不可持续。

**How to apply**：任何项目特定值必须放到 `<Project> Design System/harness.config.json`。主 skill 启动时按 `projects.json` 解析当前项目并加载该配置。新增项目 = 新建 harness.config.json + projects.json 加一项，主 skill 一行不改。
