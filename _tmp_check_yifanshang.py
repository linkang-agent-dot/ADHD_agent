# -*- coding: utf-8 -*-
"""
查一番赏和推币机的每日收入分布，确认实际上线时间
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

SQL = """
SELECT
    b2.iap_id_name,
    date(date_add('hour',-8,b1.created_at)) AS pay_date,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue,
    COUNT(DISTINCT b1.user_id) AS buyers
FROM (
    SELECT user_id, iap_id, pay_price, created_at
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2025-12-15' AND '2026-04-05'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
      AND (iap_id_name LIKE '%一番赏%' OR iap_id_name LIKE '%推币机%')
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, date(date_add('hour',-8,b1.created_at))
ORDER BY b2.iap_id_name, pay_date
"""

rows = api.execute_sql(SQL)

by_name = {}
for r in rows:
    name = r['iap_id_name']
    if name not in by_name:
        by_name[name] = []
    by_name[name].append((str(r['pay_date']), float(r['revenue']), int(r['buyers'])))

for name, days in sorted(by_name.items()):
    total = sum(d[1] for d in days)
    first = days[0][0]
    last = days[-1][0]
    print(f"\n{'='*50}")
    print(f"{name}  total=${total:,.0f}  {first}~{last}")
    print(f"{'='*50}")
    for dt, rev, buyers in days:
        bar = '#' * int(rev / 500)
        print(f"  {dt}  ${rev:>8,.0f}  {buyers:>4}人  {bar}")
