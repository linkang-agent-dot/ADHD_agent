# -*- coding: utf-8 -*-
"""修正复活节主题卡包描述格式
正确格式：打开即可获得2张3星以上"XXXX"游戏卡片。
"""
import subprocess, json, os, sys

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
SHEET = '卡册key（复活节）+本地化'

# 只改 desc 行（R3/R5/R7/R9），name 行（R2/R4/R6/R8）保持"XXXX卡包"格式不变
# 格式：打开即可获得2张3星以上"XXXX"游戏卡片。
# EN：Open to receive 2 \u201cXXXX\u201d game cards of 3 stars or above.

DESC_ROWS = [
    # (行号, 中文游戏名, 英文游戏名)
    (3, "矿洞寻宝", "Mine Treasure Hunt"),
    (5, "极速飞车", "Speed Racing"),
    (7, "彩蛋大亨", "Easter Tycoon"),
    (9, "异族探秘", "Alien Exploration"),
]

data_ranges = []
for row, zh_name, en_name in DESC_ROWS:
    zh_desc = f'\u6253\u5f00\u5373\u53ef\u83b7\u5f972\u53743\u661f\u4ee5\u4e0a\u201c{zh_name}\u201d\u6e38\u620f\u5361\u7247\u3002'
    en_desc = f'Open to receive 2 \u201c{en_name}\u201d game cards of 3 stars or above.'
    data_ranges.append({
        "range": f"'{SHEET}'!K{row}:L{row}",
        "majorDimension": "ROWS",
        "values": [[zh_desc, en_desc]]
    })

params = {"spreadsheetId": SPREADSHEET_ID, "valueInputOption": "RAW"}
body = {"data": data_ranges}

print(f"[写入] 共 {len(data_ranges)} 行 desc 修正")
for row, zh_name, en_name in DESC_ROWS:
    print(f"  R{row}: 打开即可获得2张3星以上\u201c{zh_name}\u201d游戏卡片。")

r = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
     '--params', json.dumps(params, ensure_ascii=False),
     '--json', json.dumps(body, ensure_ascii=False)],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)

out = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {}
if r.returncode != 0 or 'error' in out:
    print(f"[失败] {r.stderr or out}")
    sys.exit(1)

total = out.get('totalUpdatedCells', '?')
print(f"[成功] totalUpdatedCells={total}")
