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

## p2_title 前导空列错位坑（2026-06-08 合成小游戏等级表 2160）
- **带 `p2_title` 前导空列的表（如 2160 activity_metro_grade），fwcli 下载的 tsv 比仓库 canonical tsv 多一列**（下载 9 列 / 仓库 8 列），整列右移导致 ID 列错位。
- 直接套 `merge_rows.py` 会按错位的 ID 列匹配 → 报「ID not found」假阴性。
- 修法：merge 前先**剥掉下载 tsv 的前导 `p2_title` 空列、对齐仓库 8 列结构**，再追加/合并目标行。提交前 diff 确认列数与 HEAD 一致。

## 行筛选导表踩坑（2026-06-05 挖矿镐 title_icon）
- **fwcli googlexlsx 直接把全表 GSheet 写进 `fo/config/<页签>.tsv`**（`-d tmp_xlsx` 那个目录会是空的，别等 xlsx 产物）。全表会夹带别人在 GSheet 上的改动 → 必须 `merge_rows.py` 用 HEAD 基线收敛只留目标行。
- **PowerShell 沙箱会预拦 `Remove-Item tmp_xlsx\*`（误判保护路径）整条命令不执行** → 备份 `.bak` 可能没真建成。补救：`git show HEAD:fo/config/<页签>.tsv > <页签>.tsv.bak` 取干净基线；或建议带 `dangerouslyDisableSandbox`。
- **行筛选=整行替换，目标行的其它列改动会一起带进来**：merge_rows 把 GSheet 的整行覆盖 HEAD 行，所以目标行若在 GSheet 上还有别的列被人改过（本次 3 个合成行的 `A_INT_show_hud` 21121491→211200212），会**搭车进 commit**。提交前必须**逐字段 diff**（按 id 比 .bak vs 现值，列出每个变化的列名）确认每处改动都是预期的，再决定一起传还是回退非目标列。
- title_icon 落地链路全程：出图(x2-media)→真透明(remove_background)→录 DK(Display_Icon+IconBg 同 key 同 GUID)→Ctrl+Shift+E 导出 Path→写 2112 GSheet X 列(C_INT_title_icon)→行筛选导表→push。见 [[x2-dk-p2-dk-manager]]。
- ⚠️ **DK 的 Display/Path .asset 改动易被 `git checkout` 误回退**（png+meta 是 untracked 不受影响，但 .asset 是 tracked 会被还原）→ 录完 DK 别对 DisplayKey 目录做 git 丢弃；被回退了就重追加 Display 条目 + 重新 Ctrl+Shift+E。
