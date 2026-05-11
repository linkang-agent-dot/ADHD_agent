import sys; sys.stdout.reconfigure(encoding='utf-8')
import json, csv
from collections import defaultdict, Counter

# Load DB records
with open(r'C:/Users/linkang/Downloads/oap_all_records.json', 'r') as f:
    db_data = json.load(f)

# Load purchase CSV
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

# Stage 1 mapping
stage1_map = {
    2000:  (1000, 1),
    5000:  (2500, 3),
    10000: (5000, 10),
    20000: (10000, 22),
    30000: (15000, 40),
    50000: (25000, 85),
}

# Build per-player data from DB
# Exchanges (change_type=2)
player_exchanges = defaultdict(list)
for r in db_data['data']:
    if r['change_type'] == '2' and r['asset_id'] == '11631001':
        player_exchanges[r['user_id']].append({
            'coins': r['change_count'], 'time': r['created_at'], 'server': r['server_id']
        })

# Stage 1 rewards (change_type=1, paired by timestamp)
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

# All players who exchanged
all_players = sorted(player_exchanges.keys())

# Per-player purchases from CSV (monkey_currency only)
player_purchases = defaultdict(list)
for r in purchase_records:
    if 'monkey_currency' in r['package']:
        player_purchases[r['player']].append(r)

# Build detail rows
outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_detail.csv'
with open(outpath, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'server_id', 'player_id', 'record_type', 'detail',
        'coins', 'boxes_111110264', 'time'
    ])

    total_rows = 0
    for pid in all_players:
        srv = player_exchanges[pid][0]['server']
        purchases = sorted(player_purchases.get(pid, []), key=lambda x: x['time'])
        exchanges = sorted(player_exchanges[pid], key=lambda x: x['time'])
        rewards = sorted(player_s1_rewards.get(pid, []), key=lambda x: x['time'])

        # 1. Purchase records
        for p in purchases:
            pkg_short = p['package'].replace('_monkey_currency', '')
            writer.writerow([
                srv, pid, 'purchase',
                f"pkg={pkg_short}, pay=${p['payment']}",
                int(p['coins']), '', p['time']
            ])
            total_rows += 1

        # 2. Exchange records
        for ex in exchanges:
            s1c, s1b = stage1_map.get(ex['coins'], (0, 0))
            writer.writerow([
                srv, pid, 'exchange',
                f"spend {ex['coins']} coins (tier s1={s1c}c+{s1b}b)",
                -ex['coins'], '', ex['time']
            ])
            total_rows += 1

        # 3. Stage 1 rewards received
        for rw in rewards:
            writer.writerow([
                srv, pid, 's1_reward',
                f"stage1 delivered",
                rw['coins'], rw['boxes'], rw['time']
            ])
            total_rows += 1

        # 4. Compensation owed
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
                    srv, pid, 'COMP_s1_missing',
                    f"tier {ex_amt}: s1 not delivered x{s1_miss}",
                    s1c * s1_miss, s1b * s1_miss, ''
                ])
                total_rows += 1

            writer.writerow([
                srv, pid, 'COMP_s2_owed',
                f"tier {ex_amt}: s2 owed x{n}",
                s1c * n, s1b * n, ''
            ])
            total_rows += 1

print(f'Detail rows: {total_rows}')
print(f'Players: {len(all_players)}')
print(f'Saved: {outpath}')
