# -*- coding: utf-8 -*-
"""
近6个节日 × 模块收入趋势查询
每个节日: 查 ods_user_order JOIN dim_iap (iap_type='混合-节日活动')，按 iap_id_name 聚合
然后本地用关键词映射到模块
"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# ── 节日定义（名称 + 日期范围）──
FESTIVALS = [
    {"name": "万圣节",  "label": "万圣节\n10月",  "start": "2025-10-16", "start_m1": "2025-10-15", "end": "2025-11-06"},
    {"name": "感恩节",  "label": "感恩节\n11月",  "start": "2025-11-13", "start_m1": "2025-11-12", "end": "2025-12-04"},
    {"name": "圣诞节",  "label": "圣诞节\n12月",  "start": "2025-12-11", "start_m1": "2025-12-10", "end": "2026-01-01"},
    {"name": "情人节",  "label": "情人节\n2月",   "start": "2026-01-30", "start_m1": "2026-01-29", "end": "2026-02-20"},
    {"name": "科技节",  "label": "科技节\n3月",   "start": "2026-03-13", "start_m1": "2026-03-12", "end": "2026-04-03"},
]

# ── 模块映射（从 iap_module_map.json 加载）──
try:
    with open(r'C:\ADHD_agent\.cursor\skills\generate_event_review\iap_module_map.json', encoding='utf-8') as f:
        module_map = json.load(f)
    EXACT = module_map.get('exact_matches', {})
    KEYWORD_RULES = module_map.get('keyword_rules', [])
except:
    EXACT = {}
    KEYWORD_RULES = []

KEYWORD_GROUPS = [
    (["小游戏", "推币", "挖孔", "挖矿", "大富翁", "弹球", "对对碰"], "小游戏"),
    (["头像框", "铭牌", "行军", "chat skin", "装饰", "皮肤", "GACHA", "gacha", "弹珠", "幼猴节"], "外显"),
    (["通行证", "BP", "bp", "月卡", "特惠", "自选", "周卡", "团购", "累充", "每日", "成长", "掉落",
      "预购", "连锁", "集结", "解锁", "补给", "限时", "随机", "特权", "bingo", "酒馆", "kvk", "KVK",
      "基因", "千万", "泳池", "转盘", "休眠", "改造", "宝箱", "深海", "感恩", "圣诞", "情人"], "混合"),
]

def infer_module(name: str) -> str:
    if name in EXACT:
        return EXACT[name]
    for keywords, mod in KEYWORD_GROUPS:
        if any(k in name for k in keywords):
            return mod
    return "混合"

def query_festival(f):
    SQL = f"""
    SELECT
        b2.iap_id_name,
        COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
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
    rows = api.execute_sql(SQL)
    return rows

results = {}
for f in FESTIVALS:
    print(f"正在查询 {f['name']} ({f['start']} ~ {f['end']}) ...", flush=True)
    rows = query_festival(f)
    # 聚合到模块
    module_agg = {"小游戏": 0.0, "外显": 0.0, "混合": 0.0}
    total = 0.0
    pack_count = 0
    for r in rows:
        name = r.get('iap_id_name', '')
        rev = float(r.get('revenue', 0) or 0)
        mod = infer_module(name)
        module_agg[mod] = module_agg.get(mod, 0) + rev
        total += rev
        pack_count += 1
    results[f['name']] = {
        "total": round(total, 2),
        "pack_count": pack_count,
        "modules": {k: round(v, 2) for k, v in module_agg.items()},
        "raw_rows": rows[:10],   # top10礼包存下来
    }
    print(f"  -> 总收入 ${total:,.0f}，{pack_count} 种礼包，模块: {module_agg}", flush=True)

# 保存结果
out_path = r'C:\ADHD_agent\_tmp_hist_modules.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存到 {out_path}")
