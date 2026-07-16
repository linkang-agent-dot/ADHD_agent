# -*- coding: utf-8 -*-
"""
锚点礼包(B线)四代对比：元旦/情人/夏日/世界杯 合计 + 世界杯按档位
口径：无服过滤（与 _kaixiang_deep 一致）
产出 _anchor.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"

JOBS = {
  "元旦锚点":   ("2026-01-01", "2026-01-15", "'210512','210513','210514','210515'"),
  "情人节锚点": ("2026-02-06", "2026-02-16", "'210712','210713','210714','210715'"),
  "夏日锚点":   ("2026-05-29", "2026-06-08", "'210712','210713','210714','210715'"),
  "世界杯锚点": ("2026-06-26", END, "'211012','211013','211014','211015'"),
  "WC档$4.99":  ("2026-06-26", END, "'211012'"),
  "WC档$19.99": ("2026-06-26", END, "'211013'"),
  "WC档$49.99": ("2026-06-26", END, "'211014'"),
  "WC档$99.99": ("2026-06-26", END, "'211015'"),
}
out = {"END": END}
for label, (s, e, packs) in JOBS.items():
    d1 = execute_sql(f"""SELECT round(sum({USD}),0) rev, count(distinct user_id) buyers, count(1) orders
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND iap_id IN ({packs})""",
        datasource="TRINO_HF")["data"][0]
    r2 = execute_sql(f"""SELECT round(max(tot),0) mx FROM (SELECT user_id, sum({USD}) tot
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND iap_id IN ({packs})
        GROUP BY user_id) t""", datasource="TRINO_HF")
    mx = float((r2["data"][0]["mx"] if r2.get("data") else 0) or 0)
    rev = float(d1["rev"] or 0); b = d1["buyers"] or 0; o = d1["orders"] or 0
    out[label] = {"rev": rev, "buyers": b, "orders": o, "max": mx,
                  "arppu": rev/b if b else 0, "opb": o/b if b else 0}
    print(f"{label:10s} ${rev:>7,.0f}  买家{b:>4}  ARPPU${out[label]['arppu']:6.1f}  复购{out[label]['opb']:4.1f}  max${mx:,.0f}")

json.dump(out, open(os.path.join(HERE, "_anchor.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _anchor.json")
