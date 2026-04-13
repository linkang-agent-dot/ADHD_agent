# -*- coding: utf-8 -*-
"""修正整理版页签里的卡包描述 — 两个区域同步更新"""
import subprocess, json, os, sys

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
SHEET = '复活节-整理版'

# 4个主题卡包对照
PACKS = [
    ('矿洞寻宝', 'Mine Treasure Hunt'),
    ('极速飞车', 'Speed Racing'),
    ('彩蛋大亨', 'Easter Tycoon'),
    ('异族探秘', 'Alien Exploration'),
]

def zh_name(n):  return n + '卡包'
def zh_desc(n):  return '打开即可获得两张3星以上\u201c' + n + '\u201d游戏卡片。'
def en_name(e):  return e + ' Card Pack'
def en_desc(e):  return 'Open to receive 2 \u201c' + e + '\u201d game cards of 3 stars or above.'

data_ranges = []

# ── 区域1：卡包本地化 R95-R102，Col B-C ────────────────────────────
# R95 core_decipher_name, R96 desc, R97 underground_name, R98 desc ...
for i, (zh, en) in enumerate(PACKS):
    name_row = 95 + i * 2
    desc_row = 96 + i * 2
    data_ranges.append({
        'range': f"'{SHEET}'!B{name_row}:C{name_row}",
        'majorDimension': 'ROWS',
        'values': [[zh_name(zh), en_name(en)]]
    })
    data_ranges.append({
        'range': f"'{SHEET}'!B{desc_row}:C{desc_row}",
        'majorDimension': 'ROWS',
        'values': [[zh_desc(zh), en_desc(en)]]
    })

# ── 区域2：卡包描述修改版 R122-R129，Col B（中文）+ Col D（英文）────
# R122 core_decipher_name, R123 desc, R124 underground_name ...
for i, (zh, en) in enumerate(PACKS):
    name_row = 122 + i * 2
    desc_row = 123 + i * 2
    # Col B 中文
    data_ranges.append({
        'range': f"'{SHEET}'!B{name_row}",
        'majorDimension': 'ROWS',
        'values': [[zh_name(zh)]]
    })
    data_ranges.append({
        'range': f"'{SHEET}'!D{name_row}",
        'majorDimension': 'ROWS',
        'values': [[en_name(en)]]
    })
    data_ranges.append({
        'range': f"'{SHEET}'!B{desc_row}",
        'majorDimension': 'ROWS',
        'values': [[zh_desc(zh)]]
    })
    data_ranges.append({
        'range': f"'{SHEET}'!D{desc_row}",
        'majorDimension': 'ROWS',
        'values': [[en_desc(en)]]
    })

print(f"共 {len(data_ranges)} 个 range 待写入")
for p in PACKS:
    print(f"  {zh_name(p[0])} | {zh_desc(p[0])}")

params = {'spreadsheetId': SPREADSHEET_ID, 'valueInputOption': 'RAW'}
body   = {'data': data_ranges}

r = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
     '--params', json.dumps(params, ensure_ascii=False),
     '--json',   json.dumps(body,   ensure_ascii=False)],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)

out = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {}
if 'error' in out:
    print('[失败]', out)
    sys.exit(1)
print(f"[成功] totalUpdatedCells={out.get('totalUpdatedCells', '?')}")
