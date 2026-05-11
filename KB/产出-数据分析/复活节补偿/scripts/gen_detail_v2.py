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

player_exchanges = defaultdict(list)
for r in db_data['data']:
    if r['change_type'] == '2' and r['asset_id'] == '11631001':
        player_exchanges[r['user_id']].append({
            'coins': r['change_count'], 'time': r['created_at'], 'server': r['server_id']
        })

reward_paired = defaultdict(lambda: {'coins': 0, 'boxes': 0, 'time': ''})
for r in db_data['data']:
    if r['change_type'] == '1':
        key = (r['user_id'], r['created_at'])
        if r['asset_id'] == '11631001':
            reward_paired[key]['coins'] = r['change_count']
        elif r['asset_id'] == '111110264':
            reward_paired[key]['boxes'] = r['change_count']
        reward_paired[key]['time'] = r['created_at']

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
        purchase_records.append({
            'server': row[0], 'player': row[1], 'package': row[2],
            'payment': row[3], 'coins': float(row[4]), 'time': row[5]
        })

player_purchases = defaultdict(list)
for r in purchase_records:
    if 'monkey_currency' in r['package']:
        player_purchases[r['player']].append(r)

all_players = sorted(player_exchanges.keys())

outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v2.csv'
with open(outpath, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        '服务器ID', '玩家ID', '记录类型', '说明',
        '猿猴币数量', '自选宝箱数量', '时间'
    ])

    total_rows = 0
    for pid in all_players:
        srv = player_exchanges[pid][0]['server']
        purchases = sorted(player_purchases.get(pid, []), key=lambda x: x['time'])
        exchanges = sorted(player_exchanges[pid], key=lambda x: x['time'])
        rewards = sorted(player_s1_rewards.get(pid, []), key=lambda x: x['time'])

        for p in purchases:
            pkg_short = p['package'].replace('_monkey_currency', '')
            writer.writerow([
                srv, pid, '充值购买',
                f"礼包{pkg_short}, 花费${p['payment']}",
                int(p['coins']), '', p['time']
            ])
            total_rows += 1

        for ex in exchanges:
            writer.writerow([
                srv, pid, '兑换消耗',
                f"花费{ex['coins']}猿猴币兑换奖励",
                -ex['coins'], '', ex['time']
            ])
            total_rows += 1

        for rw in rewards:
            writer.writerow([
                srv, pid, '已领取-阶段一返还',
                f"返还{rw['coins']}猿猴币+{rw['boxes']}个自选宝箱",
                rw['coins'], rw['boxes'], rw['time']
            ])
            total_rows += 1

        ex_count = Counter(ex['coins'] for ex in exchanges)
        rwd_coin_count = Counter(rw['coins'] for rw in rewards)

        for ex_amt in sorted(ex_count.keys()):
            n = ex_count[ex_amt]
            s1c, s1b = stage1_map.get(ex_amt, (0, 0))
            if s1c == 0:
                continue
            s1_got = min(rwd_coin_count.get(s1c, 0), n)
            s1_miss = n - s1_got
            if s1c in rwd_coin_count:
                rwd_coin_count[s1c] = max(0, rwd_coin_count[s1c] - s1_got)

            if s1_miss > 0:
                writer.writerow([
                    srv, pid, '需补发-阶段一未发放',
                    f"兑换{ex_amt}档位, 阶段一未发放x{s1_miss}次",
                    s1c * s1_miss, s1b * s1_miss, ''
                ])
                total_rows += 1

            writer.writerow([
                srv, pid, '需补发-阶段二未发放',
                f"兑换{ex_amt}档位, 阶段二未发放x{n}次",
                s1c * n, s1b * n, ''
            ])
            total_rows += 1

print(f'明细行数: {total_rows}')
print(f'玩家数: {len(all_players)}')
print(f'已保存: {outpath}')
