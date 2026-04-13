# -*- coding: utf-8 -*-
"""检查dl_user_basic_info_d的字段，看是否包含rlevel"""
import sys, json
sys.path.insert(0, r'c:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 查 dl_user_basic_info_d 的字段
print("=== DESCRIBE dl_user_basic_info_d ===")
try:
    r = api.execute_sql("SHOW COLUMNS FROM v1041.dl_user_basic_info_d", "TRINO_AWS")
    for row in r:
        print(row)
except Exception as e:
    print(f"ERR: {str(e)[:300]}")

# 也查一下 ods_user_rlevel 是否存在
print("\n=== ods_user_rlevel ===")
try:
    r = api.execute_sql("SHOW COLUMNS FROM v1041.ods_user_rlevel", "TRINO_AWS")
    for row in r[:5]:
        print(row)
except Exception as e:
    print(f"ERR: {str(e)[:300]}")

# dl_user_portrait 看看
print("\n=== dl_user_portrait ===")
try:
    r = api.execute_sql("SHOW COLUMNS FROM v1041.dl_user_portrait", "TRINO_AWS")
    for row in r:
        print(row)
except Exception as e:
    print(f"ERR: {str(e)[:300]}")
