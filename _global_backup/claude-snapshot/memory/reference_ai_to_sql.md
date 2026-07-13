---
name: AI-to-SQL Skill
description: Datain 数仓 Trino SQL 查询技能，路径在 ADHD_agent 仓库下，支持玩家日志/建筑/资产/付费明细查询
type: reference
originSessionId: f6f8a545-b15c-4f6e-a240-0fc5532e47ae
---
## Skill 路径
`C:\ADHD_agent\.agents\skills\ai-to-sql\`（2026-07-08 实测：已迁到 `.agents\skills`，旧路径 `.claude\skills\ai-to-sql` 与 `~\.claude\skills\ai-to-sql` 均不存在）

## 核心脚本
```
C:\ADHD_agent\.agents\skills\ai-to-sql\scripts\
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

## 🔴🔴 查 X3(1090) 必须显式 `--datasource TRINO_HF`(2026-06-26 纠正,极易踩)
**`query_trino.py` / `search_tables.py` 默认 `DEFAULT_DATASOURCE="TRINO_AWS"`(老游戏 P2/AWS 集群)。X3 在 TRINO_HF，不加 `--datasource TRINO_HF` 就打到错集群**——**静默返 0 行 / `SHOW CATALOGS` 只剩 hive+system / 查任何 X3 玩家都"查不到"**，极易误判成"数仓没数据/停更/玩家不存在"。
- ✅ **加上 `--datasource TRINO_HF` 后,X3 `v1090.ods_*` 数据新鲜到当天**(2026-06-26 实测 `ods_user_activity`/`ods_user_task`/`ods_user_battle` max(partition_date)=当天,13亿+行)。**下方"ODS停更2026-01-08"是上一版打错AWS集群得出的错误结论,作废**。
- 例:`python query_trino.py --datasource TRINO_HF --sql "SELECT max(partition_date) FROM v1090.ods_user_activity"`。
- ⚠️ **TRINO_HF 上 catalog 是 hive**(不是 memory 旧写的"iceberg默认");`v1090.<表>` 直接用不加 catalog 前缀即可。`search_tables` 返回的 `iceberg.v{...}` 前缀只是元数据提示,当前 key 实际连的是 hive。

## v1090(X3) 查询字段坑(TRINO_HF)
- `user_id` / `server_id` / `partition_date` 全是 **varchar**:过滤加引号(`user_id='1684352'` / `partition_date>='2026-06-25'`),整数比较或 `date'...'` 比 partition_date 都报 `Cannot apply operator`。
- 时间戳列(`created_at` 等)比较用 **`TIMESTAMP '2026-06-26 08:00:00'`** 字面量,别用裸字符串。`created_at` 是**北京时间**。
- 直接 `SELECT * FROM v1090.<表> LIMIT 1` 看列,比 explore_tables/DESCRIBE(要 schema 前缀)省事。
- **dev/本地 `-e local` 服(如 3080)不上报数仓**(v1090 只收生产/CBT 段 server_id 1000–1560);本地服行为日志只在 `C:\x3-project\server\GameServer\bin\Debug\net8.0\logs\game-<sid>.bi.log`。
- 活动类玩家查询见 [[reference_x3_score_activity]]「BP积分诊断链路」(BP日志按升级才写/积分任务不进 ods_user_task/击杀对账走 ods_user_battle)。
