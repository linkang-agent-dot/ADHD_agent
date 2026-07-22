# -*- coding: utf-8 -*-
"""全 $19.99×3 阶梯链同价对标：夏日/尼罗/深海装饰 vs 海妖破冰(传奇提亚马特·同价$19.99)
同价隔离机制→比档间留存(该形式常态) + 档1触达(产品中心度决定,非机制)。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
LAD = {
  "夏日装饰(647)": (['210917','210918','210919'], "外显装饰 · $19.99×3"),
  "尼罗装饰(648)": (['210630','210631','210632'], "外显装饰 · $19.99×3"),
  "深海装饰(700)": (['211016','211017','211018'], "外显装饰 · $19.99×3"),
  "海妖破冰-提亚马特(605)": (['2009001','2009002','2009003'], "英雄养成 · $19.99×3(同价对标)"),
}
out={}
for name,(packs,form) in LAD.items():
    inl=",".join(f"'{p}'" for p in packs)
    rows=q(f"SELECT iap_id, count(distinct user_id) b, round(sum({USD}),0) rev, round(avg({USD}),2) price FROM v1090.ods_user_order WHERE pay_status=1 AND iap_id IN ({inl}) AND partition_date BETWEEN '2026-01-01' AND '2026-07-16' GROUP BY iap_id ORDER BY iap_id")
    d={r['iap_id']:r for r in rows}
    tiers=[{"iap":p,"buyers":(d[p]['b'] if p in d else 0),"rev":float(d[p]['rev']) if p in d else 0,"price":float(d[p]['price']) if p in d else 0} for p in packs]
    t1=tiers[0]['buyers'] or 1
    for t in tiers: t['ret']=t['buyers']/t1*100
    out[name]={"form":form,"tiers":tiers}
    print(f"\n{name} [{form}]")
    for i,t in enumerate(tiers): print(f"  档{i+1} ${t['price']:.2f}: {t['buyers']}人 (留存{t['ret']:.0f}%) ${t['rev']:,.0f}")
json.dump(out, open("_ladder_clean.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _ladder_clean.json")
