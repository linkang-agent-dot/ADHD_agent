"""
多活动评级 Step3b: 更细粒度分组重查 + 12474 分母评级
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

TOTAL_PAYERS = 12474

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

sql = f"""
WITH rlevel_snap AS (
    SELECT user_id, max_by(rlevel, create_date) AS rlevel
    FROM v1041.da_user_rlevel_pay_ratio
    WHERE create_date BETWEEN '2026-03-11' AND '2026-04-04'
    GROUP BY 1
),
orders AS (
    SELECT
        o.user_id,
        d.iap_id_name,
        CASE
            WHEN d.iap_id_name = '挖孔小游戏礼包'                    THEN '科技节-挖孔小游戏'
            WHEN d.iap_id_name IN ('推币机随机GACHA礼包','推币机礼包') THEN '科技节-推币机'
            WHEN d.iap_id_name IN ('科技节高级通行证_2025','科技节初级通行证_2025') THEN '科技节-通行证'
            WHEN d.iap_id_name = '科技节自选周卡'                     THEN '科技节-周卡'
            WHEN d.iap_id_name = '2026科技节弹珠GACHA'               THEN '科技节-弹珠GACHA'
            WHEN d.iap_id_name = '2026科技节-行军表情'                THEN '科技节-行军表情'
            WHEN d.iap_id_name = '2026科技节集结奖励解锁礼包'          THEN '科技节-集结奖励'
            WHEN d.iap_id_name = '2026科技节wonder巨猿砸蛋锤礼包'     THEN '科技节-巨猿砸蛋锤'
            WHEN d.iap_id_name IN ('挖矿小游戏活动','挖矿小游戏',
                '挖矿小游戏-产量翻倍特权','挖矿小游戏-卡包礼包-节日版本',
                '节日挖矿-砍价礼包-折扣5','节日挖矿-砍价礼包')         THEN '节日-挖矿小游戏'
            WHEN d.iap_id_name = '2025复活节大富翁礼包'               THEN '复活节-大富翁'
            WHEN d.iap_id_name IN ('节日大富翁组队礼包','节日大富翁','节日大富翁礼包') THEN '节日-大富翁'
            WHEN d.iap_id_name = '2025深海节-节日礼包团购'            THEN '深海节-节日礼包团购'
            WHEN d.iap_id_name = '2025深海节累充服务器礼包'            THEN '深海节-累充'
            WHEN d.iap_id_name IN ('2025复活节强消耗触发礼包','2025复活节-强消耗抽奖券礼包') THEN '复活节-强消耗'
            WHEN d.iap_id_name = '2026复活节-行军特效'                THEN '复活节-行军特效'
            WHEN d.iap_id_name = '2025周年庆累充服务器礼包'            THEN '周年庆-累充'
            WHEN d.iap_id_name IN ('周年庆预购连锁_schema6','周年庆预购连锁礼包_schema3-5') THEN '周年庆-预购连锁'
            WHEN d.iap_id_name = '25感恩节每日补给升级礼包'            THEN '感恩节-每日补给'
            WHEN d.iap_id_name = '万圣节小连锁随机礼包'               THEN '万圣节-小连锁'
            WHEN d.iap_id_name = '情人节BP'                          THEN '情人节-BP'
            WHEN d.iap_id_name = '情人节bingo活动宝箱礼包'            THEN '情人节-bingo'
            WHEN d.iap_id_name = '对对碰'                            THEN '节日-对对碰'
            WHEN d.iap_id_name = '限时抢购'                          THEN '节日-限时抢购'
            WHEN d.iap_id_name = '掉落转付费礼包'                     THEN '节日-掉落转付费'
            WHEN d.iap_id_name = '2023装饰兑换券礼包'                 THEN '节日-装饰兑换券'
            WHEN d.iap_id_name = '改造猴特权-节日版'                  THEN '节日-改造猴特权'
            ELSE 'other'
        END AS activity,
        o.pay_price,
        coalesce(r.rlevel, 'feiR') AS rlevel
    FROM v1041.ods_user_order o
    JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
    LEFT JOIN rlevel_snap r ON o.user_id = r.user_id
    WHERE o.partition_date BETWEEN '2026-03-11' AND '2026-04-04'
      AND date(date_add('hour', -8, o.created_at)) BETWEEN date '2026-03-12' AND date '2026-04-03'
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

print("查询细分活动 R级数据...")
rows = execute_sql(sql, 'TRINO_AWS')
print(f"返回 {len(rows)} 行")

# 聚合
from collections import defaultdict
data = defaultdict(lambda: {'pay_total': 0, 'rlevel': {}})
for r in rows:
    act = r['activity']
    rl  = r['rlevel']
    pay = float(r['pay_total'] or 0)
    cnt = int(r['pay_cnt'] or 0)
    data[act]['pay_total'] += pay
    if rl not in data[act]['rlevel']:
        data[act]['rlevel'][rl] = {'cnt': 0, 'pay': 0}
    data[act]['rlevel'][rl]['cnt'] += cnt
    data[act]['rlevel'][rl]['pay'] += pay

# 评分函数
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

results = []
for act, d in data.items():
    total_pay  = round(d['pay_total'], 2)
    total_pay_num = sum(v['cnt'] for v in d['rlevel'].values())
    arppu      = round(total_pay / total_pay_num, 2) if total_pay_num > 0 else 0
    pay_rate   = round(total_pay_num / TOTAL_PAYERS * 100, 2)
    arpu       = round(total_pay / TOTAL_PAYERS, 2)
    chaor_pay  = d['rlevel'].get('chaoR', {}).get('pay', 0)
    chaor_pct  = round(chaor_pay / total_pay * 100, 1) if total_pay > 0 else 0

    s_arppu    = score_arppu(arppu)
    s_pay_rate = score_pay_rate(pay_rate)
    s_arpu     = score_arpu(arpu)
    s_chaor    = score_chaor(chaor_pct)
    total_score = round(s_arppu*0.4 + s_pay_rate*0.3 + s_arpu*0.2 + s_chaor*0.1, 1)
    lv, tier   = grade(total_score)

    results.append({
        'activity': act, 'pay_total': total_pay, 'pay_num': total_pay_num,
        'arppu': arppu, 'pay_rate': pay_rate, 'arpu': arpu,
        'chaor_pct': chaor_pct, 'total_score': total_score, 'grade': lv, 'tier': tier,
    })

results.sort(key=lambda x: -x['total_score'])

print(f"\n分母: {TOTAL_PAYERS:,} (全量登录活跃付费玩家)\n")
print(f"{'活动':24s} {'收入':>12} {'付费人':>7} {'ARPPU':>7} {'付费率':>7} {'ARPU':>6} {'超R%':>6} | {'得分':>6} {'等级':>3} {'梯队':>3}")
print("-" * 110)
for r in results:
    print(f"{r['activity']:24s} {r['pay_total']:>12,.0f} {r['pay_num']:>7,} "
          f"{r['arppu']:>7.1f} {r['pay_rate']:>6.2f}% {r['arpu']:>6.2f} {r['chaor_pct']:>5.1f}% "
          f"| {r['total_score']:>6.1f}  {r['grade']:>3}  {r['tier']:>3}")

with open(r'C:\ADHD_agent\_tmp_multi_rating_final.json', 'w', encoding='utf-8') as f:
    json.dump({'denom': TOTAL_PAYERS, 'results': results}, f, ensure_ascii=False, indent=2)
print(f"\n已保存到 _tmp_multi_rating_final.json")
