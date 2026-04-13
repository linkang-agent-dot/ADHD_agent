# -*- coding: utf-8 -*-
"""查看科技节礼包的 iap_type 细分及购买数据"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

START = '2026-03-13'
END   = '2026-04-03'
START_PART = '2026-03-12'
END_PART   = '2026-04-03'

# 查 dim_iap 里所有节日活动礼包的细分类型（按 iap_type 展开）
SQL_IAP_TYPES = """
SELECT DISTINCT iap_type
FROM v1041.dim_iap
WHERE iap_type LIKE '%节日活动%'
   OR iap_type LIKE '%科技%'
ORDER BY iap_type
"""

print("=== dim_iap 节日活动类型 ===")
try:
    r = api.execute_sql(SQL_IAP_TYPES)
    rows = r.get('rows', []) if isinstance(r, dict) else r
    for row in rows:
        print(row)
except Exception as e:
    print(f"ERROR: {e}")

# 直接按购买时的 iap_type 统计（节日期间，节日活动礼包）
SQL_BY_IAPTYPE = f"""
SELECT 
  d.iap_type,
  COUNT(DISTINCT o.user_id) AS pay_users,
  COUNT(*) AS buy_times,
  CAST(SUM(o.pay_price) AS DECIMAL(18,2)) AS revenue,
  CAST(SUM(o.pay_price) / COUNT(*) AS DECIMAL(10,2)) AS times_arppu,
  CAST(SUM(o.pay_price) / COUNT(DISTINCT o.user_id) AS DECIMAL(10,2)) AS arppu
FROM v1041.ods_user_order o
JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
WHERE o.partition_date BETWEEN '{START_PART}' AND '{END_PART}'
  AND date(date_add('hour',-8, o.created_at)) BETWEEN date '{START}' AND date '{END}'
  AND o.pay_status = 1
  AND d.iap_type LIKE '%节日活动%'
  AND o.user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
GROUP BY d.iap_type
ORDER BY revenue DESC
"""

print("\n=== 节日活动礼包按 iap_type 付费统计 ===")
try:
    r2 = api.execute_sql(SQL_BY_IAPTYPE)
    rows2 = r2.get('rows', []) if isinstance(r2, dict) else r2
    print(f"共 {len(rows2)} 种 iap_type:")
    total_rev = 0
    for row in rows2:
        print(row)
        if isinstance(row, dict):
            total_rev += row.get('revenue', 0)
    print(f"合计收入: {total_rev:.2f}")
    with open('_tmp_iap_by_type.json', 'w', encoding='utf-8') as f:
        json.dump(rows2, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"ERROR: {e}")
