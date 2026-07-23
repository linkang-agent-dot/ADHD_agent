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
def q(sql,l=80): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
NAME={"134100":("月心珍珠(永久皮)",50000),"134101":("海风旅者·霍普金斯(皮肤)",30000),
 "134102":("美人鱼梦境(纪念卡)",3000),"134103":("传奇英雄装备宝箱",3500),"134104":("诅咒的龙骸",2500),
 "134105":("通用技能碎片",1000),"134106":("万能传奇信物",1000),"134107":("神秘金属",120),
 "134108":("传奇技能书",100),"134109":("高级木板",40),"134110":("硬木板",3),
 "134111":("深海藏宝图",100),"134112":("30分钟加速",100)}
r=q(f"""
WITH red AS (
  SELECT split(reason_sub_id,'_')[2] rsub, user_id, sum(TRY_CAST(change_count AS double)) tok
  FROM v1090.ods_user_asset WHERE asset_id='Item_1202' AND change_type='2'
  AND reason_id='activity_exchange' AND server_id IN ({SRV})
  AND partition_date BETWEEN '{S}' AND '{E}' GROUP BY 1,2),
sp AS (SELECT user_id, sum({USD}) s FROM v1090.ods_user_order WHERE pay_status=1
  AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl}) GROUP BY 1)
SELECT r.rsub, count(distinct r.user_id) users, round(sum(r.tok),0) tok,
  round(avg(COALESCE(sp.s,0)),1) avg_pay,
  count(distinct CASE WHEN sp.s>0 THEN r.user_id END) payers,
  round(approx_percentile(COALESCE(sp.s,0),0.5),1) med_pay
FROM red r LEFT JOIN sp ON r.user_id=sp.user_id GROUP BY 1
""")
rows=[]
for x in r:
    nm,price=NAME.get(x['rsub'],(x['rsub'],1))
    items=round((x['tok'] or 0)/price)
    prate=100*x['payers']/x['users'] if x['users'] else 0
    rows.append(dict(name=nm,price=price,users=x['users'],items=items,tok=x['tok'],
                     avg_pay=x['avg_pay'],med_pay=x['med_pay'],payers=x['payers'],prate=prate))
rows.sort(key=lambda z:-z['tok'])
print(f"{'兑换品':<22}{'单价':>7}{'人数':>6}{'件数':>7}{'代币消耗':>11}{'兑换者大富翁付费率':>16}{'实际平均付费':>12}{'中位付费':>9}")
for z in rows:
    print(f"{z['name']:<22}{z['price']:>7}{z['users']:>6}{z['items']:>7}{z['tok']:>11,.0f}{z['prate']:>14.0f}%  ${z['avg_pay']:>9.1f}  ${z['med_pay']:>7.1f}")
json.dump(rows, open(r'C:\ADHD_agent\KB\产出-数值设计\X3_下期节日优化清单\assets\_monopoly_shop_redeem.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
