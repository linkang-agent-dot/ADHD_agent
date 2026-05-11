import sys, csv, json
from collections import defaultdict

# === 1. Load what's owed ===
comp = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    for row in csv.DictReader(f):
        comp[row['玩家ID']] = {
            'server': row['服务器ID'],
            'coins': int(row['补发猿猴币']),
            'boxes': int(row['补发自选宝箱']),
        }

# === 2. Load mail_event_reissue sent ===
mail_sent = defaultdict(lambda: {'coins': 0, 'boxes': 0})
with open(r'C:/Users/linkang/Downloads/mail_reissue_records.json', 'r') as f:
    mail_data = json.load(f)
for r in mail_data['data']:
    pid = r['user_id']
    if r['asset_id'] == '11631001':
        mail_sent[pid]['coins'] += r['change_count']
    elif r['asset_id'] == '111110264':
        mail_sent[pid]['boxes'] += r['change_count']

# === 3. Load import_v2 sent ===
prev_sent = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_import_v2.csv', 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        pid = row[1]
        items = json.loads(row[5])
        coins = sum(i['amount'] for i in items if i['id'] == 11631001)
        boxes = sum(i['amount'] for i in items if i['id'] == 111110264)
        prev_sent[pid] = {'coins': coins, 'boxes': boxes}

# === 4. Calculate over-compensation ===
over_list = []
for pid, owed in sorted(comp.items()):
    mail_c = mail_sent[pid]['coins']
    mail_b = mail_sent[pid]['boxes']
    prev_c = prev_sent.get(pid, {}).get('coins', 0)
    prev_b = prev_sent.get(pid, {}).get('boxes', 0)

    total_sent_c = mail_c + prev_c
    total_sent_b = mail_b + prev_b

    over_c = max(0, total_sent_c - owed['coins'])
    over_b = max(0, total_sent_b - owed['boxes'])

    if over_c > 0 or over_b > 0:
        over_list.append({
            'server': owed['server'], 'player': pid,
            'owed_c': owed['coins'], 'owed_b': owed['boxes'],
            'mail_c': mail_c, 'mail_b': mail_b,
            'prev_c': prev_c, 'prev_b': prev_b,
            'total_c': total_sent_c, 'total_b': total_sent_b,
            'over_c': over_c, 'over_b': over_b,
        })

print(f'=== 超额发放统计 ===')
print(f'超额人数: {len(over_list)} 人')
print(f'超额猿猴币总量: {sum(r["over_c"] for r in over_list):,}')
print(f'超额宝箱总量:   {sum(r["over_b"] for r in over_list):,}')

print(f'\n=== 超额明细（按超额币数降序）===')
print(f'{"server":<12}{"player":<15}{"应发c":<10}{"邮件c":<10}{"前次c":<10}{"总发c":<10}{"超额c":<10}{"超额b":<8}')
print('-'*90)
for r in sorted(over_list, key=lambda x: -x['over_c']):
    print(f'{r["server"]:<12}{r["player"]:<15}{r["owed_c"]:<10}{r["mail_c"]:<10}'
          f'{r["prev_c"]:<10}{r["total_c"]:<10}{r["over_c"]:<10}{r["over_b"]:<8}')

# === 5. Generate deduction CSV ===
# Note: negative amounts for deduction
outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_deduction.csv'
with open(outpath, 'w', encoding='gbk', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['服务器 ID', '玩家 ID', '玩家信息', '标题信息', '附件资产信息', '自定义'])
    for r in sorted(over_list, key=lambda x: (x['server'], x['player'])):
        custom = []
        if r['over_c'] > 0:
            custom.append({"assetType": "innercoin", "id": 11631001, "amount": -r['over_c']})
        if r['over_b'] > 0:
            custom.append({"assetType": "item", "id": 111110264, "amount": -r['over_b']})
        writer.writerow([r['server'], r['player'], '', '', '', json.dumps(custom, ensure_ascii=False)])

print(f'\n=== 扣回导入表已生成 ===')
print(f'文件: {outpath}')
print(f'行数: {len(over_list)}')
print(f'\n=== 前5行样本 ===')
with open(outpath, 'r', encoding='gbk') as f:
    for i, line in enumerate(f):
        if i <= 5: print(line.rstrip())
