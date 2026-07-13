# -*- coding: utf-8 -*-
"""X3 六系列窗口 D0-D6 → D0-D10 重查：双图桶(A/B) + 分位统计，写回两份 json（新 key 带 D0-D10）。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

SC = r'C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\4320db8b-832c-417d-98a5-f5ada22cbf14\scratchpad'
PCTS = [0.001,0.005,0.01,0.02,0.03,0.05,0.075,0.10,0.15,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,1.00]
ARR = "ARRAY[" + ",".join(str(1-p) for p in PCTS) + "]"
A_BINS = [(i*10,(i+1)*10) for i in range(10)]
B_BINS = [(100+i*100,200+i*100) for i in range(19)]

def expr():
    parts=[]
    for i,(lo,hi) in enumerate(A_BINS): parts.append(f"sum(CASE WHEN s > {lo} AND s <= {hi} THEN 1 ELSE 0 END) a{i}")
    parts.append("sum(CASE WHEN s > 100 THEN 1 ELSE 0 END) a10")
    for i,(lo,hi) in enumerate(B_BINS): parts.append(f"sum(CASE WHEN s > {lo} AND s <= {hi} THEN 1 ELSE 0 END) b{i}")
    parts.append("sum(CASE WHEN s > 2000 THEN 1 ELSE 0 END) b19")
    return ", ".join(parts)

SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
DS = ("2026-07-03","2026-07-13")   # 深海 D0-D10（7/13 未完整/可能T+1）
XR = ("2026-05-29","2026-06-08")   # 夏日 D0-D10 = 全活动

CASES = [
    ("X3深海·转盘族(D0-D10)", DS, "'211022','211024','211026','211028','211030','13021','13022','13023','13024','1002001'", f"server_id IN ({SRV59})"),
    ("X3深海·大富翁族(D0-D10)", DS, ",".join(f"'{i}'" for i in ["2801001","2801002","2801003","2801004","2801005","2801006","2801007","2801008","2801009","2801010","2801011","207104","207105","207106","207107","207108","207109","207110","207111","207112","280001"]), f"server_id IN ({SRV59})"),
    ("X3深海·双通行证(D0-D10)", DS, "'130035','130036','130037','130046'", f"server_id IN ({SRV59})"),
    ("X3深海·许愿池单列(D0-D10)", DS, "'1002001'", f"server_id IN ({SRV59})"),
    ("X3夏日·开箱族(D0-D10全活动)", XR, "'210702','210704','210706','210708','210710','210712','210713','210714','210715'", "server_id BETWEEN '1000' AND '1870'"),
    ("X3深海·开箱(连锁+锚点)(D0-D10)", DS, "'211022','211024','211026','211028','211030','13021','13022','13023','13024'", f"server_id IN ({SRV59})"),
]

buck = json.load(open(SC+r'\p2_buckets2.json',encoding='utf-8'))
dist = json.load(open(SC+r'\p2_dist.json',encoding='utf-8'))
# 删旧 X3 key
for j in (buck["series"], dist):
    for k in [k for k in list(j) if str(k).startswith("X3")]: del j[k]

for label,(s,e),ids,sf in CASES:
    base = f"""FROM (SELECT user_id, sum(CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END) s
      FROM v1090.ods_user_order
      WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND iap_id IN ({ids})
      GROUP BY user_id)"""
    d1 = execute_sql(f"SELECT {expr()} {base}", datasource="TRINO_HF")["data"][0]
    buck["series"][label] = {"a":[d1[f"a{i}"] for i in range(11)], "b":[d1[f"b{i}"] for i in range(20)]}
    d2 = execute_sql(f"SELECT count(1) buyers, round(avg(s),1) mean, round(max(s),0) mx, approx_percentile(s,{ARR}) q {base}", datasource="TRINO_HF")["data"][0]
    dist[label] = {"pcts":PCTS, "q":d2["q"], "buyers":d2["buyers"], "mean":d2["mean"], "max":d2["mx"]}
    print(label, "buyers",d2["buyers"], "mean",d2["mean"], "max",d2["mx"], "| A",buck["series"][label]["a"])

json.dump(buck, open(SC+r'\p2_buckets2.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(dist, open(SC+r'\p2_dist.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("saved both json")
