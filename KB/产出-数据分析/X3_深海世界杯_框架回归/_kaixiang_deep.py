# -*- coding: utf-8 -*-
"""
开箱深钻三件套数据：
① 四代开箱付费分桶（$0-100每$10桶+>$100 ／ $100+每$100桶+>$2k）
② 四代分位数 p50/p75/p90/p95/p99 + max（皮肤进大奖是否拉高头部）
③ 逐服开箱付费（世界杯 vs 夏日：服均收入/买家/每服top1，本服榜效果代理）
口径：统一不加服过滤（礼包只在部署服存在）；窗口=各代活动窗
产出 _kaixiang_deep.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"

def ids(*xs): return ",".join(f"'{x}'" for x in xs)

GENS = {
  "元旦开箱": dict(s="2026-01-01", e="2026-01-15",
    packs=ids(210502,210504,210506,210508,210510,210512,210513,210514,210515)),
  "情人节开箱": dict(s="2026-02-06", e="2026-02-16",
    packs=ids(210702,210704,210706,210708,210710,210712,210713,210714,210715)),
  "夏日开箱": dict(s="2026-05-29", e="2026-06-08",
    packs=ids(210702,210704,210706,210708,210710,210712,210713,210714,210715)),
  "世界杯开箱": dict(s="2026-06-26", e=END,
    packs=ids(211002,211004,211006,211008,211010,211012,211013,211014,211015)),
}

def utot(c):
    return (f"(SELECT user_id, sum({USD}) tot FROM v1090.ods_user_order "
            f"WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}' "
            f"AND iap_id IN ({c['packs']}) GROUP BY user_id)")

out = {"END": END, "gens": {}}
for gen, c in GENS.items():
    g = {}
    # 分桶A: $0-100 每$10 + >$100（桶号10）
    rows = execute_sql(f"SELECT least(cast(floor(tot/10) as int),10) b, count(1) n FROM {utot(c)} t GROUP BY 1 ORDER BY 1",
                       datasource="TRINO_HF")["data"]
    g["bucketA"] = {int(r["b"]): r["n"] for r in rows}
    # 分桶B: $100+ 每$100（桶1=100-200 ... 19=1900-2000）+ >$2k（桶20）
    rows = execute_sql(f"SELECT least(cast(floor(tot/100) as int),20) b, count(1) n FROM {utot(c)} t WHERE tot>=100 GROUP BY 1 ORDER BY 1",
                       datasource="TRINO_HF")["data"]
    g["bucketB"] = {int(r["b"]): r["n"] for r in rows}
    # 分位数
    d = execute_sql(f"""SELECT count(1) buyers, round(sum(tot),0) rev,
          approx_percentile(tot, ARRAY[0.5,0.75,0.9,0.95,0.99]) q, round(max(tot),0) mx
        FROM {utot(c)} t""", datasource="TRINO_HF")["data"][0]
    q = d["q"] if isinstance(d["q"], list) else json.loads(str(d["q"]))
    g.update(buyers=d["buyers"], rev=float(d["rev"] or 0), max=float(d["mx"] or 0),
             p50=float(q[0]), p75=float(q[1]), p90=float(q[2]), p95=float(q[3]), p99=float(q[4]))
    # 付费玩家付费率分母：该模块有流水的服（=部署服）上、同窗总付费人数
    dp = execute_sql(f"""SELECT count(distinct user_id) payers FROM v1090.ods_user_order
        WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}'
        AND server_id IN (SELECT distinct server_id FROM v1090.ods_user_order
            WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}' AND iap_id IN ({c['packs']}))""",
        datasource="TRINO_HF")["data"][0]
    g["total_payers"] = dp["payers"]
    g["payrate"] = g["buyers"]/dp["payers"]*100 if dp["payers"] else 0
    out["gens"][gen] = g
    print(f"{gen}: 买家{g['buyers']} 付费率{g['payrate']:.1f}%(分母{g['total_payers']:,}) 收入${g['rev']:,.0f} p50/${g['p50']:.0f} p90/${g['p90']:.0f} p95/${g['p95']:.0f} p99/${g['p99']:.0f} max${g['max']:,.0f}")

# ③ 逐服：世界杯 vs 夏日
out["perserver"] = {}
for label in ["世界杯开箱", "夏日开箱"]:
    c = GENS[label]
    rows = execute_sql(f"""SELECT server_id, round(sum(tot),0) rev, count(1) buyers, round(max(tot),0) top1
        FROM (SELECT server_id, user_id, sum({USD}) tot FROM v1090.ods_user_order
          WHERE pay_status=1 AND partition_date BETWEEN '{c['s']}' AND '{c['e']}'
          AND iap_id IN ({c['packs']}) GROUP BY server_id, user_id) t
        GROUP BY server_id ORDER BY server_id""", datasource="TRINO_HF")["data"]
    out["perserver"][label] = [dict(sid=r["server_id"], rev=float(r["rev"]), buyers=r["buyers"], top1=float(r["top1"])) for r in rows]
    n = len(rows); tot = sum(r['rev'] for r in out["perserver"][label])
    t1s = sorted(r['top1'] for r in out["perserver"][label])
    print(f"{label} 有开箱流水的服 {n} 个 · 服均 ${tot/n:,.0f} · top1中位 ${t1s[n//2]:,.0f}")

json.dump(out, open(os.path.join(HERE, "_kaixiang_deep.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _kaixiang_deep.json")
