# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
SF=f"server_id IN ({SRV59})"; USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
DP="iap_id IN ('800005','800006','800007','800008','800009')"
W="partition_date BETWEEN '2026-07-03' AND '2026-07-09'"
r=q(f"SELECT count(distinct user_id) b, count(1) o, round(sum({USD}),0) rev, round(max({USD}),0) mx FROM v1090.ods_user_order WHERE pay_status=1 AND {W} AND {SF} AND {DP}")[0]
print(f"每日礼包CLEAN(800005-009): 买家{r['b']} 单{r['o']} ${float(r['rev']):,.0f} max${float(r['mx']):,.0f}")
d=q(f"SELECT n,count(1) u FROM (SELECT user_id,count(distinct iap_id) n FROM v1090.ods_user_order WHERE pay_status=1 AND {W} AND {SF} AND {DP} GROUP BY user_id) GROUP BY n ORDER BY n")
print("按买到的第N日档数(5=买全=终奖候选):")
for x in d: print(f"  买{x['n']}档: {x['u']}人")
json.dump({"clean":{"buyers":r['b'],"orders":r['o'],"rev":float(r['rev']),"max":float(r['mx'])},"tier_dist":[{"n":x['n'],"u":x['u']} for x in d]}, open("_daily_clean.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
