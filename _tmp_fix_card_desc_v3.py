# -*- coding: utf-8 -*-
"""修正复活节主题卡包描述 — 正确格式：打开即可获得两张3星以上"XXXX"游戏卡片。"""
import subprocess, json, os, sys

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
SHEET = '卡册key（复活节）+本地化'

DESC_ROWS = [
    (3,  '矿洞寻宝', 'Mine Treasure Hunt'),
    (5,  '极速飞车', 'Speed Racing'),
    (7,  '彩蛋大亨', 'Easter Tycoon'),
    (9,  '异族探秘', 'Alien Exploration'),
]

data_ranges = []
for row, zh_name, en_name in DESC_ROWS:
    zh_desc = '打开即可获得两张3星以上\u201c' + zh_name + '\u201d游戏卡片。'
    en_desc  = 'Open to receive 2 \u201c' + en_name + '\u201d game cards of 3 stars or above.'
    data_ranges.append({
        'range': f"'{SHEET}'!K{row}:L{row}",
        'majorDimension': 'ROWS',
        'values': [[zh_desc, en_desc]]
    })
    print(f"R{row} ZH: {zh_desc}")
    print(f"R{row} EN: {en_desc}")

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
