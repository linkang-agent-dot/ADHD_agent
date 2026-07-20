# -*- coding: utf-8 -*-
"""P2 春节异族大富翁（2026-01-13~02-09 28天）上限参照数据：
① 全窗 buyers/rev/orders/max + survival(同 _ds_monopoly_dist 阈值) + top20
② 固定 vs 随机双轨分件（2025异族大富翁 / 异族大富翁随机礼包）
③ 随机礼包按档位（pay_price）结构 + 顶档复购
产出 _p2_monopoly_cny.json。口径=跨游戏对比用占比（交接包铁律2）。
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
S, E = "2026-01-13", "2026-02-09"
NAMES = ["2025异族大富翁", "异族大富翁随机礼包"]
ALLN = ",".join(f"'{w}'" for w in NAMES)
THRESH = [10, 20, 50, 100, 200, 300, 500, 1000]

def q(sql):
    return execute_sql(sql)["data"]

base = f"""FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
  WHERE i.iap_id_name IN ({ALLN}) AND o.partition_date BETWEEN '{S}' AND '{E}'"""

out = {"window": f"{S}~{E}", "names": NAMES}

# ① 全窗 + survival + top20
d = q(f"""SELECT count(distinct o.user_id) buyers, round(sum(o.pay_price),0) rev, count(1) orders {base}""")[0]
out.update(buyers=d["buyers"], rev=float(d["rev"]), orders=d["orders"])
surv_sel = ",".join(f"count_if(s>={t}) c{t}" for t in THRESH)
d = q(f"""SELECT {surv_sel}, round(max(s),0) mx
  FROM (SELECT o.user_id, sum(o.pay_price) s {base} GROUP BY o.user_id)""")[0]
out["max"] = float(d["mx"]); out["surv"] = {str(t): d[f"c{t}"] for t in THRESH}
top = q(f"""SELECT round(s,0) s FROM (SELECT o.user_id, sum(o.pay_price) s {base} GROUP BY o.user_id)
  ORDER BY s DESC LIMIT 20""")
out["top20"] = [float(r["s"]) for r in top]
print(f"① 全窗 buyers {out['buyers']:,} rev ${out['rev']:,.0f} orders {out['orders']:,} max ${out['max']:,.0f}")
print("   surv:", out["surv"])

# ② 双轨分件
out["components"] = {}
for name in NAMES:
    b1 = base.replace(ALLN, f"'{name}'")
    d = q(f"""SELECT count(distinct o.user_id) buyers, round(sum(o.pay_price),0) rev, count(1) orders {b1}""")[0]
    mx = q(f"""SELECT round(max(s),0) mx FROM (SELECT o.user_id, sum(o.pay_price) s {b1} GROUP BY o.user_id)""")[0]
    b = d["buyers"]; rev = float(d["rev"] or 0); o = d["orders"] or 0
    out["components"][name] = dict(buyers=b, rev=rev, orders=o, max=float(mx["mx"] or 0),
                                   arppu=rev / b if b else 0, opb=o / b if b else 0)
    print(f"② {name}: ${rev:,.0f} 买家{b} ARPPU${rev/b if b else 0:.1f} 复购{o/b if b else 0:.1f}单 max${float(mx['mx'] or 0):,.0f}")

# ③ 档位结构（按 pay_price）× 双轨
out["tiers"] = {}
for name in NAMES:
    b1 = base.replace(ALLN, f"'{name}'")
    rows = q(f"""SELECT o.pay_price p, count(distinct o.user_id) buyers, count(1) orders,
      round(sum(o.pay_price),0) rev {b1} GROUP BY o.pay_price ORDER BY o.pay_price""")
    out["tiers"][name] = [dict(price=float(r["p"]), buyers=r["buyers"], orders=r["orders"],
                               rev=float(r["rev"]), opb=r["orders"] / r["buyers"]) for r in rows]
    print(f"③ {name} 档位:")
    for t in out["tiers"][name]:
        print(f"   ${t['price']:>6.2f}: 买家{t['buyers']:>5} 单数{t['orders']:>6} 人均{t['opb']:.1f}单 ${t['rev']:,.0f}")

json.dump(out, open(os.path.join(HERE, "_p2_monopoly_cny.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _p2_monopoly_cny.json")
