# -*- coding: utf-8 -*-
"""查ods_user_order里iap_id的实际格式 - 无前缀过滤"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

START_PART = "20260313"
END_PART   = "20260403"

# 直接看前20条订单的iap_id
SQL1 = f"""
SELECT iap_id, pay_price, pay_status
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{START_PART}' AND '{END_PART}'
    AND pay_status = 1
LIMIT 20
"""
print("=== ods_user_order 样本 iap_id ===")
try:
    r = api.execute_sql(SQL1)
    rows = r if isinstance(r, list) else r.get('rows', [])
    for row in rows:
        print(row)
except Exception as e:
    print(f"ERROR: {e}")

print()

# 看一下原来SQL里面用的是什么join
# 从P2_节日活动付费数据情况_图表SQL.sql里看
