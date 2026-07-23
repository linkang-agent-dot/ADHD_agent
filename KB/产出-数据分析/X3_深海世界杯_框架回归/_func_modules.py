# -*- coding: utf-8 -*-
"""深海功能模块回归数据(SQL侧聚合防截断)：累充转化 / 签到每天人数 / 酒馆任务完成率。"""
import sys, json, re
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
SRV=[1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010]
SF=f"server_id IN ({','.join(chr(39)+str(x)+chr(39) for x in SRV)})"
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
wl=re.findall(r'"(\d+)"', re.search(r'FALLBACK_PACK_IDS\s*=\s*\[(.*?)\]', open(r"C:\ADHD_agent\skills\x3-festival-monitor\x3_deepsea_daily.py",encoding="utf-8").read(), re.S).group(1))
WL=",".join(f"'{p}'" for p in wl)
out={}

# 1. 累充转化(SQL侧聚合) — 标准X3累充十档 $阈值
TIERS=[10,40,100,200,400,700,1000,1300,1600,2000]
cif=", ".join(f"count_if(sp>={t}) t{t}" for t in TIERS)
r=q(f"""SELECT count(*) part, {cif} FROM (
  SELECT user_id, sum({USD}) sp FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND {SF} AND iap_id IN ({WL})
  GROUP BY user_id)""")[0]
part=r['part']
out["recharge"]={"participants":part,"tiers":[{"tier_usd":t,"reached":r[f't{t}']} for t in TIERS]}
print(f"累充参与者(买≥1白名单包){part}人:")
for t in TIERS: print(f"  ≥${t}: {r[f't{t}']}人 ({r[f't{t}']/part*100:.1f}%)")

# 2. 签到每天人数(SRV59·单服活动)
r=q(f"""SELECT partition_date d, count(distinct user_id) u FROM v1090.ods_user_activity
  WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND {SF} AND activity_type='0'
  AND attribute1 LIKE '%"activityCfgID":101406%' GROUP BY partition_date ORDER BY partition_date""")
out["signin"]=[{"d":x['d'],"u":x['u']} for x in r]
print(f"\n签到每天人数: {[(x['d'][5:],x['u']) for x in r]}")

# 3. 酒馆任务完成率(跨服·cfg圈定不加server过滤·SQL侧聚合)
NAME={1:"精英水手",2:"城建加速",3:"英雄晋升",4:"研究加速",5:"一掷千金",6:"突发危机",7:"声望提升"}
TOP={1:70000,2:70000,3:70000,4:70000,5:50000,6:70000,7:70000}
r=q("""SELECT st, count(*) part, count_if(sc>=10000) e, count_if(sc>=30000) t2, count_if(sc>=50000) t3, count_if(sc>=70000) t4 FROM (
  SELECT activity_step st, user_id, max(cast(regexp_extract(attribute1,'"stepScore":(\d+)',1) as bigint)) sc
  FROM v1090.ods_user_activity WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-12'
  AND activity_type='4' AND attribute1 LIKE '%"activityCfgID":10071704%' GROUP BY activity_step, user_id)
  GROUP BY st ORDER BY st""")
tav=[]
for x in r:
    st=int(x['st']); top=TOP[st]; full=x['t4'] if top==70000 else x['t3']
    tav.append({"stage":st,"name":NAME[st],"participants":x['part'],"entry":x['e'],
                "full":full,"full_rate":full/x['part']*100 if x['part'] else 0,
                "entry_rate":x['e']/x['part']*100 if x['part'] else 0})
out["tavern"]=tav
print(f"\n酒馆逐阶段(完成率=达顶档{'/50k' }):")
for t in tav: print(f"  阶段{t['stage']} {t['name']}: 参与{t['participants']} 完成{t['full']}({t['full_rate']:.0f}%) 入门率{t['entry_rate']:.0f}%")

json.dump(out, open("_func_modules.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _func_modules.json")
