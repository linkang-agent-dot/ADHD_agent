---
name: reference-x3-media-skill-location
description: x3-media 活 skill 位置 + 版本控制现状（活目录无 git，但 ClaudeWeeklyBackup 每周一自动镜像进 ADHD_agent 仓快照）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3f4fffaf-4635-47a9-8c65-604b98a228ff
---

# x3-media skill 位置与版本控制现状

**活的 skill（实际生效、要改就改这里）**：`C:\Users\linkang\.claude\skills\x3-media\`
- 结构：`SKILL.md`（Type Router 表 = 注册 type 的地方）+ `references/type-*.md`（每个 type 一份工作流）+ `scripts/` + `config.json`（grfal_cookie）。
- 加 type 的范式 = 写 `references/type-<key>.md` + 在 SKILL.md「Type Router」表加一行 + 在 description 触发词补词（可选放复用脚本到 scripts/）。

**版本控制现状（2026-07-13 更新）**：
- 活目录本身不在任何 git 仓（home 目录 `.git` 已删，见 [[reference-disk-migration-20260713]]）。
- 但 git 里有**自动周镜像**：计划任务 **ClaudeWeeklyBackup**（每周一 12:00，`C:\ADHD_agent\scripts\weekly_global_backup.ps1`）把整个 `.claude`（memory/agents/hooks/settings.json/skills 文本类文件≤512KB）robocopy /MIR 到 `C:\ADHD_agent\_global_backup\claude-snapshot\`，当晚 18:00 PushADHD commit+push。2026-07-13 核实快照与活 skill 一致（早前"停在 2026-06-03 需手动同步"的说法已过时）。

**How to apply（改完 skill 收尾）**：改 `.claude\skills\` 下任何 skill 后，活目录是唯一真身；周一自动镜像会兜底，但**周一 12:00 之后的改动要等下周一才进快照**——重大改动当周想保命，可手动跑一次 `weekly_global_backup.ps1` 再 push ADHD_agent 仓。

**已固化的相关改动**：2026-06-25 给 x3-media 加了 `ui_reskin` type（改造现有界面出效果图：真组件拼装→AI reskin 五步法+横竖转换variant），见 `references/type-ui-reskin.md` + 脚本 `scripts/gen_ui_reskin_template.py`。
**项目仓内也有一份方法快照（给 x3-project 同事）**：`C:\x3-project\docs\UI_Reskin_Workflow\`（五步法01+实操附录02+Morphix prompt库03+方法论源04；commit `2213babbad0 X3NEW- docs: add UI reskin workflow`）。**已 push 到 `origin/dev_festival`，但只在该节日 feature 分支，未合入主线 `dev`**（2026-06-25 核实：`git branch -r --contains 2213babbad0` 只返回 origin/dev_festival）。要进 dev 需走 dev_festival 的 MR 合并。2026-07-11 补核：本地 `circus-homeland-port` 分支上该目录可见（实存 4 个文件，无 README/scripts）；⚠️ x3-project 仓内 `.claude\skills\x3-media\references\` 副本**没有** `type-ui-reskin.md`（旧版本），查 ui_reskin 一律以活 skill `C:\Users\linkang\.claude\skills\x3-media\references\type-ui-reskin.md` 为准。出图方法论本体见 [[reference_morphix_reskin_prompts]] 及 `KB\方法论\X3_AI出图工作流…`。教学包自包含范式见 [[feedback_teaching_pack_self_contained]]。
