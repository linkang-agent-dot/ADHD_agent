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
def q(sql,l=100): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
# 10+ 的玩家：每人张数 + 大富翁付费 + 卡来源(成就直发 vs 转盘集市宝珠兑)
r=q(f"""
WITH cards AS (SELECT user_id, sum(TRY_CAST(change_count AS INTEGER)) got
  FROM v1090.ods_user_asset WHERE asset_id='Item_180080' AND change_type='1'
  AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}' GROUP BY user_id),
sp AS (SELECT user_id, sum({USD}) s FROM v1090.ods_user_order WHERE pay_status=1
  AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl}) GROUP BY 1),
exch AS (SELECT user_id, sum(TRY_CAST(change_count AS double)) tok
  FROM v1090.ods_user_asset WHERE asset_id='Item_1201' AND change_type='2' AND reason_id='activity_exchange'
  AND split(reason_sub_id,'_')[2]='134002' AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}' GROUP BY 1)
SELECT c.got, count(*) u, round(avg(COALESCE(sp.s,0)),0) avg_pay,
  round(avg(COALESCE(e.tok,0)/400.0),1) avg_exch_cards
FROM cards c LEFT JOIN sp ON c.user_id=sp.user_id LEFT JOIN exch e ON c.user_id=e.user_id
WHERE c.got>=10 GROUP BY c.got ORDER BY c.got
""")
print(f"{'张数':>5}{'人数':>5}{'人均大富翁付费':>14}{'人均转盘集市兑卡':>16}")
tot=0
for x in r:
    print(f"{x['got']:>5}{x['u']:>5}   ${x['avg_pay']:>10,.0f}   {x['avg_exch_cards']:>10.1f}张"); tot+=x['u']
print(f"合计 {tot} 人")
# 汇总分桶
r2=q(f"""
WITH cards AS (SELECT user_id, sum(TRY_CAST(change_count AS INTEGER)) got
  FROM v1090.ods_user_asset WHERE asset_id='Item_180080' AND change_type='1'
  AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}' GROUP BY user_id),
sp AS (SELECT user_id, sum({USD}) s FROM v1090.ods_user_order WHERE pay_status=1
  AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl}) GROUP BY 1)
SELECT CASE WHEN got BETWEEN 10 AND 14 THEN '10-14' WHEN got BETWEEN 15 AND 19 THEN '15-19'
  WHEN got BETWEEN 20 AND 29 THEN '20-29' ELSE '30+' END bkt,
  count(*) u, round(avg(COALESCE(sp.s,0)),0) avg_pay, max(got) mx
FROM cards c LEFT JOIN sp ON c.user_id=sp.user_id WHERE got>=10 GROUP BY 1 ORDER BY 1""")
print("\n分桶:")
for x in r2: print(f"  {x['bkt']:<7}{x['u']:>3}人  人均付费${x['avg_pay']:>7,.0f}  段内最高{x['mx']}张")
