"""
多活动评级 Step1: 查 dim_iap 找到37个礼包名对应的 iap_id
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

# 用户给出的礼包名（精确名+模糊匹配组合）
PACK_NAMES_EXACT = [
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

name_list = "','".join(PACK_NAMES_EXACT)
sql = f"""
SELECT iap_id, iap_id_name
FROM v1041.dim_iap
WHERE iap_id_name IN ('{name_list}')
ORDER BY iap_id_name, iap_id
"""

print("查询 dim_iap 精确匹配...")
rows = execute_sql(sql, 'TRINO_AWS')
print(f"精确匹配结果: {len(rows)} 条")

# 按名称分组统计
by_name = {}
for r in rows:
    name = r['iap_id_name']
    if name not in by_name:
        by_name[name] = []
    by_name[name].append(r['iap_id'])

print("\n--- 精确匹配汇总 ---")
matched_names = set(by_name.keys())
for name in PACK_NAMES_EXACT:
    ids = by_name.get(name, [])
    if ids:
        print(f"[OK] {name}: {len(ids)} iap_id")
    else:
        print(f"[NO] {name}: not found, need LIKE")

unmatched = [n for n in PACK_NAMES_EXACT if n not in matched_names]
print(f"\n未精确匹配: {len(unmatched)} 个")

# 对未匹配的做LIKE模糊搜索
if unmatched:
    print("\n执行LIKE模糊查询...")
    like_parts = " OR ".join([f"iap_id_name LIKE '%{n}%'" for n in unmatched])
    sql2 = f"""
    SELECT iap_id, iap_id_name
    FROM v1041.dim_iap
    WHERE {like_parts}
    ORDER BY iap_id_name, iap_id
    """
    rows2 = execute_sql(sql2, 'TRINO_AWS')
    print(f"LIKE模糊匹配结果: {len(rows2)} 条")
    for r in rows2:
        print(f"  {r['iap_id_name']}: {r['iap_id']}")
    rows.extend(rows2)

# 保存全部结果
all_ids = list({r['iap_id'] for r in rows})
all_name_map = {r['iap_id']: r['iap_id_name'] for r in rows}

with open(r'C:\ADHD_agent\_tmp_multi_iap_map.json', 'w', encoding='utf-8') as f:
    json.dump({'by_name': by_name, 'id_to_name': all_name_map, 'all_ids': all_ids}, f, ensure_ascii=False, indent=2)

print(f"\n共找到 iap_id: {len(all_ids)} 个")
print("已保存到 _tmp_multi_iap_map.json")
