import csv, json
from collections import defaultdict

comp = {}
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    for row in csv.DictReader(f):
        comp[row['玩家ID']] = {'server': row['服务器ID'], 'coins': int(row['补发猿猴币']), 'boxes': int(row['补发自选宝箱'])}

mail_sent = defaultdict(lambda: {'coins': 0, 'boxes': 0})
with open(r'C:/Users/linkang/Downloads/mail_reissue_records.json', 'r') as f:
    for r in json.load(f)['data']:
        if r['asset_id'] == '11631001': mail_sent[r['user_id']]['coins'] += r['change_count']
        elif r['asset_id'] == '111110264': mail_sent[r['user_id']]['boxes'] += r['change_count']

# 现状：玩家身上有 owed（import_v2留下的）
# 目标：玩家身上应有 mail（正确补偿）
# 调整 = mail - owed（正=补给玩家，负=再扣玩家）
corrections = []
for pid, owed in sorted(comp.items()):
    mail_c = mail_sent[pid]['coins']
    mail_b = mail_sent[pid]['boxes']
    if mail_c == 0 and mail_b == 0:
        continue
    adj_c = mail_c - owed['coins']
    adj_b = mail_b - owed['boxes']
    if adj_c != 0 or adj_b != 0:
        corrections.append({'server': owed['server'], 'player': pid, 'adj_c': adj_c, 'adj_b': adj_b})

print(f'需调整人数: {len(corrections)}')
print(f'需补还给玩家 猿猴币: {sum(r["adj_c"] for r in corrections if r["adj_c"] > 0):,}')
print(f'需补还给玩家 宝箱:   {sum(r["adj_b"] for r in corrections if r["adj_b"] > 0):,}')
print(f'需再扣玩家   猿猴币: {sum(-r["adj_c"] for r in corrections if r["adj_c"] < 0):,}')
print(f'需再扣玩家   宝箱:   {sum(-r["adj_b"] for r in corrections if r["adj_b"] < 0):,}')

# GM命令：adj直接作为amount（正=给，负=扣）
cmds = []
for r in corrections:
    if r['adj_c'] != 0:
        cmds.append({
            "server_ids": [int(r['server'])],
            "cmd": "addasset",
            "players": [int(r['player'])],
            "args": ["11631001", str(r['adj_c'])]
        })
    if r['adj_b'] != 0:
        cmds.append({
            "server_ids": [int(r['server'])],
            "cmd": "addasset",
            "players": [int(r['player'])],
            "args": ["111110264", str(r['adj_b'])]
        })

outpath = r'C:/Users/linkang/Downloads/p2_easter_correction_cmds_v2.csv'
with open(outpath, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    for cmd in cmds:
        writer.writerow([json.dumps(cmd, ensure_ascii=False, separators=(', ', ': '))])

print(f'\nGM命令数: {len(cmds)}')
print(f'已保存: {outpath}')
print(f'\n前5行样本:')
with open(outpath, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 5: break
        print(line.rstrip())
