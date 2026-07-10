# -*- coding: utf-8 -*-
"""P2 节日深挖复用脚本A（2026-07-09 三大节拉通案固化）：节日×礼包全量 + 周弹药带 + 窗口大盘。改 FESTS 即换节日。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
FESTS = [
    ("春节",   "2026-01-13", "2026-02-09"),
    ("拓荒节", "2026-05-12", "2026-06-09"),
    ("深海节", "2026-06-10", "2026-07-01"),
]

def q(sql, limit=1000):
    return execute_sql(sql.strip().rstrip(";"), limit=limit)

results = {}

# A) 各节日 × 礼包 全量（收入+买家）
for name, s, e in FESTS:
    sql = f"""
    SELECT i.iap_id_name nm, i.iap_type2 t2,
           round(sum(o.pay_price),0) rev, count(distinct o.user_id) buyers
    FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
    WHERE i.iap_type='混合-节日活动' AND o.partition_date BETWEEN '{s}' AND '{e}'
    GROUP BY 1,2 ORDER BY rev DESC
    """
    results[f"packs_{name}"] = q(sql)

# B) 各节日 × 周 × 礼包（弹药带）
for name, s, e in FESTS:
    sql = f"""
    SELECT floor(date_diff('day', date '{s}', date(o.partition_date)) / 7) wk,
           i.iap_id_name nm, round(sum(o.pay_price),0) rev
    FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
    WHERE i.iap_type='混合-节日活动' AND o.partition_date BETWEEN '{s}' AND '{e}'
    GROUP BY 1,2 ORDER BY 1, rev DESC
    """
    results[f"weekly_{name}"] = q(sql)

# C) 各节日窗口大盘（总付费额/人）供占比与ARPU
for name, s, e in FESTS:
    sql = f"""
    SELECT round(sum(o.pay_price),0) total_rev, count(distinct o.user_id) payers
    FROM v1041.dl_user_order o
    WHERE o.partition_date BETWEEN '{s}' AND '{e}'
    """
    results[f"total_{name}"] = q(sql)

with open(os.path.join(HERE, "p2_3fest_full.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("saved p2_3fest_full.json")
for name, s, e in FESTS:
    packs = results[f"packs_{name}"]["data"]
    tot = results[f"total_{name}"]["data"][0]
    fest_rev = sum(r["rev"] for r in packs)
    print(f"\n===== {name} {s}~{e}  节日${fest_rev:,.0f} / 大盘${tot['total_rev']:,.0f} ({fest_rev/tot['total_rev']*100:.0f}%) / 付费{tot['payers']:,}人 =====")
    for r in packs[:22]:
        print(f"  {r['rev']:>9,.0f}  {r['buyers']:>5}  [{(r['t2'] or '').replace('混合-节日活动-','')}] {r['nm']}")
