# -*- coding: utf-8 -*-
"""
修正2月独立周期：只含推币机/一番赏/砍价/抢购，其余归回春节
重新查询7期数据，输出 _tmp_hist_v5.json
"""
import sys, io, json
from datetime import datetime, timedelta
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 2月独立周期只包含这些活动的关键词
FEB_INDEPENDENT_KEYWORDS = ["推币机", "一番赏", "砍价", "限时抢购"]

def is_feb_independent(pack_name):
    for kw in FEB_INDEPENDENT_KEYWORDS:
        if kw in pack_name:
            return True
    return False

TYPE2_MODULE = {
    "混合-节日活动-节日特惠":   "节日特惠",
    "混合-节日活动-节日皮肤":   "节日皮肤",
    "混合-节日活动-节日BP":     "节日BP",
    "混合-节日活动-挖矿小游戏": "挖矿小游戏",
}

def query_festival_packs(start, end):
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
        WHERE partition_date BETWEEN '{start_m1}' AND '{end}'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '{start}' AND date '{end}'
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

# 非春节的节日直接查
OTHER_FESTIVALS = [
    {"name": "万圣节",  "start": "2025-10-17", "end": "2025-11-06"},
    {"name": "感恩节",  "start": "2025-11-13", "end": "2025-12-04"},
    {"name": "圣诞节",  "start": "2025-12-12", "end": "2026-01-01"},
    {"name": "情人节",  "start": "2026-02-11", "end": "2026-03-05"},
    {"name": "科技节",  "start": "2026-03-13", "end": "2026-04-03"},
]

all_results = {}

# ── 1. 非春节节日 ──
for f in OTHER_FESTIVALS:
    print(f"\n查询 {f['name']} ({f['start']}~{f['end']})...")
    rows = query_festival_packs(f["start"], f["end"])
    modules = {}
    packs = []
    for r in rows:
        rev = float(r['revenue'])
        buyers = int(r['pay_user_cnt'])
        mod = TYPE2_MODULE.get(r['iap_type2'], "其他")
        modules[mod] = modules.get(mod, 0) + rev
        packs.append({"name": r['iap_id_name'], "type2": r['iap_type2'], "module": mod, "rev": rev, "buyers": buyers})
    all_results[f["name"]] = {"modules": modules, "packs": packs, "total": sum(p["rev"] for p in packs)}
    print(f"  {f['name']}: {len(packs)} packs, total=${all_results[f['name']]['total']/1000:.0f}K")

# ── 2. 春节：查01-13~02-08全量，然后按规则拆分 ──
print(f"\n查询 春节全量 (01-13~02-08)...")
cny_rows = query_festival_packs("2026-01-13", "2026-02-08")

# 同时查02-02~02-08子窗口，用于精确拆分
print(f"查询 02-02~02-08子窗口...")
feb_rows = query_festival_packs("2026-02-02", "2026-02-08")

# 构建 feb 子窗口的 {name: {rev, buyers}} 映射
feb_by_name = {}
for r in feb_rows:
    name = r['iap_id_name']
    rev = float(r['revenue'])
    buyers = int(r['pay_user_cnt'])
    if name not in feb_by_name:
        feb_by_name[name] = {"rev": 0, "buyers": 0}
    feb_by_name[name]["rev"] += rev
    feb_by_name[name]["buyers"] = max(feb_by_name[name]["buyers"], buyers)

# 先用全量构建春节 + 独立周期
cny_modules = {}
cny_packs = []
feb_modules = {}
feb_packs = []

# 全量数据按名字聚合（因为同名可能有多个iap_id）
cny_by_name = {}
for r in cny_rows:
    name = r['iap_id_name']
    rev = float(r['revenue'])
    buyers = int(r['pay_user_cnt'])
    t2 = r['iap_type2']
    if name not in cny_by_name:
        cny_by_name[name] = {"rev": 0, "buyers": 0, "type2": t2}
    cny_by_name[name]["rev"] += rev
    cny_by_name[name]["buyers"] = max(cny_by_name[name]["buyers"], buyers)

for name, d in cny_by_name.items():
    mod = TYPE2_MODULE.get(d["type2"], "其他")
    
    if is_feb_independent(name) and name in feb_by_name:
        # 这个礼包在02-02~02-08有收入且属于独立周期活动
        feb_rev = feb_by_name[name]["rev"]
        feb_buyers = feb_by_name[name]["buyers"]
        cny_rev = d["rev"] - feb_rev  # 春节 = 全量 - 独立周期部分
        
        if feb_rev > 0:
            feb_modules[mod] = feb_modules.get(mod, 0) + feb_rev
            feb_packs.append({"name": name, "type2": d["type2"], "module": mod, "rev": round(feb_rev, 2), "buyers": feb_buyers})
        
        if cny_rev > 0:
            cny_modules[mod] = cny_modules.get(mod, 0) + cny_rev
            cny_packs.append({"name": name, "type2": d["type2"], "module": mod, "rev": round(cny_rev, 2), "buyers": d["buyers"]})
    else:
        # 不属于独立周期活动 → 全部归春节
        cny_modules[mod] = cny_modules.get(mod, 0) + d["rev"]
        cny_packs.append({"name": name, "type2": d["type2"], "module": mod, "rev": round(d["rev"], 2), "buyers": d["buyers"]})

cny_packs.sort(key=lambda x: -x["rev"])
feb_packs.sort(key=lambda x: -x["rev"])

all_results["春节"] = {"modules": cny_modules, "packs": cny_packs, "total": sum(p["rev"] for p in cny_packs)}
all_results["2月独立周期"] = {"modules": feb_modules, "packs": feb_packs, "total": sum(p["rev"] for p in feb_packs)}

print(f"\n  春节(修正后): {len(cny_packs)} packs, total=${all_results['春节']['total']/1000:.0f}K")
print(f"  2月独立周期(修正): {len(feb_packs)} packs, total=${all_results['2月独立周期']['total']/1000:.0f}K")

# 打印独立周期内容
print(f"\n  独立周期礼包明细:")
for p in feb_packs:
    print(f"    {p['name']:40s}  ${p['rev']:>10,.2f}")

# 打印春节被拆走了多少
print(f"\n  修正前春节(01-13~02-01): 旧数据")
print(f"  修正后春节(01-13~02-08, 扣独立): ${all_results['春节']['total']/1000:.0f}K")
print(f"  修正后独立周期(推币机/一番赏/砍价/抢购): ${all_results['2月独立周期']['total']/1000:.0f}K")

# 保存
FEST_ORDER = ["万圣节", "感恩节", "圣诞节", "春节", "2月独立周期", "情人节", "科技节"]
output = {"festivals": FEST_ORDER, "data": {}}
for f in FEST_ORDER:
    d = all_results[f]
    output["data"][f] = {
        "total": round(d["total"], 2),
        "modules": {k: round(v, 2) for k, v in d["modules"].items()},
        "packs": d["packs"],
    }

with open(r'C:\ADHD_agent\_tmp_hist_v5.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nDone: _tmp_hist_v5.json")
print(f"\n节日总收入汇总:")
for f in FEST_ORDER:
    print(f"  {f:12s}  ${all_results[f]['total']/1000:.0f}K  ({len(all_results[f]['packs'])} packs)")
