# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
S,E="2026-07-03","2026-07-16"
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV=",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
MONO=[f"280100{i}" for i in range(1,10)]+["2801010","2801011"]+[str(x) for x in range(207104,207113)]+["280001","130036","130037"]
idl=",".join("'"+x+"'" for x in MONO)
def q(sql,l=20): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
r=q(f"""
WITH dice AS (SELECT DISTINCT user_id FROM v1090.ods_user_asset WHERE change_type='2'
   AND asset_id IN ('Item_1057','Item_1058') AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}'),
exch AS (SELECT DISTINCT user_id FROM v1090.ods_user_asset WHERE asset_id='Item_1202' AND change_type='2'
   AND reason_id='activity_exchange' AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}'),
card AS (SELECT DISTINCT user_id FROM v1090.ods_user_asset WHERE asset_id='Item_1202' AND change_type='2'
   AND reason_id='activity_exchange' AND split(reason_sub_id,'_')[2]='134102'
   AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}'),
pay AS (SELECT DISTINCT user_id FROM v1090.ods_user_order WHERE pay_status=1
   AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl}))
SELECT
 (SELECT count(*) FROM dice) dice,
 (SELECT count(*) FROM exch) exch,
 (SELECT count(*) FROM card) card,
 (SELECT count(*) FROM pay) pay,
 (SELECT count(*) FROM pay p WHERE p.user_id IN (SELECT user_id FROM exch)) pay_exch,
 (SELECT count(*) FROM pay p WHERE p.user_id IN (SELECT user_id FROM card)) pay_card,
 (SELECT count(*) FROM dice d WHERE d.user_id IN (SELECT user_id FROM pay)) dice_pay
""")[0]
print(json.dumps(r,ensure_ascii=False,indent=1))
d=r
print(f"\n=== 全量玩家漏斗 ===")
print(f"掷骰参与     {d['dice']:>6}  100%")
print(f"进店兑换     {d['exch']:>6}  {100*d['exch']/d['dice']:.1f}%")
print(f"兑换纪念卡   {d['card']:>6}  {100*d['card']/d['dice']:.1f}%")
print(f"\n=== 付费玩家漏斗(大富翁付费) ===")
print(f"大富翁付费   {d['pay']:>6}  100%")
print(f" ├掷骰参与   {d['dice_pay']:>6}  {100*d['dice_pay']/d['pay']:.1f}%")
print(f" ├进店兑换   {d['pay_exch']:>6}  {100*d['pay_exch']/d['pay']:.1f}%")
print(f" └兑换纪念卡 {d['pay_card']:>6}  {100*d['pay_card']/d['pay']:.1f}%")
json.dump(r, open(r'C:\ADHD_agent\KB\产出-数值设计\X3_下期节日优化清单\assets\_card_funnel.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
