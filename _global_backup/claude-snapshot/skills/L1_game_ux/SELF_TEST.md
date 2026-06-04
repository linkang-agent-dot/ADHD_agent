# L1_game_ux Harness 自测表

> 实施后自查清单。每条都是 grep / 文件存在性 / JSON 解析 等客观检测，独立 agent 可复跑。

## A. 文件落地 (8 条)

| # | 路径 | 检测 | 结果 |
|---|---|---|---|
| A1 | `C:\Users\caoxinying\.claude\skills\L1_game_ux\SKILL.md` | Test-Path | |
| A2 | `C:\Users\caoxinying\.claude\skills\L1_game_ux\ETHOS.md` | Test-Path | |
| A3 | `C:\Users\caoxinying\.claude\skills\L1_game_ux\ARCHITECTURE.md` | Test-Path | |
| A4 | `C:\Users\caoxinying\.claude\skills\L1_game_ux\config\projects.json` | Test-Path + JSON 合法 | |
| A5 | `E:\AIProgram\A-X2Gxd\X2 Design System\harness.config.json` | Test-Path + JSON 合法 | |
| A6 | `C:\Users\caoxinying\.claude\agents\l1-game-ux-checker.md` | Test-Path + frontmatter 解析 | |
| A7 | `C:\Users\caoxinying\.claude\skills\L1_game_ux\templates\` 下 6 个 template 文件 | Glob count = 6 | |
| A8 | `C:\Users\caoxinying\.claude\projects\C--Users-caoxinying\memory\feedback_project_agnostic_harness.md` + MEMORY.md 索引一行 | Test-Path + grep | |

## B. 项目无关性 (4 条) — ETHOS 原则 3

| # | 检测 | 命中目标 |
|---|---|---|
| B1 | `Grep "(--x2-\|#0D1520\|#F9CB64\|OPlusSans\|Fredoka)" SKILL.md` | = 0 |
| B2 | `Grep "1080\|1920" SKILL.md` 排除注释段 | = 0（除 templates 路径或文档说明） |
| B3 | `Grep "(X2 Design System\|SceneBackdrop\|MainTabs)" l1-game-ux-checker.md` | = 0 |
| B4 | `Grep "(--x2-\|#0D1520\|OPlusSans)" l1-game-ux-checker.md` | = 0 |

## C. 关键协议字段存在 (8 条)

| # | 检测 | 期望 |
|---|---|---|
| C1 | `Grep "## Preamble" SKILL.md` | ≥ 1 |
| C2 | `Grep "Completion Status Protocol" SKILL.md` | ≥ 1 |
| C3 | `Grep "AskUserQuestion" SKILL.md` | ≥ 1 |
| C4 | `Grep "DONE_WITH_CONCERNS\|BLOCKED\|NEEDS_CONTEXT" SKILL.md` | ≥ 3 不同 |
| C5 | `Grep "approved_version" SKILL.md` | ≥ 2 |
| C6 | `Grep "harness.config.json" SKILL.md` | ≥ 8 |
| C7 | `Grep "projects.json" SKILL.md` | ≥ 3 |
| C8 | `Grep "l1-game-ux-checker" SKILL.md` | ≥ 4 |

## D. 质检 agent 沙箱 (3 条) — ETHOS 原则 2

| # | 检测 | 期望 |
|---|---|---|
| D1 | `Grep "^tools:" l1-game-ux-checker.md` | 仅含 Read/Grep/Glob/Bash，**无 Edit/Write** |
| D2 | `Grep "CHECK_DONE" l1-game-ux-checker.md` | ≥ 1（终止协议存在） |
| D3 | `Grep "PHASE=\|FEATURE_DIR=" l1-game-ux-checker.md` | ≥ 1（输入协议存在） |

## E. 五阶段产物契约完整性 (5 条)

| # | 检测 | 期望 |
|---|---|---|
| E1 | SKILL.md 含"阶段 1"~"阶段 5"五段标题 | 5 段都存在 |
| E2 | SKILL.md 含"独立图标入口" | ≥ 1 |
| E3 | l1-game-ux-checker.md 含 5 个阶段质检表 + icon 模式 | 6 表 |
| E4 | templates 含 state/feature_readme/intro_notes/analysis/annotation/asset_reuse_map | 6 文件 |
| E5 | SKILL.md 提到子目录布局（01_intro/02_structure/03_mockups/04_split/05_html/06_videos） | 6 子目录都出现 |

## F. typo / skill 名修复 (2 条)

| # | 检测 | 期望 |
|---|---|---|
| F1 | `Grep "L0_user_research" SKILL.md`（带下划线）| = 0 |
| F2 | `Grep "L0_user-research" SKILL.md`（带连字符） | ≥ 1 |

## G. X2 harness.config.json 实例完整性 (8 条)

| # | 字段 | 检测 |
|---|---|---|
| G1 | `canvas.width / height` | 1080 / 1920 |
| G2 | `color_tokens` 数组长度 | ≥ 30（X2 有 30+ 个 token）|
| G3 | `font_sizes_allowed` 数组长度 | = 7（22/28/32/36/48/64/72）|
| G4 | `available_components` 数组 | 含 SceneBackdrop / Header / MainTabs / PrimaryBtn / QualityItem |
| G5 | `easing_whitelist` 数组长度 | ≥ 19 |
| G6 | `media_keywords.reject_list` | ≥ 5 项，含 "no Pixar style" / "no realistic photography" |
| G7 | `asset_naming_regex` | regex 字符串合法 |
| G8 | `html_load_order` | 含 colors_and_type.css + animations.jsx + Frame.jsx + Buttons.jsx + QualityItem.jsx + app.jsx |

## 自测执行方式

派一个独立 Explore agent 跑这张表，输出每条 PASS/FAIL + 短证据。Explore agent 只读，刚好够用。
