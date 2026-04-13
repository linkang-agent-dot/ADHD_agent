# -*- coding: utf-8 -*-
"""
查 R级表的可用 create_date 和活跃用户表结构
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 1. 查 R级表有哪些 create_date，及各 rlevel 人数
print("=== da_user_rlevel_pay_ratio create_date 分布 ===", flush=True)
rows = api.execute_sql("""
SELECT create_date, rlevel, COUNT(*) as cnt
FROM v1041.da_user_rlevel_pay_ratio
GROUP BY create_date, rlevel
ORDER BY create_date DESC, cnt DESC
""")
for r in rows:
    print(f"  {r['create_date']}  {r['rlevel']:8s}  {r['cnt']:,}")

# 2. 查活跃用户日表结构
print("\n=== dl_active_user_d 样本 ===", flush=True)
try:
    rows2 = api.execute_sql("SELECT * FROM v1041.dl_active_user_d LIMIT 2")
    if rows2:
        print("列:", list(rows2[0].keys()))
        for r in rows2:
            print(" ", json.dumps(r, ensure_ascii=False, default=str)[:250])
except Exception as e:
    print(f"❌ {e}")
