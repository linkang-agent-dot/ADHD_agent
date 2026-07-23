# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
S,E="2026-07-03","2026-07-16"
SRV=",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
MONO=[f"280100{i}" for i in range(1,10)]+["2801010","2801011"]+[str(x) for x in range(207104,207113)]+["280001","130036","130037"]
idl=",".join("'"+x+"'" for x in MONO)
def q(sql,l=100): return execute_sql(sql,datasource="TRINO_HF",limit=l)["data"]
r=q(f"""
WITH cards AS (SELECT user_id, sum(TRY_CAST(change_count AS INTEGER)) got
  FROM v1090.ods_user_asset WHERE asset_id='Item_180080' AND change_type='1'
  AND server_id IN ({SRV}) AND partition_date BETWEEN '{S}' AND '{E}' GROUP BY user_id),
pay AS (SELECT DISTINCT user_id FROM v1090.ods_user_order WHERE pay_status=1
  AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV}) AND iap_id IN ({idl})),
j AS (SELECT c.user_id, c.got, CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END is_pay
  FROM cards c LEFT JOIN pay p ON c.user_id=p.user_id WHERE c.got>0)
SELECT got, count(*) all_u, sum(is_pay) pay_u FROM j GROUP BY got ORDER BY got
""")
allT=sum(x['all_u'] for x in r); payT=sum(x['pay_u'] for x in r); freeT=allT-payT
print(f"全量兑卡{allT}人 / 付费{payT} / 免费{freeT}")
# 分桶 1..9,10+
buk={}
for x in r:
    g=x['got']; k=str(g) if g<10 else '10+'
    buk.setdefault(k,{'all':0,'pay':0}); buk[k]['all']+=x['all_u']; buk[k]['pay']+=x['pay_u']
order=[str(i) for i in range(1,10)]+['10+']
print(f"\n{'张数':<5}{'全量人数':>8}{'全量占比':>9}{'付费人数':>8}{'付费占比':>9}{'免费占比':>9}")
out=[]
for k in order:
    b=buk.get(k,{'all':0,'pay':0}); a=b['all']; p=b['pay']; f=a-p
    ap=100*a/allT if allT else 0; pp=100*p/payT if payT else 0; fp=100*f/freeT if freeT else 0
    out.append(dict(k=k,all_u=a,all_pct=round(ap,1),pay_u=p,pay_pct=round(pp,1),free_pct=round(fp,1)))
    print(f"{k:<5}{a:>8}{ap:>8.1f}%{p:>8}{pp:>8.1f}%{fp:>8.1f}%")
json.dump({"all":allT,"pay":payT,"free":freeT,"dist":out},
  open(r'C:\ADHD_agent\KB\产出-数值设计\X3_下期节日优化清单\assets\_card_dist.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
