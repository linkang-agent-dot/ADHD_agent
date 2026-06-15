---
name: x3-dau
description: 给定节日上线日反推 D35+ 可覆盖服 + 当期DAU 的数仓查法，含真实开服时间/合服剔除两坑
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2d23c11d-b63c-47f1-ad55-2dc40097ba60
---

X3 节日排期常问「X 月 X 日上线能覆盖哪些 D35+ 服、各服 DAU 多少」。固定查法 + 两个必踩坑。

## 口径
- **D35+ 判定**：服龄 = 上线日 − 真实开服日 ≥ 35 → 开服日 ≤ (上线日 − 35天)。临界服=开服日正好等于该阈值（D35）。
- **真实开服时间 ≠ `dim_open_server.open_time`**（那是配置计划值，老服严重失真，如 1000 配置 2024-07-05 实际 2023-08-15）。
  **用每服第一个玩家登录/注册时间**：`MIN(min_register_time)` from `iceberg.v1090.dl_server_login_info`（per server per day 的最早注册时点，取全历史 min）。
- **⚠️ 合服坑（最大）**：按 server_id 区间数会虚高。老服(如 1000~1160)合服后**原 id 作废、零登录**，玩家迁到存活服。
  真实存在的服 = **近期有登录活动的 id**（用 `ods_user_login` 近 7 日有 DAU 来过滤），合掉的空 id 自动排除。2026-06 实测：1000~1980 名义 99 个，实际活跃仅 61 个，38 个已合服。
- **DAU**：`ods_user_login`(有 server_id) count distinct user_id per server per day，取近 7 日均值。`dl_active_user_d` 没有 server_id 不能用。新服处爆发期 DAU 偏高、随服龄回落。
- 特殊服 9998(server_type=1，跨服/测试，DAU 个位数)按惯例剔除。

## 一条 SQL 出表（改两个日期即可复用）
```sql
WITH opens AS (
  SELECT server_id, MIN(min_register_time) AS open_ts
  FROM iceberg.v1090.dl_server_login_info
  WHERE min_register_time IS NOT NULL AND server_id <> ''
  GROUP BY server_id ),
dau AS (
  SELECT server_id, ROUND(AVG(d),0) AS avg_dau FROM (
    SELECT server_id, partition_date, COUNT(DISTINCT user_id) AS d
    FROM iceberg.v1090.ods_user_login
    WHERE partition_date BETWEEN '<近7日起>' AND '<近7日止>'
    GROUP BY server_id, partition_date) GROUP BY server_id )
SELECT d.server_id, date(o.open_ts) AS open_date,
  date_diff('day', date(o.open_ts), date '<上线日>') AS age, d.avg_dau
FROM dau d JOIN opens o ON d.server_id = o.server_id
WHERE date(o.open_ts) <= date '<上线日-35天>'
  AND TRY_CAST(d.server_id AS INTEGER) BETWEEN 1000 AND 1990   -- 排 9998
ORDER BY TRY_CAST(d.server_id AS INTEGER);
```
跑数仓走 ai-to-sql `query_trino.py --datasource TRINO_HF`（见 [[reference_ai_to_sql]]）。数仓时区=北京时间，partition_date 按北京日切（见 [[reference_x3_festival_monitor]]）。

## 实测基准（2026-06-08 数据，近7日均DAU）
- 6.19 上线 → D35+ = 开服≤05-15 = **56 服 / ≈7,100 DAU**；临界服 1930(05-15,D35)。
- 6.29 上线 → D35+ = 开服≤05-25 = **61 服 / ≈8,900 DAU**；临界服 1980(05-25,D35)。
- 共性：DAU 高度集中在最新几个服(1900~1930 各 250~900)，老服(D120+)普遍 20~200。
- 节日实际投放未必=全部 D35+，夏日只投到 1870（见 [[reference_x3_festival_monitor]]）；也可按尼罗 D17–D35 最佳窗口另切（见 [[reference_x3_festival_performance]]）。
