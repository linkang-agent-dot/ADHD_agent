# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
USD="CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
packs = [f"20100{i:02d}" if i<10 else f"2010{i:02d}" for i in range(1,9)]  # 2010001-2010008
inlist = ",".join(f"'{p}'" for p in ['2010001','2010002','2010003','2010004','2010005','2010006','2010007','2010008'])
rows = q(f"SELECT iap_id, count(distinct user_id) b, round(sum({USD}),0) rev, round(avg({USD}),2) price FROM v1090.ods_user_order WHERE pay_status=1 AND iap_id IN ({inlist}) AND partition_date BETWEEN '2026-01-01' AND '2026-07-16' GROUP BY iap_id ORDER BY iap_id")
print("海妖提升-提亚马特 全8档(604):")
for r in rows: print(f"  {r['iap_id']} ${float(r['price']):.2f}: 买家{r['b']} ${float(r['rev']):,.0f}")
