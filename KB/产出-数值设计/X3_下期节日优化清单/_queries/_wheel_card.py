# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
S,E="2026-07-03","2026-07-16"
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV=",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
MONO=[f"280100{i}" for i in range(1,10)]+["2801010","2801011"]+[str(x) for x in range(207104,207113)]+["280001","130036","130037"]
idl=",".join("'"+x+"'" for x in MONO)
def q(sql,l=50): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
r=q(f"""
WITH exch AS (SELECT user_id, sum(TRY_CAST(change_count AS double)) tok
  FROM v1090.ods_user_asset WHERE asset_id='Item_1201' AND change_type='2'
  AND reason_id='activity_exchange' AND split(reason_sub_id,'_')[2]='134002'
  AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}' GROUP BY user_id),
pay AS (SELECT DISTINCT user_id FROM v1090.ods_user_order WHERE pay_status=1
  AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl}))
SELECT count(*) users, round(sum(tok),0) tok, round(sum(tok)/400,0) cards,
  count(CASE WHEN p.user_id IS NOT NULL THEN 1 END) pay_u,
  round(sum(CASE WHEN p.user_id IS NOT NULL THEN tok END)/400,0) pay_cards
FROM exch e LEFT JOIN pay p ON e.user_id=p.user_id
""")[0]
print(f"转盘集市(400宝珠)兑换 远航之歌180080:")
print(f"  兑换人数 = {r['users']:,}  (其中大富翁付费玩家 {r['pay_u']})")
print(f"  消耗宝珠 = {r['tok']:,.0f}  → 兑换卡数 = {r['cards']:,.0f} 张")
print(f"  付费玩家兑 {r['pay_cards']:,.0f} 张 / 免费玩家兑 {r['cards']-r['pay_cards']:,.0f} 张")
# 对比:成就礼包直发
d=q(f"""SELECT
  sum(CASE WHEN iap_id='2801005' THEN 1 ELSE 0 END)*1
  + sum(CASE WHEN iap_id IN ('2801006','2801007','2801008','2801009','2801010','2801011') THEN 1 ELSE 0 END)*2 cards
  FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}'
  AND server_id IN ({SRV})""")[0]
print(f"\n对比 成就礼包直发 = {d['cards']:,} 张")
print(f"远航之歌总获取(之前查) = 2,115 张")
