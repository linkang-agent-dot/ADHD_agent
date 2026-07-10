# -*- coding: utf-8 -*-
"""双图桶：图A=$0-100每$10一档(+>$100尾)，图B=$100+每$100一档到$2k(+>$2k尾)。17系列。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))

# 图A: (0,10],(10,20]...(90,100], >100  → 11桶 a0..a10
A_BINS = [(i*10, (i+1)*10) for i in range(10)]
A_LABELS = [f"${lo}-{hi}" for lo, hi in A_BINS] + [">$100"]
# 图B: (100,200]...(1900,2000], >2000 → 20桶 b0..b19
B_BINS = [(100+i*100, 200+i*100) for i in range(19)]
B_LABELS = [f"${lo}-{hi}" if hi<1000 else f"${lo/1000:g}k-{hi/1000:g}k".replace("$0.", "$.") for lo, hi in B_BINS] + [">$2k"]

def expr():
    parts = []
    for i, (lo, hi) in enumerate(A_BINS):
        parts.append(f"sum(CASE WHEN s > {lo} AND s <= {hi} THEN 1 ELSE 0 END) a{i}")
    parts.append("sum(CASE WHEN s > 100 THEN 1 ELSE 0 END) a10")
    for i, (lo, hi) in enumerate(B_BINS):
        parts.append(f"sum(CASE WHEN s > {lo} AND s <= {hi} THEN 1 ELSE 0 END) b{i}")
    parts.append("sum(CASE WHEN s > 2000 THEN 1 ELSE 0 END) b19")
    return ", ".join(parts)

P2_CASES = [
    ("P2春节·异族大富翁(28天)", "2026-01-13","2026-02-09", ["2025异族大富翁","异族大富翁随机礼包"]),
    ("P2春节·挖孔(28天)",       "2026-01-13","2026-02-09", ["挖孔小游戏礼包"]),
    ("P2春节·MJ8(28天)",        "2026-01-13","2026-02-09", ["MJ8小游戏"]),
    ("P2春节·钓鱼(28天)",       "2026-01-13","2026-02-09", ["钓鱼活动礼包"]),
    ("P2拓荒·挖孔(29天)",       "2026-05-12","2026-06-09", ["挖孔礼包"]),
    ("P2拓荒·弹珠GACHA(29天)",  "2026-05-12","2026-06-09", ["升级版本弹珠GACHA礼包","升级版本弹珠随机GACHA礼包"]),
    ("P2拓荒·推币机(29天)",     "2026-05-12","2026-06-09", ["推币机礼包","推币机随机GACHA礼包"]),
    ("P2深海·猜酒杯(22天)",     "2026-06-10","2026-07-01", ["2026深海节-猜酒杯"]),
    ("P2深海·钓鱼(22天)",       "2026-06-10","2026-07-01", ["钓鱼活动礼包"]),
    ("P2深海·限时抢购(22天)",   "2026-06-10","2026-07-01", ["限时抢购"]),
    ("P2深海·节日大富翁(22天)", "2026-06-10","2026-07-01", ["节日大富翁"]),
]
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
X3_CASES = [
    ("X3深海·转盘族(D0-D6)", "2026-07-03","2026-07-09", "'211022','211024','211026','211028','211030','13021','13022','13023','13024','1002001'", f"server_id IN ({SRV59})"),
    ("X3深海·大富翁族(D0-D6)", "2026-07-03","2026-07-09", ",".join(f"'{i}'" for i in ["2801001","2801002","2801003","2801004","2801005","2801006","2801007","2801008","2801009","2801010","2801011","207104","207105","207106","207107","207108","207109","207110","207111","207112","280001"]), f"server_id IN ({SRV59})"),
    ("X3深海·双通行证(D0-D6)", "2026-07-03","2026-07-09", "'130035','130036','130037','130046'", f"server_id IN ({SRV59})"),
    ("X3深海·许愿池单列(D0-D6)", "2026-07-03","2026-07-09", "'1002001'", f"server_id IN ({SRV59})"),
    ("X3夏日·开箱族(D0-D6)", "2026-05-29","2026-06-04", "'210702','210704','210706','210708','210710','210712','210713','210714','210715'", "server_id BETWEEN '1000' AND '1870'"),
    ("X3深海·开箱(连锁+锚点)(D0-D6)", "2026-07-03","2026-07-09", "'211022','211024','211026','211028','211030','13021','13022','13023','13024'", f"server_id IN ({SRV59})"),
]

out = {"a_labels": A_LABELS, "b_labels": B_LABELS, "series": {}}
for label, s, e, weapons in P2_CASES:
    names = ",".join(f"'{w}'" for w in weapons)
    sql = f"""SELECT {expr()} FROM (
      SELECT o.user_id, sum(o.pay_price) s
      FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
      WHERE i.iap_id_name IN ({names}) AND o.partition_date BETWEEN '{s}' AND '{e}' GROUP BY o.user_id)"""
    d = execute_sql(sql)["data"][0]
    out["series"][label] = {"a": [d[f"a{i}"] for i in range(11)], "b": [d[f"b{i}"] for i in range(20)]}
    print(label, "A", out["series"][label]["a"], "Btail", sum(out["series"][label]["b"]))
for label, s, e, ids, sf in X3_CASES:
    sql = f"""SELECT {expr()} FROM (
      SELECT user_id, sum(CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END) s
      FROM v1090.ods_user_order
      WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND iap_id IN ({ids}) GROUP BY user_id)"""
    d = execute_sql(sql, datasource="TRINO_HF")["data"][0]
    out["series"][label] = {"a": [d[f"a{i}"] for i in range(11)], "b": [d[f"b{i}"] for i in range(20)]}
    print(label, "A", out["series"][label]["a"], "Btail", sum(out["series"][label]["b"]))

json.dump(out, open(os.path.join(HERE, "p2_buckets2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
