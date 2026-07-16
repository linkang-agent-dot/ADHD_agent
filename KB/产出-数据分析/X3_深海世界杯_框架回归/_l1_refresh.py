# -*- coding: utf-8 -*-
"""
母题4 数据层：改自 skills/p2-festival-monitor/x3_l1_metrics.py
窗口刷到收口(默认7/15,终版 7/21 传 2026-07-20)，加母题4 所需拆分：
- WC: 开箱连锁 vs 券锚点分开(W2)、竞猜按档位尾号(W3)、竞猜付费档按轮窗口(W6)
- 深海: 转盘连锁 vs 藏宝图锚点分开(D2)、BP按线拆(D4)、存钱罐单列(D7)
产出: _l1_m4.json (同目录)
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])

def ids(*xs): return ",".join(f"'{x}'" for x in xs)
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"

FESTS = {
  "深海节": {
    "window": ("2026-07-03", END), "sf": f"server_id IN ({SRV59})",
    "modules": {
      "转盘连锁5档": ids(211022,211024,211026,211028,211030),
      "藏宝图锚点4档": ids(13021,13022,13023,13024),
      "许愿池": ids(1002001),
      "大富翁成就礼包": ids(*[f"280100{i}" for i in range(1,10)],"2801010","2801011"),
      "大富翁罗盘连锁": ids(*[str(x) for x in range(207104,207113)]),
      "存钱罐": ids(280001),
      "BP大富翁线(130036/37)": ids(130036,130037),
      "BP转盘线(130035/46)": ids(130035,130046),
      "每日礼包": "iap_id LIKE '8000%'",
      "节日周卡": ids(2026101,2026102,2026103,2026104),
      "拜访礼包": ids(211020),
      "装饰礼包": ids(211016,211017,211018),
      "头像框(深海印记)": ids(211019),
    }},
  "世界杯": {
    "window": ("2026-06-26", END), "sf": "server_id BETWEEN '1000' AND '2250'",
    "modules": {
      "竞猜礼包全档": "iap_id LIKE '894%'",
      "竞猜$4.99档(尾1)": "iap_id LIKE '894%' AND substr(iap_id,-1)='1'",
      "竞猜$9.99框档(尾2)": "iap_id LIKE '894%' AND substr(iap_id,-1)='2'",
      "竞猜$19.99表情档(尾3)": "iap_id LIKE '894%' AND substr(iap_id,-1)='3'",
      "开箱福箱连锁": ids(211002,211004,211006,211008,211010),
      "开箱券锚点(可复购)": ids(211012,211013,211014,211015),
      "通行证(130020/21)": ids(130020,130021),
    }},
}
# ⚠️许愿池1002001=深海模块（累充白名单外溢进世界杯口径），世界杯侧不列

out = {"END": END}
for fest, cfg in FESTS.items():
    (s, e), sf = cfg["window"], cfg["sf"]
    base = execute_sql(f"""SELECT count(distinct user_id) payers, round(sum({USD}),0) total
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf}""",
        datasource="TRINO_HF")["data"][0]
    out[fest] = {"payers": base["payers"], "total": float(base["total"]), "modules": {}}
    print(f"\n===== {fest} {s}~{e}  总付费{base['payers']:,}人 / 大盘${base['total']:,.0f} =====")
    for mod, pred in cfg["modules"].items():
        cond = pred if "LIKE" in pred else f"iap_id IN ({pred})"
        d1 = execute_sql(f"""SELECT round(sum({USD}),0) rev, count(distinct user_id) buyers, count(1) orders
            FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}""",
            datasource="TRINO_HF")["data"][0]
        r2 = execute_sql(f"""SELECT round(max(tot),0) mx FROM (SELECT user_id, sum({USD}) tot
            FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}
            GROUP BY user_id) t""", datasource="TRINO_HF")
        d2 = r2["data"][0] if r2.get("data") else {"mx": 0}
        rev = float(d1["rev"] or 0); b = d1["buyers"] or 0; o = d1["orders"] or 0
        payers = base["payers"]
        m = {"rev": rev, "buyers": b, "orders": o, "max": float(d2["mx"] or 0),
             "payrate": b/payers*100 if payers else 0,
             "arppu": rev/b if b else 0, "opb": o/b if b else 0}
        out[fest]["modules"][mod] = m
        print(f"  {mod:24s} ${rev:>9,.0f}  买家{b:>5}({m['payrate']:4.1f}%)  ARPPU${m['arppu']:7.1f}  复购{m['opb']:4.1f}单  max${m['max']:,.0f}")

# 竞猜付费档按轮窗口（W6 奖励逐轮升级效果）
ROUNDS = [("R32", "2026-06-26", "2026-07-02"), ("R16", "2026-07-03", "2026-07-08"),
          ("QF", "2026-07-09", "2026-07-12"), ("SF", "2026-07-13", END)]
out["竞猜按轮"] = {}
print("\n===== 竞猜付费档按轮（下注窗口切分）=====")
for rd, a, b in ROUNDS:
    d = execute_sql(f"""SELECT round(sum({USD}),0) rev, count(distinct user_id) buyers, count(1) orders
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{a}' AND '{b}'
        AND server_id BETWEEN '1000' AND '2250' AND iap_id LIKE '894%'""",
        datasource="TRINO_HF")["data"][0]
    out["竞猜按轮"][rd] = {"rev": float(d["rev"] or 0), "buyers": d["buyers"] or 0, "orders": d["orders"] or 0, "win": f"{a}~{b}"}
    print(f"  {rd:4s} {a}~{b}  ${float(d['rev'] or 0):>8,.0f}  买家{d['buyers'] or 0:>4}  单数{d['orders'] or 0:>5}")

json.dump(out, open(os.path.join(HERE, "_l1_m4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _l1_m4.json")
