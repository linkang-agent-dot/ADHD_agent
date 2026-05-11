import sys; sys.stdout.reconfigure(encoding='utf-8')
import csv, json

# Load detail v4 (source of truth)
detail = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    for row in csv.DictReader(f):
        pid = row['玩家ID']
        detail[pid] = {
            'server': row['服务器ID'],
            'coins': int(row['补发猿猴币']),
            'boxes': int(row['补发自选宝箱']),
        }

# Load import CSV (the file going into iGame)
imp = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_import.csv', 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        pid = row[1]
        items = json.loads(row[4])
        coins = 0
        boxes = 0
        for item in items:
            if item['id'] == 11631001:
                coins = item['amount']
            elif item['id'] == 111110264:
                boxes = item['amount']
        imp[pid] = {'server': row[0], 'coins': coins, 'boxes': boxes}

print(f'明细表玩家数: {len(detail)}')
print(f'导入表玩家数: {len(imp)}')

# Check 1: same player set
only_in_detail = set(detail.keys()) - set(imp.keys())
only_in_import = set(imp.keys()) - set(detail.keys())

print(f'\n=== 人员核对 ===')
print(f'只在明细表: {len(only_in_detail)}')
print(f'只在导入表: {len(only_in_import)}')

if only_in_detail:
    for pid in sorted(only_in_detail):
        d = detail[pid]
        print(f'  明细表有/导入表无: srv={d["server"]} player={pid} comp={d["coins"]}c+{d["boxes"]}b')

if only_in_import:
    for pid in sorted(only_in_import):
        i = imp[pid]
        print(f'  导入表有/明细表无: srv={i["server"]} player={pid} comp={i["coins"]}c+{i["boxes"]}b')

# Check 2: amount match for common players
common = set(detail.keys()) & set(imp.keys())
mismatches = []
for pid in sorted(common):
    d = detail[pid]
    i = imp[pid]
    if d['coins'] != i['coins'] or d['boxes'] != i['boxes']:
        mismatches.append((pid, d, i))

print(f'\n=== 金额核对 ({len(common)} 人) ===')
print(f'金额不一致: {len(mismatches)}')
if mismatches:
    for pid, d, i in mismatches[:20]:
        print(f'  player={pid}: 明细={d["coins"]}c+{d["boxes"]}b, 导入={i["coins"]}c+{i["boxes"]}b')

# Check 3: server match
srv_mismatch = []
for pid in common:
    if detail[pid]['server'] != imp[pid]['server']:
        srv_mismatch.append((pid, detail[pid]['server'], imp[pid]['server']))

print(f'服务器不一致: {len(srv_mismatch)}')
if srv_mismatch:
    for pid, ds, is_ in srv_mismatch[:10]:
        print(f'  player={pid}: 明细={ds}, 导入={is_}')

# Check 4: totals
d_coins = sum(v['coins'] for v in detail.values())
d_boxes = sum(v['boxes'] for v in detail.values())
i_coins = sum(v['coins'] for v in imp.values())
i_boxes = sum(v['boxes'] for v in imp.values())

print(f'\n=== 总量核对 ===')
print(f'明细表: {d_coins:>12,} 猿猴币  {d_boxes:>8,} 宝箱')
print(f'导入表: {i_coins:>12,} 猿猴币  {i_boxes:>8,} 宝箱')
print(f'猿猴币一致: {d_coins == i_coins}')
print(f'宝箱一致:   {d_boxes == i_boxes}')

if len(only_in_detail) == 0 and len(only_in_import) == 0 and len(mismatches) == 0 and len(srv_mismatch) == 0 and d_coins == i_coins and d_boxes == i_boxes:
    print(f'\n✓ 明细表 vs 导入表 完全一致，可以放心补发')
else:
    print(f'\n✗ 有差异，需要排查')
