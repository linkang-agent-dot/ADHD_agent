---
name: x2-weekly-card-datain-query
description: X2「周卡没领到7次」类工单的数仓核查口径——区分节日自选周卡(festival_time_card_reward)与普通时长卡(iap_week_card_claim_all)，按购买+领取双向核对
metadata: 
  node_type: memory
  type: reference
  originSessionId: 54ad7792-bb2a-44f8-83ae-f21c1f498681
---

X2 玩家报「周卡没领到 7 次」时，**先分清是哪种周卡**——两种产品、两个 reason、核查口径完全不同（2026-06-25 工单 920120/877115 沉淀）。数仓 = `v1089.ods_user_asset`（领取流水）+ `v1089.ods_user_order`（购买），脚本 `C:\ADHD_agent\.claude\skills\ai-to-sql\scripts\query_trino.py --datasource TRINO_HF`。

## 两种「周卡」的判别（最关键，别混）
| 产品 | 购买 iap_id | 领取 reason_id | 机制 |
|---|---|---|---|
| **节日自选周卡** fes_weekly_card | `2013920150~153_fes_weekly_card`（拓荒：150=29.99/151=19.99/152=9.99/153=49.99）| `festival_time_card_reward` | 7 天，每天领 1 次，`reason_sub_id`=**活动ID**(拓荒=`21127366`) |
| **普通时长卡**（周/月卡）| `*_time_card`（如 `201340002_time_card` $4.99）| `iap_week_card_claim_all`（周）/ `iap_month_card`（月）| 每天自动到账，`reason_sub_id` 为空，长期连续日领 ≠ 7 天卡 |

⚠️ 报单人嘴里的「周卡」常指**节日自选周卡**(festival_time_card_reward)。普通 time_card 长期天天领、断不了，几乎不会是「没领到7次」的真主体。

## 核查 SQL（套用即可）
**① 先看玩家买了哪种卡**（user_id 就是数仓 user_id；服号 server_id 7 位）：
```sql
SELECT user_id, server_id, created_at_str, iap_id, pay_price, pay_status
FROM v1089.ods_user_order
WHERE user_id IN ('<id1>','<id2>') AND partition_date>='<起>'
  AND (lower(iap_id) LIKE '%time_card%' OR lower(iap_id) LIKE '%weekly%' OR iap_id LIKE '%2013920%')
ORDER BY user_id, created_at_str
```
pay_status=1 为成功。没有 `*_fes_weekly_card` 行 = 玩家**根本没买**节日周卡（别再往节日周卡 bug 上查）。

**② 数领取次数 = 按「秒级时间戳聚成 session」**（一次领取会拆成多笔 asset 行，差几秒；不能用 count(*) 当次数）：
```sql
SELECT substr(created_at_str,1,19) ts
FROM v1089.ods_user_asset
WHERE user_id='<id>' AND reason_id='festival_time_card_reward'
  AND reason_sub_id='<活动ID>' AND partition_date>='<起>'
GROUP BY substr(created_at_str,1,19) ORDER BY ts
```
拿到的 ts 列再按「相邻 ≤15 秒归一组」聚类 → 组数 = **真实领取次数**。普通卡同理用 `count(distinct substr(created_at_str,1,10))` 数天数。

## 实战结论范式（2026-06-25）
- **920120**(服1006502)：买 2013920153 $49.99 fes_weekly_card → festival_time_card_reward 聚出 **7 个 session**(06-20×2+06-21~25)=领满 7 次，**奖励全到账非 bug**；首日领 2 次→日历只跨 6 天易被误判「少一天」。
- **877115**(服1006102)：6 月只买 `*_time_card`，**无 fes_weekly_card 购买**；iap_week_card_claim_all 6 月 25 天 0 断档=普通卡正常。报「周卡没领到7次」对不上任何节日周卡购买。
- 时区：created_at_str 是**北京时间不转 UTC**（见 [[x2-datain-asset-query]]）。

## 排查方向
- 数仓有领取 session = 奖励已到账；玩家仍说没领满 → 多半是**游戏内计数 UI**（首日双领致计数跳）或玩家记错日历天，不是丢奖励。
- 真要查节日自选周卡「置灰/剩余天数=0」类 bug（订阅道具1111指向不存在的2013）→ 见 [[x2-config-library]] X2-43099 段。
