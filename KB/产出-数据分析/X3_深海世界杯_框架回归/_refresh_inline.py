# -*- coding: utf-8 -*-
"""
终版刷新：原内联查询固化版（top20 / 券供给 / 竞猜逐服）
用法: python _refresh_inline.py [END 默认2026-07-16]
更新: _kx_top20.json / _ticket_sources.json / _ticket_summer.json(wc_total) / _jingcai_srv.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-16"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
DS_END = min(END, "2026-07-16")   # 深海 7/16 收官

# ---- top20 ----
JOBS = {
 "夏日_老服top20": ("2026-05-29","2026-06-08","server_id BETWEEN '1000' AND '1870'",
   "'210702','210704','210706','210708','210710','210712','210713','210714','210715'"),
 "世界杯_老服top20": ("2026-06-26",END,"server_id BETWEEN '1000' AND '1870'",
   "'211002','211004','211006','211008','211010','211012','211013','211014','211015'"),
 "世界杯_全服top20": ("2026-06-26",END,"server_id BETWEEN '1000' AND '2250'",
   "'211002','211004','211006','211008','211010','211012','211013','211014','211015'"),
 "深海_转盘top20": ("2026-07-03",DS_END,"server_id BETWEEN '1000' AND '2250'",
   "'211022','211024','211026','211028','211030','13021','13022','13023','13024'"),
}
t20 = {}
for label,(s,e,sf,packs) in JOBS.items():
    rows = execute_sql(f"""SELECT user_id, server_id, round(sum({USD}),0) tot
      FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}'
      AND {sf} AND iap_id IN ({packs}) GROUP BY user_id, server_id ORDER BY 3 DESC LIMIT 20""",
      datasource="TRINO_HF")["data"]
    t20[label] = [dict(sid=r['server_id'], tot=float(r['tot'])) for r in rows]
    print(label, ' '.join(f"{v['tot']:.0f}" for v in t20[label][:8]), '...')
json.dump(t20, open(os.path.join(HERE,'_kx_top20.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- 券供给（世界杯1146）----
r = execute_sql(f"""SELECT
    CASE WHEN cast(reason_sub_id as varchar) LIKE '894%0' THEN '免费竞猜档'
         WHEN cast(reason_sub_id as varchar) LIKE '894%' THEN '竞猜付费档'
         WHEN cast(reason_sub_id as varchar) LIKE '211%' THEN '开箱礼包购买'
         ELSE '其他(BP/邮件/兑换等)' END src,
    count(distinct user_id) u, round(sum(change_count),0) qty
  FROM v1090.ods_user_asset WHERE partition_date BETWEEN '2026-06-26' AND '{END}'
  AND asset_id='Item_1146' AND cast(change_type as varchar)='1' GROUP BY 1 ORDER BY 3 DESC""",
  datasource="TRINO_HF")["data"]
json.dump(r, open(os.path.join(HERE,'_ticket_sources.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
r2 = execute_sql(f"""SELECT count(distinct user_id) u, round(sum(change_count),0) qty
  FROM v1090.ods_user_asset WHERE partition_date BETWEEN '2026-06-26' AND '{END}'
  AND asset_id='Item_1146' AND cast(change_type as varchar)='1'""", datasource="TRINO_HF")["data"][0]
d = json.load(open(os.path.join(HERE,'_ticket_summer.json'), encoding='utf-8'))
d['wc_total'] = {'u': r2['u'], 'qty': float(r2['qty'])}
json.dump(d, open(os.path.join(HERE,'_ticket_summer.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"WC券总供给: {r2['u']:,}人 / {float(r2['qty']):,.0f}张")

# ---- 竞猜逐服 ----
out = {}
rows = execute_sql(f"""SELECT server_id sid, count(distinct user_id) b, round(sum({USD}),0) rev
  FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-06-26' AND '{END}'
  AND iap_id LIKE '894%' GROUP BY server_id""", datasource="TRINO_HF")["data"]
out['pay'] = {r['sid']: dict(b=r['b'], rev=float(r['rev'])) for r in rows}
rows = execute_sql(f"""SELECT server_id sid, count(distinct user_id) u
  FROM v1090.ods_user_asset WHERE partition_date BETWEEN '2026-06-26' AND '{END}'
  AND cast(reason_sub_id as varchar) LIKE '894%' GROUP BY server_id""", datasource="TRINO_HF")["data"]
out['part'] = {r['sid']: r['u'] for r in rows}
json.dump(out, open(os.path.join(HERE,'_jingcai_srv.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('竞猜逐服 OK; saved all')
