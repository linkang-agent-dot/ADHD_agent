# -*- coding: utf-8 -*-
"""
开箱付费率下钻：为什么世界杯(9.6%)低于夏日(20.3%)
① 逐服总付费人数（两窗）→ 同服段对齐付费率 + WC老服/扩服拆分
② 两代按档位(包id)买家 → 入口结构
产出 _kx_payrate.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
out = {"END": END}

SM = dict(s="2026-05-29", e="2026-06-08", packs="'210702','210704','210706','210708','210710','210712','210713','210714','210715'")
WCC = dict(s="2026-06-26", e=END, packs="'211002','211004','211006','211008','211010','211012','211013','211014','211015'")

# ① 逐服：该窗总付费人数 + 开箱买家
for label, c in [("夏日", SM), ("世界杯", WCC)]:
    rows = execute_sql(f"""SELECT server_id sid, count(distinct user_id) payers
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}'
        GROUP BY server_id""", datasource="TRINO_HF")["data"]
    out[f"{label}_payers"] = {r["sid"]: r["payers"] for r in rows}
    rows = execute_sql(f"""SELECT server_id sid, count(distinct user_id) kb
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}'
        AND iap_id IN ({c['packs']}) GROUP BY server_id""", datasource="TRINO_HF")["data"]
    out[f"{label}_kxbuyers"] = {r["sid"]: r["kb"] for r in rows}

# ② 档位结构
for label, c in [("夏日", SM), ("世界杯", WCC)]:
    rows = execute_sql(f"""SELECT iap_id, count(distinct user_id) b, round(sum({USD}),0) rev, count(1) o
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}'
        AND iap_id IN ({c['packs']}) GROUP BY iap_id ORDER BY iap_id""", datasource="TRINO_HF")["data"]
    out[f"{label}_tiers"] = [dict(iap=r["iap_id"], buyers=r["b"], rev=float(r["rev"]), orders=r["o"]) for r in rows]
    print(f"{label} 档位:", [(r['iap_id'], r['b']) for r in rows])

# 汇总口径
def agg(label, sid_lo, sid_hi):
    P = out[f"{label}_payers"]; K = out[f"{label}_kxbuyers"]
    pay = sum(v for k, v in P.items() if sid_lo <= int(k) <= sid_hi)
    kb = sum(v for k, v in K.items() if sid_lo <= int(k) <= sid_hi)
    return kb, pay, kb/pay*100 if pay else 0

print("\n== 同服段对齐付费率 ==")
for label in ["夏日", "世界杯"]:
    kb, pay, pr = agg(label, 1000, 1870)
    print(f"{label} 成熟段1000-1870: 开箱买家{kb} / 总付费{pay:,} = {pr:.1f}%")
kb, pay, pr = agg("世界杯", 1880, 1970); print(f"世界杯 1880-1970: {kb}/{pay:,} = {pr:.1f}%")
kb, pay, pr = agg("世界杯", 1980, 2250); print(f"世界杯 扩服1980-2250: {kb}/{pay:,} = {pr:.1f}%")

json.dump(out, open(os.path.join(HERE, "_kx_payrate.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _kx_payrate.json")
