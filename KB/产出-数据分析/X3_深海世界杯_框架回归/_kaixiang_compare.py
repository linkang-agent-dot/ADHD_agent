# -*- coding: utf-8 -*-
"""
开箱三代对打数据：情人节(2/6-2/16·2107xx) / 夏日(5/29-6/8·复用2107xx) / 世界杯(6/26-END·211xxx)
每代: 连锁/锚点/合并 L1 + max + 溢出率($100+买家占比) + p50/p90
产出 _kaixiang.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"

def ids(*xs): return ",".join(f"'{x}'" for x in xs)

GENS = {
  "情人节开箱(致她的信)": dict(s="2026-02-06", e="2026-02-16", sf="server_id BETWEEN '1000' AND '1540'",
    chain=ids(210702,210704,210706,210708,210710), anchor=ids(210712,210713,210714,210715)),
  "夏日开箱(复用情人包)": dict(s="2026-05-29", e="2026-06-08", sf="server_id BETWEEN '1000' AND '1870'",
    chain=ids(210702,210704,210706,210708,210710), anchor=ids(210712,210713,210714,210715)),
  "世界杯开箱(福箱)": dict(s="2026-06-26", e=END, sf="server_id BETWEEN '1000' AND '2250'",
    chain=ids(211002,211004,211006,211008,211010), anchor=ids(211012,211013,211014,211015)),
}

out = {"END": END}
for gen, c in GENS.items():
    s, e, sf = c["s"], c["e"], c["sf"]
    out[gen] = {"window": f"{s}~{e}"}
    for part, pred in [("连锁", c["chain"]), ("锚点", c["anchor"]), ("合并", c["chain"] + "," + c["anchor"])]:
        cond = f"iap_id IN ({pred})"
        d1 = execute_sql(f"""SELECT round(sum({USD}),0) rev, count(distinct user_id) buyers, count(1) orders
            FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}""",
            datasource="TRINO_HF")["data"][0]
        d2 = execute_sql(f"""SELECT round(max(tot),0) mx, count_if(tot>=100) over100, count_if(tot>=500) over500,
              round(approx_percentile(tot, 0.5),0) p50, round(approx_percentile(tot, 0.9),0) p90
            FROM (SELECT user_id, sum({USD}) tot FROM v1090.ods_user_order
              WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}
              GROUP BY user_id) t""", datasource="TRINO_HF")["data"][0]
        rev = float(d1["rev"] or 0); b = d1["buyers"] or 0; o = d1["orders"] or 0
        m = {"rev": rev, "buyers": b, "orders": o,
             "arppu": rev/b if b else 0, "opb": o/b if b else 0,
             "max": float(d2["mx"] or 0), "p50": float(d2["p50"] or 0), "p90": float(d2["p90"] or 0),
             "over100": (d2["over100"] or 0)/b*100 if b else 0, "over500": (d2["over500"] or 0)/b*100 if b else 0}
        out[gen][part] = m
        print(f"{gen} {part:3s} ${rev:>8,.0f} 买家{b:>4} ARPPU${m['arppu']:6.1f} 复购{m['opb']:4.1f} "
              f"p50${m['p50']:>4,.0f} p90${m['p90']:>4,.0f} 溢出100 {m['over100']:4.1f}% 溢出500 {m['over500']:4.1f}% max${m['max']:,.0f}")

json.dump(out, open(os.path.join(HERE, "_kaixiang.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _kaixiang.json")
