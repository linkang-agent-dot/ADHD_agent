# -*- coding: utf-8 -*-
"""装饰/阶梯礼包 逐档转化对比：深海装饰(211016-18) vs 尼罗装饰(210630-32) vs 海妖提升(2010001-08/2010101-08)
比的是档间留存比例(tier2/tier1, tier3/tier1)，看深海断档是否属常态。全服·各链自身售卖窗口。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
LADDERS = {
  "深海装饰(700)": ['211016','211017','211018'],
  "尼罗装饰(648)": ['210630','210631','210632'],
  "海妖提升-提亚马特(604)": ['2010001','2010002','2010003','2010004','2010005'],
  "海妖提升-阿斯忒里亚(649)": ['2010101','2010102','2010103','2010104','2010105'],
}
out={}
for name, packs in LADDERS.items():
    inlist = ",".join(f"'{p}'" for p in packs)
    # 每档：买家/收入/单价/售卖窗口
    rows = q(f"""SELECT iap_id, count(distinct user_id) b, round(sum({USD}),0) rev, round(avg({USD}),2) price,
        min(partition_date) mn, max(partition_date) mx
        FROM v1090.ods_user_order WHERE pay_status=1 AND iap_id IN ({inlist})
        AND partition_date BETWEEN '2026-01-01' AND '2026-07-16' GROUP BY iap_id ORDER BY iap_id""")
    d = {r['iap_id']: r for r in rows}
    tiers = []
    for p in packs:
        if p in d:
            r=d[p]; tiers.append({"iap":p,"buyers":r['b'],"rev":float(r['rev']),"price":float(r['price']),"win":f"{r['mn']}~{r['mx']}"})
        else:
            tiers.append({"iap":p,"buyers":0,"rev":0,"price":0,"win":"-"})
    out[name]=tiers
    t1=tiers[0]['buyers'] or 1
    print(f"\n== {name} ==")
    for i,t in enumerate(tiers):
        ret = t['buyers']/t1*100
        print(f"  档{i+1} {t['iap']} ${t['price']:.2f}: 买家{t['buyers']:4d} (占档1 {ret:5.1f}%) 收入${t['rev']:,.0f}  {t['win']}")
json.dump(out, open("_ladder_compare.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _ladder_compare.json")
