# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
S,E="2026-07-03","2026-07-16"
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV=",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
def q(sql,l=50): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
# 列名
cols=q("SELECT * FROM v1090.ods_user_asset LIMIT 1")
print("ods_user_asset 列:", list(cols[0].keys()) if cols else "空")
# 宝珠1201 总产出+消耗
r=q(f"""SELECT
  sum(CASE WHEN change_type='1' THEN TRY_CAST(change_count AS INTEGER) ELSE 0 END) got,
  sum(CASE WHEN change_type='2' THEN TRY_CAST(change_count AS INTEGER) ELSE 0 END) used,
  count(distinct CASE WHEN change_type='1' THEN user_id END) got_u
 FROM v1090.ods_user_asset WHERE asset_id='Item_1201'
 AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}'""")[0]
print(f"\n深海宝珠1201: 产出 {r['got']:,} / 消耗 {r['used']:,} / 产出人数 {r['got_u']:,}")
# 转盘模块付费(连锁211022-30 + 藏宝图锚点1302x + 转盘BP130035/046 + 许愿池1002001)
WHEEL={"转盘连锁":[str(x) for x in range(211022,211031)],
       "藏宝图锚点":["13021","13022","13023","13024","130210","130211","130212","130213","130214"],
       "转盘BP":["130035","130046"]}
for name,ids in WHEEL.items():
    idl=",".join("'"+x+"'" for x in ids)
    d=q(f"""SELECT round(sum({USD}),0) sp, count(distinct user_id) u, count(*) o
      FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}'
      AND server_id IN ({SRV}) AND iap_id IN ({idl})""")[0]
    print(f"  {name:<10} 付费${d['sp'] or 0:>8,.0f}  {d['u'] or 0}人  {d['o'] or 0}单")
