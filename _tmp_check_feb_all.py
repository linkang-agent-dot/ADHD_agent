# -*- coding: utf-8 -*-
"""
查2月整月所有节日活动礼包的日收入，找出春节-情人节之间是否有独立事件周期
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 1. 查所有节日礼包在1.20~2.20的每日收入（按名称分）
SQL = """
SELECT
    b2.iap_id_name,
    date(date_add('hour',-8,b1.created_at)) AS pay_date,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price, created_at
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2026-01-20' AND '2026-02-20'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, date(date_add('hour',-8,b1.created_at))
HAVING SUM(b1.pay_price) >= 100
ORDER BY pay_date, revenue DESC
"""

rows = api.execute_sql(SQL)

# 按日期聚合看哪些活动在跑
by_date = {}
for r in rows:
    dt = str(r['pay_date'])
    if dt not in by_date:
        by_date[dt] = []
    by_date[dt].append((r['iap_id_name'], float(r['revenue'])))

print("=== 1.20~2.20 每日活跃的节日活动礼包 ===\n")
for dt in sorted(by_date.keys()):
    items = by_date[dt]
    total = sum(i[1] for i in items)
    print(f"\n--- {dt}  total=${total:,.0f}  ({len(items)}种) ---")
    for name, rev in sorted(items, key=lambda x: -x[1])[:10]:
        print(f"  ${rev:>8,.0f}  {name}")
    if len(items) > 10:
        print(f"  ... +{len(items)-10} more")
