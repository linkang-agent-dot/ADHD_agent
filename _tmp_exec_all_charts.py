# -*- coding: utf-8 -*-
"""
科技节报告数据查询 - 2026-03-13~04-03
查询：图表5（R级分层付费）+ 图表1（日收入趋势）+ 礼包总收入验证
"""
import sys, json
sys.path.insert(0, r'c:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

START = '2026-03-13'
END   = '2026-04-03'
START_PART = '2026-03-12'  # partition_date 提前一天覆盖UTC边界
END_PART   = '2026-04-03'
FESTIVAL_ID = '%2112%'

# ============================================================
# 图表5：R级分层付费（全体/付费玩家/各R级）
# ============================================================
SQL_CHART5 = f"""
with log_info as (
select aa.user_id, coalesce(cc.rlevel, 'feiR') as rlevel from 
(select user_id, a.partition_date, real_server_id,
        max(cast(schema as integer)) as schema 
from 
(select user_id, real_server_id, partition_date 
 from v1041.ods_user_login
 where create_time >= '2026-03'
 and date(date_add('hour',-8,created_at)) between date '{START}' and date '{END}'
 and user_id not in (select user_id from v1041.dl_test_user where 1=1)
 group by 1, 2, 3 ) a 
left join 
(select partition_date, event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id 
 from v1041.ods_logic_server_event
 where create_time >= '2023-01'
 and event_type = 'schema'
 and cast(event_period as integer) <= 6 
 and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id 
 from v1041.ods_user_click 
 where partition_date between '{START_PART}' and '{END_PART}'
 and date(date_add('hour',-8,created_at)) between date '{START}' and date '{END}'
 and control_id like '{FESTIVAL_ID}'
 group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(varchar_val, partition_date) as rlevel 
 from v1041.dl_user_portrait
 where partition_date between '{START_PART}' and '{END_PART}'
 and map_key = 'user_pay' and map_type = 'rlevel'
 group by 1) cc on aa.user_id = cc.user_id 
group by 1, 2 
),
pay_info as (
select a.user_id, a.rlevel, b.pay_price, b.pay_total 
from log_info a 
left join 
(select user_id,
        sum(case when iap_type like '%节日活动%' then pay_price else 0 end) as pay_price,
        sum(pay_price) as pay_total 
 from 
 (select user_id, iap_id, pay_price 
  from v1041.ods_user_order 
  where partition_date between '{START_PART}' and '{END_PART}'
  and date(date_add('hour',-8,created_at)) between date '{START}' and date '{END}'
  and pay_status = 1 ) b1 
 left join 
 (select iap_id, iap_type from v1041.dim_iap where 1=1) b2 on b1.iap_id = b2.iap_id 
 group by 1) b on a.user_id = b.user_id 
)
select label, log_num, buy_num, pay_price, pay_total,
       round(1.0 * COALESCE(pay_price, 0) / NULLIF(pay_total, 0) * 100, 2) as price_ratio, 
       round(1.0 * buy_num / NULLIF(log_num, 0) * 100, 2) as buy_ratio,
       round(1.0 * COALESCE(pay_price, 0) / NULLIF(buy_num, 0), 2) as arppu,
       round(1.0 * COALESCE(pay_price, 0) / NULLIF(log_num, 0), 2) as arpu
from (
  select '全体玩家' as label, 
         count(distinct user_id) as log_num,
         count(distinct case when COALESCE(pay_price,0) > 0 then user_id end) as buy_num,
         sum(COALESCE(pay_price,0)) as pay_price, sum(COALESCE(pay_total,0)) as pay_total 
  from pay_info
  union all 
  select '付费玩家' as label, 
         count(distinct user_id) as log_num, 
         count(distinct case when COALESCE(pay_price,0) > 0 then user_id end) as buy_num,
         sum(COALESCE(pay_price,0)) as pay_price, sum(COALESCE(pay_total,0)) as pay_total 
  from pay_info where rlevel != 'feiR'
  union all 
  select rlevel as label, 
         count(distinct user_id) as log_num, 
         count(distinct case when COALESCE(pay_price,0) > 0 then user_id end) as buy_num,
         sum(COALESCE(pay_price,0)) as pay_price, sum(COALESCE(pay_total,0)) as pay_total 
  from pay_info where rlevel != 'feiR'
  group by 1 
)
order by log_num desc
"""

# ============================================================
# 图表1：每日收入趋势（节日礼包 vs 全品）
# ============================================================
SQL_DAILY = f"""
select 
  date(date_add('hour',-8,created_at)) as pay_date,
  sum(case when iap_type like '%节日活动%' then pay_price else 0 end) as festival_revenue,
  sum(pay_price) as total_revenue
from 
(select user_id, iap_id, pay_price, created_at
 from v1041.ods_user_order 
 where partition_date between '{START_PART}' and '{END_PART}'
 and date(date_add('hour',-8,created_at)) between date '{START}' and date '{END}'
 and pay_status = 1
 and user_id not in (select user_id from v1041.dl_test_user where 1=1) ) b1 
left join 
(select iap_id, iap_type from v1041.dim_iap where 1=1) b2 on b1.iap_id = b2.iap_id 
group by 1
order by 1
"""

# ============================================================
# 节日礼包收入汇总（按 iap_type 分组验证）
# ============================================================
SQL_PKG_CHECK = f"""
select iap_type, 
       count(distinct user_id) as pay_users,
       sum(pay_price) as revenue,
       round(sum(pay_price) * 100.0 / sum(sum(pay_price)) over(), 1) as pct
from 
(select user_id, iap_id, pay_price
 from v1041.ods_user_order 
 where partition_date between '{START_PART}' and '{END_PART}'
 and date(date_add('hour',-8,created_at)) between date '{START}' and date '{END}'
 and pay_status = 1
 and user_id not in (select user_id from v1041.dl_test_user where 1=1) ) b1 
left join 
(select iap_id, iap_type from v1041.dim_iap where 1=1) b2 on b1.iap_id = b2.iap_id 
group by 1
order by revenue desc
"""

results = {}

print("=" * 60)
print(f"查询时段: {START} ~ {END}，活动ID: {FESTIVAL_ID}")
print("=" * 60)

for name, sql in [("chart5_rlevel", SQL_CHART5), 
                   ("daily_revenue", SQL_DAILY),
                   ("pkg_breakdown", SQL_PKG_CHECK)]:
    print(f"\n>>> 执行 {name} ...")
    try:
        rows = api.execute_sql(sql, "TRINO_AWS")
        results[name] = rows
        print(f"    OK: {len(rows)} 行")
        if rows:
            headers = list(rows[0].keys())
            print("    " + "\t".join(headers))
            for r in rows:
                print("    " + "\t".join(str(v) for v in r.values()))
    except Exception as e:
        print(f"    ERROR: {str(e)[:400]}")
        results[name] = None

with open(r"c:\ADHD_agent\_tmp_all_charts_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n\n已写入 _tmp_all_charts_result.json")
