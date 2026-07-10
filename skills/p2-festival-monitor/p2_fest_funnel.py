# -*- coding: utf-8 -*-
"""弹药武器玩家逐层转化漏斗：P2 三节 W1/W2 主力武器 vs X3 深海转盘族。
层级：窗口付费人数 → 武器买家(进场) → ≥$19.99(升档) → $99.99(顶档) → 顶档复购(单/人) → 武器人均消费"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import query_trino
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}

# ---------- P2 侧 ----------
P2_CASES = [
    # (标签, 窗口start, 窗口end, 武器名列表)
    ("春节W1·挖孔",        "2026-01-13", "2026-01-19", ["挖孔小游戏礼包"]),
    ("春节W1·异族大富翁",  "2026-01-13", "2026-01-19", ["2025异族大富翁", "异族大富翁随机礼包"]),
    ("春节W2·钓鱼",        "2026-01-20", "2026-01-26", ["钓鱼活动礼包"]),
    ("拓荒W1·推币机",      "2026-05-12", "2026-05-18", ["推币机礼包", "推币机随机GACHA礼包"]),
    ("拓荒W2·弹珠GACHA",   "2026-05-19", "2026-05-25", ["升级版本弹珠GACHA礼包", "升级版本弹珠随机GACHA礼包"]),
    ("拓荒W3·挖孔",        "2026-05-26", "2026-06-01", ["挖孔礼包"]),
    ("深海W1·猜酒杯",      "2026-06-10", "2026-06-16", ["2026深海节-猜酒杯"]),
    ("深海W2·弹珠+GACHA本体","2026-06-17", "2026-06-23", ["升级版本弹珠GACHA礼包", "升级版本弹珠随机GACHA礼包", "2025深海节本体GACHA礼包", "2025深海节本体GACHA随机礼包"]),
]

payer_cache = {}
def p2_payers(s, e):
    if (s, e) not in payer_cache:
        r = execute_sql(f"SELECT count(distinct user_id) p FROM v1041.dl_user_order WHERE partition_date BETWEEN '{s}' AND '{e}'")
        payer_cache[(s, e)] = r["data"][0]["p"]
    return payer_cache[(s, e)]

print("===== P2 =====")
for label, s, e, weapons in P2_CASES:
    names = ",".join(f"'{w}'" for w in weapons)
    sql = f"""
    SELECT count(distinct o.user_id) b_any,
           count(distinct CASE WHEN i.iap_price >= 19.98 THEN o.user_id END) b_mid,
           count(distinct CASE WHEN i.iap_price >= 99.98 THEN o.user_id END) b_top,
           sum(CASE WHEN i.iap_price >= 99.98 THEN 1 ELSE 0 END) o_top,
           round(sum(CASE WHEN i.iap_price >= 99.98 THEN o.pay_price ELSE 0 END),0) rev_top,
           round(sum(o.pay_price),0) rev, count(1) orders
    FROM v1041.dl_user_order o LEFT JOIN v1041.dim_iap i ON o.iap_id=i.iap_id
    WHERE i.iap_id_name IN ({names}) AND o.partition_date BETWEEN '{s}' AND '{e}'
    """
    d = execute_sql(sql)["data"][0]
    payers = p2_payers(s, e)
    d.update(payers=payers, label=label, window=f"{s}~{e}")
    OUT[label] = d
    ent = d["b_any"] / payers * 100
    mid = d["b_mid"] / d["b_any"] * 100 if d["b_any"] else 0
    top = d["b_top"] / d["b_any"] * 100 if d["b_any"] else 0
    opb = d["o_top"] / d["b_top"] if d["b_top"] else 0
    apb = d["rev"] / d["b_any"] if d["b_any"] else 0
    print(f"{label:22s} 付费{payers:>6,} → 进场{d['b_any']:>5,}({ent:4.1f}%) → 升档{d['b_mid']:>4,}({mid:4.1f}%) → 顶档{d['b_top']:>4,}({top:4.1f}%) 顶档人均{opb:4.1f}单  武器人均${apb:6.1f}  总${d['rev']:,.0f}")

# ---------- X3 侧（深海转盘族 D0-D6 = 7/3~7/9 · 59服）----------
SRV = "'1170','1270','1310','1350','1390','1400','1420','1440','1460','1510','1530','1540','1550','1560','1570','1580','1590','1600','1610','1620','1630','1640','1650','1660','1670','1680','1690','1700','1710','1720','1730','1740','1750','1760','1770','1780','1790','1800','1810','1820','1830','1840','1850','1860','1870','1880','1890','1900','1910','1920','1930','1940','1950','1960','1970','1980','1990','2000','2010'"
WHEEL = "'211022','211024','211026','211028','211030','13021','13022','13023','13024','1002001'"
TOPIDS = "'211030','13024'"   # $99.99 档
MIDIDS = "'211026','211028','13022','13023','211030','13024'"  # >= $19.99

query_trino.DEFAULT_DATASOURCE = "TRINO_HF"
def xq(sql):
    return execute_sql(sql, datasource="TRINO_HF")

xp = xq(f"SELECT count(distinct user_id) p FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09' AND server_id IN ({SRV})")["data"][0]["p"]
sqlx = f"""
SELECT count(distinct user_id) b_any,
       count(distinct CASE WHEN iap_id IN ({MIDIDS}) THEN user_id END) b_mid,
       count(distinct CASE WHEN iap_id IN ({TOPIDS}) THEN user_id END) b_top,
       sum(CASE WHEN iap_id IN ({TOPIDS}) THEN 1 ELSE 0 END) o_top,
       round(sum(CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END),0) rev,
       count(1) orders
FROM v1090.ods_user_order
WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09'
  AND server_id IN ({SRV}) AND iap_id IN ({WHEEL})
"""
dx = xq(sqlx)["data"][0]
dx.update(payers=xp, label="X3深海W1·转盘族", window="2026-07-03~07-09")
OUT["X3深海W1·转盘族"] = dx
# 每档明细
dx_tier = xq(f"""
SELECT iap_id, round(sum(CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END),0) rev,
       count(1) orders, count(distinct user_id) buyers
FROM v1090.ods_user_order
WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09'
  AND server_id IN ({SRV}) AND iap_id IN ({WHEEL})
GROUP BY 1 ORDER BY rev DESC""")["data"]
OUT["X3_tier"] = dx_tier

print("\n===== X3 =====")
ent = dx["b_any"] / xp * 100
mid = dx["b_mid"] / dx["b_any"] * 100 if dx["b_any"] else 0
top = dx["b_top"] / dx["b_any"] * 100 if dx["b_any"] else 0
opb = dx["o_top"] / dx["b_top"] if dx["b_top"] else 0
apb = dx["rev"] / dx["b_any"] if dx["b_any"] else 0
print(f"X3深海W1·转盘族      付费{xp:>6,} → 进场{dx['b_any']:>5,}({ent:4.1f}%) → 升档{dx['b_mid']:>4,}({mid:4.1f}%) → 顶档{dx['b_top']:>4,}({top:4.1f}%) 顶档人均{opb:4.1f}单  武器人均${apb:6.1f}  总${dx['rev']:,.0f}")
for r in dx_tier:
    print(f"   iap {r['iap_id']:>8}  ${r['rev']:>7,.0f}  {r['orders']:>4}单/{r['buyers']:>4}人")

with open(os.path.join(HERE, "p2_funnel.json"), "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("\nsaved p2_funnel.json")
