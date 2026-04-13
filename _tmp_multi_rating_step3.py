"""
多活动评级 Step3: 
  - 用 CASE WHEN 按活动分组，精确 count distinct user_id
  - 同时查各活动对应分服的活跃人数（登录用户数），作为付费率分母
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

# ======= Part A: 唯一付费人数 + 收入 + R级分解 =======
sql_rev = """
WITH rlevel_snap AS (
    SELECT user_id, max_by(rlevel, create_date) AS rlevel
    FROM v1041.da_user_rlevel_pay_ratio
    WHERE create_date BETWEEN '2026-03-11' AND '2026-04-04'
    GROUP BY 1
),
orders AS (
    SELECT
        o.user_id,
        o.server_id,
        d.iap_id_name,
        CASE
            WHEN d.iap_id_name = '挖孔小游戏礼包'                  THEN '科技节-挖孔小游戏'
            WHEN d.iap_id_name IN ('推币机随机GACHA礼包','推币机礼包') THEN '科技节-推币机'
            WHEN d.iap_id_name IN ('科技节高级通行证_2025','科技节初级通行证_2025') THEN '科技节-通行证'
            WHEN d.iap_id_name = '科技节自选周卡'                   THEN '科技节-周卡'
            WHEN d.iap_id_name = '2026科技节弹珠GACHA'             THEN '科技节-弹珠GACHA'
            WHEN d.iap_id_name = '2026科技节-行军表情'              THEN '科技节-行军表情'
            WHEN d.iap_id_name = '2026科技节集结奖励解锁礼包'        THEN '科技节-集结奖励'
            WHEN d.iap_id_name = '2026科技节wonder巨猿砸蛋锤礼包'   THEN '科技节-巨猿砸蛋锤'
            WHEN d.iap_id_name IN ('挖矿小游戏活动','挖矿小游戏',
                '挖矿小游戏-产量翻倍特权','挖矿小游戏-卡包礼包-节日版本',
                '节日挖矿-砍价礼包-折扣5','节日挖矿-砍价礼包')       THEN '挖矿小游戏'
            WHEN d.iap_id_name IN ('2025复活节大富翁礼包','节日大富翁组队礼包',
                '节日大富翁','节日大富翁礼包')                        THEN '大富翁'
            WHEN d.iap_id_name IN ('2025深海节-节日礼包团购','2025深海节累充服务器礼包') THEN '深海节'
            WHEN d.iap_id_name IN ('2025复活节强消耗触发礼包','2025复活节-强消耗抽奖券礼包') THEN '复活节-强消耗'
            WHEN d.iap_id_name = '2026复活节-行军特效'              THEN '复活节-行军特效'
            WHEN d.iap_id_name IN ('2025周年庆累充服务器礼包','周年庆预购连锁_schema6','周年庆预购连锁礼包_schema3-5') THEN '周年庆'
            WHEN d.iap_id_name = '25感恩节每日补给升级礼包'          THEN '感恩节-每日补给'
            WHEN d.iap_id_name = '万圣节小连锁随机礼包'              THEN '万圣节-小连锁'
            WHEN d.iap_id_name IN ('情人节BP','情人节bingo活动宝箱礼包') THEN '情人节'
            WHEN d.iap_id_name = '对对碰'                          THEN '对对碰'
            WHEN d.iap_id_name = '限时抢购'                        THEN '限时抢购'
            WHEN d.iap_id_name = '掉落转付费礼包'                   THEN '掉落转付费'
            WHEN d.iap_id_name = '2023装饰兑换券礼包'               THEN '装饰兑换券'
            WHEN d.iap_id_name = '改造猴特权-节日版'                THEN '改造猴特权'
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
      AND d.iap_id_name IN (
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
      )
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

print("Part A: 查询唯一付费人数+R级分解...")
rows_rev = execute_sql(sql_rev, 'TRINO_AWS')
print(f"  返回 {len(rows_rev)} 行")

# ======= Part B: 各活动对应分服活跃人数（登录人数）=======
# 原理：查每个activity的server_id集合，再统计那些server的登录人数
sql_server = """
WITH orders_srv AS (
    SELECT
        CASE
            WHEN d.iap_id_name = '挖孔小游戏礼包'                   THEN '科技节-挖孔小游戏'
            WHEN d.iap_id_name IN ('推币机随机GACHA礼包','推币机礼包') THEN '科技节-推币机'
            WHEN d.iap_id_name IN ('科技节高级通行证_2025','科技节初级通行证_2025') THEN '科技节-通行证'
            WHEN d.iap_id_name = '科技节自选周卡'                    THEN '科技节-周卡'
            WHEN d.iap_id_name = '2026科技节弹珠GACHA'              THEN '科技节-弹珠GACHA'
            WHEN d.iap_id_name = '2026科技节-行军表情'               THEN '科技节-行军表情'
            WHEN d.iap_id_name = '2026科技节集结奖励解锁礼包'         THEN '科技节-集结奖励'
            WHEN d.iap_id_name = '2026科技节wonder巨猿砸蛋锤礼包'    THEN '科技节-巨猿砸蛋锤'
            WHEN d.iap_id_name IN ('挖矿小游戏活动','挖矿小游戏',
                '挖矿小游戏-产量翻倍特权','挖矿小游戏-卡包礼包-节日版本',
                '节日挖矿-砍价礼包-折扣5','节日挖矿-砍价礼包')        THEN '挖矿小游戏'
            WHEN d.iap_id_name IN ('2025复活节大富翁礼包','节日大富翁组队礼包',
                '节日大富翁','节日大富翁礼包')                         THEN '大富翁'
            WHEN d.iap_id_name IN ('2025深海节-节日礼包团购','2025深海节累充服务器礼包') THEN '深海节'
            WHEN d.iap_id_name IN ('2025复活节强消耗触发礼包','2025复活节-强消耗抽奖券礼包') THEN '复活节-强消耗'
            WHEN d.iap_id_name = '2026复活节-行军特效'               THEN '复活节-行军特效'
            WHEN d.iap_id_name IN ('2025周年庆累充服务器礼包','周年庆预购连锁_schema6','周年庆预购连锁礼包_schema3-5') THEN '周年庆'
            WHEN d.iap_id_name = '25感恩节每日补给升级礼包'           THEN '感恩节-每日补给'
            WHEN d.iap_id_name = '万圣节小连锁随机礼包'               THEN '万圣节-小连锁'
            WHEN d.iap_id_name IN ('情人节BP','情人节bingo活动宝箱礼包') THEN '情人节'
            WHEN d.iap_id_name = '对对碰'                           THEN '对对碰'
            WHEN d.iap_id_name = '限时抢购'                         THEN '限时抢购'
            WHEN d.iap_id_name = '掉落转付费礼包'                    THEN '掉落转付费'
            WHEN d.iap_id_name = '2023装饰兑换券礼包'                THEN '装饰兑换券'
            WHEN d.iap_id_name = '改造猴特权-节日版'                 THEN '改造猴特权'
            ELSE 'other'
        END AS activity,
        o.server_id
    FROM v1041.ods_user_order o
    JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
    WHERE o.partition_date BETWEEN '2026-03-11' AND '2026-04-04'
      AND date(date_add('hour', -8, o.created_at)) BETWEEN date '2026-03-12' AND date '2026-04-03'
      AND o.pay_status = 1
      AND d.iap_id_name IN (
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
      )
    GROUP BY 1, 2
),
login_srv AS (
    SELECT server_id, count(distinct user_id) AS login_cnt
    FROM v1041.ods_user_login
    WHERE partition_date BETWEEN '2026-03-11' AND '2026-04-04'
      AND date(date_add('hour', -8, created_at)) BETWEEN date '2026-03-12' AND date '2026-04-03'
    GROUP BY 1
)
SELECT
    s.activity,
    sum(l.login_cnt) AS login_total,
    count(distinct s.server_id) AS server_cnt
FROM orders_srv s
JOIN login_srv l ON s.server_id = l.server_id
GROUP BY 1
ORDER BY login_total DESC
"""

print("Part B: 查询各活动分服活跃人数...")
rows_login = execute_sql(sql_server, 'TRINO_AWS')
print(f"  返回 {len(rows_login)} 行")
for r in rows_login:
    print(f"  {r['activity']}: {r['login_total']} 活跃, {r['server_cnt']} 服")

# ======= 汇总计算评级指标 =======
from collections import defaultdict

# 构建收入数据
rev_data = defaultdict(lambda: {'pay_total': 0, 'pay_cnt': 0, 'rlevel': {}})
for r in rows_rev:
    act = r['activity']
    rl = r['rlevel']
    pay = float(r['pay_total'] or 0)
    cnt = int(r['pay_cnt'] or 0)
    rev_data[act]['pay_total'] += pay
    rev_data[act]['pay_cnt'] += cnt  # 仍有重复，后面用最大R级代替
    if rl not in rev_data[act]['rlevel']:
        rev_data[act]['rlevel'][rl] = {'cnt': 0, 'pay': 0}
    rev_data[act]['rlevel'][rl]['cnt'] += cnt
    rev_data[act]['rlevel'][rl]['pay'] += pay

# 构建登录数据
login_data = {r['activity']: {'login': int(r['login_total'] or 0), 'servers': int(r['server_cnt'] or 0)}
              for r in rows_login}

# 对于付费人数重复计数：用 sum(rlevel cnt) 为近似值（同活动跨pack会重算，但R级分布准确）
# 实际精确unique payer数 = sum不超过...需再查，但作为近似值可用
# 计算指标
final = {}
for act, d in rev_data.items():
    total_pay = round(d['pay_total'], 2)
    # 精确付费人数: 每个rlevel已是distinct，但跨rlevel求和不重复，所以sum rlevel cnt = 总唯一付费人数
    total_payers = sum(v['cnt'] for v in d['rlevel'].values())
    arppu = round(total_pay / total_payers, 2) if total_payers > 0 else 0
    login_info = login_data.get(act, {'login': 0, 'servers': 0})
    log_num = login_info['login']
    pay_rate = round(total_payers / log_num * 100, 2) if log_num > 0 else None
    arpu = round(total_pay / log_num, 4) if log_num > 0 else None
    chaor_pay = d['rlevel'].get('chaoR', {}).get('pay', 0)
    chaor_pct = round(chaor_pay / total_pay * 100, 1) if total_pay > 0 else 0
    final[act] = {
        'pay_total': total_pay,
        'pay_num': total_payers,
        'arppu': arppu,
        'log_num': log_num,
        'server_cnt': login_info['servers'],
        'pay_rate': pay_rate,
        'arpu': arpu,
        'chaor_pay': round(chaor_pay, 2),
        'chaor_pct': chaor_pct,
        'rlevel': {k: {'cnt': v['cnt'], 'pay': round(v['pay'], 2)} for k, v in d['rlevel'].items()}
    }

# 打印汇总表
print("\n=== 活动评级数据汇总 (3.12-4.03) ===")
hdr = f"{'活动':22s} {'总收入':>12} {'付费人数':>8} {'ARPPU':>8} {'付费率':>7} {'ARPU':>7} {'超R%':>6} {'活跃':>7} {'服数':>5}"
print(hdr)
print("-" * 100)
for act, m in sorted(final.items(), key=lambda x: -x[1]['pay_total']):
    pay_rate_str = f"{m['pay_rate']:.2f}%" if m['pay_rate'] is not None else "N/A"
    arpu_str = f"{m['arpu']:.2f}" if m['arpu'] is not None else "N/A"
    print(f"{act:22s} {m['pay_total']:>12,.2f} {m['pay_num']:>8,} {m['arppu']:>8.2f} "
          f"{pay_rate_str:>7} {arpu_str:>7} {m['chaor_pct']:>5.1f}% {m['log_num']:>7,} {m['server_cnt']:>5}")

with open(r'C:\ADHD_agent\_tmp_multi_final.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print("\n已保存到 _tmp_multi_final.json")
