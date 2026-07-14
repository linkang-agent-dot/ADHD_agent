# -*- coding: utf-8 -*-
"""X3 三节日 L1 层：各模块 付费率/ARPU/ARPPU/复购。深海+世界杯主、夏日辅。"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])

def ids(*xs): return ",".join(f"'{x}'" for x in xs)

FESTS = {
  "深海节(7/3-7/13·59服)": {
    "window": ("2026-07-03","2026-07-13"), "sf": f"server_id IN ({SRV59})",
    "modules": {
      "转盘(连锁+锚点)": ids(211022,211024,211026,211028,211030,13021,13022,13023,13024),
      "许愿池": ids(1002001),
      "大富翁族(成就+罗盘连锁+存钱罐)": ids(*[f"280100{i}" for i in range(1,10)],"2801010","2801011",*[str(x) for x in range(207104,207113)],"280001"),
      "双通行证": ids(130035,130036,130037,130046),
      "每日礼包": "iap_id LIKE '8000%'",
      "节日周卡": ids(2026101,2026102,2026103,2026104),
      "拜访礼包": ids(211020),
      "装饰礼包": ids(211016,211017,211018),
      "头像框(深海印记)": ids(211019),
    }},
  "世界杯(6/26-7/13·98服)": {
    "window": ("2026-06-26","2026-07-13"), "sf": "server_id BETWEEN '1000' AND '1970'",
    "modules": {
      "竞猜礼包": "iap_id LIKE '894%'",
      "开箱族(福箱连锁+券锚点)": ids(211002,211004,211006,211008,211010,211012,211013,211014,211015),
      "通行证(130020/21)": ids(130020,130021),
      "许愿池(与深海共用)": ids(1002001),
    }},
  "夏日恋语·辅助(5/29-6/8·88服)": {
    "window": ("2026-05-29","2026-06-08"), "sf": "server_id BETWEEN '1000' AND '1870'",
    "modules": {
      "开箱族(连锁+券锚点)": ids(210702,210704,210706,210708,210710,210712,210713,210714,210715),
      "通行证(130020/21)": ids(130020,130021),
      "装饰礼包": ids(210917,210918,210919),
      "拜访皮肤": ids(210921),
      "家具礼包": ids(210717),
      "许愿池": ids(1002001),
    }},
}

USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
out = {}
for fest, cfg in FESTS.items():
    (s, e), sf = cfg["window"], cfg["sf"]
    base = execute_sql(f"""SELECT count(distinct user_id) payers, round(sum({USD}),0) total
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf}""",
        datasource="TRINO_HF")["data"][0]
    out[fest] = {"payers": base["payers"], "total": float(base["total"]), "modules": {}}
    print(f"\n===== {fest}  总付费{base['payers']:,}人 / 大盘${base['total']:,.0f} =====")
    for mod, pred in cfg["modules"].items():
        cond = pred if "LIKE" in pred else f"iap_id IN ({pred})"
        d = execute_sql(f"""SELECT round(sum({USD}),0) rev, count(distinct user_id) buyers, count(1) orders
            FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}""",
            datasource="TRINO_HF")["data"][0]
        rev = float(d["rev"] or 0); b = d["buyers"] or 0; o = d["orders"] or 0
        payers = base["payers"]
        m = {"rev": rev, "buyers": b, "orders": o,
             "payrate": b/payers*100 if payers else 0,
             "arpu": rev/payers if payers else 0,
             "arppu": rev/b if b else 0,
             "opb": o/b if b else 0}
        out[fest]["modules"][mod] = m
        print(f"  {mod:26s} ${rev:>9,.0f}  买家{b:>5}({m['payrate']:4.1f}%)  ARPU${m['arpu']:6.2f}  ARPPU${m['arppu']:7.1f}  复购{m['opb']:4.1f}单")

json.dump(out, open(os.path.join(HERE,"x3_l1_metrics.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved x3_l1_metrics.json")
