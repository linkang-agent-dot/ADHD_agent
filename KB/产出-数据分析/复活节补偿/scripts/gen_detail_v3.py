import sys; sys.stdout.reconfigure(encoding='utf-8')
import json, csv
from collections import defaultdict, Counter

with open(r'C:/Users/linkang/Downloads/oap_all_records.json', 'r') as f:
    db_data = json.load(f)

stage1_map = {
    2000:  (1000, 1),
    5000:  (2500, 3),
    10000: (5000, 10),
    20000: (10000, 22),
    30000: (15000, 40),
    50000: (25000, 85),
}
tier_order = [2000, 5000, 10000, 20000, 30000, 50000]

player_exchanges = defaultdict(list)
for r in db_data['data']:
    if r['change_type'] == '2' and r['asset_id'] == '11631001':
        player_exchanges[r['user_id']].append({
            'coins': r['change_count'], 'server': r['server_id']
        })

reward_paired = defaultdict(lambda: {'coins': 0, 'boxes': 0})
for r in db_data['data']:
    if r['change_type'] == '1':
        key = (r['user_id'], r['created_at'])
        if r['asset_id'] == '11631001':
            reward_paired[key]['coins'] = r['change_count']
        elif r['asset_id'] == '111110264':
            reward_paired[key]['boxes'] = r['change_count']

player_s1_rewards = defaultdict(list)
for (uid, ts), val in reward_paired.items():
    player_s1_rewards[uid].append(val)

purchase_records = []
with open(r'C:/Users/linkang/Downloads/p2_monkey_coin_0415_0420.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 6:
            continue
        purchase_records.append({'player': row[1], 'package': row[2], 'coins': float(row[4])})

player_purchases = defaultdict(list)
for r in purchase_records:
    if r['package'] != '':  # all purchases (ape + monkey_currency)
        player_purchases[r['player']].append(r)

all_players = sorted(player_exchanges.keys())

# Build one row per player
rows = []
for pid in all_players:
    srv = player_exchanges[pid][0]['server']
    purchases = player_purchases.get(pid, [])
    exchanges = player_exchanges[pid]
    rewards = player_s1_rewards.get(pid, [])

    # Purchase summary - group by package short name
    pkg_counter = Counter()
    for p in purchases:
        pkg = p['package'].replace('_monkey_currency', '').replace('_cd_oap2', '').replace('_cd_oap_month2', '(月)').replace('_cd_oap_month1', '(月)').replace('_cd_oap_anni', '(周年)').replace('_cn', '(国)')
        pkg_counter[f"{pkg}({int(p['coins'])}币)"] += 1
    purch_parts = [f"{name}x{n}" for name, n in sorted(pkg_counter.items())]
    purch_total = sum(int(p['coins']) for p in purchases)
    purch_str = ', '.join(purch_parts) if purch_parts else '-'

    # Exchange count per tier (for compensation calc only)
    ex_counter = Counter(ex['coins'] for ex in exchanges)

    # Stage 1 delivered summary
    rwd_counter = Counter()
    rwd_box_counter = Counter()
    for rw in rewards:
        rwd_counter[rw['coins']] += 1
        rwd_box_counter[rw['coins']] += rw['boxes']
    s1_coins_total = sum(rw['coins'] for rw in rewards)
    s1_boxes_total = sum(rw['boxes'] for rw in rewards)
    s1_parts = [f"{c}c+{rwd_box_counter[c]}b" for c in sorted(rwd_counter.keys())]
    s1_str = ', '.join(s1_parts) if s1_parts else '无'

    # Compensation calc per tier
    rwd_coin_avail = Counter(rw['coins'] for rw in rewards)
    comp_coins = 0
    comp_boxes = 0
    comp_parts = []

    for ex_amt in sorted(ex_counter.keys()):
        n = ex_counter[ex_amt]
        s1c, s1b = stage1_map.get(ex_amt, (0, 0))
        if s1c == 0:
            continue
        s1_got = min(rwd_coin_avail.get(s1c, 0), n)
        s1_miss = n - s1_got
        if s1c in rwd_coin_avail:
            rwd_coin_avail[s1c] = max(0, rwd_coin_avail[s1c] - s1_got)

        tier_comp_c = s1c * s1_miss + s1c * n  # s1 missing + s2 all
        tier_comp_b = s1b * s1_miss + s1b * n
        comp_coins += tier_comp_c
        comp_boxes += tier_comp_b

        if s1_miss > 0:
            comp_parts.append(f"{ex_amt}档: 阶段一缺{s1_miss}次+阶段二{n}次={tier_comp_c}c+{tier_comp_b}b")
        else:
            comp_parts.append(f"{ex_amt}档: 阶段二{n}次={tier_comp_c}c+{tier_comp_b}b")

    comp_detail = '; '.join(comp_parts)

    rows.append({
        'srv': srv, 'pid': pid,
        'purch_str': purch_str, 'purch_total': purch_total,
        's1_str': s1_str, 's1_coins': s1_coins_total, 's1_boxes': s1_boxes_total,
        'comp_detail': comp_detail,
        'comp_coins': comp_coins, 'comp_boxes': comp_boxes,
    })

# Write CSV
outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv'
with open(outpath, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        '服务器ID', '玩家ID',
        '充值明细', '充值总猿猴币',
        '阶段一已领明细', '阶段一已领猿猴币', '阶段一已领宝箱',
        '补发计算过程',
        '补发猿猴币', '补发自选宝箱',
    ])
    for r in rows:
        writer.writerow([
            r['srv'], r['pid'],
            r['purch_str'], int(r['purch_total']),
            r['s1_str'], r['s1_coins'], r['s1_boxes'],
            r['comp_detail'],
            r['comp_coins'], r['comp_boxes'],
        ])

print(f'玩家数: {len(rows)}')
print(f'已保存: {outpath}')

# Verify totals
tc = sum(r['comp_coins'] for r in rows)
tb = sum(r['comp_boxes'] for r in rows)
print(f'补发总计: {tc:,} 猿猴币 + {tb:,} 自选宝箱')
