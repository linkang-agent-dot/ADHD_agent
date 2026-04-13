# -*- coding: utf-8 -*-
"""查dim_iap字段列表"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 先查 dim_iap 的字段
SQL_COLS = "SELECT * FROM v1041.dim_iap LIMIT 3"
print("=== dim_iap 字段 ===")
try:
    r = api.execute_sql(SQL_COLS)
    cols = r.get('columns', []) if isinstance(r, dict) else []
    rows = r.get('rows', []) if isinstance(r, dict) else r
    print("columns:", cols)
    for row in rows:
        print(row)
except Exception as e:
    print(f"ERROR: {e}")
