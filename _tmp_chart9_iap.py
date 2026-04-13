# -*- coding: utf-8 -*-
"""用正确的partition_date格式（带横线）"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

START = "2026-03-13"
END   = "2026-04-03"
START_MINUS1 = "2026-03-12"

# 先验证有没有数据
SQL_CHECK = f"""
SELECT COUNT(*) AS cnt
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{START_MINUS1}' AND '{END}'
    AND pay_status = 1
"""
print("=== 检查数据量 ===")
try:
    r = api.execute_sql(SQL_CHECK)
    print(r)
except Exception as e:
    print(f"ERROR: {e}")

print()

# 图表9正式SQL（用v1041.dim_iap替换dim.iap）
SQL9 = f"""
SELECT
    b2.iap_id_name,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
    COUNT(*) AS buy_times,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '{START_MINUS1}' AND '{END}'
        AND date(date_add('hour',-8,created_at)) BETWEEN date '{START}' AND date '{END}'
        AND pay_status = 1
        AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name
ORDER BY revenue DESC
"""
print("=== 图表9: 节日活动各礼包付费情况 ===")
try:
    r9 = api.execute_sql(SQL9)
    rows9 = r9 if isinstance(r9, list) else r9.get('rows', [])
    total_rev = sum(float(row.get('revenue',0)) for row in rows9)
    print(f"共 {len(rows9)} 种礼包，总收入: ${total_rev:,.2f}")
    for row in rows9:
        print(row)
except Exception as e:
    print(f"ERROR: {e}")
