import sys, csv, json

# Read comp final
rows = []
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_final.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for r in reader:
        coins = int(r['total_comp_coins'])
        boxes = int(r['total_comp_boxes'])
        if coins > 0 or boxes > 0:
            rows.append({
                'server': r['server_id'],
                'player': r['player_id'],
                'coins': coins,
                'boxes': boxes,
            })

print(f'Source rows: {len(rows)}')

# Generate iGame import CSV
outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_import.csv'
with open(outpath, 'w', encoding='gbk', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['服务器 ID', '玩家 ID', '玩家信息', '标题信息', '附件资产信息', '自定义'])

    total_coins = 0
    total_boxes = 0
    for r in rows:
        attachments = []
        if r['coins'] > 0:
            attachments.append({"assetType": "item", "id": 11631001, "amount": r['coins']})
            total_coins += r['coins']
        if r['boxes'] > 0:
            attachments.append({"assetType": "item", "id": 111110264, "amount": r['boxes']})
            total_boxes += r['boxes']

        json_str = json.dumps(attachments, ensure_ascii=False)
        writer.writerow([r['server'], r['player'], '', '', json_str, ''])

print(f'Output rows: {len(rows)}')
print(f'Total coins (11631001): {total_coins:,}')
print(f'Total boxes (111110264): {total_boxes:,}')
print(f'Saved: {outpath}')

# Verify: re-read and check
print('\n=== Verification ===')
verify_rows = 0
verify_coins = 0
verify_boxes = 0
with open(outpath, 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    header = next(reader)
    print(f'Header: {header}')
    for row in reader:
        verify_rows += 1
        attachment_json = row[4]
        items = json.loads(attachment_json)
        for item in items:
            if item['id'] == 11631001:
                verify_coins += item['amount']
            elif item['id'] == 111110264:
                verify_boxes += item['amount']

print(f'Verify rows: {verify_rows}')
print(f'Verify coins: {verify_coins:,} (match: {verify_coins == total_coins})')
print(f'Verify boxes: {verify_boxes:,} (match: {verify_boxes == total_boxes})')
print(f'JSON parse errors: 0')

# Show first 5 rows
print('\n=== Sample (first 5) ===')
with open(outpath, 'r', encoding='gbk') as f:
    for i, line in enumerate(f):
        if i <= 5:
            print(line.rstrip())
