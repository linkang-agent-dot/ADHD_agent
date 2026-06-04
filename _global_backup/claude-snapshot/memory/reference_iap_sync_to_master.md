---
name: IAP 礼包同步 skill (X2 主数据)
description: X2 项目 iap-sync-to-master skill — 从实际礼包表 QA 页签增量同步新礼包到主数据表的礼包维表
type: reference
originSessionId: 0057db61-c2b8-4421-8e43-6b3209b0f76a
---
# iap-sync-to-master skill

X2 项目把 QA 礼包表（iap_template_x2 qa 页签）增量同步到主数据表（礼包维表-iap）的工具。

## 路径
- Skill 目录: `C:/Users/linkang/skills/iap-sync-to-master/`
  - `SKILL.md` — 触发条件、字段映射、分类规则
  - `sync_iap.js` — 同步脚本（含 70+ 条 NAME_RULES 分类规则）
  - `主数据同步.html` — skill 文档可视化版

注意：不在 `~/.claude/skills/` 下，所以不会被 Claude Code 自动加载为内置 skill；需要手动 `node` 调用。

## 数据源
- **QA 表（源）**: SheetID `1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E`，页签 `iap_template_x2（qa）` (gid=1938706798)，从第 8 行开始读，A8:Z10000
- **主数据表（目标）**: SheetID `1rPK9k75RvSb897-BS6l-9ZvrU-iAefE-e9H2-uAnCc4`，页签 `礼包维表-iap`

## 触发词
"同步礼包" / "礼包同步" / "sync iap" / "X2 主数据同步"

## 使用
```bash
# 预览
node C:/Users/linkang/skills/iap-sync-to-master/sync_iap.js --dry-run
# 执行
node C:/Users/linkang/skills/iap-sync-to-master/sync_iap.js
```

## 关键约束
- 只做增量追加，不改/删已有数据
- QA 表数据先按 iap_id 去重（同一 ID 留第一条）
- 分批写入每批 5 条（避命令行长度限制 ENAMETOOLONG）
- iap_id 格式: `{A_INT_id}_{A_STR_temp_type}`
- 未匹配关键词的礼包标记为"未分类"（最近一次同步约 1579 条待补分类）

## 字段映射（写入 9 列 A-I）
| QA 表 | 主数据表 |
|-------|---------|
| `{A_INT_id}_{A_STR_temp_type}` | A: iap_id |
| N_STR_temp_desc | B: iap_id_name |
| `{A_INT_id}_{A_STR_temp_type}` | C: iap_id_name_en |
| A_FLT_price | D: iap_price |
| 名称关键词匹配 (NAME_RULES) | E-H: iap_type / iap_type2 / iap_type3 / iap_type4 |
| iap_type 前缀映射 (NOTE_RULES) | I: note（顶层模块大类） |

**Note 列规则**：基于 iap_type 前缀映射，覆盖 `机甲/收藏品/战车/军备+兵种技能/英雄装备+洗练/英雄/混合/小游戏/SLG/SHOP/未分类` 11 类。特殊：`混合-节日活动` → `节日`（必须前缀长的优先匹配），`SHOP` → `混合`，`小游戏-打造` → `小游戏`（用户拍板）。

**历史背景**：2026-04-15 之前同步的行 note 列都是空的，因为旧脚本 hard-code 写空字符串。新版脚本（v1.5）补齐了这个推导逻辑。如果需要回填旧空行，单独跑 backfill 任务。

## 待优化
- 补分类规则（未分类约 1579 条）
- 支持多页签同步（如"掉落转付费"独立页签）
- 加同步日志
