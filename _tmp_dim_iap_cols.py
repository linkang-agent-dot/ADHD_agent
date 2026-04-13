# -*- coding: utf-8 -*-
"""查dim.iap的科技节礼包列表 - 用iap_id_name字段"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 先看dim.iap实际字段
SQL = """
SELECT *
FROM v1041.dim_iap
WHERE iap_id_name LIKE '%科技%'
LIMIT 20
"""

print("=== 查科技节礼包 ===")
try:
    r = api.execute_sql(SQL)
    if isinstance(r, dict):
        cols = r.get('columns', [])
        rows = r.get('rows', [])
        print("columns:", cols)
        for row in rows:
            print(row)
    else:
        print(r)
except Exception as e:
    print(f"ERROR: {e}")
    # 尝试另一个写法
    SQL2 = "SELECT * FROM v1041.dim_iap LIMIT 3"
    try:
        r2 = api.execute_sql(SQL2)
        print("=== LIMIT 3 结果 ===")
        print(r2)
    except Exception as e2:
        print(f"ERROR2: {e2}")
