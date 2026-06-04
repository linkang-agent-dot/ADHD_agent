---
name: X2导表工作流
description: X2 配置表从 Google Sheets 下载到 x2gdconf 仓库的完整流程，含路由规则和 download skill 路径
type: reference
originSessionId: c62f4c2c-8b51-486f-b004-0ce34c2efe37
---
# X2 导表工作流

## 触发词
X2导表、X2下载表、X2刷表、X2拉取配置

## 执行协议
每次收到"X2导表"类请求，按以下顺序加载：
1. **读路由规则**：`C:\ADHD_agent\.cursor\rules\x2-gsheet.mdc`
2. **读 download skill**：`C:\ADHD_agent\.cursor\skills\x2-config-download\SKILL.md`
3. 按 skill 规则执行具体下载流程

## 关键路径
- 仓库：`D:\UGit\x2gdconf`
- 工具：`D:\UGit\x2gdconf\tools\fwcli.exe`
- GSheet ID：`1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc`
- 主 Skill（仓库内）：`D:\UGit\x2gdconf\.cursor\skills\gsheet_sync\SKILL.md`
- Download Skill（ADHD维护）：`C:\ADHD_agent\.cursor\skills\x2-config-download\SKILL.md`
- 合并 Skill：`D:\UGit\x2gdconf\scripts\gsheet_skill_merge.md`
- 冲突 Skill：`D:\UGit\x2gdconf\scripts\gsheet_skill_conflict.md`

## 与 P2 导表的区别
| | P2 | X2 |
|---|---|---|
| 仓库 | `C:\gdconfig` | `D:\UGit\x2gdconf` |
| 工具 | `GSheetDownloader.exe` | `fwcli.exe` |
| 交互方式 | stdin 管道 | 命令行参数 |
