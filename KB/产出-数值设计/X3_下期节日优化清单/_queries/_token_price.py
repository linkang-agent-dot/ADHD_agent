# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
S,E="2026-07-03","2026-07-16"
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV=",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
def q(sql,l=50): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
# 大富翁付费(成就+罗盘连锁+存钱罐+BP大富翁线)
MONO=[f"280100{i}" for i in range(1,10)]+["2801010","2801011"]+[str(x) for x in range(207104,207113)]+["280001","130036","130037"]
idl=",".join("'"+x+"'" for x in MONO)
sp=q(f"""SELECT round(sum({USD}),0) sp FROM v1090.ods_user_order WHERE pay_status=1
 AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl})""")[0]['sp']
# 代币1202 产出/消耗
tk=q(f"""SELECT
  sum(CASE WHEN change_type='1' THEN TRY_CAST(change_count AS INTEGER) ELSE 0 END) got,
  sum(CASE WHEN change_type='2' THEN TRY_CAST(change_count AS INTEGER) ELSE 0 END) used
 FROM v1090.ods_user_asset WHERE asset_id='Item_1202'
 AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}'""")[0]
# 两张卡各自获取
for cid,nm in [("180041","美人鱼梦境(大富翁集市3000代币)"),("180080","远航之歌(成就直发+转盘集市400宝珠)")]:
    c=q(f"""SELECT sum(CASE WHEN change_type='1' THEN TRY_CAST(change_count AS INTEGER) ELSE 0 END) got,
      count(distinct CASE WHEN change_type='1' THEN user_id END) u
     FROM v1090.ods_user_asset WHERE asset_id='Item_{cid}'
     AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}'""")[0]
    print(f"  {nm:<38} 获取{c['got'] or 0:>6}张 / {c['u'] or 0}人")
print(f"\n大富翁总付费 = ${sp:,.0f}")
print(f"代币1202: 产出 {tk['got']:,} / 消耗 {tk['used']:,}")
usd_per_token = sp/tk['got'] if tk['got'] else 0
print(f"隐含 $/代币 = ${usd_per_token:.5f}")
print(f"大富翁集市卡 3000代币 → 实际 ≈ ${3000*usd_per_token:.2f}/张 (上限,付费还买了骰子/钻石等)")
