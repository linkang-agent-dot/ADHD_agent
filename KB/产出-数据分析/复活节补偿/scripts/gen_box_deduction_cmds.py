import sys, csv, json
from collections import defaultdict

# Load over-compensation data (recompute)
comp = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    for row in csv.DictReader(f):
        comp[row['玩家ID']] = {
            'server': row['服务器ID'],
            'coins': int(row['补发猿猴币']),
            'boxes': int(row['补发自选宝箱']),
        }

mail_sent = defaultdict(lambda: {'coins': 0, 'boxes': 0})
with open(r'C:/Users/linkang/Downloads/mail_reissue_records.json', 'r') as f:
    mail_data = json.load(f)
for r in mail_data['data']:
    pid = r['user_id']
    if r['asset_id'] == '11631001':
        mail_sent[pid]['coins'] += r['change_count']
    elif r['asset_id'] == '111110264':
        mail_sent[pid]['boxes'] += r['change_count']

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

# Calculate over-compensation for both coins and boxes
deductions = []
for pid, owed in sorted(comp.items()):
    mail_c = mail_sent[pid]['coins']
    mail_b = mail_sent[pid]['boxes']
    prev_c = prev_sent.get(pid, {}).get('coins', 0)
    prev_b = prev_sent.get(pid, {}).get('boxes', 0)
    over_c = max(0, (mail_c + prev_c) - owed['coins'])
    over_b = max(0, (mail_b + prev_b) - owed['boxes'])
    if over_c > 0 or over_b > 0:
        deductions.append({
            'server': owed['server'],
            'player': pid,
            'over_c': over_c,
            'over_b': over_b,
        })

print(f'需扣除人数: {len(deductions)}')
print(f'扣回猿猴币总量: {sum(r["over_c"] for r in deductions):,}')
print(f'扣回宝箱总量:   {sum(r["over_b"] for r in deductions):,}')

# Generate GM commands: one command per asset per player
cmds = []
for r in deductions:
    if r['over_c'] > 0:
        cmds.append({
            "server_ids": [int(r['server'])],
            "cmd": "addasset",
            "players": [int(r['player'])],
            "args": ["11631001", str(-r['over_c'])]
        })
    if r['over_b'] > 0:
        cmds.append({
            "server_ids": [int(r['server'])],
            "cmd": "addasset",
            "players": [int(r['player'])],
            "args": ["111110264", str(-r['over_b'])]
        })

print(f'GM命令总条数: {len(cmds)}')

outpath_csv = r'C:/Users/linkang/Downloads/p2_easter_deduction_cmds_v3.csv'
with open(outpath_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    for cmd in cmds:
        line = json.dumps(cmd, ensure_ascii=False, separators=(', ', ': '))
        writer.writerow([line])

print(f'\n命令文件: {outpath_csv}')
print(f'\n前3行样本:')
with open(outpath_csv, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 3: break
        print(line.rstrip())
