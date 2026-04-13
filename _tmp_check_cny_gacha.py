# -*- coding: utf-8 -*-
"""检查春节期间所有皮肤相关礼包的收入明细"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 春节完整周期 01-13 ~ 02-08
SQL = """
SELECT
    b2.iap_id_name,
    b2.iap_type2,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
    COUNT(*) AS buy_times,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price, date(date_add('hour',-8,created_at)) AS buy_date
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
WHERE b2.iap_type2 = '混合-节日活动-节日皮肤'
GROUP BY b2.iap_id_name, b2.iap_type2
ORDER BY revenue DESC
"""

print("=== 春节完整周期(01-13~02-08) 皮肤类礼包 ===")
rows = api.execute_sql(SQL)
total = 0
for r in rows:
    rev = float(r['revenue'])
    total += rev
    print(f"  {r['iap_id_name']:40s}  buyers={str(r['pay_user_cnt']):>5s}  rev=${rev:>10,.2f}")
print(f"  {'TOTAL':40s}  ${total:>10,.2f}")

# 再查春节期间所有 GACHA 关键词的礼包（不限 iap_type2）
SQL2 = """
SELECT
    b2.iap_id_name,
    b2.iap_type,
    b2.iap_type2,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
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
    SELECT iap_id, iap_id_name, iap_type, iap_type2
    FROM v1041.dim_iap
) b2 ON b1.iap_id = b2.iap_id
WHERE lower(b2.iap_id_name) LIKE '%gacha%'
   OR b2.iap_id_name LIKE '%抽奖%'
   OR b2.iap_id_name LIKE '%皮肤%'
GROUP BY b2.iap_id_name, b2.iap_type, b2.iap_type2
ORDER BY revenue DESC
"""

print("\n=== 春节(01-13~02-08) 含GACHA/抽奖/皮肤关键词的所有礼包 ===")
rows2 = api.execute_sql(SQL2)
total2 = 0
for r in rows2:
    rev = float(r['revenue'])
    total2 += rev
    print(f"  {r['iap_id_name']:45s}  type={r['iap_type2']:35s}  buyers={str(r['pay_user_cnt']):>5s}  rev=${rev:>10,.2f}")
print(f"  {'TOTAL':45s}  ${total2:>10,.2f}")

# 看看按日分布
SQL3 = """
SELECT
    date(date_add('hour',-8,created_at)) AS buy_date,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue,
    COUNT(DISTINCT b1.user_id) AS buyers
FROM (
    SELECT user_id, iap_id, pay_price, created_at
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2026-01-12' AND '2026-02-08'
      AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-01-13' AND date '2026-02-08'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
      AND iap_type2 = '混合-节日活动-节日皮肤'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY 1
ORDER BY 1
"""

print("\n=== 春节皮肤类-按日分布 ===")
rows3 = api.execute_sql(SQL3)
for r in rows3:
    rev = float(r['revenue'])
    print(f"  {r['buy_date']}  buyers={str(r['buyers']):>4s}  rev=${rev:>8,.2f}")
