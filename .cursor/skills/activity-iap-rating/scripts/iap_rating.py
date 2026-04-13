"""
节日礼包付费评级脚本
参考 SKILL.md 获取完整说明

使用方式：
1. 修改下方 CONFIG 区块（礼包列表、时间、分组规则、分母、GSheet 行）
2. cd C:\ADHD_agent\.agents\skills\ai-to-sql\scripts
3. python C:\ADHD_agent\.cursor\skills\activity-iap-rating\scripts\iap_rating.py
"""
import sys, json, subprocess
from collections import defaultdict

sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

# ============================================================
# CONFIG  ← 每次修改这里
# ============================================================

TOTAL_PAYERS = 12474          # 全量登录活跃付费玩家数（向用户确认）

PARTITION_START = '2026-03-11'  # 比 DATE_START 早1天
PARTITION_END   = '2026-04-04'  # 比 DATE_END 晚1天
DATE_START      = '2026-03-12'
DATE_END        = '2026-04-03'

# 礼包名列表（iap_id_name 精确匹配）
PACK_NAMES = [
    # ← 粘贴礼包名列表
]

# 活动分组：礼包名 → 活动简称
# 格式: 'iap_id_name': '节日-类型'  或  ['name1','name2']: '节日-类型'
# 直接写入 CASE_WHEN_SQL 变量（见下方）
CASE_WHEN_SQL = """
        CASE
            -- ← 在这里添加 WHEN 条件
            -- WHEN d.iap_id_name = '礼包A'           THEN '活动1'
            -- WHEN d.iap_id_name IN ('礼包B','礼包C') THEN '活动2'
            ELSE 'other'
        END
"""

# 活动 → (短名, 节日时间)  用于写入 GSheet
SHORT_NAME = {
    # '节日-类型': ('短名', '节日标识'),
    # '科技节-挖孔小游戏': ('挖孔小游戏', '2026科技节'),
}

# GSheet 写入配置
GWS_CMD     = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET = "1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q"
SHEET       = "评分表（每月更新）"
DATA_START  = 36   # 数据第一行（区块标题在 DATA_START-2，列头在 DATA_START-1）

OUTPUT_JSON = r'C:\ADHD_agent\_tmp_iap_rating_result.json'

# ============================================================
# 评分函数（不需要修改）
# ============================================================

def score_xianli(v):
    if v >= 40:  return 100
    if v >= 10:  return 85
    if v >= 2.5: return 70
    if v >= 1.5: return 55
    if v >= 0.2: return 40
    return 20

def score_zhuanhua(v):
    if v >= 20:  return 100
    if v >= 15:  return 80
    if v >= 10:  return 60
    if v >= 5:   return 40
    return 20

def score_jingyu(v):
    if 50 <= v <= 70:  return 100
    if (45 <= v < 50) or (70 < v <= 75): return 85
    if (40 <= v < 45) or (75 < v <= 80): return 70
    if (35 <= v < 40) or (80 < v <= 85): return 55
    return 40

def score_fenceng(v):
    if 3 <= v <= 8:   return 100
    if (2 <= v < 3) or (8 < v <= 15):    return 80
    if (1.5 <= v < 2) or (15 < v <= 30): return 60
    if (1 <= v < 1.5) or (30 < v <= 50): return 40
    return 20

def grade(s):
    if s >= 73.5: return 'A'
    if s >= 56:   return 'B'
    if s >= 41:   return 'C'
    return 'D'

# ============================================================
# STEP 2：查询 Trino
# ============================================================

if not PACK_NAMES:
    print("[ERROR] PACK_NAMES 为空，请先填写礼包列表")
    sys.exit(1)

name_list = "','".join(PACK_NAMES)

sql = f"""
WITH rlevel_snap AS (
    SELECT user_id, max_by(rlevel, create_date) AS rlevel
    FROM v1041.da_user_rlevel_pay_ratio
    WHERE create_date BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'
    GROUP BY 1
),
orders AS (
    SELECT
        o.user_id,
        {CASE_WHEN_SQL} AS activity,
        o.pay_price,
        coalesce(r.rlevel, 'feiR') AS rlevel
    FROM v1041.ods_user_order o
    JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
    LEFT JOIN rlevel_snap r ON o.user_id = r.user_id
    WHERE o.partition_date BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'
      AND date(date_add('hour', -8, o.created_at)) BETWEEN date '{DATE_START}' AND date '{DATE_END}'
      AND o.pay_status = 1
      AND d.iap_id_name IN ('{name_list}')
)
SELECT
    activity,
    rlevel,
    count(distinct user_id) AS pay_cnt,
    round(sum(pay_price), 2)  AS pay_total
FROM orders
GROUP BY 1, 2
ORDER BY activity, pay_total DESC
"""

print("查询 Trino R级分解数据...")
rows = execute_sql(sql, 'TRINO_AWS')
print(f"返回 {len(rows)} 行")

# ============================================================
# STEP 3：聚合
# ============================================================

raw = defaultdict(lambda: {'pay_total': 0, 'rlevel': {}})
for r in rows:
    act, rl = r['activity'], r['rlevel']
    pay, cnt = float(r['pay_total'] or 0), int(r['pay_cnt'] or 0)
    raw[act]['pay_total'] += pay
    if rl not in raw[act]['rlevel']:
        raw[act]['rlevel'][rl] = {'cnt': 0, 'pay': 0}
    raw[act]['rlevel'][rl]['cnt'] += cnt
    raw[act]['rlevel'][rl]['pay'] += pay

# ============================================================
# STEP 4：四维评分
# ============================================================

results = []
for act, d in raw.items():
    total_pay = round(d['pay_total'], 2)
    rl = d['rlevel']
    total_num  = sum(v['cnt'] for v in rl.values())
    arppu      = round(total_pay / total_num, 2) if total_num > 0 else 0
    pay_rate   = round(total_num / TOTAL_PAYERS * 100, 2)
    arpu       = round(total_pay / TOTAL_PAYERS, 2)
    chaor_pay  = rl.get('chaoR', {}).get('pay', 0)
    chaor_cnt  = rl.get('chaoR', {}).get('cnt', 0)
    xiaor_cnt  = rl.get('xiaoR', {}).get('cnt', 0)
    chaor_pct  = round(chaor_pay / total_pay * 100, 1) if total_pay > 0 else 0
    fenceng_ratio = round(chaor_cnt / xiaor_cnt, 2) if xiaor_cnt > 0 else 99.0

    xianli_val  = round(arpu * pay_rate / 10, 3)
    s_xianli    = score_xianli(xianli_val)
    s_zhuanhua  = score_zhuanhua(pay_rate)
    s_jingyu    = score_jingyu(chaor_pct)
    s_fenceng   = score_fenceng(fenceng_ratio)
    total_score = round(s_xianli*0.5 + s_zhuanhua*0.25 + s_jingyu*0.15 + s_fenceng*0.10, 1)
    lv = grade(total_score)

    results.append({
        'activity': act,
        'pay_total': total_pay,
        'pay_num': total_num,
        'arppu': arppu,
        'arpu': arpu,
        'pay_rate': pay_rate,
        'chaor_pct': chaor_pct,
        'chaor_cnt': chaor_cnt,
        'xiaor_cnt': xiaor_cnt,
        'fenceng_ratio': fenceng_ratio,
        'xianli_val': xianli_val,
        's_xianli': s_xianli,
        's_zhuanhua': s_zhuanhua,
        's_jingyu': s_jingyu,
        's_fenceng': s_fenceng,
        'total_score': total_score,
        'grade': lv,
    })

results.sort(key=lambda x: -x['total_score'])

print(f"\n[结果] 分母: {TOTAL_PAYERS:,}  共 {len(results)} 个活动\n")
print(f"{'活动':<22} {'总收入':>10} {'ARPU':>7} {'付费率':>7} {'超R%':>6} {'变现':>5} {'转化':>5} {'鲸鱼':>5} {'分层':>5} {'综合':>6} 级")
print("-"*95)
for r in results:
    print(f"{r['activity']:<22} {r['pay_total']:>10,.0f} {r['arpu']:>7.2f} "
          f"{r['pay_rate']:>6.2f}% {r['chaor_pct']:>5.1f}% "
          f"{r['s_xianli']:>5} {r['s_zhuanhua']:>5} {r['s_jingyu']:>5} "
          f"{r['s_fenceng']:>5} {r['total_score']:>6.1f}  {r['grade']}")

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump({'denom': TOTAL_PAYERS, 'results': results}, f, ensure_ascii=False, indent=2)
print(f"\n已保存: {OUTPUT_JSON}")

# ============================================================
# STEP 5：写入 GSheet
# ============================================================

rows_data = []
for r in results:
    act = r['activity']
    short, jieri = SHORT_NAME.get(act, (act, '未知节日'))
    rows_data.append([
        short,                          # A 活动短名
        1,                              # B 上线次数
        act,                            # C 原始活动（这里用分组名，可替换为礼包名）
        r['total_score'],               # D 综合得分
        r['grade'],                     # E 等级
        r['s_xianli'],                  # F 变现力得分
        r['s_zhuanhua'],                # G 转化力得分
        r['s_jingyu'],                  # H 鲸鱼依赖度得分
        r['s_fenceng'],                 # I 分层清晰度得分
        round(r['arpu'], 4),            # J 付费ARPU
        round(r['pay_rate'], 4),        # K 付费率
        round(r['chaor_pct'], 2),       # L 超R收入占比
        round(r['pay_total'], 2),       # M 总付费额（实际收入RMB）
        '',                             # N 投放内容（留空）
        jieri,                          # O 节日时间
    ])

end_row   = DATA_START + len(rows_data) - 1
range_str = f"'{SHEET}'!A{DATA_START}:O{end_row}"
params    = json.dumps({"spreadsheetId": SPREADSHEET})
body      = json.dumps({
    "valueInputOption": "USER_ENTERED",
    "data": [{"range": range_str, "majorDimension": "ROWS", "values": rows_data}]
}, ensure_ascii=False)

print(f"\n写入 GSheet {range_str} ...")
result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
     '--params', params, '--json', body],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if result.returncode == 0:
    resp = json.loads(result.stdout)
    print(f"[OK] 已写入 {resp.get('totalUpdatedRows',0)} 行, {resp.get('totalUpdatedCells',0)} 格")
else:
    print("[ERROR]", result.stdout[:500])
