import csv, json
from collections import defaultdict

# Load over-compensation player list (same logic as deduction)
comp = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    for row in csv.DictReader(f):
        comp[row['玩家ID']] = {'server': row['服务器ID'], 'coins': int(row['补发猿猴币']), 'boxes': int(row['补发自选宝箱'])}

mail_sent = defaultdict(lambda: {'coins': 0, 'boxes': 0})
with open(r'C:/Users/linkang/Downloads/mail_reissue_records.json', 'r') as f:
    for r in json.load(f)['data']:
        if r['asset_id'] == '11631001': mail_sent[r['user_id']]['coins'] += r['change_count']
        elif r['asset_id'] == '111110264': mail_sent[r['user_id']]['boxes'] += r['change_count']

prev_sent = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_import_v2.csv', 'r', encoding='gbk') as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        items = json.loads(row[5])
        prev_sent[row[1]] = {
            'coins': sum(i['amount'] for i in items if i['id'] == 11631001),
            'boxes': sum(i['amount'] for i in items if i['id'] == 111110264),
        }

over_players = []
for pid, owed in sorted(comp.items()):
    m = mail_sent[pid]
    p = prev_sent.get(pid, {'coins': 0, 'boxes': 0})
    over_c = max(0, (m['coins'] + p['coins']) - owed['coins'])
    over_b = max(0, (m['boxes'] + p['boxes']) - owed['boxes'])
    if over_c > 0 or over_b > 0:
        over_players.append({'server': owed['server'], 'player': pid})

# Generate iGame import CSV: 5 boxes per player
APOLOGY_BOXES = 5
outpath = r'C:/Users/linkang/Downloads/p2_easter_apology_mail.csv'
with open(outpath, 'w', encoding='gbk', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['服务器 ID', '玩家 ID', '玩家信息', '标题信息', '附件资产信息', '自定义'])
    for r in sorted(over_players, key=lambda x: (x['server'], x['player'])):
        custom = [{"assetType": "item", "id": 111110264, "amount": APOLOGY_BOXES}]
        writer.writerow([r['server'], r['player'], '', '', '', json.dumps(custom, ensure_ascii=False)])

print(f'发送人数: {len(over_players)}')
print(f'每人宝箱: {APOLOGY_BOXES}')
print(f'宝箱总量: {len(over_players) * APOLOGY_BOXES}')
print(f'已保存: {outpath}')
print(f'\n前3行样本:')
with open(outpath, 'r', encoding='gbk') as f:
    for i, line in enumerate(f):
        if i <= 3: print(line.rstrip())
