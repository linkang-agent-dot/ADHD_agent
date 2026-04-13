# -*- coding: utf-8 -*-
"""直接调 ai-to-sql 的 _datain_api 执行图表5 SQL"""
import sys, json
sys.path.insert(0, r'c:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 先搜索 rlevel 相关表
print("=== 搜索 rlevel 表 ===")
try:
    r = api.search_tables("rlevel")
    for t in r:
        print(f"  {t}")
except Exception as e:
    print(f"  search error: {e}")

# 图表5 SQL - 用 v1041 视图，rlevel 表先用 ods_user_rlevel
SQL = """
with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= '2026-03'
and date(date_add('hour',-8,created_at)) between date '2026-03-13' and date '2026-04-02'
and user_id not in (select user_id from v1041.dl_test_user where 1=1)
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id 
from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between '2026-03-12' and '2026-04-02'
and date(date_add('hour',-8,created_at)) between date '2026-03-13' and date '2026-04-02'
and control_id like '%2112%'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from v1041.dl_user_rlevel_all_info
where create_date between '2026-03-12' and '2026-04-02'
group by 1 ) cc on aa.user_id = cc.user_id 
group by 1, 2 ),

pay_info as (
select a.*, pay_price, pay_total from log_info a 
left join 
(select user_id,
        sum(case when iap_type = '混合-节日活动' then pay_price else null end) as pay_price,
        sum(pay_price) as pay_total from 
(select user_id, iap_id, pay_price from v1041.ods_user_order 
where partition_date between '2026-03-12' and '2026-04-02'
and date(date_add('hour',-8,created_at)) between date '2026-03-13' and date '2026-04-02'
and pay_status = 1 ) b1 
left join 
(select iap_id, iap_type from v1041.dim_iap where 1=1) b2 on b1.iap_id = b2.iap_id 
group by 1) b on a.user_id = b.user_id )

select label, log_num, buy_num, pay_price, pay_total,
       round(1.0 * pay_price / pay_total * 100, 2) as price_ratio, 
       round(1.0 * buy_num / log_num * 100, 2) as buy_ratio,
       round(1.0 * pay_price / NULLIF(buy_num, 0), 2) as arppu,
       round(1.0 * pay_price / NULLIF(log_num, 0), 2) as arpu from 
(select '全体玩家' as label, 
        count(distinct user_id) as log_num,
        count(distinct case when pay_price > 0 then user_id end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_total) as pay_total from pay_info
union all 
select '付费玩家' as label, 
        count(distinct user_id) as log_num, 
        count(distinct case when pay_price > 0 then user_id end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_total) as pay_total from pay_info
where rlevel != 'feiR'
union all 
select rlevel as label, 
        count(distinct user_id) as log_num, 
        count(distinct case when pay_price > 0 then user_id end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_total) as pay_total from pay_info
where rlevel != 'feiR'
group by 1 )
order by log_num desc
"""

print("\n=== 执行图表5 SQL ===")
try:
    rows = api.execute_sql(SQL, "TRINO_AWS")
    result = {"rows": rows}
    cols = list(rows[0].keys()) if rows else []
    print(f"列名: {cols}")
    print(f"行数: {len(rows)}")
    for row in rows:
        print(row)
    with open(r"c:\ADHD_agent\_tmp_chart5_result.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("\n已写入 _tmp_chart5_result.json")
except Exception as e:
    print(f"ERROR: {e}")
