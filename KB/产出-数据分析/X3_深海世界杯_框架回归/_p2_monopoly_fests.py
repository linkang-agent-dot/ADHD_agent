# -*- coding: utf-8 -*-
"""P2 三节「节日大富翁」同形式参照（用户 07-20 定：春节异族大富翁形式不同不可比，换情人/科技/拓荒）：
每窗 = buyers/rev/orders/max + survival(同 _ds_monopoly_dist 阈值) + 按包名分件。
族包名（同一玩法形式）：节日大富翁 / 节日大富翁礼包 / 节日大富翁组队礼包 / 2025复活节大富翁礼包(历史复用名)。
排除：异族大富翁*(春节特有形式) / 战装大富翁(常驻非节日)。
产出 _p2_monopoly_fests.json。
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["节日大富翁", "节日大富翁礼包", "节日大富翁组队礼包", "2025复活节大富翁礼包"]
ALLN = ",".join(f"'{w}'" for w in NAMES)
WINDOWS = [
    ("情人节", "2026-02-10", "2026-03-09"),
    ("科技节", "2026-03-12", "2026-04-08"),
    ("拓荒节", "2026-05-12", "2026-06-09"),
]
THRESH = [10, 20, 50, 100, 200, 300, 500, 1000]

def q(sql):
    return execute_sql(sql)["data"]

out = {"names": NAMES, "windows": {}}
for fest, S, E in WINDOWS:
    base = f"""FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
      WHERE i.iap_id_name IN ({ALLN}) AND o.partition_date BETWEEN '{S}' AND '{E}'"""
    w = {"window": f"{S}~{E}"}
    d = q(f"SELECT count(distinct o.user_id) buyers, round(sum(o.pay_price),0) rev, count(1) orders {base}")[0]
    w.update(buyers=d["buyers"], rev=float(d["rev"]), orders=d["orders"])
    surv_sel = ",".join(f"count_if(s>={t}) c{t}" for t in THRESH)
    d = q(f"""SELECT {surv_sel}, round(max(s),0) mx
      FROM (SELECT o.user_id, sum(o.pay_price) s {base} GROUP BY o.user_id)""")[0]
    w["max"] = float(d["mx"]); w["surv"] = {str(t): d[f"c{t}"] for t in THRESH}
    top = q(f"""SELECT round(s,0) s FROM (SELECT o.user_id, sum(o.pay_price) s {base} GROUP BY o.user_id)
      ORDER BY s DESC LIMIT 20""")
    w["top20"] = [float(r["s"]) for r in top]
    # 分件（按包名）
    w["components"] = {}
    rows = q(f"""SELECT i.iap_id_name nm, count(distinct o.user_id) buyers, round(sum(o.pay_price),0) rev,
      count(1) orders {base} GROUP BY 1 ORDER BY 3 DESC""")
    for r in rows:
        nm = r["nm"]; b = r["buyers"]; rev = float(r["rev"] or 0); o = r["orders"] or 0
        b1 = base.replace(ALLN, f"'{nm}'")
        mx = q(f"SELECT round(max(s),0) mx FROM (SELECT o.user_id, sum(o.pay_price) s {b1} GROUP BY o.user_id)")[0]
        w["components"][nm] = dict(buyers=b, rev=rev, orders=o, max=float(mx["mx"] or 0),
                                   arppu=rev / b if b else 0, opb=o / b if b else 0)
    out["windows"][fest] = w
    print(f"{fest} {S}~{E}: buyers {w['buyers']:,} rev ${w['rev']:,.0f} orders {w['orders']:,} max ${w['max']:,.0f}")
    print("  surv:", w["surv"])
    for nm, m in w["components"].items():
        print(f"  {nm}: ${m['rev']:,.0f} 买家{m['buyers']:,} ARPPU${m['arppu']:.1f} 复购{m['opb']:.1f}单 max${m['max']:,.0f}")

json.dump(out, open(os.path.join(HERE, "_p2_monopoly_fests.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _p2_monopoly_fests.json")
