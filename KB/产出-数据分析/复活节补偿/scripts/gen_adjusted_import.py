import sys, csv, json
from collections import defaultdict

# === 1. Load what's owed (original compensation) ===
comp = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    for row in csv.DictReader(f):
        comp[row['玩家ID']] = {
            'server': row['服务器ID'],
            'coins': int(row['补发猿猴币']),
            'boxes': int(row['补发自选宝箱']),
        }

# === 2. Load what mail_event_reissue already sent ===
mail_sent = defaultdict(lambda: {'coins': 0, 'boxes': 0})
with open(r'C:/Users/linkang/Downloads/mail_reissue_records.json', 'r') as f:
    mail_data = json.load(f)
for r in mail_data['data']:
    pid = r['user_id']
    if r['asset_id'] == '11631001':
        mail_sent[pid]['coins'] += r['change_count']
    elif r['asset_id'] == '111110264':
        mail_sent[pid]['boxes'] += r['change_count']

# === 3. Load what prev import already sent ===
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

# === 4. Calculate remaining ===
results = []
for pid, owed in sorted(comp.items()):
    mail_c = mail_sent[pid]['coins']
    mail_b = mail_sent[pid]['boxes']
    prev_c = prev_sent.get(pid, {}).get('coins', 0)
    prev_b = prev_sent.get(pid, {}).get('boxes', 0)

    already_sent_c = mail_c + prev_c
    already_sent_b = mail_b + prev_b

    remain_c = max(0, owed['coins'] - already_sent_c)
    remain_b = max(0, owed['boxes'] - already_sent_b)

    results.append({
        'server': owed['server'], 'player': pid,
        'owed_c': owed['coins'], 'owed_b': owed['boxes'],
        'mail_c': mail_c, 'mail_b': mail_b,
        'prev_c': prev_c, 'prev_b': prev_b,
        'remain_c': remain_c, 'remain_b': remain_b,
    })

# Summary
need_comp = [r for r in results if r['remain_c'] > 0 or r['remain_b'] > 0]
fully_done = [r for r in results if r['remain_c'] == 0 and r['remain_b'] == 0]
over_comp  = [r for r in results if
              (r['mail_c'] + r['prev_c']) > r['owed_c'] or
              (r['mail_b'] + r['prev_b']) > r['owed_b']]

print(f'=== 扣除已发后的差额统计 ===')
print(f'原补发名单: {len(results)} 人')
print(f'已足额/超额，不需再补: {len(fully_done)} 人')
print(f'仍有差额，需要补: {len(need_comp)} 人')
print(f'  其中超额发放(多了): {len(over_comp)} 人 (不追回，仅记录)')
print(f'\n剩余补发总量:')
print(f'  猿猴币(11631001): {sum(r["remain_c"] for r in need_comp):,}')
print(f'  自选宝箱(111110264): {sum(r["remain_b"] for r in need_comp):,}')

print(f'\n=== 仍需补发的玩家明细 ===')
print(f'{"server":<12}{"player":<15}{"应发c":<10}{"邮件c":<10}{"前次c":<10}{"剩余c":<10}{"应发b":<8}{"邮件b":<8}{"前次b":<8}{"剩余b":<8}')
print('-'*100)
for r in sorted(need_comp, key=lambda x: -x['remain_c']):
    print(f'{r["server"]:<12}{r["player"]:<15}{r["owed_c"]:<10}{r["mail_c"]:<10}{r["prev_c"]:<10}{r["remain_c"]:<10}'
          f'{r["owed_b"]:<8}{r["mail_b"]:<8}{r["prev_b"]:<8}{r["remain_b"]:<8}')

# Generate new import CSV
outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_import_v3.csv'
with open(outpath, 'w', encoding='gbk', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['服务器 ID', '玩家 ID', '玩家信息', '标题信息', '附件资产信息', '自定义'])
    for r in sorted(need_comp, key=lambda x: (x['server'], x['player'])):
        custom = []
        if r['remain_c'] > 0:
            custom.append({"assetType": "innercoin", "id": 11631001, "amount": r['remain_c']})
        if r['remain_b'] > 0:
            custom.append({"assetType": "item", "id": 111110264, "amount": r['remain_b']})
        writer.writerow([r['server'], r['player'], '', '', '', json.dumps(custom, ensure_ascii=False)])

# Verify
v_rows = 0
v_c = 0
v_b = 0
with open(outpath, 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        v_rows += 1
        for item in json.loads(row[5]):
            if item['id'] == 11631001: v_c += item['amount']
            elif item['id'] == 111110264: v_b += item['amount']

print(f'\n=== 新导入表校验 ===')
print(f'行数: {v_rows}')
print(f'猿猴币: {v_c:,}  |  宝箱: {v_b:,}')
print(f'JSON解析错误: 0')
print(f'已保存: {outpath}')

print(f'\n=== 前5行样本 ===')
with open(outpath, 'r', encoding='gbk') as f:
    for i, line in enumerate(f):
        if i <= 5: print(line.rstrip())
