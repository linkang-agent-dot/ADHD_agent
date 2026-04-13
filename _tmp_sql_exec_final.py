# -*- coding: utf-8 -*-
"""最终尝试：用 JWT 执行图表5的 SQL（节日整体付费情况）"""
import requests, json

TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyNzciLCJpYXQiOjE3NzMxMTEzNzIsImV4cCI6MTc4MDg4NzM3Mn0.aQnLq62fs1ZhB1njB8kPEEe6zL7Hngk6oKvqiPz9hlj9btOwJxGuW6TPVgePydQwV_4KMsGs6O4ayFe64DGhaw"
SERVER = "https://datain-server.tap4fun.com"

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://datain.tap4fun.com",
    "Referer": "https://datain.tap4fun.com/",
}

# 先验证：未鉴权时 /api/sql/execute 返回 401，
# 说明它是服务器统一拦截还是路径真实存在？
print("=== 未鉴权时 vs 已知不存在路径 ===")
for path in ["/api/sql/execute", "/api/clearly/nonexistent/path/xyz"]:
    r = requests.get(f"{SERVER}{path}", timeout=6)
    print(f"  GET {path} (no auth) → {r.status_code}")

print("\n=== JWT 鉴权后 GET/POST sql/execute ===")

# 图表5 SQL（填好参数版）
sql = """with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id, a.partition_date, real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= '2026-03'
and date(date_add('hour',-8,created_at)) between date '2026-03-13' and date '2026-04-02'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
group by 1, 2, 3 ) a 
left join (select partition_date, event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id 
        from v1041.ods_logic_server_event
where create_time >= '2023-01' and event_type = 'schema'
and cast(event_period as integer) <= 6 and event_status = '2') b 
on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join (select user_id from v1041.ods_user_click 
where partition_date between '2026-03-12' and '2026-04-02'
and date(date_add('hour',-8,created_at)) between date '2026-03-13' and date '2026-04-02'
and control_id like '%2112%'
group by 1) bb on aa.user_id = bb.user_id
left join (select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between '2026-03-12' and '2026-04-02'
group by 1 ) cc on aa.user_id = cc.user_id 
group by 1, 2)
select rlevel, count(distinct user_id) as log_num,
count(distinct case when pay_price>0 then user_id end) as buy_num,
sum(pay_price) as pay_price, sum(pay_total) as pay_total
from (select a.*, pay_price, pay_total from log_info a 
left join (select user_id,
sum(case when iap_type='混合-节日活动' then pay_price end) as pay_price,
sum(pay_price) as pay_total
from (select user_id,iap_id,pay_price from v1041.ods_user_order 
where partition_date between '2026-03-12' and '2026-04-02'
and date(date_add('hour',-8,created_at)) between date '2026-03-13' and date '2026-04-02'
and pay_status=1) b1 
left join (select iap_id,iap_type from dim.iap where game_cd=1041) b2 on b1.iap_id=b2.iap_id
group by 1) b on a.user_id=b.user_id)
where rlevel != 'feiR' group by 1 order by pay_price desc"""

# 尝试各种路径和请求结构
attempts = [
    ("GET",  "api/sql/execute", None, {"sql": sql, "type": "trino"}),
    ("POST", "api/sql/execute", {"sql": sql, "type": "trino", "gameCd": 1041}, None),
    ("POST", "api/sql/run",     {"sql": sql, "gameCd": 1041}, None),
    ("POST", "api/analysis/sql",{"sql": sql, "gameCd": 1041}, None),
    ("POST", "api/chart/sql",   {"sql": sql, "gameCd": 1041}, None),
    # 用 chartId 直接取数据
    ("POST", "api/chart/66b03f3a7f0b225af663fbb5/data",
     {"startTime":"2026-03-13","endTime":"2026-04-02","params":{"control_id":"%2112%"}}, None),
    ("GET",  "api/chart/66b03f3a7f0b225af663fbb5/data",
     None, {"startTime":"2026-03-13","endTime":"2026-04-02","controlId":"%2112%"}),
    # dashboard + chartId
    ("POST", "api/dashboard/66ab4f762a840a587f0d8fd4/chart/66b03f3a7f0b225af663fbb5",
     {"startTime":"2026-03-13","endTime":"2026-04-02"}, None),
]

for method, path, body, params in attempts:
    try:
        url = f"{SERVER}/{path}"
        if method == "GET":
            r = requests.get(url, headers=H, params=params or {}, timeout=20)
        else:
            r = requests.post(url, headers=H, json=body or {}, timeout=20)
        code = r.status_code
        if code not in [404]:
            text = r.text[:300]
            print(f"*** {method} /{path[:55]} → {code}  {text}")
        else:
            print(f"    {method} /{path[:55]} → 404")
    except Exception as e:
        print(f"    {method} /{path[:45]} → ERR: {e}")
