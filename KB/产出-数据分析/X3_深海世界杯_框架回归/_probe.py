# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
# 1. ods_user_activity 里有哪些 activity_type，含 101406/10071704/100598 cfg 的记录
print("=== ods_user_activity 按 activity_type 计数(7/3-16, 全服) ===")
try:
    r=q("""SELECT activity_type, count(1) n, count(distinct user_id) u FROM v1090.ods_user_activity
        WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' GROUP BY activity_type ORDER BY n DESC LIMIT 20""")
    for x in r: print(f"  type={x['activity_type']:>4}  行{x['n']:>8}  人{x['u']:>7}")
except Exception as e: print("ERR", str(e)[:200])
print("\n=== 含 cfg 101406/10071704/100598 的 attribute1 样本 ===")
for cfg in ['101406','10071704','100598']:
    try:
        r=q(f"""SELECT activity_type, attribute1, count(1) n, count(distinct user_id) u FROM v1090.ods_user_activity
            WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND attribute1 LIKE '%{cfg}%'
            GROUP BY activity_type, attribute1 LIMIT 5""")
        print(f"cfg {cfg}: {len(r)} 组")
        for x in r: print(f"   type={x['activity_type']} attr={str(x['attribute1'])[:70]} 行{x['n']} 人{x['u']}")
    except Exception as e: print(f"cfg {cfg} ERR", str(e)[:150])
