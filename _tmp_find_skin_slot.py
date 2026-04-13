# -*- coding: utf-8 -*-
"""
查各节日"皮肤抽奖"槽位的所有关联礼包
重点：找出春节的骰子系列
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

FESTIVALS = [
    {"name": "万圣节",    "start": "2025-10-17", "end": "2025-11-06"},
    {"name": "感恩节",    "start": "2025-11-13", "end": "2025-12-04"},
    {"name": "圣诞节",    "start": "2025-12-12", "end": "2026-01-01"},
    {"name": "春节",      "start": "2026-01-13", "end": "2026-02-08"},
    {"name": "情人节",    "start": "2026-02-11", "end": "2026-03-05"},
    {"name": "科技节",    "start": "2026-03-13", "end": "2026-04-03"},
]

# 春节用完整范围 01-13~02-08（按用户要求，独立周期只拆推币机/一番赏/砍价/抢购）

def query_skin_packs(f):
    from datetime import datetime, timedelta
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
          AND iap_type2 = '混合-节日活动-节日皮肤'
    ) b2 ON b1.iap_id = b2.iap_id
    GROUP BY b2.iap_id_name, b2.iap_type2
    ORDER BY revenue DESC
    """
    return api.execute_sql(SQL)

# 春节额外查骰子关键词（可能分布在各 iap_type2）
def query_dice_packs():
    SQL = """
    SELECT
        b2.iap_id_name,
        b2.iap_type,
        b2.iap_type2,
        COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
        COUNT(*) AS buy_times,
        CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
    FROM (
        SELECT user_id, iap_id, pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN '2026-01-12' AND '2026-02-08'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-01-13' AND date '2026-02-08'
          AND pay_status = 1
          AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    ) b1
    INNER JOIN (
        SELECT iap_id, iap_id_name, iap_type, iap_type2
        FROM v1041.dim_iap
    ) b2 ON b1.iap_id = b2.iap_id
    WHERE b2.iap_id_name LIKE '%骰子%'
       OR b2.iap_id_name LIKE '%骰%'
       OR b2.iap_id_name LIKE '%dice%'
       OR b2.iap_id_name LIKE '%大富翁%'
       OR b2.iap_id_name LIKE '%春节GACHA%'
       OR b2.iap_id_name LIKE '%春节随机%'
       OR b2.iap_id_name LIKE '%登月%'
       OR b2.iap_id_name LIKE '%春节抽奖%'
    GROUP BY b2.iap_id_name, b2.iap_type, b2.iap_type2
    ORDER BY revenue DESC
    """
    return api.execute_sql(SQL)

# 情人节查云上探宝
def query_valentine_explore():
    SQL = """
    SELECT
        b2.iap_id_name,
        b2.iap_type,
        b2.iap_type2,
        COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
        CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
    FROM (
        SELECT user_id, iap_id, pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN '2026-02-10' AND '2026-03-05'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-02-11' AND date '2026-03-05'
          AND pay_status = 1
          AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    ) b1
    INNER JOIN (
        SELECT iap_id, iap_id_name, iap_type, iap_type2
        FROM v1041.dim_iap
        WHERE iap_type = '混合-节日活动'
    ) b2 ON b1.iap_id = b2.iap_id
    WHERE b2.iap_id_name LIKE '%云上%'
       OR b2.iap_id_name LIKE '%探宝%'
    GROUP BY b2.iap_id_name, b2.iap_type, b2.iap_type2
    ORDER BY revenue DESC
    """
    return api.execute_sql(SQL)

results = {}

# 各节日皮肤类全量
for f in FESTIVALS:
    print(f"\n=== {f['name']} ({f['start']}~{f['end']}) 节日皮肤类 ===")
    rows = query_skin_packs(f)
    total = 0
    packs = []
    for r in rows:
        rev = float(r['revenue'])
        total += rev
        packs.append({"name": r['iap_id_name'], "rev": rev, "buyers": int(r['pay_user_cnt'])})
        print(f"  {r['iap_id_name']:45s}  buyers={str(r['pay_user_cnt']):>5s}  rev=${rev:>10,.2f}")
    print(f"  {'皮肤类合计':45s}  ${total:>10,.2f}")
    results[f['name']] = {"skin_packs": packs, "skin_total": total}

# 春节骰子/大富翁详查
print(f"\n=== 春节 骰子/大富翁/GACHA 关键词搜索 ===")
dice_rows = query_dice_packs()
for r in dice_rows:
    rev = float(r['revenue'])
    print(f"  {r['iap_id_name']:45s}  type2={r['iap_type2']:35s}  buyers={str(r['pay_user_cnt']):>5s}  rev=${rev:>10,.2f}")

# 情人节云上探宝
print(f"\n=== 情人节 云上探宝 ===")
val_rows = query_valentine_explore()
for r in val_rows:
    rev = float(r['revenue'])
    print(f"  {r['iap_id_name']:45s}  type2={r['iap_type2']:35s}  buyers={str(r['pay_user_cnt']):>5s}  rev=${rev:>10,.2f}")

# 保存结果
with open(r'C:\ADHD_agent\_tmp_skin_slot_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nDone: _tmp_skin_slot_data.json")
