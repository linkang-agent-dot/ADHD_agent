# -*- coding: utf-8 -*-
"""形式对比·统一服段口径：世界杯4形式限深海59服段(SRV59=1170-2010)，窗口=世界杯窗 6/26-END → _jc_form_ds59.json
目的=ARPU排位图统一用深海服段分母（用户07-21定：新服+老服整体口径与深海59服不可比）
用法: python _jc_form_ds59.py [END日]"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-16"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
S, E = "2026-06-26", END
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
SRV = f"server_id IN ({SRV59})"
out = {"END": END, "seg": "深海59服段(1170-2010)"}

def ids(*xs): return ",".join(f"'{x}'" for x in xs)
JOBS = {
  "竞猜894全档": "iap_id LIKE '894%'",
  "开箱福箱连锁": f"iap_id IN ({ids(211002,211004,211006,211008,211010)})",
  "开箱券锚点(可复购)": f"iap_id IN ({ids(211012,211013,211014,211015)})",
  "通行证(130020/21)": "iap_id IN ('130020','130021')",
}
dp = execute_sql(f"""SELECT count(distinct user_id) payers FROM v1090.ods_user_order
    WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}' AND {SRV}""",
    datasource="TRINO_HF")["data"][0]
out["payers"] = dp["payers"]
print(f"深海59服段 世界杯窗总付费 {dp['payers']:,} 人")
for label, cond in JOBS.items():
    d = execute_sql(f"""SELECT count(1) buyers, round(sum(tot),0) rev, round(sum(o),0) orders, round(max(tot),0) mx
        FROM (SELECT user_id, sum({USD}) tot, count(1) o FROM v1090.ods_user_order
          WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}' AND {SRV} AND {cond}
          GROUP BY user_id) t""", datasource="TRINO_HF")["data"][0]
    b = d["buyers"] or 0
    out[label] = {"rev": float(d["rev"] or 0), "buyers": b, "orders": int(d["orders"] or 0),
                  "max": float(d["mx"] or 0), "opb": (d["orders"] or 0)/b if b else 0,
                  "arppu": float(d["rev"] or 0)/b if b else 0}
    m = out[label]
    print(f"{label}: ${m['rev']:,.0f} 买家{b} ARPU${m['rev']/dp['payers']:.2f} ARPPU${m['arppu']:.1f} 复购{m['opb']:.1f} max${m['max']:,.0f}")

json.dump(out, open(os.path.join(HERE, "_jc_form_ds59.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _jc_form_ds59.json")
