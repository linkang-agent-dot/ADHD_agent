# -*- coding: utf-8 -*-
"""
查 dim_iap 的 iap_type2~type8 分类字段，看有没有更精确的子活动分类
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 查节日活动礼包的 type2 分布
for col in ['iap_type2', 'iap_type3', 'iap_type4', 'iap_type5']:
    print(f"\n=== {col} 分布 ===", flush=True)
    SQL = f"""
    SELECT {col}, COUNT(*) AS cnt
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
      AND {col} IS NOT NULL AND {col} != ''
    GROUP BY {col}
    ORDER BY cnt DESC
    LIMIT 30
    """
    rows = api.execute_sql(SQL)
    for r in rows:
        print(f"  {r[col]:50s}  {r['cnt']:>4}")
