# -*- coding: utf-8 -*-
"""
查各节日皮肤抽奖槽位的完整收入
槽位定义：
  万圣节: 万圣节皮肤GACHA (随机+普通+每日)
  感恩节: 感恩节皮肤GACHA (随机+普通+每日)
  圣诞节: 弹珠GACHA (圣诞出现的弹珠) + GACHA每日
  春节: 春节GACHA (随机+普通) + GACHA每日-登月节 + 春节抽奖成就礼包
  情人节: 云上探宝
  科技节: 推币机 + 弹珠GACHA（科技节的）

也查各节日的成就礼包，确认是否每个节日都有配套
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

FESTIVALS = [
    {"name": "万圣节", "start": "2025-10-17", "end": "2025-11-06"},
    {"name": "感恩节", "start": "2025-11-13", "end": "2025-12-04"},
    {"name": "圣诞节", "start": "2025-12-12", "end": "2026-01-01"},
    {"name": "春节",   "start": "2026-01-13", "end": "2026-02-08"},
    {"name": "情人节", "start": "2026-02-11", "end": "2026-03-05"},
    {"name": "科技节", "start": "2026-03-13", "end": "2026-04-03"},
]

# 槽位关键词映射（按节日定义哪些礼包名属于该节日的皮肤抽奖槽位）
SLOT_KEYWORDS = {
    "万圣节": {
        "include": ["2024万圣节随机GACHA", "2024万圣节GACHA", "25万圣节gacha每日"],
        "exclude": ["弹珠", "机甲"],
    },
    "感恩节": {
        "include": ["2024感恩节随机GACHA", "2024感恩节GACHA", "25感恩节本体gacha每日"],
        "exclude": [],
    },
    "圣诞节": {
        "include": ["弹珠"],  # 圣诞节的皮肤抽奖是弹珠GACHA
        "exclude": [],
    },
    "春节": {
        "include": ["2025春节随机GACHA", "2025春节GACHA", "GACHA每日礼包-登月节", "春节抽奖成就"],
        "exclude": ["推币机", "一番赏"],
    },
    "情人节": {
        "include": ["云上探宝"],
        "exclude": [],
    },
    "科技节": {
        "include": ["推币机", "2026科技节弹珠GACHA"],
        "exclude": [],
    },
}

from datetime import datetime, timedelta

results = {}

for f in FESTIVALS:
    start_m1 = (datetime.strptime(f["start"], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    
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
    
    rows = api.execute_sql(SQL)
    
    slot_cfg = SLOT_KEYWORDS[f["name"]]
    slot_packs = []
    slot_total = 0
    
    print(f"\n{'='*60}")
    print(f"  {f['name']} ({f['start']}~{f['end']})")
    print(f"{'='*60}")
    
    for r in rows:
        name = r['iap_id_name']
        rev = float(r['revenue'])
        
        # 检查是否属于槽位
        in_slot = False
        for kw in slot_cfg["include"]:
            if kw in name:
                excluded = False
                for ex in slot_cfg["exclude"]:
                    if ex in name:
                        excluded = True
                        break
                if not excluded:
                    in_slot = True
                    break
        
        if in_slot:
            slot_packs.append({"name": name, "rev": rev, "buyers": int(r['pay_user_cnt']), "type2": r['iap_type2']})
            slot_total += rev
            print(f"  ✅ {name:45s}  ${rev:>10,.2f}  (buyers={r['pay_user_cnt']})")
    
    print(f"  {'─'*60}")
    print(f"  槽位合计: ${slot_total:>10,.2f}  ({len(slot_packs)} 个礼包)")
    
    results[f["name"]] = {
        "format": {
            "万圣节": "传统GACHA",
            "感恩节": "传统GACHA",
            "圣诞节": "弹珠GACHA",
            "春节": "骰子",
            "情人节": "云上探宝",
            "科技节": "推币机+弹珠",
        }[f["name"]],
        "slot_total": round(slot_total, 2),
        "packs": slot_packs,
    }

# 汇总
print(f"\n{'='*60}")
print(f"  皮肤抽奖槽位 横向汇总")
print(f"{'='*60}")
for name, data in results.items():
    print(f"  {name:8s}  [{data['format']:12s}]  ${data['slot_total']:>10,.2f}  ({len(data['packs'])} packs)")

with open(r'C:\ADHD_agent\_tmp_skin_slot_final.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nDone: _tmp_skin_slot_final.json")
