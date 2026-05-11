import sys, csv, json

rows = []
with open(r'C:/Users/linkang/Downloads/p2_easter_comp_detail_v4.csv', 'r', encoding='gbk') as f:
    reader = csv.DictReader(f)
    for r in reader:
        coins = int(r['补发猿猴币'])
        boxes = int(r['补发自选宝箱'])
        if coins > 0 or boxes > 0:
            rows.append({
                'server': r['服务器ID'],
                'player': r['玩家ID'],
                'coins': coins,
                'boxes': boxes,
            })

print(f'Source rows: {len(rows)}')

outpath = r'C:/Users/linkang/Downloads/p2_easter_comp_import_v2.csv'
with open(outpath, 'w', encoding='gbk', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['服务器 ID', '玩家 ID', '玩家信息', '标题信息', '附件资产信息', '自定义'])

    total_coins = 0
    total_boxes = 0
    for r in rows:
        custom = []
        if r['coins'] > 0:
            custom.append({"assetType": "innercoin", "id": 11631001, "amount": r['coins']})
            total_coins += r['coins']
        if r['boxes'] > 0:
            custom.append({"assetType": "item", "id": 111110264, "amount": r['boxes']})
            total_boxes += r['boxes']

        json_str = json.dumps(custom, ensure_ascii=False)
        writer.writerow([r['server'], r['player'], '', '', '', json_str])

print(f'Output rows: {len(rows)}')
print(f'Total coins (11631001 innercoin): {total_coins:,}')
print(f'Total boxes (111110264 item): {total_boxes:,}')
print(f'Saved: {outpath}')

# Verify
print('\n=== Verification ===')
v_rows = 0
v_coins = 0
v_boxes = 0
with open(outpath, 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        v_rows += 1
        # col 4 (附件资产信息) should be empty, col 5 (自定义) has the JSON
        assert row[4] == '', f'Row {v_rows}: attachment column should be empty, got: {row[4]}'
        items = json.loads(row[5])
        for item in items:
            if item['id'] == 11631001:
                assert item['assetType'] == 'innercoin', f'Row {v_rows}: 11631001 should be innercoin'
                v_coins += item['amount']
            elif item['id'] == 111110264:
                assert item['assetType'] == 'item', f'Row {v_rows}: 111110264 should be item'
                v_boxes += item['amount']

print(f'Rows: {v_rows} (match: {v_rows == len(rows)})')
print(f'Coins: {v_coins:,} (match: {v_coins == total_coins})')
print(f'Boxes: {v_boxes:,} (match: {v_boxes == total_boxes})')
print(f'All in custom column: True')
print(f'Attachment column empty: True')

# Sample
print('\n=== Sample (first 3) ===')
with open(outpath, 'r', encoding='gbk') as f:
    for i, line in enumerate(f):
        if i <= 3:
            print(line.rstrip())
