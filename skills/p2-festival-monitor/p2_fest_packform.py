# -*- coding: utf-8 -*-
"""P2 节日深挖复用脚本B（同案固化）：头部武器价位结构+复购率（礼包形式层）。改 FESTS/WEAPONS 即复用。"""
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
WEAPONS = ["挖孔小游戏礼包","挖孔礼包","2025异族大富翁","异族大富翁随机礼包","钓鱼活动礼包",
           "2026深海节-猜酒杯","升级版本弹珠随机GACHA礼包","升级版本弹珠GACHA礼包","机甲GACHA",
           "推币机礼包","推币机随机GACHA礼包","MJ8小游戏","一番赏GACHA礼包","限时抢购",
           "节日大富翁","2025深海节本体GACHA礼包","2025深海节本体GACHA随机礼包","春节抽奖成就礼包"]
names = ",".join(f"'{w}'" for w in WEAPONS)

results = {}
for name, s, e in FESTS:
    sql = f"""
    SELECT i.iap_id_name nm, i.iap_price price,
           round(sum(o.pay_price),0) rev, count(1) orders, count(distinct o.user_id) buyers
    FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
    WHERE i.iap_type='混合-节日活动' AND o.partition_date BETWEEN '{s}' AND '{e}'
      AND i.iap_id_name IN ({names})
    GROUP BY 1,2 ORDER BY 1, rev DESC
    """
    results[f"form_{name}"] = execute_sql(sql.strip(), limit=1000)

with open(os.path.join(HERE, "p2_3fest_form.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

for name, s, e in FESTS:
    rows = results[f"form_{name}"]["data"]
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows: by[r["nm"]].append(r)
    print(f"\n===== {name} =====")
    for nm, rs in sorted(by.items(), key=lambda kv: -sum(r["rev"] for r in kv[1])):
        tot = sum(r["rev"] for r in rs); ob = sum(r["orders"] for r in rs)
        allb = max(r["buyers"] for r in rs)  # 近似：跨价位买家有重叠，取各档明细自己看
        print(f"  ◆ {nm}  ${tot:,.0f}  orders={ob}")
        for r in sorted(rs, key=lambda x: -(x["rev"] or 0))[:6]:
            opb = r["orders"]/r["buyers"] if r["buyers"] else 0
            print(f"      ${r['price']!s:>6} × {r['orders']:>5}单 / {r['buyers']:>5}人 (人均{opb:4.1f}单)  ${r['rev']:>9,.0f}")
