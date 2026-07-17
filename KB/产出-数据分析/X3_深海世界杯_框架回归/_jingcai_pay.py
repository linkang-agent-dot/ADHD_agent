# -*- coding: utf-8 -*-
"""竞猜基本付费分析：894全档 + 通行证(参照) 的完整指标（p50/p90/溢出/max/付费率分母）→ _jingcai_pay.json"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
S, E = "2026-06-26", END
out = {"END": END}

JOBS = {
  "竞猜894全档": "iap_id LIKE '894%'",
  "通行证": "iap_id IN ('130020','130021')",
}
for label, cond in JOBS.items():
    d = execute_sql(f"""SELECT count(1) buyers, round(sum(tot),0) rev, round(sum(o),0) orders,
          round(max(tot),0) mx, approx_percentile(tot, ARRAY[0.5,0.9]) q,
          count_if(tot>=100) over100, count_if(tot>=500) over500
        FROM (SELECT user_id, sum({USD}) tot, count(1) o FROM v1090.ods_user_order
          WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}' AND {cond}
          GROUP BY user_id) t""", datasource="TRINO_HF")["data"][0]
    dp = execute_sql(f"""SELECT count(distinct user_id) payers FROM v1090.ods_user_order
        WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}'
        AND server_id IN (SELECT distinct server_id FROM v1090.ods_user_order
            WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}' AND {cond})""",
        datasource="TRINO_HF")["data"][0]
    q = d["q"] if isinstance(d["q"], list) else json.loads(str(d["q"]))
    b = d["buyers"] or 0
    out[label] = {"rev": float(d["rev"] or 0), "buyers": b, "orders": int(d["orders"] or 0),
                  "max": float(d["mx"] or 0), "p50": float(q[0]), "p90": float(q[1]),
                  "over100": (d["over100"] or 0)/b*100 if b else 0, "over500": (d["over500"] or 0)/b*100 if b else 0,
                  "total_payers": dp["payers"], "payrate": b/dp["payers"]*100 if dp["payers"] else 0}
    m = out[label]
    print(f"{label}: ${m['rev']:,.0f} 买家{b} 付费率{m['payrate']:.1f}%(/{m['total_payers']:,}) ARPPU${m['rev']/b:.1f} 复购{m['orders']/b:.1f} p50${m['p50']:.0f} p90${m['p90']:.0f} 100+{m['over100']:.1f}% 500+{m['over500']:.1f}% max${m['max']:,.0f}")

json.dump(out, open(os.path.join(HERE, "_jingcai_pay.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _jingcai_pay.json")
