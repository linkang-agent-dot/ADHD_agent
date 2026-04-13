# -*- coding: utf-8 -*-
"""
重建7期数据（春节拆为纯春节+2月独立周期），用v4合并规则生成完整子活动横向对比
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 7期定义（春节缩短到02-01，新增2月独立周期）
FESTIVALS = [
    {"name": "万圣节",    "start": "2025-10-17", "end": "2025-11-06"},
    {"name": "感恩节",    "start": "2025-11-13", "end": "2025-12-04"},
    {"name": "圣诞节",    "start": "2025-12-12", "end": "2026-01-01"},
    {"name": "春节",      "start": "2026-01-13", "end": "2026-02-01"},
    {"name": "2月独立周期", "start": "2026-02-02", "end": "2026-02-08"},
    {"name": "情人节",    "start": "2026-02-11", "end": "2026-03-05"},
    {"name": "科技节",    "start": "2026-03-13", "end": "2026-04-03"},
]

TYPE2_MODULE = {
    "混合-节日活动-节日特惠": "节日特惠",
    "混合-节日活动-节日皮肤": "节日皮肤",
    "混合-节日活动-节日BP":   "节日BP",
    "混合-节日活动-挖矿小游戏": "挖矿小游戏",
}

def query_festival(f):
    from datetime import datetime, timedelta
    start = f["start"]
    start_m1 = (datetime.strptime(start, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
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
        WHERE partition_date BETWEEN '{start_m1}' AND '{f["end"]}'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '{start}' AND date '{f["end"]}'
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

all_data = {}
for f in FESTIVALS:
    print(f"Querying [{f['name']}] {f['start']}~{f['end']}...", flush=True)
    rows = query_festival(f)
    
    module_agg = {}
    packs = []
    total = 0.0
    for r in rows:
        name = r.get('iap_id_name', '')
        t2 = r.get('iap_type2', '') or ''
        mod = TYPE2_MODULE.get(t2, t2)
        rev = float(r.get('revenue', 0) or 0)
        buyers = int(r.get('pay_user_cnt', 0) or 0)
        times = int(r.get('buy_times', 0) or 0)
        if mod not in module_agg:
            module_agg[mod] = {"rev": 0, "packs": 0}
        module_agg[mod]["rev"] += rev
        module_agg[mod]["packs"] += 1
        total += rev
        packs.append({
            "name": name, "module": mod, "revenue": round(rev, 2),
            "buyers": buyers, "times": times
        })

    all_data[f['name']] = {
        "start": f["start"], "end": f["end"],
        "total": round(total, 2),
        "modules": {k: {"rev": round(v["rev"], 2), 
                         "pct": round(v["rev"]/total*100, 1) if total > 0 else 0}
                    for k, v in module_agg.items()},
        "top_packs": packs[:30],
    }
    print(f"  total=${total:,.0f}  ({len(packs)} packs)")

# 保存
with open(r'C:\ADHD_agent\_tmp_hist_v4.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

# 汇总打印
print("\n" + "="*60)
print("7期汇总")
print("="*60)
for f in FESTIVALS:
    d = all_data[f['name']]
    mods = "  ".join(f"{k}:{v['pct']}%" for k, v in 
                      sorted(d['modules'].items(), key=lambda x: -x[1]['rev']))
    print(f"  {f['name']:10s}  {f['start']}~{f['end']}  ${d['total']:>10,.0f}  {mods}")

print("\nDone: saved _tmp_hist_v4.json")
