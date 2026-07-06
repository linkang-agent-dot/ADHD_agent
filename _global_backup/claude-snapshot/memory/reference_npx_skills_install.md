---
name: npx-skills-install
description: 用 npx skills add 从 git 仓库装/更新 skill 的固定姿势与落盘位置
metadata: 
  node_type: memory
  type: reference
  originSessionId: d45c1806-9e97-4044-acda-edd10fa9f03e
---

装/更新 skill：`npx skills add <git地址> --skill '<名字>'`（如 `git@git.tap4fun.com:skills/dingtalk-workspace.git --skill 'dws'`）。

- 实体落在 `~\.agents\skills\<名字>`，通过 **Junction** 链到 `~\.claude\skills\<名字>`（Claude Code）及 Cursor / Gemini CLI 等其他 agent 目录，一次安装多端生效。
- 重复执行 = 覆盖更新到仓库最新版，可放心重跑。
- 公司内部 skill 仓库前缀：`git@git.tap4fun.com:skills/`。已装：`dws`（钉钉全产品能力，2026-07-03）。
