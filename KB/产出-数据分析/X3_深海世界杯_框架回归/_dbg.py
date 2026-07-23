# -*- coding: utf-8 -*-
import sys, re
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
SRV=[1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010]
SF=f"server_id IN ({','.join(chr(39)+str(x)+chr(39) for x in SRV)})"
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
wl=re.findall(r'"(\d+)"', re.search(r'FALLBACK_PACK_IDS\s*=\s*\[(.*?)\]', open(r"C:\ADHD_agent\skills\x3-festival-monitor\x3_deepsea_daily.py",encoding="utf-8").read(), re.S).group(1))
print("wl 全list:", wl)
WL=",".join(f"'{p}'" for p in wl)
# A) 累充: 白名单买家 distinct
r=q(f"SELECT count(distinct user_id) u, count(1) o FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND {SF} AND iap_id IN ({WL})")[0]
print(f"A 白名单买家(SRV59): {r['u']}人 {r['o']}单")
# B) 已知大包 130036 单独
r=q(f"SELECT count(distinct user_id) u FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND {SF} AND iap_id='130036'")[0]
print(f"B 130036单独买家: {r['u']}")
# C) 酒馆跨服: 不加server过滤, 每阶段人数
r=q("""SELECT activity_step st, count(distinct user_id) u FROM v1090.ods_user_activity
  WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-12' AND activity_type='4'
  AND attribute1 LIKE '%"activityCfgID":10071704%' GROUP BY activity_step ORDER BY st""")
print("C 酒馆各阶段(全服无过滤):", [(x['st'],x['u']) for x in r])
# D) 酒馆 stepScore regexp 抽取验证(全服 step1)
r=q("""SELECT count(1) n, count(regexp_extract(attribute1,'"stepScore":(\d+)',1)) hascore,
  approx_percentile(cast(regexp_extract(attribute1,'"stepScore":(\d+)',1) as bigint),0.5) p50
  FROM v1090.ods_user_activity WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-12'
  AND activity_type='4' AND attribute1 LIKE '%"activityCfgID":10071704%' AND activity_step=1""")[0]
print(f"D 酒馆step1(全服): 行{r['n']} 有score{r['hascore']} p50分{r['p50']}")
