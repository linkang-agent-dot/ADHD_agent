# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
# 候选海妖链的头3档 + 夏日装饰
cands = {
 "604 提升-提亚(递进)": ['2010002','2010004','2010006'],
 "649 提升-阿斯(递进)": ['2010102','2010104','2010106'],
 "606 提亚等级好礼1": ['2011001','2011002','2011003'],
 "609 提亚技能好礼1": ['2012001','2012002','2012003'],
 "612 提亚经验耗尽": ['2013001','2013002','2013003'],
 "605 传奇提亚破冰": ['2009001','2009002','2009003'],
 "2008 提亚成就礼包": ['2008001','2008002','2008003'],
 "夏日装饰647": ['210917','210918','210919'],
}
allids = sorted(set(i for v in cands.values() for i in v))
inl=",".join(f"'{i}'" for i in allids)
rows=q(f"SELECT iap_id, count(distinct user_id) b, round(avg({USD}),2) price FROM v1090.ods_user_order WHERE pay_status=1 AND iap_id IN ({inl}) AND partition_date BETWEEN '2026-01-01' AND '2026-07-16' GROUP BY iap_id")
d={r['iap_id']:r for r in rows}
for name,ids in cands.items():
    parts=[f"{i}=${float(d[i]['price']):.2f}/{d[i]['b']}人" if i in d else f"{i}=无单" for i in ids]
    print(f"{name:22s}  " + "  ".join(parts))
