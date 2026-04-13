# -*- coding: utf-8 -*-
"""
诊断：查挖孔小游戏礼包按日收入，反推各节日实际日期范围
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 1. 查挖孔礼包近5个月的日收入（按天聚合）
SQL = """
SELECT
    date(date_add('hour',-8,b1.created_at)) AS pay_date,
    COUNT(DISTINCT b1.user_id) AS buyers,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price, created_at
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2025-10-01' AND '2026-04-05'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name
    FROM v1041.dim_iap
    WHERE iap_id_name LIKE '%挖孔%'
      AND iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY date(date_add('hour',-8,b1.created_at))
ORDER BY pay_date
"""

print("正在查询挖孔小游戏礼包历史日收入...", flush=True)
rows = api.execute_sql(SQL)
print(f"共 {len(rows)} 天有收入")
print()

# 找出活跃期（日收入 > 1000 认为是节日期间）
active_days = [(r['pay_date'], float(r['revenue'])) for r in rows if float(r.get('revenue',0)) > 1000]
print("活跃日（收入>$1000）：")
for day, rev in active_days:
    bar = '█' * int(rev / 2000)
    print(f"  {day}  ${rev:>8,.0f}  {bar}")

print()
print("完整数据（月合计）：")
month_agg = {}
for r in rows:
    m = str(r['pay_date'])[:7]
    month_agg[m] = month_agg.get(m, 0) + float(r.get('revenue', 0))
for m, rev in sorted(month_agg.items()):
    print(f"  {m}  ${rev:>10,.0f}")
