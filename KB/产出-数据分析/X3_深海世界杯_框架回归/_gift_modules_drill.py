# -*- coding: utf-8 -*-
"""深海节 4 尾部礼包模块回归的下钻数据：
- 每日礼包(102993/Type29): 第N日购买漏斗(800005-009 逐档)+买全人数(=X3NEW-1829终奖候选)
- 周卡(109101): 迟开6天口径校正(7/9-16窗口总付费人数当分母)+按用户花费分布($260 max归属)+逐档
- 装饰阶梯(106103/ChainPack700): 逐档到达(211016-018)看链断档
口径: 深海59服段。产出 _gift_drill.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
SF = f"server_id IN ({SRV59})"
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
def q(sql): return execute_sql(sql, datasource="TRINO_HF")["data"]
out = {}

# ---- 各模块自身窗口的总付费人数(付费率分母校正) ----
def payers(s, e):
    return q(f"SELECT count(distinct user_id) p, round(sum({USD}),0) t FROM v1090.ods_user_order "
             f"WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {SF}")[0]
WINDOWS = {"深海全窗7/3-16": ("2026-07-03","2026-07-16"),
           "每日礼包7/3-9": ("2026-07-03","2026-07-09"),
           "周卡7/9-16": ("2026-07-09","2026-07-16"),
           "装饰7/6-16": ("2026-07-06","2026-07-16")}
out["payer_base"] = {}
for k,(s,e) in WINDOWS.items():
    r = payers(s,e); out["payer_base"][k] = {"payers": r["p"], "total": float(r["t"])}
    print(f"{k}: 总付费{r['p']}人 / ${float(r['t']):,.0f}")

# ---- 1. 每日礼包 第N日漏斗 ----
print("\n== 每日礼包 每档(iap_id LIKE 8000%) 7/3-9 ==")
rows = q(f"""SELECT iap_id, count(distinct user_id) buyers, count(1) orders, round(sum({USD}),0) rev
    FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09'
    AND {SF} AND iap_id LIKE '8000%' GROUP BY iap_id ORDER BY iap_id""")
out["daily_by_iap"] = [{"iap": r["iap_id"], "buyers": r["buyers"], "orders": r["orders"], "rev": float(r["rev"])} for r in rows]
for r in rows: print(f"  {r['iap_id']}: 买家{r['buyers']} 单{r['orders']} ${float(r['rev']):,.0f}")
# 买全档数分布：一个用户买了几个不同的 daily iap
dist = q(f"""SELECT n_tiers, count(1) users FROM (
    SELECT user_id, count(distinct iap_id) n_tiers FROM v1090.ods_user_order
    WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-09'
    AND {SF} AND iap_id LIKE '8000%' GROUP BY user_id) GROUP BY n_tiers ORDER BY n_tiers""")
out["daily_tier_count_dist"] = [{"n_tiers": r["n_tiers"], "users": r["users"]} for r in dist]
print("  按买到的不同档数分布(买全=5=终奖候选):")
for r in dist: print(f"    买{r['n_tiers']}档: {r['users']}人")

# ---- 2. 周卡 按用户花费分布 + 逐档 ----
print("\n== 周卡 逐档(2026101-104) 7/9-16 ==")
WC = "iap_id IN ('2026101','2026102','2026103','2026104')"
rows = q(f"""SELECT iap_id, count(distinct user_id) buyers, count(1) orders, round(sum({USD}),0) rev
    FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-09' AND '2026-07-16'
    AND {SF} AND {WC} GROUP BY iap_id ORDER BY iap_id""")
out["weekly_by_iap"] = [{"iap": r["iap_id"], "buyers": r["buyers"], "orders": r["orders"], "rev": float(r["rev"])} for r in rows]
for r in rows: print(f"  {r['iap_id']}: 买家{r['buyers']} 单{r['orders']} ${float(r['rev']):,.0f}")
spend = q(f"""SELECT user_id, count(1) orders, round(sum({USD}),0) spend FROM v1090.ods_user_order
    WHERE pay_status=1 AND partition_date BETWEEN '2026-07-09' AND '2026-07-16'
    AND {SF} AND {WC} GROUP BY user_id ORDER BY spend DESC LIMIT 15""")
out["weekly_top_spenders"] = [{"orders": r["orders"], "spend": float(r["spend"])} for r in spend]
print("  Top15 花费(周卡是可续买/自选周卡):")
for r in spend: print(f"    {r['orders']}单 ${float(r['spend']):,.0f}")

# ---- 3. 装饰阶梯 逐档 (链断档) ----
print("\n== 装饰阶梯 逐档(211016/017/018) 7/6-16 ==")
DEC = "iap_id IN ('211016','211017','211018')"
rows = q(f"""SELECT iap_id, count(distinct user_id) buyers, count(1) orders, round(sum({USD}),0) rev
    FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-06' AND '2026-07-16'
    AND {SF} AND {DEC} GROUP BY iap_id ORDER BY iap_id""")
out["decor_by_iap"] = [{"iap": r["iap_id"], "buyers": r["buyers"], "orders": r["orders"], "rev": float(r["rev"])} for r in rows]
for r in rows: print(f"  {r['iap_id']}: 买家{r['buyers']} 单{r['orders']} ${float(r['rev']):,.0f}")
dist = q(f"""SELECT n_tiers, count(1) users FROM (
    SELECT user_id, count(distinct iap_id) n_tiers FROM v1090.ods_user_order
    WHERE pay_status=1 AND partition_date BETWEEN '2026-07-06' AND '2026-07-16'
    AND {SF} AND {DEC} GROUP BY user_id) GROUP BY n_tiers ORDER BY n_tiers""")
out["decor_tier_count_dist"] = [{"n_tiers": r["n_tiers"], "users": r["users"]} for r in dist]
print("  按买到的不同档数分布(阶梯链 1->2->3):")
for r in dist: print(f"    买{r['n_tiers']}档: {r['users']}人")

# ---- 4. 拜访 (仅确认单档+复购) ----
print("\n== 拜访 211020 7/3-16 ==")
rows = q(f"""SELECT iap_id, count(distinct user_id) buyers, count(1) orders, round(sum({USD}),0) rev, round(max({USD}),0) mx
    FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '2026-07-03' AND '2026-07-16'
    AND {SF} AND iap_id='211020' GROUP BY iap_id""")
out["visit"] = [{"iap": r["iap_id"], "buyers": r["buyers"], "orders": r["orders"], "rev": float(r["rev"])} for r in rows]
for r in rows: print(f"  {r['iap_id']}: 买家{r['buyers']} 单{r['orders']} ${float(r['rev']):,.0f}")

json.dump(out, open(os.path.join(HERE,"_gift_drill.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _gift_drill.json")
