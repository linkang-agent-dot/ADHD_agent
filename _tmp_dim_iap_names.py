# -*- coding: utf-8 -*-
"""
查"其他礼包"里的具体名称和 iap_type2 分类
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 查所有在近6个月有收入的节日活动礼包名称 + type2
SQL = """
SELECT
    b2.iap_id_name,
    b2.iap_type2,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue,
    COUNT(DISTINCT b1.user_id) AS buyers
FROM (
    SELECT user_id, iap_id, pay_price
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2025-10-01' AND '2026-04-05'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name, iap_type2
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, b2.iap_type2
HAVING SUM(b1.pay_price) > 5000
ORDER BY revenue DESC
"""

print("查询所有有收入的节日礼包（按 type2 + 名称）...", flush=True)
rows = api.execute_sql(SQL)
print(f"共 {len(rows)} 条（收入>$5K）\n")

# 按 iap_type2 分组显示
by_type2 = {}
for r in rows:
    t2 = r.get('iap_type2', '') or '(空)'
    if t2 not in by_type2:
        by_type2[t2] = []
    by_type2[t2].append(r)

for t2, items in sorted(by_type2.items(), key=lambda x: -sum(float(i['revenue']) for i in x[1])):
    total = sum(float(i['revenue']) for i in items)
    print(f"\n{'='*60}")
    print(f"[{t2}]  总计 ${total:,.0f}  ({len(items)} 种礼包)")
    print(f"{'='*60}")
    for r in items:
        name = r['iap_id_name']
        rev = float(r['revenue'])
        buyers = int(r['buyers'])
        print(f"  ${rev:>10,.0f}  {buyers:>5,}人  {name}")
