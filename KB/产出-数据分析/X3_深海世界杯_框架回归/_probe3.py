# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
SRV59="1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010"
SF=f"server_id IN ({','.join(chr(39)+x+chr(39) for x in SRV59.split(','))})"
# 酒馆 cfg=10071704: 看 activity_step + activity_total_step + stepScore 范围(SRV59)
print("=== 酒馆 10071704 type=4 (SRV59): step/score 分布 ===")
r=q(f"""SELECT activity_step, count(distinct user_id) u FROM v1090.ods_user_activity
   WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-12' AND {SF} AND activity_type='4'
   AND attribute1 LIKE '%"activityCfgID":10071704%' GROUP BY activity_step ORDER BY activity_step LIMIT 20""")
print(" activity_step -> 人数:", [(x['activity_step'],x['u']) for x in r])
# 签到 cfg=101406 type=0: 每天人数(SRV59)
print("\n=== 签到 101406 type=0 (SRV59): 每天参与人数 ===")
r=q(f"""SELECT partition_date d, count(distinct user_id) u FROM v1090.ods_user_activity
   WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND {SF} AND activity_type='0'
   AND attribute1 LIKE '%"activityCfgID":101406%' GROUP BY partition_date ORDER BY partition_date""")
for x in r: print(f"  {x['d']}: {x['u']}人")
