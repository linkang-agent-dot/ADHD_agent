"""
多活动评级 Final v4:
  使用 Google Sheet "评分表（每月更新）" 的四维体系：
    变现力    (50%) = ARPU × 付费率(%) / 10 → 评分
    转化力    (25%) = 付费率(%) → 评分
    鲸鱼依赖度 (15%) = 超R收入占比(%) → 评分
    分层清晰度 (10%) = chaoR付费人数 / xiaoR付费人数 → 评分

  综合得分 = 变现力×0.5 + 转化力×0.25 + 鲸鱼依赖度×0.15 + 分层清晰度×0.10
  等级: ≥73.5→A, 56≤x<73.5→B, 41≤x<56→C, <41→D
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

# 活动分组 CASE WHEN（和 v3 一致，合并同类 AAA）
CASE_WHEN = """
        CASE
            WHEN d.iap_id_name = '挖孔小游戏礼包'                     THEN '科技节-挖孔小游戏'
            WHEN d.iap_id_name IN ('推币机随机GACHA礼包','推币机礼包')  THEN '科技节-推币机'
            WHEN d.iap_id_name IN ('科技节高级通行证_2025','科技节初级通行证_2025') THEN '科技节-通行证'
            WHEN d.iap_id_name = '科技节自选周卡'                      THEN '科技节-周卡'
            WHEN d.iap_id_name = '2026科技节弹珠GACHA'                THEN '科技节-弹珠GACHA'
            WHEN d.iap_id_name = '2026科技节集结奖励解锁礼包'           THEN '科技节-集结奖励'
            WHEN d.iap_id_name = '2026科技节wonder巨猿砸蛋锤礼包'      THEN '科技节-巨猿砸蛋锤'
            WHEN d.iap_id_name IN ('挖矿小游戏活动','挖矿小游戏',
                '挖矿小游戏-产量翻倍特权','挖矿小游戏-卡包礼包-节日版本',
                '节日挖矿-砍价礼包-折扣5','节日挖矿-砍价礼包')          THEN '节日-挖矿小游戏'
            WHEN d.iap_id_name IN ('2025复活节大富翁礼包','节日大富翁组队礼包',
                '节日大富翁','节日大富翁礼包')                           THEN '节日-大富翁'
            WHEN d.iap_id_name = '2025深海节-节日礼包团购'             THEN '深海节-节日礼包团购'
            WHEN d.iap_id_name IN ('2025复活节强消耗触发礼包',
                '2025复活节-强消耗抽奖券礼包')                          THEN '复活节-强消耗'
            WHEN d.iap_id_name IN ('2026科技节-行军表情','2026复活节-行军特效') THEN '节日-行军外观'
            WHEN d.iap_id_name IN ('周年庆预购连锁_schema6',
                '周年庆预购连锁礼包_schema3-5')                         THEN '周年庆-预购连锁'
            WHEN d.iap_id_name = '25感恩节每日补给升级礼包'             THEN '感恩节-每日补给'
            WHEN d.iap_id_name = '万圣节小连锁随机礼包'                THEN '万圣节-小连锁'
            WHEN d.iap_id_name = '情人节BP'                           THEN '情人节-BP'
            WHEN d.iap_id_name = '情人节bingo活动宝箱礼包'             THEN '情人节-bingo'
            WHEN d.iap_id_name = '对对碰'                             THEN '节日-对对碰'
            WHEN d.iap_id_name = '限时抢购'                           THEN '节日-限时抢购'
            WHEN d.iap_id_name = '掉落转付费礼包'                      THEN '节日-掉落转付费'
            WHEN d.iap_id_name = '2023装饰兑换券礼包'                  THEN '节日-装饰兑换券'
            WHEN d.iap_id_name = '改造猴特权-节日版'                   THEN '节日-改造猴特权'
            WHEN d.iap_id_name IN ('2025周年庆累充服务器礼包',
                '2025深海节累充服务器礼包')                             THEN '节日-累充'
            ELSE 'other'
        END
"""

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
        {CASE_WHEN} AS activity,
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

print("查询 R级分解（含 chaoR/xiaoR）...")
rows = execute_sql(sql, 'TRINO_AWS')
print(f"返回 {len(rows)} 行")

from collections import defaultdict
data = defaultdict(lambda: {'pay_total': 0, 'rlevel': {}})
for r in rows:
    act, rl = r['activity'], r['rlevel']
    pay, cnt = float(r['pay_total'] or 0), int(r['pay_cnt'] or 0)
    data[act]['pay_total'] += pay
    if rl not in data[act]['rlevel']:
        data[act]['rlevel'][rl] = {'cnt': 0, 'pay': 0}
    data[act]['rlevel'][rl]['cnt'] += cnt
    data[act]['rlevel'][rl]['pay'] += pay

# ===== 评分函数 =====
def score_xianli(v):
    """变现力: ARPU × 付费率(%) / 10"""
    if v >= 40:  return 100
    if v >= 10:  return 85
    if v >= 2.5: return 70
    if v >= 1.5: return 55
    if v >= 0.2: return 40
    return 20

def score_zhuanhua(v):
    """转化力: 付费率(%)"""
    if v >= 20:  return 100
    if v >= 15:  return 80
    if v >= 10:  return 60
    if v >= 5:   return 40
    return 20

def score_jingyu(v):
    """鲸鱼依赖度: 超R收入占比(%), 50-70%最健康"""
    if 50 <= v <= 70: return 100
    if (45 <= v < 50) or (70 < v <= 75): return 85
    if (40 <= v < 45) or (75 < v <= 80): return 70
    if (35 <= v < 40) or (80 < v <= 85): return 55
    return 40

def score_fenceng(v):
    """
    分层清晰度: chaoR人数 / xiaoR人数
    3-8x 最健康（超R明显更愿意付但小R仍参与），过大代表小R完全不买（鲸鱼专属），过小代表无分层
    """
    if 3 <= v <= 8:   return 100   # 最佳梯度
    if (2 <= v < 3) or (8 < v <= 15):  return 80
    if (1.5 <= v < 2) or (15 < v <= 30): return 60
    if (1 <= v < 1.5) or (30 < v <= 50): return 40
    return 20   # <1x（无分层）或 >50x（纯鲸鱼）

def grade(s):
    if s >= 73.5: return 'A'
    if s >= 56:   return 'B'
    if s >= 41:   return 'C'
    return 'D'

# ===== 计算各活动指标 =====
# 原始活动名映射（用于表内 C列）
ORIGIN_NAMES = {
    '科技节-挖孔小游戏': '挖孔小游戏礼包',
    '科技节-推币机': '推币机随机GACHA礼包, 推币机礼包',
    '科技节-通行证': '科技节高级通行证_2025, 科技节初级通行证_2025',
    '科技节-周卡': '科技节自选周卡',
    '科技节-弹珠GACHA': '2026科技节弹珠GACHA',
    '科技节-集结奖励': '2026科技节集结奖励解锁礼包',
    '科技节-巨猿砸蛋锤': '2026科技节wonder巨猿砸蛋锤礼包',
    '节日-挖矿小游戏': '挖矿小游戏活动, 挖矿小游戏, 挖矿小游戏-产量翻倍特权, 节日挖矿-砍价礼包',
    '节日-大富翁': '2025复活节大富翁礼包, 节日大富翁组队礼包, 节日大富翁, 节日大富翁礼包',
    '深海节-节日礼包团购': '2025深海节-节日礼包团购',
    '复活节-强消耗': '2025复活节强消耗触发礼包, 2025复活节-强消耗抽奖券礼包',
    '节日-行军外观': '2026科技节-行军表情, 2026复活节-行军特效',
    '周年庆-预购连锁': '周年庆预购连锁_schema6, 周年庆预购连锁礼包_schema3-5',
    '感恩节-每日补给': '25感恩节每日补给升级礼包',
    '万圣节-小连锁': '万圣节小连锁随机礼包',
    '情人节-BP': '情人节BP',
    '情人节-bingo': '情人节bingo活动宝箱礼包',
    '节日-对对碰': '对对碰',
    '节日-限时抢购': '限时抢购',
    '节日-掉落转付费': '掉落转付费礼包',
    '节日-装饰兑换券': '2023装饰兑换券礼包',
    '节日-改造猴特权': '改造猴特权-节日版',
    '节日-累充': '2025周年庆累充服务器礼包, 2025深海节累充服务器礼包',
}

results = []
for act, d in data.items():
    total_pay  = round(d['pay_total'], 2)
    rl = d['rlevel']
    total_num  = sum(v['cnt'] for v in rl.values())
    arppu      = round(total_pay / total_num, 2) if total_num > 0 else 0
    pay_rate   = round(total_num / TOTAL_PAYERS * 100, 2)
    arpu       = round(total_pay / TOTAL_PAYERS, 2)
    chaor_pay  = rl.get('chaoR', {}).get('pay', 0)
    chaor_cnt  = rl.get('chaoR', {}).get('cnt', 0)
    xiaor_cnt  = rl.get('xiaoR', {}).get('cnt', 0)
    chaor_pct  = round(chaor_pay / total_pay * 100, 1) if total_pay > 0 else 0

    # 分层清晰度：chaoR人数 / xiaoR人数（用比率衡量层级分化）
    # xiaoR=0 说明小R完全不参与，视为极端（>50x，D级）
    fenceng_ratio = round(chaor_cnt / xiaor_cnt, 2) if xiaor_cnt > 0 else 99.0

    # 四维评分
    xianli_val  = round(arpu * pay_rate / 10, 3)
    s_xianli    = score_xianli(xianli_val)
    s_zhuanhua  = score_zhuanhua(pay_rate)
    s_jingyu    = score_jingyu(chaor_pct)
    s_fenceng   = score_fenceng(fenceng_ratio)
    total_score = round(s_xianli*0.5 + s_zhuanhua*0.25 + s_jingyu*0.15 + s_fenceng*0.10, 1)
    lv = grade(total_score)

    results.append({
        'activity': act,
        'origin': ORIGIN_NAMES.get(act, act),
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

print(f"\n分母: {TOTAL_PAYERS:,}  四维体系评分\n")
print(f"{'活动':<22} {'总收入':>10} {'ARPPU':>7} {'付费率':>7} {'超R%':>6} {'变现力':>5} {'转化力':>5} {'鲸鱼':>5} {'分层':>5} {'得分':>6} {'级'}  {'分层比'}")
print("-"*108)
for r in results:
    fc = f"{r['fenceng_ratio']:.1f}x ({r['chaor_cnt']}/{r['xiaor_cnt']})"
    print(f"{r['activity']:<22} {r['pay_total']:>10,.0f} {r['arppu']:>7.1f} {r['pay_rate']:>6.2f}% "
          f"{r['chaor_pct']:>5.1f}% {r['s_xianli']:>5} {r['s_zhuanhua']:>5} {r['s_jingyu']:>5} "
          f"{r['s_fenceng']:>5} {r['total_score']:>6.1f}  {r['grade']}  {fc}")

with open(r'C:\ADHD_agent\_tmp_rating_v4.json', 'w', encoding='utf-8') as f:
    json.dump({'denom': TOTAL_PAYERS, 'results': results}, f, ensure_ascii=False, indent=2)
print("\n已保存到 _tmp_rating_v4.json")
