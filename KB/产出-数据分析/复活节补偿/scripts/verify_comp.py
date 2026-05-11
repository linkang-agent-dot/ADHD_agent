import sys; sys.stdout.reconfigure(encoding='utf-8')
import json, csv
from collections import defaultdict, Counter

# === Load DB raw records ===
with open(r'C:/Users/linkang/Downloads/oap_all_records.json', 'r') as f:
    db_data = json.load(f)

# === Load import CSV (the file to verify) ===
import_rows = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_import.csv', 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        srv, pid = row[0], row[1]
        items = json.loads(row[4])
        coins = 0
        boxes = 0
        for item in items:
            if item['id'] == 11631001:
                coins = item['amount']
            elif item['id'] == 111110264:
                boxes = item['amount']
        import_rows[pid] = {'server': srv, 'coins': coins, 'boxes': boxes}

print(f'Import CSV: {len(import_rows)} players')

# === Rebuild from DB raw data ===
stage1_map = {
    2000:  (1000, 1),
    5000:  (2500, 3),
    10000: (5000, 10),
    20000: (10000, 22),
    30000: (15000, 40),
    50000: (25000, 85),
}

# Exchanges per player (change_type=2, asset=11631001)
player_exchanges = defaultdict(list)
for r in db_data['data']:
    if r['change_type'] == '2' and r['asset_id'] == '11631001':
        player_exchanges[r['user_id']].append(r['change_count'])

# Stage 1 rewards per player (change_type=1, paired by timestamp)
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

# Recalculate expected compensation per player
db_expected = {}
for uid, exs in player_exchanges.items():
    ex_count = Counter(exs)
    rwd_coin_count = Counter(rw['coins'] for rw in player_s1_rewards.get(uid, []))

    total_comp_c = 0
    total_comp_b = 0

    for ex_amt in sorted(ex_count.keys()):
        n = ex_count[ex_amt]
        s1c, s1b = stage1_map.get(ex_amt, (0, 0))
        if s1c == 0:
            continue

        s1_got = min(rwd_coin_count.get(s1c, 0), n)
        s1_miss = n - s1_got

        # Stage 1 missing
        total_comp_c += s1c * s1_miss
        total_comp_b += s1b * s1_miss
        # Stage 2 all owed
        total_comp_c += s1c * n
        total_comp_b += s1b * n

        if s1c in rwd_coin_count:
            rwd_coin_count[s1c] = max(0, rwd_coin_count[s1c] - s1_got)

    if total_comp_c > 0 or total_comp_b > 0:
        db_expected[uid] = {'coins': total_comp_c, 'boxes': total_comp_b}

print(f'DB recalculated: {len(db_expected)} players')

# === Cross-verify ===
mismatches = []
missing_in_import = []
extra_in_import = []

for uid, exp in db_expected.items():
    if uid not in import_rows:
        missing_in_import.append((uid, exp))
    else:
        imp = import_rows[uid]
        if imp['coins'] != exp['coins'] or imp['boxes'] != exp['boxes']:
            mismatches.append((uid, exp, imp))

for uid, imp in import_rows.items():
    if uid not in db_expected:
        extra_in_import.append((uid, imp))

print(f'\n=== VERIFICATION RESULT ===')
print(f'Players in import CSV:    {len(import_rows)}')
print(f'Players from DB recalc:   {len(db_expected)}')
print(f'Mismatches (wrong amount): {len(mismatches)}')
print(f'Missing in import CSV:     {len(missing_in_import)}')
print(f'Extra in import CSV:       {len(extra_in_import)}')

if mismatches:
    print(f'\n!!! MISMATCHES !!!')
    for uid, exp, imp in mismatches[:20]:
        print(f'  player={uid}: DB expects {exp["coins"]}c+{exp["boxes"]}b, import has {imp["coins"]}c+{imp["boxes"]}b')

if missing_in_import:
    print(f'\n!!! MISSING FROM IMPORT !!!')
    for uid, exp in missing_in_import[:20]:
        print(f'  player={uid}: DB expects {exp["coins"]}c+{exp["boxes"]}b, not in import')

if extra_in_import:
    print(f'\n!!! EXTRA IN IMPORT !!!')
    for uid, imp in extra_in_import[:20]:
        print(f'  player={uid}: in import ({imp["coins"]}c+{imp["boxes"]}b) but no DB exchange record')

# Total verification
import_total_c = sum(r['coins'] for r in import_rows.values())
import_total_b = sum(r['boxes'] for r in import_rows.values())
db_total_c = sum(r['coins'] for r in db_expected.values())
db_total_b = sum(r['boxes'] for r in db_expected.values())

print(f'\n=== TOTALS ===')
print(f'Import:  {import_total_c:>12,} coins  {import_total_b:>8,} boxes')
print(f'DB calc: {db_total_c:>12,} coins  {db_total_b:>8,} boxes')
print(f'Match:   coins={import_total_c == db_total_c}, boxes={import_total_b == db_total_b}')

if len(mismatches) == 0 and len(missing_in_import) == 0 and len(extra_in_import) == 0:
    print(f'\n✓ ALL CHECKS PASSED - import CSV is accurate')
else:
    print(f'\n✗ ISSUES FOUND - review above')
