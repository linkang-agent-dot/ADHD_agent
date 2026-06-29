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

## 🔑 reason_id + reason_sub_id：按来源拆资产变动（隔离竞猜/免费领取等）
`ods_user_asset` 有 **`reason_id`(来源类型)** + **`reason_sub_id`(来源具体id)** + reason_sub_id_level/reason_status。这是按「为什么获得」拆资产流水的关键（订单表拆不出免费/非付费时用它）。
- Item_1146(世界杯抽奖券)获取 reason_id 分布(2026-06-27实测)：**`buy_gift`(买礼包,reason_sub_id=礼包号)** / `activity_battle_pass_score_reward`(BP) / `activity_reward`(累充/签到等) / item_op_activity_unclaimed_reward。
- **竞猜参与(含免费!)的正确查法**=`asset_id='Item_1146' AND change_type='1' AND reason_id='buy_gift' AND reason_sub_id LIKE '894%'`,按 reason_sub_id 分组=每个竞猜礼包的领取(免费档894xx0=进界面+选队=触达;付费894xx1/2/3=买家,与订单表对得上)。
- **界面触达率代理**=免费竞猜领取distinct人数 / 55服DAU(`ods_user_login` distinct,同期);竞猜无UI曝光埋点([[reference_x3_config]]),免费参与率是最佳触达代理(领免费=必进界面选队)。2026-06-27 D0实测=2192/6375=34.4%,付费23人/0.36%,免费→付费转化1.05%。
- 通用:任何"买礼包/免费领礼包"参与都可用 `reason_id='buy_gift' + reason_sub_id=礼包号` 拆,不限竞猜。
- ⚠️**活动奖励类拆不出单个cfgId**:`activity_reward`/`activity_daily_free_reward`/`activity_resign` 的 **reason_sub_id 都是空**,且 **asset 表 activity_id 列全空**(没用)→无法把签到(101403)等精确锁到单活动。只有"买礼包"(buy_gift)带reason_sub_id=礼包号。签到的最佳口径=`reason_id='activity_daily_free_reward'`(每日免费奖励·签到走它,但可能含其他每日免费活动,非严格101403);补签=`activity_resign`(给Item_1002钻·小众·付费玩家0)。
- **付费玩家触达对比口径(2026-06-27 D0实测)**:付费玩家=`ods_user_order pay_status=1`当日distinct(55服);触达=JOIN asset对应reason的distinct user。结果:付费玩家499,**竞猜触达316/63.3%**(buy_gift 894%) vs **签到94.2%**(daily_free_reward)。付费玩家碰竞猜概率≈普通DAU(34.4%)的2倍。⚠️今日订单数仓T+1延迟(订单max分区滞后1天),"今天"无数据时用最新可用日。

## 其他表
- `dl_active_user_asset_balance_d`：活跃用户资产**余额快照**（无 server_id，要 join 用户→服）。注意：皮肤"用后解锁"余额可能为0，拥有看 ods_user_asset 的 change_type='1' 流水更准。

## 工具选择
- **按道具ID查拥有/付费明细 → 用 ai-to-sql（Trino 明细查询）**，不要用 `datain-skill`（那是聚合指标 DNU/留存/付费，查不了单道具拥有）。

实战来源：2026-06 深海节查海风旅者(Item_5303401,41人/超R5)、赛米拉(Item_53017,17人)、月心珍珠(Skin_1011/Item_81101,30人/人均终身$22k)。
