---
name: reference-x3-media-skill-location
description: x3-media 活 skill 位置 + 它不在 git 仓（只有 ADHD_agent 旧快照），改 skill 后要手动同步备份否则会丢
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3f4fffaf-4635-47a9-8c65-604b98a228ff
---

# x3-media skill 位置与版本控制现状

**活的 skill（实际生效、要改就改这里）**：`C:\Users\linkang\.claude\skills\x3-media\`
- 结构：`SKILL.md`（Type Router 表 = 注册 type 的地方）+ `references/type-*.md`（每个 type 一份工作流）+ `scripts/` + `config.json`（grfal_cookie）。
- 加 type 的范式 = 写 `references/type-<key>.md` + 在 SKILL.md「Type Router」表加一行 + 在 description 触发词补词（可选放复用脚本到 scripts/）。

**⚠️ 它不在任何 git 仓**：
- 所在 home 目录 `C:\Users\linkang` 虽是 git 仓（remote `github.com/linkang-agent-dot/ADHD_agent.git`），但 `.claude/skills/` 下文件**完全未跟踪**（`git ls-files .claude/skills/` 为空），也没 ignore = 纯未版本控制。
- git 里唯一有 x3-media 的是**旧快照**：`C:\ADHD_agent\_global_backup\claude-snapshot\skills\x3-media\` + `_global_backup\2026-06-03\x3-media-scripts\`，被 ADHD_agent 仓（`git@github.com:linkang-agent-dot/ADHD_agent.git`）跟踪，但停在 2026-06-03，**不是活 skill**。

**How to apply（改完 skill 收尾）**：改 `.claude\skills\` 下任何 skill 后，活目录是唯一真身、无版本控制——要保命就**手动同步进 `_global_backup\claude-snapshot\skills\` 再 commit push ADHD_agent 仓**，否则清 .claude / 换机会丢。

**已固化的相关改动**：2026-06-25 给 x3-media 加了 `ui_reskin` type（改造现有界面出效果图：真组件拼装→AI reskin 五步法+横竖转换variant），见 `references/type-ui-reskin.md` + 脚本 `scripts/gen_ui_reskin_template.py`。
**项目仓内也有一份方法快照（给 x3-project 同事）**：`C:\x3-project\docs\UI_Reskin_Workflow\`（README+五步法+实操附录+Morphix prompt库+两份方法论源+scripts；commit `2213babbad0 X3NEW- docs: add UI reskin workflow`）。**已 push 到 `origin/dev_festival`，但只在该节日 feature 分支，未合入主线 `dev`**（2026-06-25 核实：`git branch -r --contains 2213babbad0` 只返回 origin/dev_festival）。要进 dev 需走 dev_festival 的 MR 合并。出图方法论本体见 [[reference_morphix_reskin_prompts]] 及 `KB\方法论\X3_AI出图工作流…`。教学包自包含范式见 [[feedback_teaching_pack_self_contained]]。
