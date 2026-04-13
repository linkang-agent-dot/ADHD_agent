# -*- coding: utf-8 -*-
"""
用 iap_type2 做精确分类，重查6期节日数据
同时按 iap_id_name 输出明细，验证分类准确性
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

FESTIVALS = [
    {"name": "万圣节",  "start": "2025-10-17", "start_m1": "2025-10-16", "end": "2025-11-06"},
    {"name": "感恩节",  "start": "2025-11-13", "start_m1": "2025-11-12", "end": "2025-12-04"},
    {"name": "圣诞节",  "start": "2025-12-12", "start_m1": "2025-12-11", "end": "2026-01-01"},
    {"name": "春节",    "start": "2026-01-13", "start_m1": "2026-01-12", "end": "2026-02-08"},
    {"name": "情人节",  "start": "2026-02-11", "start_m1": "2026-02-10", "end": "2026-03-05"},
    {"name": "科技节",  "start": "2026-03-13", "start_m1": "2026-03-12", "end": "2026-04-03"},
]

def query_festival(f):
    SQL = f"""
    SELECT
        b2.iap_id_name,
        b2.iap_type2,
        COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
        COUNT(*) AS buy_times,
        CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
    FROM (
        SELECT user_id, iap_id, pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN '{f["start_m1"]}' AND '{f["end"]}'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '{f["start"]}' AND date '{f["end"]}'
          AND pay_status = 1
          AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    ) b1
    INNER JOIN (
        SELECT iap_id, iap_id_name, iap_type2
        FROM v1041.dim_iap
        WHERE iap_type = '混合-节日活动'
    ) b2 ON b1.iap_id = b2.iap_id
    GROUP BY b2.iap_id_name, b2.iap_type2
    ORDER BY revenue DESC
    """
    return api.execute_sql(SQL)

# ── 模块映射（基于 iap_type2） ──
TYPE2_MODULE = {
    "混合-节日活动-节日特惠": "节日特惠",
    "混合-节日活动-节日皮肤": "节日皮肤",
    "混合-节日活动-节日BP":   "节日BP",
    "混合-节日活动-挖矿小游戏": "挖矿小游戏",
}

all_data = {}
for f in FESTIVALS:
    print(f"\n{'='*60}", flush=True)
    print(f"[{f['name']}] {f['start']} ~ {f['end']}", flush=True)
    rows = query_festival(f)

    # 按 type2 聚合
    module_agg = {}
    pack_details = []
    total = 0.0
    for r in rows:
        name = r.get('iap_id_name', '')
        t2 = r.get('iap_type2', '') or '未分类'
        mod = TYPE2_MODULE.get(t2, t2)
        rev = float(r.get('revenue', 0) or 0)
        buyers = int(r.get('pay_user_cnt', 0) or 0)
        times = int(r.get('buy_times', 0) or 0)
        if mod not in module_agg:
            module_agg[mod] = {"rev": 0, "packs": 0}
        module_agg[mod]["rev"] += rev
        module_agg[mod]["packs"] += 1
        total += rev
        pack_details.append({
            "name": name, "module": mod, "revenue": round(rev, 2),
            "buyers": buyers, "times": times
        })

    # 打印汇总
    for mod, d in sorted(module_agg.items(), key=lambda x: -x[1]["rev"]):
        pct = d["rev"] / total * 100 if total > 0 else 0
        print(f"  {mod:14s}  ${d['rev']:>10,.0f}  {pct:5.1f}%  ({d['packs']}种)")

    print(f"  {'总计':14s}  ${total:>10,.0f}")

    # top10 礼包
    print(f"  --- Top10 礼包 ---")
    for p in pack_details[:10]:
        print(f"    [{p['module']:6s}]  ${p['revenue']:>10,.0f}  {p['buyers']:>5,}人  {p['name']}")

    all_data[f['name']] = {
        "total": round(total, 2),
        "modules": {k: {"rev": round(v["rev"], 2), "pct": round(v["rev"]/total*100, 1) if total > 0 else 0, "packs": v["packs"]}
                    for k, v in module_agg.items()},
        "top_packs": pack_details[:20],
    }

# 保存
out = r'C:\ADHD_agent\_tmp_hist_v3.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"\n\n✅ 已保存至 {out}")
