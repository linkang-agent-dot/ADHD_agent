# -*- coding: utf-8 -*-
"""扩充付费分布曲线模块池，合并进 p2_dist.json。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, "p2_dist.json")
out = json.load(open(J, encoding="utf-8"))

PCTS = [0.001,0.005,0.01,0.02,0.03,0.05,0.075,0.10,0.15,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,1.00]
ARR = "ARRAY[" + ",".join(str(1-p) for p in PCTS) + "]"

P2_MORE = [
    ("P2春节·挖孔(28天)",     "2026-01-13", "2026-02-09", ["挖孔小游戏礼包"]),
    ("P2春节·MJ8(28天)",      "2026-01-13", "2026-02-09", ["MJ8小游戏"]),
    ("P2春节·钓鱼(28天)",     "2026-01-13", "2026-02-09", ["钓鱼活动礼包"]),
    ("P2拓荒·推币机(29天)",   "2026-05-12", "2026-06-09", ["推币机礼包","推币机随机GACHA礼包"]),
    ("P2深海·钓鱼(22天)",     "2026-06-10", "2026-07-01", ["钓鱼活动礼包"]),
    ("P2深海·限时抢购(22天)", "2026-06-10", "2026-07-01", ["限时抢购"]),
    ("P2深海·节日大富翁(22天)","2026-06-10", "2026-07-01", ["节日大富翁"]),
]
for label, s, e, weapons in P2_MORE:
    if label in out: continue
    names = ",".join(f"'{w}'" for w in weapons)
    sql = f"""
    SELECT count(1) buyers, round(avg(s),1) mean, round(max(s),0) mx, approx_percentile(s, {ARR}) q
    FROM (SELECT o.user_id, sum(o.pay_price) s
          FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
          WHERE i.iap_id_name IN ({names}) AND o.partition_date BETWEEN '{s}' AND '{e}'
          GROUP BY o.user_id)"""
    d = execute_sql(sql)["data"][0]
    out[label] = {"pcts": PCTS, "q": d["q"], "buyers": d["buyers"], "mean": d["mean"], "max": d["mx"]}
    print(label, d["buyers"], d["mean"], d["mx"])

SRV = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
X3_MORE = [
    ("X3深海·双通行证(D0-D6)", ["130035","130036","130037","130046"]),
    ("X3深海·许愿池单列(D0-D6)", ["1002001"]),
    ("X3深海·每日礼包(D0-D6)", None),  # 用名字匹配不了,ID未知→跳过
]
for label, ids in X3_MORE:
    if ids is None or label in out: continue
    idl = ",".join(f"'{i}'" for i in ids)
    sql = f"""
    SELECT count(1) buyers, round(avg(s),1) mean, round(max(s),0) mx, approx_percentile(s, {ARR}) q
    FROM (SELECT user_id, sum(CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END) s
          FROM v1090.ods_user_order
          WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09'
            AND server_id IN ({SRV}) AND iap_id IN ({idl})
          GROUP BY user_id)"""
    d = execute_sql(sql, datasource="TRINO_HF")["data"][0]
    out[label] = {"pcts": PCTS, "q": d["q"], "buyers": d["buyers"], "mean": d["mean"], "max": d["mx"]}
    print(label, d["buyers"], d["mean"], d["mx"])

json.dump(out, open(J, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total series:", len(out))
