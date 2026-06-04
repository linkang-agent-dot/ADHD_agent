---
name: x3-gdconfig-repo
description: X3 配置仓库（git.tap4fun.com/x3/gdconfig）；导入只认 tsv（C:\x3\gdconfig\tsv\），配置改动直接改 tsv 不碰 xlsx，旧 C:\X3\、C:\x3dev\ 已弃用
metadata: 
  node_type: memory
  type: reference
  originSessionId: 22c25965-252c-40fd-9575-d6ee02470233
---

## X3 配置仓库（2026-05-25 起）

| 项 | 值 |
|----|----|
| Remote | `https://git.tap4fun.com/x3/gdconfig` |
| 本地仓库根 | `C:\x3\gdconfig\` |
| **配置真源（改这里）** | `C:\x3\gdconfig\tsv\`（导入只认 tsv） |
| xlsx 目录 | `C:\x3\gdconfig\data\` — **仅历史备份，下周删，不要改/导** |
| 常用分支 | `master` / `dev` / `feature/summer-love-song` / `dev-summer-love-song` |

## ⚠️ 已弃用路径（不要读写）

- `C:\X3\` — SVN 时代残留，无 .git
- `C:\x3dev\` — 中间过渡目录残留，无 .git
- `C:\x3\gdconfig\data\*.xlsx` — 仅备份；**导入/改表绝不找 xlsx**，全部在 `tsv\` 下操作

## ⚠️ 导入只认 tsv（2026-05-29 起）

Jenkins「X3导配置」读仓库里提交的 **tsv 缓存**，不读 xlsx。**配置改动直接改 `tsv\` 下文件**（用 `x3-config-export` skill 的 `tsv_edit.py`），改完 commit tsv → push → jolt 导表。**绝不对已 tsv-改过的表跑 xlsx_to_tsv 重生成**（xlsx 是旧的，会覆盖回去）。详见 [[reference_x3_tsv_export_migration]]。

## 常用配置表速查（tsv 真源）

tsv 命名：`tsv/{文件名}__{Sheet名}.tsv`。具体 sheet 用 `tsv_edit.py show` 确认。

| 用途 | tsv（部分 sheet） |
|------|------|
| 主活动表 | `tsv/ActvOnline__ActvOnline.tsv` |
| 时间周期 | `tsv/TimeCycle__*.tsv` |
| 累充任务档位 | `tsv/ActvTask__*.tsv` |
| 拜访礼包 | `tsv/ActvVisitPack__*.tsv` |
| 礼包 | `tsv/Pack__Pack.tsv` / `Pack__ChainPack.tsv` / `Pack__PackTypeInfo.tsv` |
| 奖励组 | `tsv/Reward__*.tsv` |
| 排行榜 | `tsv/Rank__RankCfg.tsv` / `Rank__RankRewardSlotCfg.tsv` |
| 每日榜 | `tsv/ActvDailyRank__*.tsv` |

## 工作流

- 改配置一条龙（定位→改tsv→提交→导表→验证）：skill `x3-config-export`
- push 后触发并验证导表：[[workflow_x3_auto_jolt_export]]（用 jolt_verify.py）
- Reward 写入约束：见 [[reference_x3_reward_table_rules]]
- 累充隔离机制：见 [[reference_x3_recharge_isolation]]

**How to apply:** X3 配置读写一律走 `C:\x3\gdconfig\tsv\`。看到上下文提 `data\*.xlsx`、`C:\X3\`、`C:\x3dev\` 等旧路径要主动纠正——导入这块永远不找 xlsx。
