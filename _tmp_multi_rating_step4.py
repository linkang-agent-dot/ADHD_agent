"""
多活动评级 Step4:
  - 分母 = 3.12-4.03 内购买过任意一张活动礼包的唯一玩家总数（整体付费人数）
  - 用该分母计算各活动付费率 / ARPU
  - 套 1041 评分体系并输出评级表
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

PACK_NAMES = [
    '挖孔小游戏礼包','推币机随机GACHA礼包','推币机礼包',
    '科技节高级通行证_2025','科技节初级通行证_2025','科技节自选周卡',
    '2026科技节弹珠GACHA','2026科技节-行军表情','2026科技节集结奖励解锁礼包',
    '2026科技节wonder巨猿砸蛋锤礼包',
    '挖矿小游戏活动','挖矿小游戏','挖矿小游戏-产量翻倍特权',
    '挖矿小游戏-卡包礼包-节日版本','节日挖矿-砍价礼包-折扣5','节日挖矿-砍价礼包',
    '2025复活节大富翁礼包','节日大富翁组队礼包','节日大富翁','节日大富翁礼包',
    '2025深海节-节日礼包团购','2025深海节累充服务器礼包',
    '2025复活节强消耗触发礼包','2025复活节-强消耗抽奖券礼包',
    '2026复活节-行军特效',
    '2025周年庆累充服务器礼包','周年庆预购连锁_schema6','周年庆预购连锁礼包_schema3-5',
    '25感恩节每日补给升级礼包','万圣节小连锁随机礼包',
    '情人节BP','情人节bingo活动宝箱礼包',
    '对对碰','限时抢购','掉落转付费礼包','2023装饰兑换券礼包','改造猴特权-节日版'
]

name_list = "','".join(PACK_NAMES)

# 查整体唯一付费人数（分母）
sql_denom = f"""
SELECT count(distinct o.user_id) AS total_payers
FROM v1041.ods_user_order o
JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
WHERE o.partition_date BETWEEN '2026-03-11' AND '2026-04-04'
  AND date(date_add('hour', -8, o.created_at)) BETWEEN date '2026-03-12' AND date '2026-04-03'
  AND o.pay_status = 1
  AND d.iap_id_name IN ('{name_list}')
"""
print("查询整体付费人数（分母）...")
rows_d = execute_sql(sql_denom, 'TRINO_AWS')
TOTAL_PAYERS = int(rows_d[0]['total_payers'])
print(f"整体付费人数（分母）: {TOTAL_PAYERS:,}")

# 读取 step3 的活动数据
with open(r'C:\ADHD_agent\_tmp_multi_final.json', encoding='utf-8') as f:
    raw = json.load(f)

# ===== 评分函数 =====
def score_arppu(v):
    if v >= 100: return 100
    if v >= 70:  return 90
    if v >= 50:  return 80
    if v >= 35:  return 70
    if v >= 25:  return 60
    if v >= 15:  return 45
    return 30

def score_pay_rate(v):
    if v >= 15: return 100
    if v >= 12: return 90
    if v >= 10: return 80
    if v >= 8:  return 70
    if v >= 6:  return 55
    if v >= 4:  return 40
    return 25

def score_arpu(v):
    if v >= 20: return 100
    if v >= 15: return 90
    if v >= 10: return 80
    if v >= 7:  return 70
    if v >= 5:  return 60
    if v >= 3:  return 45
    return 30

def score_chaor(v):
    if 60 <= v <= 70: return 100
    if (55 <= v < 60) or (70 < v <= 75): return 85
    if (50 <= v < 55) or (75 < v <= 80): return 70
    if (45 <= v < 50) or (80 < v <= 85): return 55
    return 40

def grade(score):
    if score >= 85: return 'S', 'T1'
    if score >= 80: return 'A', 'T1'
    if score >= 75: return 'A', 'T2'
    if score >= 65: return 'B', 'T2'
    if score >= 50: return 'C', 'T3'
    return 'D', 'T3'

# ===== 计算并输出评级 =====
results = []
for act, m in raw.items():
    pay_num   = m['pay_num']
    pay_total = m['pay_total']
    arppu     = m['arppu']
    chaor_pct = m['chaor_pct']

    pay_rate = round(pay_num / TOTAL_PAYERS * 100, 2)
    arpu     = round(pay_total / TOTAL_PAYERS, 2)

    s_arppu    = score_arppu(arppu)
    s_pay_rate = score_pay_rate(pay_rate)
    s_arpu     = score_arpu(arpu)
    s_chaor    = score_chaor(chaor_pct)
    total_score = round(s_arppu*0.4 + s_pay_rate*0.3 + s_arpu*0.2 + s_chaor*0.1, 1)
    lv, tier   = grade(total_score)

    results.append({
        'activity': act,
        'pay_total': pay_total,
        'pay_num': pay_num,
        'arppu': arppu,
        'pay_rate': pay_rate,
        'arpu': arpu,
        'chaor_pct': chaor_pct,
        's_arppu': s_arppu,
        's_pay_rate': s_pay_rate,
        's_arpu': s_arpu,
        's_chaor': s_chaor,
        'total_score': total_score,
        'grade': lv,
        'tier': tier,
    })

results.sort(key=lambda x: -x['total_score'])

print(f"\n分母（整体付费人数）: {TOTAL_PAYERS:,}\n")
print(f"{'活动':22s} {'收入':>12} {'付费人':>7} {'ARPPU':>7} {'付费率':>7} {'ARPU':>6} {'超R%':>6} | {'得分':>6} {'等级':>5} {'梯队':>4}")
print("-" * 105)
for r in results:
    print(f"{r['activity']:22s} {r['pay_total']:>12,.0f} {r['pay_num']:>7,} "
          f"{r['arppu']:>7.1f} {r['pay_rate']:>6.2f}% {r['arpu']:>6.2f} {r['chaor_pct']:>5.1f}% "
          f"| {r['total_score']:>6.1f}  {r['grade']:>3}  {r['tier']:>3}")

print(f"\n分母说明: 整体付费人数 = {TOTAL_PAYERS:,}（3.12-4.03 购买过以上任意礼包的唯一玩家数）")

with open(r'C:\ADHD_agent\_tmp_multi_rating_result.json', 'w', encoding='utf-8') as f:
    json.dump({'denom': TOTAL_PAYERS, 'results': results}, f, ensure_ascii=False, indent=2)
print("\n已保存到 _tmp_multi_rating_result.json")
