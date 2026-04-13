"""
多活动评级 Step2: 查3.12-4.03各礼包组的付费+R级分解
然后按活动分组合并，输出各组核心指标
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

# 精确礼包名列表（来自用户需求）
PACK_NAMES = [
    '挖孔小游戏礼包', '挖矿小游戏活动', '2025深海节-节日礼包团购',
    '2025复活节大富翁礼包', '2026科技节弹珠GACHA', '25感恩节每日补给升级礼包',
    '万圣节小连锁随机礼包', '2026科技节-行军表情', '推币机随机GACHA礼包',
    '2025深海节累充服务器礼包', '节日大富翁组队礼包', '2025周年庆累充服务器礼包',
    '科技节自选周卡', '节日大富翁', '情人节BP', '对对碰',
    '周年庆预购连锁_schema6', '限时抢购', '2026科技节集结奖励解锁礼包',
    '节日挖矿-砍价礼包-折扣5', '2025复活节强消耗触发礼包', '2025复活节-强消耗抽奖券礼包',
    '掉落转付费礼包', '节日大富翁礼包', '2026科技节wonder巨猿砸蛋锤礼包',
    '节日挖矿-砍价礼包', '2023装饰兑换券礼包', '推币机礼包',
    '科技节初级通行证_2025', '2026复活节-行军特效', '科技节高级通行证_2025',
    '改造猴特权-节日版', '周年庆预购连锁礼包_schema3-5',
    '情人节bingo活动宝箱礼包', '挖矿小游戏-产量翻倍特权',
    '挖矿小游戏-卡包礼包-节日版本', '挖矿小游戏'
]

# 活动分组定义（名称 -> 活动标签）
ACTIVITY_MAP = {
    '挖孔小游戏礼包':             '科技节-挖孔小游戏',
    '推币机随机GACHA礼包':        '科技节-推币机',
    '推币机礼包':                 '科技节-推币机',
    '科技节高级通行证_2025':      '科技节-通行证',
    '科技节初级通行证_2025':      '科技节-通行证',
    '科技节自选周卡':             '科技节-周卡',
    '2026科技节弹珠GACHA':       '科技节-弹珠GACHA',
    '2026科技节-行军表情':        '科技节-行军表情',
    '2026科技节集结奖励解锁礼包':  '科技节-集结奖励',
    '2026科技节wonder巨猿砸蛋锤礼包': '科技节-巨猿砸蛋锤',
    '挖矿小游戏活动':             '挖矿小游戏',
    '挖矿小游戏':                 '挖矿小游戏',
    '挖矿小游戏-产量翻倍特权':    '挖矿小游戏',
    '挖矿小游戏-卡包礼包-节日版本':'挖矿小游戏',
    '节日挖矿-砍价礼包-折扣5':   '挖矿小游戏',
    '节日挖矿-砍价礼包':          '挖矿小游戏',
    '2025复活节大富翁礼包':       '大富翁',
    '节日大富翁组队礼包':         '大富翁',
    '节日大富翁':                 '大富翁',
    '节日大富翁礼包':             '大富翁',
    '2025深海节-节日礼包团购':    '深海节',
    '2025深海节累充服务器礼包':   '深海节',
    '2025复活节强消耗触发礼包':   '复活节-强消耗',
    '2025复活节-强消耗抽奖券礼包':'复活节-强消耗',
    '2026复活节-行军特效':        '复活节-行军特效',
    '2025周年庆累充服务器礼包':   '周年庆',
    '周年庆预购连锁_schema6':     '周年庆',
    '周年庆预购连锁礼包_schema3-5':'周年庆',
    '25感恩节每日补给升级礼包':   '感恩节-每日补给',
    '万圣节小连锁随机礼包':       '万圣节-小连锁',
    '情人节BP':                   '情人节',
    '情人节bingo活动宝箱礼包':    '情人节',
    '对对碰':                     '对对碰',
    '限时抢购':                   '限时抢购',
    '掉落转付费礼包':             '掉落转付费',
    '2023装饰兑换券礼包':         '装饰兑换券',
    '改造猴特权-节日版':          '改造猴特权',
}

# 构建SQL查询 - 以iap_id_name分组，R级分解
name_list = "','".join(PACK_NAMES)
sql = f"""
WITH rlevel_snap AS (
    SELECT user_id, max_by(rlevel, create_date) AS rlevel
    FROM v1041.da_user_rlevel_pay_ratio
    WHERE create_date BETWEEN '2026-03-11' AND '2026-04-04'
    GROUP BY 1
),
orders AS (
    SELECT o.user_id, d.iap_id_name, o.pay_price,
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
    iap_id_name,
    rlevel,
    count(distinct user_id) AS pay_cnt,
    round(sum(pay_price), 2) AS pay_total
FROM orders
GROUP BY 1, 2
ORDER BY iap_id_name, pay_total DESC
"""

print("查询 3.12-4.03 各礼包组付费+R级分解...")
rows = execute_sql(sql, 'TRINO_AWS')
print(f"返回 {len(rows)} 行")

# 按 iap_id_name -> activity 聚合
from collections import defaultdict
act_data = defaultdict(lambda: {'pay_total': 0, 'pay_pax': set(), 'rlevel': defaultdict(lambda: {'cnt': set(), 'pay': 0})})

for r in rows:
    name = r['iap_id_name']
    act = ACTIVITY_MAP.get(name, '其他-' + name)
    act_data[act]['pay_total'] += float(r['pay_total'] or 0)
    rl = r['rlevel']
    cnt = int(r['pay_cnt'] or 0)
    pay = float(r['pay_total'] or 0)
    act_data[act]['rlevel'][rl]['pay'] += pay
    # 注意：人数不能直接加（同一人可能买多个礼包），存原始数据
    act_data[act]['rlevel'][rl]['cnt_raw'] = act_data[act]['rlevel'][rl].get('cnt_raw', 0) + cnt

# 整理输出
results = {}
for act, d in act_data.items():
    total_pay = d['pay_total']
    total_payers_approx = sum(v['cnt_raw'] for v in d['rlevel'].values())
    chaor_pay = d['rlevel'].get('chaoR', {}).get('pay', 0)
    chaor_pct = round(chaor_pay / total_pay * 100, 1) if total_pay > 0 else 0
    arppu_approx = round(total_pay / total_payers_approx, 2) if total_payers_approx > 0 else 0
    results[act] = {
        'pay_total': round(total_pay, 2),
        'payers_raw': total_payers_approx,
        'arppu_approx': arppu_approx,
        'chaor_pay': round(chaor_pay, 2),
        'chaor_pct': chaor_pct,
        'rlevel': {
            k: {'cnt': v['cnt_raw'], 'pay': round(v['pay'], 2)}
            for k, v in d['rlevel'].items()
        }
    }

# 按付费总额排序打印
sorted_acts = sorted(results.items(), key=lambda x: -x[1]['pay_total'])
print("\n=== 活动分组汇总 (3.12-4.03) ===")
print(f"{'活动':30s} {'付费总额':>12} {'付费人次':>8} {'ARPPU(近似)':>12} {'超R占比':>8}")
print("-" * 80)
for act, m in sorted_acts:
    print(f"{act:30s} {m['pay_total']:>12,.2f} {m['payers_raw']:>8,} {m['arppu_approx']:>12.2f} {m['chaor_pct']:>7.1f}%")

with open(r'C:\ADHD_agent\_tmp_multi_act_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\n已保存到 _tmp_multi_act_data.json")
