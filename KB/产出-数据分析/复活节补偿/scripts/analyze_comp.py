import sys; sys.stdout.reconfigure(encoding='utf-8')
import json, csv
from collections import defaultdict, Counter

# Load DB records
with open(r'C:/Users/linkang/Downloads/oap_all_records.json', 'r') as f:
    db_data = json.load(f)
print(f'DB records loaded: {db_data["row_count"]}')

# Exchange tier -> stage 1 reward mapping
stage1_map = {
    2000:  (1000, 1),
    5000:  (2500, 3),
    10000: (5000, 10),
    20000: (10000, 22),
    30000: (15000, 40),
    50000: (25000, 85),
}

# Exchanges: change_type=2, asset=11631001
player_exchanges = defaultdict(list)
for r in db_data['data']:
    if r['change_type'] == '2' and r['asset_id'] == '11631001':
        player_exchanges[r['user_id']].append({
            'server': r['server_id'], 'coins': r['change_count']
        })

# Rewards delivered (stage1): change_type=1, paired by (user_id, timestamp)
reward_paired = defaultdict(lambda: {'coins': 0, 'boxes': 0})
for r in db_data['data']:
    if r['change_type'] == '1':
        key = (r['user_id'], r['created_at'])
        if r['asset_id'] == '11631001':
            reward_paired[key]['coins'] = r['change_count']
        elif r['asset_id'] == '111110264':
            reward_paired[key]['boxes'] = r['change_count']

player_rewards = defaultdict(list)
for (uid, ts), val in reward_paired.items():
    player_rewards[uid].append(val)

print(f'Players with exchanges: {len(player_exchanges)}')

# Exchange distribution
exchange_dist = Counter()
for uid, exs in player_exchanges.items():
    for ex in exs:
        exchange_dist[ex['coins']] += 1
print(f'\nExchange tier distribution:')
for amt, cnt in sorted(exchange_dist.items()):
    s1c, s1b = stage1_map.get(amt, (0, 0))
    print(f'  Spend {amt} -> s1 return {s1c}c+{s1b}b | s2 owed same | {cnt} times')

# Per player compensation
comp_results = []
for uid in sorted(player_exchanges.keys()):
    exchanges = player_exchanges[uid]
    rewards = player_rewards.get(uid, [])
    srv = exchanges[0]['server']

    ex_count = Counter(ex['coins'] for ex in exchanges)
    rwd_coin_count = Counter(rw['coins'] for rw in rewards)

    total_s1_miss_c = 0
    total_s1_miss_b = 0
    total_s2_c = 0
    total_s2_b = 0
    total_s1_got_c = 0
    total_s1_got_b = 0
    tier_details = []

    for ex_amt in sorted(ex_count.keys()):
        n = ex_count[ex_amt]
        s1c, s1b = stage1_map.get(ex_amt, (0, 0))
        if s1c == 0:
            continue

        # Stage 1 delivered
        s1_got = min(rwd_coin_count.get(s1c, 0), n)
        s1_miss = n - s1_got

        total_s1_got_c += s1c * s1_got
        total_s1_got_b += s1b * s1_got
        total_s1_miss_c += s1c * s1_miss
        total_s1_miss_b += s1b * s1_miss
        total_s2_c += s1c * n
        total_s2_b += s1b * n

        tier_details.append(f'{ex_amt}x{n}')

        if s1c in rwd_coin_count:
            rwd_coin_count[s1c] = max(0, rwd_coin_count[s1c] - s1_got)

    comp_c = total_s1_miss_c + total_s2_c
    comp_b = total_s1_miss_b + total_s2_b

    if comp_c > 0 or comp_b > 0:
        comp_results.append({
            'server': srv, 'player': uid,
            'detail': ', '.join(tier_details),
            's1_got_c': total_s1_got_c, 's1_got_b': total_s1_got_b,
            's1_miss_c': total_s1_miss_c, 's1_miss_b': total_s1_miss_b,
            's2_c': total_s2_c, 's2_b': total_s2_b,
            'comp_c': comp_c, 'comp_b': comp_b,
        })

# Summary
print(f'\n=== COMPENSATION SUMMARY ===')
print(f'Players needing compensation: {len(comp_results)}')
s1m_c = sum(r['s1_miss_c'] for r in comp_results)
s1m_b = sum(r['s1_miss_b'] for r in comp_results)
s2_c = sum(r['s2_c'] for r in comp_results)
s2_b = sum(r['s2_b'] for r in comp_results)
gc = sum(r['comp_c'] for r in comp_results)
gb = sum(r['comp_b'] for r in comp_results)

print(f'Stage 1 undelivered:  {s1m_c:>10,} coins + {s1m_b:>6} boxes')
print(f'Stage 2 all owed:     {s2_c:>10,} coins + {s2_b:>6} boxes')
print(f'GRAND TOTAL to comp:  {gc:>10,} coins(11631001) + {gb:>6} boxes(111110264)')

# Print table (top 30 + all)
print(f'\n{"srv":<12}{"player":<15}{"exchanges":<30}{"s1_got":<16}{"s1_miss":<16}{"s2_owed":<16}{"TOTAL_COMP":<20}')
print('-' * 125)
for r in sorted(comp_results, key=lambda x: -x['comp_c']):
    s1g = f"{r['s1_got_c']}c+{r['s1_got_b']}b"
    s1m = f"{r['s1_miss_c']}c+{r['s1_miss_b']}b"
    s2 = f"{r['s2_c']}c+{r['s2_b']}b"
    tot = f"{r['comp_c']}c+{r['comp_b']}b"
    print(f"{r['server']:<12}{r['player']:<15}{r['detail']:<30}{s1g:<16}{s1m:<16}{s2:<16}{tot:<20}")

# Save CSV
outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_final.csv'
with open(outpath, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['server_id','player_id','exchange_detail',
                     's1_delivered_coins','s1_delivered_boxes',
                     's1_missing_coins','s1_missing_boxes',
                     's2_owed_coins','s2_owed_boxes',
                     'total_comp_coins','total_comp_boxes',
                     'compensation_items'])
    for r in sorted(comp_results, key=lambda x: (x['server'], x['player'])):
        items = f"11631001:{r['comp_c']}, 111110264:{r['comp_b']}"
        writer.writerow([r['server'], r['player'], r['detail'],
                        r['s1_got_c'], r['s1_got_b'],
                        r['s1_miss_c'], r['s1_miss_b'],
                        r['s2_c'], r['s2_b'],
                        r['comp_c'], r['comp_b'], items])

print(f'\nSaved: {outpath}')
