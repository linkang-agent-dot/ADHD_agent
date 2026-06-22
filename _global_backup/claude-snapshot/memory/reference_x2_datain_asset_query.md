---
name: x2-datain-asset-query
description: "X2 数仓查资产流水/道具被回收名单的正确口径（v1089, asset_id 裸数字无前缀, change_type 1增2减, 北京时间）"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7b1bb7c2-9c3c-4449-8062-5172b01dc4d0
---

X2 Datain（TRINO_HF，game_cd=1089，视图 `v1089`）查**道具流水 / 被回收名单 / 拥有率**。脚本同 X3：`C:\ADHD_agent\.claude\skills\ai-to-sql\scripts\query_trino.py --datasource TRINO_HF`（或 `_datain_api.execute_sql(sql,'TRINO_HF')`）。

## 资产表 `v1089.ods_user_asset`（与 X3 的关键差异）
- 🔴 **asset_id 是裸数字字符串**（如 `'111111315'`），**不带类型前缀**——区别于 X3 的 `Item_xxx`/`Skin_xxx`。X3 那套前缀口径别套到 X2。
- `change_type`：`'1'`=增加（获得），`'2'`=扣减（消耗/回收）。字符串比较用 `='2'` 不是 `=2`。
- `change_count`：变动数量（正值，方向看 change_type），`balance`=变动后余额。
- `reason_id`=变动原因（如 `item_recycle`/`event_task`/`iap_pack`/`battle_pass_rewards`/`chrismas_gacha_2022_outside`...），`reason_sub_id` 偶尔放子id（多数为空）。
- 时间：`created_at` / `created_at_str` 是**北京时间**（`time_zone_name='Asia/Shanghai'`），**不做 UTC 转换**；`partition_date` 用北京日期。
- 服/人：`server_id`（如 `1003702`，X2 线上服 7 位），`user_id`。

## 「被回收」道具名单（补偿场景标准查法）
```sql
SELECT server_id, user_id, asset_id, sum(change_count) amount, count(*) events
FROM v1089.ods_user_asset
WHERE reason_id='item_recycle' AND asset_id='<道具cfgId>' AND partition_date='<北京日期>'
GROUP BY 1,2,3 ORDER BY CAST(server_id AS bigint), CAST(user_id AS bigint)
```
- 先按 `substr(created_at_str,1,13)` 看回收发生在哪几小时——活动结束的批量回收常集中在某一时刻，可借此判「这一周」实际就是某天某批。
- ⚠️ 数仓有 ETL 延迟（实测晚几小时），正式发补偿前**重新刷一次名单**避免漏掉新增的人。

## ⚠️ 数仓 asset_id == 道具配置 cfgId（实测一致），但发邮件仍可能 illegal
- 实测 `asset_id='111111315'` 在 X2 道具表(1111)里就是 cfgId 111111315（拓荒节2026抽奖代币，class=`event`，quality5）——数仓 asset_id 与配置 cfgId 同值。
- 但 iGame 批量发邮件附件填 `{"assetType":"item","id":111111315}` 时**报过 `item cfgId illegal`**（2026-06-16 待定位）：疑似 ① 发送环境/服的配置版本没加载该 event 道具，或 ② iGame 拦 `class=event` 活动代币禁邮件。结论未定，遇到时先要 iGame 完整报错+环境再判，别硬试。

实战来源：2026-06-16 X2 拓荒节抽奖代币(111111315)误回收补偿，171人/3001个，全在 06-16 08:00–12:00 一批回收。
