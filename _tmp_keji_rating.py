"""
科技节 2025 (3.13-4.03) 付费评级数据查询
- 科技节专属礼包: 挖孔小游戏 + 推币机 + 科技节高级通行证
- R级分母: 来自整体付费数据 (活跃17972)
"""
import sys, json, os
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

# 科技节专属礼包 iap_ids（含完整后缀，与 ods_user_order 一致）
KEJI_IAPS = [
    '2013505006_normal', '2013505013_normal', '2013505014_normal', '2013505015_normal',
    '2013505016_normal', '2013505017_normal', '2013505020_normal', '2013505028_normal',
    '2013510220_random', '2013510222_random', '2013510227_normal',
    '201390129_battle_pass'
]
iap_list = "','".join(KEJI_IAPS)

# SQL: 科技节专属礼包 按R级分解 (3.13-4.03)
sql = f"""
WITH pay_info AS (
    SELECT
        a.user_id,
        coalesce(rlevel, 'feiR') AS rlevel,
        sum(a.pay_price) AS pay_price
    FROM (
        SELECT user_id, pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN '2026-03-12' AND '2026-04-03'
        AND date(date_add('hour', -8, created_at)) BETWEEN date '2026-03-13' AND date '2026-04-03'
        AND pay_status = 1
        AND iap_id IN ('{iap_list}')
    ) a
    LEFT JOIN (
        SELECT user_id, max_by(rlevel, create_date) AS rlevel
        FROM v1041.da_user_rlevel_pay_ratio
        WHERE create_date BETWEEN '2026-03-12' AND '2026-04-03'
        GROUP BY 1
    ) b ON a.user_id = b.user_id
    GROUP BY 1, 2
)
SELECT
    rlevel,
    count(distinct user_id) AS pay_cnt,
    round(sum(pay_price), 2) AS pay_total,
    round(sum(pay_price) / count(distinct user_id), 2) AS arppu
FROM pay_info
GROUP BY 1
ORDER BY pay_total DESC
"""

print("=== 科技节专属礼包 R级付费分解 (3.13-4.03) ===")
rows = execute_sql(sql, 'TRINO_AWS')
results = {}
for row in rows:
    print(row)
    results[row['rlevel']] = row

# 汇总
total_pay = sum(r['pay_total'] for r in results.values())
total_payers = sum(r['pay_cnt'] for r in results.values())
print(f"\n科技节专属礼包合计: 付费总额={total_pay:.2f}, 付费人数={total_payers}")

# 整体数据来自图片 (整体R级基准)
# 活跃人数: 17972 (全服指定服务器 3.13-4.03)
LOG_NUM = 17972

pay_rate = total_payers / LOG_NUM * 100
arpu = total_pay / LOG_NUM
arppu = total_pay / total_payers if total_payers > 0 else 0

chaor_pay = results.get('chaoR', {}).get('pay_total', 0)
chaor_pct = chaor_pay / total_pay * 100 if total_pay > 0 else 0

print(f"\n=== 科技节专属礼包核心指标 ===")
print(f"活跃人数(整体基准): {LOG_NUM}")
print(f"付费人数: {total_payers}")
print(f"付费率: {pay_rate:.2f}%")
print(f"付费总额: {total_pay:.2f}")
print(f"ARPPU: {arppu:.2f}")
print(f"ARPU: {arpu:.2f}")
print(f"超R付费: {chaor_pay:.2f} ({chaor_pct:.1f}%)")

# R级分解
print(f"\n=== R级分解 ===")
for rl in ['chaoR', 'daR', 'zhongR', 'xiaoR', 'feiR']:
    r = results.get(rl, {})
    print(f"{rl}: 人数={r.get('pay_cnt',0)}, 付费={r.get('pay_total',0):.2f}, ARPPU={r.get('arppu',0):.2f}")

out = {
    'log_num': LOG_NUM,
    'pay_num': total_payers,
    'pay_rate': round(pay_rate, 2),
    'pay_total': round(total_pay, 2),
    'arppu': round(arppu, 2),
    'arpu': round(arpu, 2),
    'chaor_pay': round(chaor_pay, 2),
    'chaor_pct': round(chaor_pct, 1),
    'rlevel': {k: {'pay_cnt': v.get('pay_cnt',0), 'pay_total': float(v.get('pay_total',0)), 'arppu': float(v.get('arppu',0))} for k, v in results.items()}
}
with open(r'C:\ADHD_agent\_tmp_keji_metrics.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n已保存到 _tmp_keji_metrics.json")
