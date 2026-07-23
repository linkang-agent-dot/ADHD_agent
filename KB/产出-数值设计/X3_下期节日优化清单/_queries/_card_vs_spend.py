# -*- coding: utf-8 -*-
"""大富翁付费额度 × 纪念卡180080获取张数：查真实卡片获取与付费关系。窗口7/3-7/16·59服。"""
import sys, json
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

S, E = "2026-07-03", "2026-07-16"
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
COMP = {
  "成就礼包": [f"280100{i}" for i in range(1,10)]+["2801010","2801011"],
  "罗盘连锁": [str(x) for x in range(207104,207113)],
  "存钱罐": ["280001"],
  "BP大富翁线": ["130036","130037"],
}
ALL_IDS = ",".join(chr(39)+x+chr(39) for name,ids in COMP.items() for x in ids)
ACH99 = ",".join(chr(39)+x+chr(39) for x in [f"280100{i}" for i in range(6,10)]+["2801010","2801011"])  # $99.99六档
ACH49 = "'2801005'"  # $49.99

def q(sql, limit=2000):
    return execute_sql(sql, datasource="TRINO_HF", limit=limit)["data"]

# 1) 每玩家大富翁付费额度 + 成就礼包直发卡数(49.99×1 + 99.99×2) + 实际获卡总张数
sql = f"""
WITH spend AS (
  SELECT user_id, SUM({USD}) sp,
    SUM(CASE WHEN iap_id={ACH49} THEN 1 ELSE 0 END) c49,
    SUM(CASE WHEN iap_id IN ({ACH99}) THEN 1 ELSE 0 END) c99
  FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}'
    AND server_id IN ({SRV59}) AND iap_id IN ({ALL_IDS})
  GROUP BY user_id
),
cards AS (
  SELECT user_id,
    SUM(CASE WHEN change_type='1' THEN TRY_CAST(change_count AS INTEGER) ELSE 0 END) got
  FROM v1090.ods_user_asset
  WHERE asset_id='Item_180080' AND server_id IN ({SRV59})
    AND partition_date BETWEEN '{S}' AND '{E}'
  GROUP BY user_id
),
j AS (
  SELECT s.user_id, s.sp, (s.c49*1 + s.c99*2) paid_cards, COALESCE(c.got,0) got_cards
  FROM spend s LEFT JOIN cards c ON s.user_id=c.user_id
),
b AS (
  SELECT *, CASE
    WHEN sp<=0 THEN '0 (仅其他/免费)'
    WHEN sp<=10 THEN 'a (0,10]'
    WHEN sp<=30 THEN 'b (10,30]'
    WHEN sp<=50 THEN 'c (30,50]'
    WHEN sp<=100 THEN 'd (50,100]'
    WHEN sp<=200 THEN 'e (100,200]'
    WHEN sp<=500 THEN 'f (200,500]'
    ELSE 'g (500+)' END bkt
  FROM j
)
SELECT bkt,
  count(*) users,
  round(sum(sp),0) tot_spend,
  round(avg(sp),1) avg_spend,
  sum(paid_cards) tot_paid_cards,
  round(avg(paid_cards),2) avg_paid_cards,
  sum(got_cards) tot_got_cards,
  round(avg(got_cards),2) avg_got_cards
FROM b GROUP BY bkt ORDER BY bkt
"""
rows = q(sql)
print(f"{'档(大富翁付费$)':<18}{'人数':>6}{'总付费$':>9}{'人均$':>8}{'付费直发卡':>10}{'人均直发':>8}{'实获总卡':>9}{'人均实获':>8}{'折合$/张(直发)':>14}")
tot_sp=tot_paid=tot_got=0
for r in rows:
    sp=r['tot_spend'] or 0; paid=r['tot_paid_cards'] or 0; got=r['tot_got_cards'] or 0
    per = (sp/paid) if paid else 0
    if not r['bkt'].startswith('0'):
        tot_sp+=sp; tot_paid+=paid; tot_got+=got
    print(f"{r['bkt']:<18}{r['users']:>6}{sp:>9.0f}{r['avg_spend']:>8.1f}{paid:>10}{r['avg_paid_cards']:>8}{got:>9}{r['avg_got_cards']:>8}{per:>14.2f}")
print("-"*95)
print(f"{'付费玩家合计':<18}{'':>6}{tot_sp:>9.0f}{'':>8}{tot_paid:>10}{'':>8}{tot_got:>9}{'':>8}{(tot_sp/tot_paid if tot_paid else 0):>14.2f}")
print(f"\n口径：折合$/张(直发)=该档总付费÷成就礼包直发卡数（$49.99×1+$99.99×2）；实获总卡=asset实际获取(含集市免费兑换)。")
json.dump(rows, open(r'C:\ADHD_agent\KB\产出-数值设计\X3_下期节日优化清单\assets\_card_vs_spend.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
