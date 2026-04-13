# -*- coding: utf-8 -*-
"""扩大搜索春节期间的所有节日礼包，找出骰子相关的"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 春节全量（01-13~02-08），按收入排序，不限 type2
SQL = """
SELECT
    b2.iap_id_name,
    b2.iap_type2,
    b2.iap_id,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
    COUNT(*) AS buy_times,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2026-01-12' AND '2026-02-08'
      AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-01-13' AND date '2026-02-08'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name, iap_type2
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, b2.iap_type2, b2.iap_id
ORDER BY revenue DESC
"""

print("=== 春节(01-13~02-08) 全部节日活动礼包 按收入排序 ===")
rows = api.execute_sql(SQL)
total = 0
for i, r in enumerate(rows):
    rev = float(r['revenue'])
    total += rev
    print(f"  {i+1:>3d}. {r['iap_id_name']:45s}  type2={r['iap_type2'].replace('混合-节日活动-',''):12s}  iap_id={str(r['iap_id']):>10s}  buyers={str(r['pay_user_cnt']):>5s}  rev=${rev:>10,.2f}")
print(f"\n  总计 {len(rows)} 个礼包  总收入 ${total:>10,.2f}")
