# -*- coding: utf-8 -*-
"""
查 dim_iap 中节日相关 iap_type 分布
"""
import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

SQL = r"""
SELECT
    iap_type,
    COUNT(*) AS cnt
FROM v1041.dim_iap
WHERE iap_type LIKE '%\u6df7\u5408%'
   OR iap_type LIKE '%festival%'
GROUP BY iap_type
ORDER BY cnt DESC
"""

# Simpler: just get all distinct iap_type
SQL2 = """
SELECT DISTINCT iap_type
FROM v1041.dim_iap
ORDER BY iap_type
"""

result = api.execute_sql(SQL2)
rows = result.get('data', {}).get('rows', [])
print(f"Total distinct iap_type: {len(rows)}")
for r in rows:
    t = r[0] if isinstance(r, list) else r.get('iap_type', r)
    print(repr(t))
