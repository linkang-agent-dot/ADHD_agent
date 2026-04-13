# -*- coding: utf-8 -*-
"""
通过节日礼包日收入分布，自动识别各节日实际上线/下线日期
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

SQL = """
SELECT
    date(date_add('hour',-8,b1.created_at)) AS pay_date,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price, created_at
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2025-09-01' AND '2026-04-05'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY date(date_add('hour',-8,b1.created_at))
ORDER BY pay_date
"""

print("查询节日礼包整体日收入...", flush=True)
rows = api.execute_sql(SQL)
print(f"共 {len(rows)} 天有数据\n")

# 找出各节日活跃期（日收入 > 5000 认为是节日在线）
days = [(r['pay_date'], float(r.get('revenue', 0))) for r in rows]

THRESHOLD = 5000  # 日收入阈值
print(f"所有活跃日（日收入>${THRESHOLD:,}）：")
clusters = []
cur_cluster = []
for day, rev in days:
    if rev >= THRESHOLD:
        cur_cluster.append((day, rev))
    else:
        if cur_cluster:
            clusters.append(cur_cluster)
            cur_cluster = []
if cur_cluster:
    clusters.append(cur_cluster)

for i, cluster in enumerate(clusters):
    start = cluster[0][0]
    end = cluster[-1][0]
    total = sum(r for _, r in cluster)
    days_n = len(cluster)
    print(f"\n[节日 {i+1}]  {start} ~ {end}  ({days_n}天)  总 ${total:,.0f}")
    peak_day, peak_rev = max(cluster, key=lambda x: x[1])
    print(f"         峰值: {peak_day} ${peak_rev:,.0f}")
    for day, rev in cluster:
        bar = '▓' * int(rev / 5000)
        print(f"         {day}  ${rev:>9,.0f}  {bar}")
