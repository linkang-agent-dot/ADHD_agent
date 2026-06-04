---
name: P2 数仓 created_at 是北京时间
description: P2 (game_cd=1041) ods_user_asset 表的 created_at 字段存储的是北京时间，查询时不需要做 UTC-8h 转换
type: feedback
originSessionId: 3513cac8-14a9-4520-be94-7fa136eb5b49
---
P2 数仓 (TRINO_AWS, game_cd=1041) 的 `ods_user_asset` 表中 `created_at` 字段已经是北京时间 (UTC+8)，不是 UTC。

**Why:** 首次查询时按 UTC 做了 -8h 转换，导致时间窗口偏移、数据量少了约 75%（3,019 vs 5,492 玩家）。与用户对照数据后确认是时区问题。

**How to apply:** 查 P2 数仓 `created_at` 时，直接用北京时间条件过滤，不做 UTC 转换。`partition_date` 同理，用北京日期即可。其他游戏（X2/X3）待验证是否同理。
