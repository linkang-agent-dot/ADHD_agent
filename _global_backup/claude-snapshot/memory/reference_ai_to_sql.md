---
name: AI-to-SQL Skill
description: Datain 数仓 Trino SQL 查询技能，路径在 ADHD_agent 仓库下，支持玩家日志/建筑/资产/付费明细查询
type: reference
originSessionId: f6f8a545-b15c-4f6e-a240-0fc5532e47ae
---
## Skill 路径
`C:\ADHD_agent\.claude\skills\ai-to-sql\`

## 核心脚本
```
C:\ADHD_agent\.claude\skills\ai-to-sql\scripts\
  get_game_info.py    # 获取游戏列表+表权限（每次会话先执行）
  search_tables.py    # 搜索表名 --keyword "xxx"
  rag_search.py       # 检索指标参考 SQL + wiki 文档
  explore_tables.py   # 探索表结构（字段、类型、分区）
  query_trino.py      # 执行 Trino SQL
```

## 游戏编码
- 1041: P2 (TRINO_AWS)
- 1089: X2 (TRINO_HF)
- **1090: X3 (TRINO_HF)**
- 1076: P2_CN (TRINO_AWS)

## X3 关键表（TRINO_HF，non-full-access 用 v1090 视图格式）
- `v1090.ods_user_daily` — 玩家每日快照
- `v1090.dl_user_rlevel_all_info` — 等级明细
- `v1090.dim_building` — 建筑维度
- `v1090.ods_user_order` — 付费订单
- `v1090.ods_user_asset` — 资产变动
- `v1090.ods_user_activity` — 活动参与

## 视图格式规则（non-full-access）
- 表格式: `v{game_cd}.{layer}_{table}`
- 例如: `ods.user_daily` → `v1090.ods_user_daily`
- v1090 视图已内置 game_cd 过滤，SQL 无需再加 WHERE game_cd=1090
- TRINO_HF 环境: iceberg catalog 为默认，hive 的表需加 `hive.` 前缀

## 鉴权
- 使用环境变量 `DATAIN_API_KEY`（同 datain-skill 共享）
- 不需要 web session，API Key 直接可用

## How to apply
查游戏玩家明细数据（建筑等级、付费订单、活动参与等）时用 ai-to-sql skill，不用 datain-skill 的聚合 API。
datain-skill 适合查 Cohort LTV/ARPU 等聚合指标；ai-to-sql 适合查明细原始数据。
