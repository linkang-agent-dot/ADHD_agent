# -*- coding: utf-8 -*-
"""
用修正后的实际节日日期重查 6 个节日的模块收入
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# ── 修正后的实际节日日期 ──
FESTIVALS = [
    {"name": "万圣节",  "label": "万圣节\n10月", "start": "2025-10-17", "start_m1": "2025-10-16", "end": "2025-11-06"},
    {"name": "感恩节",  "label": "感恩节\n11月", "start": "2025-11-13", "start_m1": "2025-11-12", "end": "2025-12-04"},
    {"name": "圣诞节",  "label": "圣诞节\n12月", "start": "2025-12-12", "start_m1": "2025-12-11", "end": "2026-01-01"},
    {"name": "春节",    "label": "春节\n1月",   "start": "2026-01-13", "start_m1": "2026-01-12", "end": "2026-02-08"},
    {"name": "情人节",  "label": "情人节\n2月",  "start": "2026-02-11", "start_m1": "2026-02-10", "end": "2026-03-05"},
    {"name": "科技节",  "label": "科技节\n3月",  "start": "2026-03-13", "start_m1": "2026-03-12", "end": "2026-04-03"},
]

KEYWORD_GROUPS = [
    (["小游戏", "推币", "挖孔", "挖矿", "大富翁", "弹球", "对对碰"], "小游戏"),
    (["头像框", "铭牌", "行军", "装饰兑换", "皮肤", "GACHA", "gacha", "弹珠", "幼猴节", "chat"], "外显"),
]

def infer_module(name):
    for keywords, mod in KEYWORD_GROUPS:
        if any(k in name for k in keywords):
            return mod
    return "混合"

SUB_TYPES = [
    (["挖孔"], "挖孔小游戏"),
    (["推币"], "推币机"),
    (["挖矿"], "挖矿小游戏"),
    (["大富翁"], "大富翁"),
    (["对对碰"], "对对碰"),
    (["弹珠", "GACHA", "gacha", "Gacha"], "弹珠/GACHA"),
    (["头像框"], "头像框"),
    (["铭牌", "nameplate"], "铭牌"),
    (["行军表情", "行军特效"], "行军表情/特效"),
    (["装饰兑换"], "装饰兑换"),
    (["通行证", "BP", "bp"], "通行证/BP"),
    (["团购"], "节日团购"),
    (["每日补给", "daily"], "每日补给"),
    (["限时抢购", "限时"], "限时特惠"),
    (["预购", "连锁"], "预购连锁"),
    (["集结"], "集结奖励"),
]

def infer_subtype(name):
    for keywords, sub in SUB_TYPES:
        if any(k in name for k in keywords):
            return sub
    return "其他礼包"

def query_festival(f):
    SQL = f"""
    SELECT
        b2.iap_id_name,
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
        SELECT iap_id, iap_id_name
        FROM v1041.dim_iap
        WHERE iap_type = '混合-节日活动'
    ) b2 ON b1.iap_id = b2.iap_id
    GROUP BY b2.iap_id_name
    ORDER BY revenue DESC
    """
    return api.execute_sql(SQL)

all_modules = {}
all_subtypes = {}

for f in FESTIVALS:
    print(f"查询 {f['name']} ({f['start']} ~ {f['end']}) ...", flush=True)
    rows = query_festival(f)

    module_agg = {"小游戏": 0.0, "外显": 0.0, "混合": 0.0}
    sub_agg = {}
    total = 0.0

    for r in rows:
        name = r.get('iap_id_name', '')
        rev = float(r.get('revenue', 0) or 0)
        buyers = int(r.get('pay_user_cnt', 0) or 0)
        times = int(r.get('buy_times', 0) or 0)
        mod = infer_module(name)
        module_agg[mod] += rev
        sub = infer_subtype(name)
        if sub not in sub_agg:
            sub_agg[sub] = {"revenue": 0, "buyers": 0, "times": 0, "packs": []}
        sub_agg[sub]["revenue"] += rev
        sub_agg[sub]["buyers"] += buyers
        sub_agg[sub]["times"] += times
        sub_agg[sub]["packs"].append({"name": name, "revenue": rev})
        total += rev

    all_modules[f['name']] = {
        "total": round(total, 2),
        "start": f['start'],
        "end": f['end'],
        "modules": {k: {"rev": round(v,2), "pct": round(v/total*100,1) if total > 0 else 0}
                    for k, v in module_agg.items()},
    }

    sub_list = []
    for sub, d in sub_agg.items():
        sub_list.append({
            "sub": sub,
            "revenue": round(d["revenue"], 2),
            "share": round(d["revenue"]/total*100, 1) if total > 0 else 0,
            "top_pack": d["packs"][0]["name"] if d["packs"] else "",
        })
    sub_list.sort(key=lambda x: -x["revenue"])
    all_subtypes[f['name']] = {"total": round(total,2), "subtypes": sub_list}

    # 打印汇总
    mg = all_modules[f['name']]["modules"]
    print(f"  总 ${total:,.0f}  |  小游戏 {mg['小游戏']['pct']}%  外显 {mg['外显']['pct']}%  混合 {mg['混合']['pct']}%")
    for s in sub_list[:5]:
        print(f"    {s['sub']:14s}  ${s['revenue']:>10,.0f}  {s['share']:5.1f}%")

# 保存
with open(r'C:\ADHD_agent\_tmp_hist_modules_v2.json', 'w', encoding='utf-8') as f:
    json.dump(all_modules, f, ensure_ascii=False, indent=2)
with open(r'C:\ADHD_agent\_tmp_hist_subact_v2.json', 'w', encoding='utf-8') as f:
    json.dump(all_subtypes, f, ensure_ascii=False, indent=2)
print("\n✅ 数据已保存")
