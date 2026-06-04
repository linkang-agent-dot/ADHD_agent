---
name: x3
description: X3 Datain 查皮肤/道具拥有率、R级分布、付费额的正确口径——asset_id 带类型前缀是最大坑
metadata: 
  node_type: memory
  type: reference
  originSessionId: 490ce72b-3baa-4614-9fe0-430f6331e079
---

X3 Datain（TRINO_HF, v1090）查外显/道具的**拥有率、R级分布、付费额**。脚本走 `C:\ADHD_agent\skills\ai-to-sql\scripts\_datain_api.py` 的 `execute_sql(sql,'TRINO_HF')`。

## 🔴 最大坑：asset_id 带类型前缀（裸 ID 全返 0）
`ods_user_asset` / `dl_active_user_asset_balance_d` 里 **asset_id 是带类型前缀的字符串**，不是裸数字 ID：
- 道具：`Item_5303401`（英雄皮肤道具）、`Item_81101`(岛屿皮肤道具·永久)/`Item_81103`(3天)/`Item_81104`(7天)
- 皮肤本体：`Skin_1011`（岛屿皮肤解锁，岛屿皮肤的"拥有"看这个）、`Hero_1034`（英雄）、`FurnitureSkin_1003`（家具皮肤）
- ⚠️ `asset_id='5303401'`（裸）→ **0 条**；必须 `asset_id='Item_5303401'`。`change_type` 也是字符串，用 `change_type='1'`（不是 `=1`，否则 varchar=integer 报错）。
- **不知道前缀就反查 `dim_asset`**：`SELECT asset_id,asset_name FROM v1090.dim_asset WHERE asset_name LIKE '%海风旅者%'` → 给出真实 asset_id。

## 拥有率（曾获得=拥有，外显永久）
```sql
SELECT count(distinct user_id) owners
FROM v1090.ods_user_asset
WHERE asset_id='Item_5303401' AND change_type='1'
  AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 1880   -- 1-88/89服
```
- 岛屿皮肤拥有口径优先用 `Skin_xxxx`（解锁本体）；英雄皮肤用 `Item_530xxxx`（道具，皮肤"使用后获得"）。
- 拥有率分母：MAU = `ods_user_login` 近30天去重(`partition_date>='YYYY-MM-DD'`，partition_date 是 **varchar**)；或累计登录总玩家。

## 拥有者 × R级分布
join `dl_user_rlevel_all_info`（按日快照，game_cd=1090，rlevel=chaoR/daR/zhongR/xiaoR=超/大/中/小R；表不全→未命中=未分级）：
```sql
WITH o AS (SELECT DISTINCT user_id FROM v1090.ods_user_asset WHERE asset_id='Item_5303401' AND change_type='1' AND <服段>)
SELECT COALESCE(r.rlevel,'未分级') lv, count(DISTINCT o.user_id) c
FROM o LEFT JOIN (SELECT user_id,rlevel FROM v1090.dl_user_rlevel_all_info WHERE game_cd=1090 AND partition_date='<最新>') r
  ON CAST(o.user_id AS varchar)=CAST(r.user_id AS varchar)
GROUP BY 1
```

## 拥有者付费额
join `ods_user_order`（pay_status=1；USD: `currency_type IN ('usd','TOKEN') ? actual_charge : pay_price`）。可算终身付费 / 某活动礼包付费（iap_id IN 礼包集）。礼包名反查 `dim_iap.iap_id_name`。

## 其他表
- `dl_active_user_asset_balance_d`：活跃用户资产**余额快照**（无 server_id，要 join 用户→服）。注意：皮肤"用后解锁"余额可能为0，拥有看 ods_user_asset 的 change_type='1' 流水更准。

## 工具选择
- **按道具ID查拥有/付费明细 → 用 ai-to-sql（Trino 明细查询）**，不要用 `datain-skill`（那是聚合指标 DNU/留存/付费，查不了单道具拥有）。

实战来源：2026-06 深海节查海风旅者(Item_5303401,41人/超R5)、赛米拉(Item_53017,17人)、月心珍珠(Skin_1011/Item_81101,30人/人均终身$22k)。
