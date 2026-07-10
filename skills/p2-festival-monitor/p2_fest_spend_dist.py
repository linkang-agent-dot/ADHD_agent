# -*- coding: utf-8 -*-
"""武器级付费分布曲线数据：每个武器 = 活动内每买家付费额的分位数组（gacha回归同款图）。
横轴=买家百分位(按付费额降序) 纵轴=付费额度。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
# 分位点：细化头部（top1/2/5/10...）
PCTS = [0.001,0.005,0.01,0.02,0.03,0.05,0.075,0.10,0.15,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,1.00]
ARR = "ARRAY[" + ",".join(str(1-p) for p in PCTS) + "]"   # top-p% == quantile(1-p)

P2_CASES = [
    ("P2深海·猜酒杯(22天)",   "2026-06-10", "2026-07-01", ["2026深海节-猜酒杯"]),
    ("P2拓荒·挖孔(29天)",     "2026-05-12", "2026-06-09", ["挖孔礼包"]),
    ("P2拓荒·弹珠GACHA(29天)","2026-05-12", "2026-06-09", ["升级版本弹珠GACHA礼包","升级版本弹珠随机GACHA礼包"]),
    ("P2春节·异族大富翁(28天)","2026-01-13", "2026-02-09", ["2025异族大富翁","异族大富翁随机礼包"]),
]

out = {}
for label, s, e, weapons in P2_CASES:
    names = ",".join(f"'{w}'" for w in weapons)
    sql = f"""
    SELECT count(1) buyers, round(avg(s),1) mean, round(max(s),0) mx,
           approx_percentile(s, {ARR}) q
    FROM (SELECT o.user_id, sum(o.pay_price) s
          FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
          WHERE i.iap_id_name IN ({names}) AND o.partition_date BETWEEN '{s}' AND '{e}'
          GROUP BY o.user_id)
    """
    d = execute_sql(sql)["data"][0]
    out[label] = {"pcts": PCTS, "q": d["q"], "buyers": d["buyers"], "mean": d["mean"], "max": d["mx"]}
    print(label, "buyers", d["buyers"], "mean", d["mean"], "max", d["mx"])

# X3 侧
SRV = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
X3_CASES = [
    ("X3深海·转盘族(D0-D6)", ["211022","211024","211026","211028","211030","13021","13022","13023","13024","1002001"]),
    ("X3深海·大富翁族(D0-D6)", ["2801001","2801002","2801003","2801004","2801005","2801006","2801007","2801008","2801009","2801010","2801011","207104","207105","207106","207107","207108","207109","207110","207111","207112","280001"]),
]
for label, ids in X3_CASES:
    idl = ",".join(f"'{i}'" for i in ids)
    sql = f"""
    SELECT count(1) buyers, round(avg(s),1) mean, round(max(s),0) mx,
           approx_percentile(s, {ARR}) q
    FROM (SELECT user_id, sum(CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END) s
          FROM v1090.ods_user_order
          WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09'
            AND server_id IN ({SRV}) AND iap_id IN ({idl})
          GROUP BY user_id)
    """
    d = execute_sql(sql, datasource="TRINO_HF")["data"][0]
    out[label] = {"pcts": PCTS, "q": d["q"], "buyers": d["buyers"], "mean": d["mean"], "max": d["mx"]}
    print(label, "buyers", d["buyers"], "mean", d["mean"], "max", d["mx"])

with open(os.path.join(HERE, "p2_dist.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved p2_dist.json")
for label, v in out.items():
    pts = ", ".join(f"top{p*100:g}%=${q:,.0f}" for p, q in list(zip(v["pcts"], v["q"]))[:8])
    print(f"{label}: {pts}")
