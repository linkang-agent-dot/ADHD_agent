import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
NEW_TAB = '复活节-整理版'
NEW_SHEET_ID = 512019199

def gws_values_update(range_name, values, value_input_option='RAW'):
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'range': range_name,
        'valueInputOption': value_input_option,
    })
    body = json.dumps({'values': values}, ensure_ascii=False)
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def gws_batch_update(requests_list):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID})
    body = json.dumps({'requests': requests_list}, ensure_ascii=False)
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'batchUpdate', '--params', params, '--json', body]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"ERROR batchUpdate: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

# Card group theme data following the 科技节 pattern
# 科技节: R83-R91, IDs 151104485-151104493
# Easter: cards end at 151104969, themes should be 151104970-151104978
THEMES = [
    ['151104970', '复活节卡册主题-欢乐寻蛋'],
    ['151104971', '复活节卡册主题-彩绘时光'],
    ['151104972', '复活节卡册主题-春日花园'],
    ['151104973', '复活节卡册主题-金蛋工坊'],
    ['151104974', '复活节卡册主题-拳击冒险'],
    ['151104975', '复活节卡册主题-极速飞车'],
    ['151104976', '复活节卡册主题-矿洞寻宝'],
    ['151104977', '复活节卡册主题-彩蛋大亨'],
    ['151104978', '复活节卡册主题-异族探秘'],
]

# Insert rows at R84 (after R83 = last card row, before R85 = current 【卡包本地化】 section)
# First, insert 12 rows (1 blank + 1 title + 1 header + 9 data = 12 rows) at row 84
print("Inserting 12 rows at R84...")
insert_req = {
    'insertDimension': {
        'range': {
            'sheetId': NEW_SHEET_ID,
            'dimension': 'ROWS',
            'startIndex': 83,   # 0-indexed: row 84
            'endIndex': 95      # 12 rows
        },
        'inheritFromBefore': False
    }
}
resp = gws_batch_update([insert_req])
if resp:
    print("  Rows inserted OK")
else:
    print("  ERROR inserting rows")
    sys.exit(1)

# Write the new section
# R84 = blank separator (already blank from insert)
# R85 = title
# R86 = header
# R87-R95 = 9 theme entries
section_data = [
    [],  # R84 blank
    ['【卡册主题】9 个卡组主题'],  # R85 title
    ['资源ID', '主题名称'],  # R86 header
]
section_data.extend(THEMES)  # R87-R95

range_name = f"'{NEW_TAB}'!A84"
print(f"Writing theme section at {range_name}...")
resp = gws_values_update(range_name, section_data)
if resp:
    print(f"  Written OK: {resp.get('updatedRows', '?')} rows")
else:
    print("  ERROR writing data")

# Format title and header rows
# Title at row 85 (0-indexed: 84)
# Header at row 86 (0-indexed: 85)
format_requests = [
    {
        'repeatCell': {
            'range': {
                'sheetId': NEW_SHEET_ID,
                'startRowIndex': 84,
                'endRowIndex': 85,
                'startColumnIndex': 0,
                'endColumnIndex': 10
            },
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': True, 'fontSize': 12},
                    'backgroundColor': {'red': 0.85, 'green': 0.92, 'blue': 1.0}
                }
            },
            'fields': 'userEnteredFormat(textFormat,backgroundColor)'
        }
    },
    {
        'repeatCell': {
            'range': {
                'sheetId': NEW_SHEET_ID,
                'startRowIndex': 85,
                'endRowIndex': 86,
                'startColumnIndex': 0,
                'endColumnIndex': 10
            },
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
                }
            },
            'fields': 'userEnteredFormat(textFormat,backgroundColor)'
        }
    }
]

print("Applying formatting...")
resp = gws_batch_update(format_requests)
if resp:
    print("  Format OK")
else:
    print("  ERROR formatting")

# Also write to the original tab R83-R91 to fill the empty area
EASTER_TAB = '卡册key（复活节）+本地化'
orig_data = []
for theme in THEMES:
    orig_data.append(['', '', '', '', theme[0], theme[1]])

print(f"\nAlso writing to original tab R83-R91...")
resp = gws_values_update(f"'{EASTER_TAB}'!A83", orig_data)
if resp:
    print(f"  Written OK: {resp.get('updatedRows', '?')} rows")
else:
    print("  ERROR writing to original tab")

print("\nDone! Card group theme section added.")
