# -*- coding: utf-8 -*-
"""
各节日子活动类型横向对比 — 把礼包进一步归为具体玩法
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

FESTIVALS = [
    {"name": "万圣节",  "start": "2025-10-16", "start_m1": "2025-10-15", "end": "2025-11-06"},
    {"name": "感恩节",  "start": "2025-11-13", "start_m1": "2025-11-12", "end": "2025-12-04"},
    {"name": "圣诞节",  "start": "2025-12-11", "start_m1": "2025-12-10", "end": "2026-01-01"},
    {"name": "情人节",  "start": "2026-01-30", "start_m1": "2026-01-29", "end": "2026-02-20"},
    {"name": "科技节",  "start": "2026-03-13", "start_m1": "2026-03-12", "end": "2026-04-03"},
]

# 子活动类型关键词 → 玩法名
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

def query_festival_full(f):
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

all_data = {}
for f in FESTIVALS:
    print(f"查询 {f['name']} ...", flush=True)
    rows = query_festival_full(f)
    # 按子活动类型聚合
    sub_agg = {}
    total = 0.0
    for r in rows:
        name = r.get('iap_id_name', '')
        rev = float(r.get('revenue', 0) or 0)
        buyers = int(r.get('pay_user_cnt', 0) or 0)
        times = int(r.get('buy_times', 0) or 0)
        sub = infer_subtype(name)
        if sub not in sub_agg:
            sub_agg[sub] = {"revenue": 0, "buyers": 0, "times": 0, "packs": []}
        sub_agg[sub]["revenue"] += rev
        sub_agg[sub]["buyers"] += buyers
        sub_agg[sub]["times"] += times
        sub_agg[sub]["packs"].append({"name": name, "revenue": rev})
        total += rev

    # 按收入排序，加占比
    sub_list = []
    for sub, d in sub_agg.items():
        sub_list.append({
            "sub": sub,
            "revenue": round(d["revenue"], 2),
            "share": round(d["revenue"]/total*100, 1) if total > 0 else 0,
            "buyers": d["buyers"],
            "top_pack": d["packs"][0]["name"] if d["packs"] else "",
        })
    sub_list.sort(key=lambda x: -x["revenue"])
    all_data[f["name"]] = {"total": round(total,2), "subtypes": sub_list}
    print(f"  总 ${total:,.0f}，子活动类型分布：")
    for s in sub_list[:6]:
        print(f"    {s['sub']:12s}  ${s['revenue']:>9,.0f}  {s['share']:5.1f}%  代表：{s['top_pack'][:20]}")

out = r'C:\ADHD_agent\_tmp_hist_subact.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"\n已保存 {out}")
