# -*- coding: utf-8 -*-
"""周卡 价格+名称+备注 落地脚本。默认 dry-run；加 --apply 写线上。
按行 ID 只改 col6(备注)/col7(Price)/col35(Name)，不影响其它行。"""
import csv, json, os, sys, shutil

LIVE = r'C:\x3\gdconfig\tsv\Pack__Pack.tsv'
STG = os.path.dirname(os.path.abspath(__file__))
patch = {
    '2026101': {'col6_Note': '9.99',  'col7_Price': '107', 'col35_Name': '基础周卡'},
    '2026102': {'col6_Note': '19.99', 'col7_Price': '111', 'col35_Name': '进阶周卡'},
    '2026103': {'col6_Note': '29.99', 'col7_Price': '112', 'col35_Name': '至尊周卡'},
    '2026104': {'col6_Note': '49.99', 'col7_Price': '116', 'col35_Name': '周卡全包'},
}
json.dump(patch, open(os.path.join(STG, 'patch_spec.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
apply = '--apply' in sys.argv

rows = list(csv.reader(open(LIVE, encoding='utf-8'), delimiter='\t'))
changes = []
for r in rows:
    if r and r[0] in patch:
        p = patch[r[0]]
        changes.append((r[0], 'Note(col6)', r[6], p['col6_Note']))
        changes.append((r[0], 'Price(col7)', r[7], p['col7_Price']))
        changes.append((r[0], 'Name(col35)', r[35], p['col35_Name']))
        if apply:
            r[6], r[7], r[35] = p['col6_Note'], p['col7_Price'], p['col35_Name']

print('=== 计划改动 ===')
for c in changes:
    print(f'  {c[0]} {c[1]}: {c[2]!r} -> {c[3]!r}')

if apply:
    shutil.copy2(LIVE, os.path.join(STG, 'Pack__Pack.PRE_APPLY_BACKUP.tsv'))
    with open(LIVE, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(rows)
    print('\n[APPLIED] 已写入线上 tsv（落地前备份: Pack__Pack.PRE_APPLY_BACKUP.tsv）')
else:
    print('\n[DRY-RUN] 未写线上。加 --apply 落地。')
