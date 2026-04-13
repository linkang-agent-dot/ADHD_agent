# -*- coding: utf-8 -*-
"""
1. 查 ods_user_click 的 control_id 有哪些节日相关的
2. 对比有/无 control_id 过滤的收入差异
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 1. 查科技节期间有哪些 control_id
print("=== 科技节期间 control_id 分布 ===", flush=True)
SQL1 = """
SELECT control_id, COUNT(DISTINCT user_id) AS users
FROM v1041.ods_user_click
WHERE partition_date BETWEEN '2026-03-12' AND '2026-04-03'
  AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-03-13' AND date '2026-04-03'
  AND (control_id LIKE '%festival%' OR control_id LIKE '%tech%' OR control_id LIKE '%event%'
       OR control_id LIKE '%节%' OR control_id LIKE '%actv%' OR control_id LIKE '%activity%')
GROUP BY control_id
ORDER BY users DESC
LIMIT 30
"""
try:
    rows = api.execute_sql(SQL1)
    for r in rows:
        print(f"  {r['control_id']:50s}  users: {r['users']:,}")
except Exception as e:
    print(f"❌ {e}")

# 2. 试一个更宽的搜索
print("\n=== 最热门 control_id top30 ===", flush=True)
SQL2 = """
SELECT control_id, COUNT(DISTINCT user_id) AS users
FROM v1041.ods_user_click
WHERE partition_date BETWEEN '2026-03-12' AND '2026-04-03'
  AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-03-13' AND date '2026-04-03'
GROUP BY control_id
ORDER BY users DESC
LIMIT 30
"""
try:
    rows2 = api.execute_sql(SQL2)
    for r in rows2:
        print(f"  {r['control_id']:50s}  users: {r['users']:,}")
except Exception as e:
    print(f"❌ {e}")
