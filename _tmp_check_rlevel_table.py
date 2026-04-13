# -*- coding: utf-8 -*-
"""检查哪个rlevel表可用，以及探索dl_user_rlevel_all_info字段"""
import sys, json
sys.path.insert(0, r'c:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 尝试DESCRIBE dl_user_rlevel_all_info
tests = [
    "SHOW COLUMNS FROM v1041.dl_user_rlevel_all_info",
    "DESCRIBE v1041.dl_user_rlevel_all_info",
    "SELECT * FROM v1041.dl_user_rlevel_all_info LIMIT 1",
    "SHOW COLUMNS FROM iceberg.v1041.dl_user_rlevel_all_info",
]
for sql in tests:
    print(f"\n--- {sql[:60]} ---")
    try:
        r = api.execute_sql(sql, "TRINO_AWS")
        print(f"  OK: {r[:2] if r else r}")
        break
    except Exception as e:
        msg = str(e)
        print(f"  ERR: {msg[:200]}")
