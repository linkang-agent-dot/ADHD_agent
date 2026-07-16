# -*- coding: utf-8 -*-
"""
世界杯模块全景的基准数据：历届同类型模块同窗数据 + 开箱族合并 + 参与侧
产出 _wc_bench.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
out = {"END": END}

def order_q(label, s, e, sf, cond):
    d1 = execute_sql(f"""SELECT round(sum({USD}),0) rev, count(distinct user_id) buyers, count(1) orders
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}""",
        datasource="TRINO_HF")["data"][0]
    r2 = execute_sql(f"""SELECT round(max(tot),0) mx FROM (SELECT user_id, sum({USD}) tot
        FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{s}' AND '{e}' AND {sf} AND {cond}
        GROUP BY user_id) t""", datasource="TRINO_HF")
    mx = float((r2["data"][0]["mx"] if r2.get("data") else 0) or 0)
    rev = float(d1["rev"] or 0); b = d1["buyers"] or 0; o = d1["orders"] or 0
    m = {"rev": rev, "buyers": b, "orders": o, "max": mx, "arppu": rev/b if b else 0, "opb": o/b if b else 0}
    out[label] = m
    print(f"  {label:34s} ${rev:>9,.0f}  买家{b:>5}  ARPPU${m['arppu']:7.1f}  复购{m['opb']:4.1f}  max${mx:,.0f}")
    return m

print("== 基准：历届同ID模块同窗 ==")
# BP 130020/21：夏日窗(88服) / 情人节窗(成熟55服)
order_q("BP_夏日窗", "2026-05-29", "2026-06-08", "server_id BETWEEN '1000' AND '1870'", "iap_id IN ('130020','130021')")
order_q("BP_情人节窗", "2026-02-06", "2026-02-16", "server_id BETWEEN '1000' AND '1540'", "iap_id IN ('130020','130021')")
# 开箱族合并（连锁+锚点 union 买家）本届
order_q("WC开箱族合并", "2026-06-26", END, "server_id BETWEEN '1000' AND '2250'",
        "iap_id IN ('211002','211004','211006','211008','211010','211012','211013','211014','211015')")

print("\n== 参与侧（asset）==")
try:
    d = execute_sql(f"""SELECT count(distinct user_id) u, count(1) n
        FROM v1090.ods_user_asset WHERE partition_date BETWEEN '2026-06-26' AND '{END}'
        AND cast(reason_sub_id as varchar) LIKE '894%'""", datasource="TRINO_HF")["data"][0]
    out["竞猜参与"] = {"users": d["u"], "records": d["n"]}
    print(f"  竞猜参与(领包/下注记录 894%): {d['u']:,} 人 / {d['n']:,} 条")
except Exception as e:
    out["竞猜参与"] = None; print("  竞猜参与查询失败:", str(e)[:200])
try:
    d = execute_sql(f"""SELECT count(distinct user_id) u, round(sum(abs(change_count)),0) amt
        FROM v1090.ods_user_asset WHERE partition_date BETWEEN '2026-06-26' AND '{END}'
        AND asset_id = 'Item_1147' AND cast(change_type as varchar) = '2'""", datasource="TRINO_HF")["data"][0]
    out["兑换消耗1147"] = {"users": d["u"], "amount": float(d["amt"] or 0)}
    print(f"  兑换商店消耗(荣耀金币1147): {d['u']:,} 人 / 消耗 {float(d['amt'] or 0):,.0f}")
except Exception as e:
    out["兑换消耗1147"] = None; print("  兑换消耗查询失败:", str(e)[:200])

json.dump(out, open(os.path.join(HERE, "_wc_bench.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _wc_bench.json")
