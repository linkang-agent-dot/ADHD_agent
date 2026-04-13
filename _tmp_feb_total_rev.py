# -*- coding: utf-8 -*-
"""
查纯春节(01-13~02-01) 和 2月独立周期(02-02~02-08) 的
总营收(全iap_type) + 活跃用户 + 付费用户 + ARPPU
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

PERIODS = [
    {"name": "春节(纯)", "start": "2026-01-13", "end": "2026-02-01"},
    {"name": "2月独立周期", "start": "2026-02-02", "end": "2026-02-08"},
]

results = {}
for p in PERIODS:
    from datetime import datetime, timedelta
    start_m1 = (datetime.strptime(p["start"], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Total revenue (all iap types)
    SQL_REV = f"""
    SELECT
        CAST(SUM(pay_price) AS DECIMAL(18,2)) AS total_revenue,
        COUNT(DISTINCT user_id) AS pay_users,
        COUNT(*) AS orders
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '{start_m1}' AND '{p["end"]}'
      AND date(date_add('hour',-8,created_at)) BETWEEN date '{p["start"]}' AND date '{p["end"]}'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    """
    
    # Active users (anyone who logged in during the period)
    SQL_DAU = f"""
    SELECT COUNT(DISTINCT user_id) AS active_users
    FROM v1041.dl_active_user_d
    WHERE partition_date BETWEEN '{p["start"]}' AND '{p["end"]}'
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    """
    
    print(f"Querying {p['name']} ({p['start']}~{p['end']})...", flush=True)
    
    rev_rows = api.execute_sql(SQL_REV)
    dau_rows = api.execute_sql(SQL_DAU)
    
    total_rev = float(rev_rows[0].get('total_revenue', 0) or 0) if rev_rows else 0
    pay_users = int(rev_rows[0].get('pay_users', 0) or 0) if rev_rows else 0
    active_users = int(dau_rows[0].get('active_users', 0) or 0) if dau_rows else 0
    
    pay_rate = pay_users / active_users * 100 if active_users > 0 else 0
    arppu = total_rev / pay_users if pay_users > 0 else 0
    arpu = total_rev / active_users if active_users > 0 else 0
    
    results[p["name"]] = {
        "start": p["start"], "end": p["end"],
        "total_revenue": round(total_rev, 2),
        "pay_users": pay_users,
        "active_users": active_users,
        "pay_rate": round(pay_rate, 2),
        "arppu": round(arppu, 2),
        "arpu": round(arpu, 2),
    }
    
    print(f"  total_rev=${total_rev:,.0f}  pay_users={pay_users:,}  active={active_users:,}")
    print(f"  pay_rate={pay_rate:.2f}%  ARPPU=${arppu:.2f}  ARPU=${arpu:.2f}")

with open(r'C:\ADHD_agent\_tmp_feb_total_rev.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nDone")
