import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
NEW_TAB = '复活节-整理版'
NEW_SHEET_ID = 512019199

def gws_batch_update(requests_list):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID})
    body = json.dumps({'requests': requests_list}, ensure_ascii=False)
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'batchUpdate', '--params', params, '--json', body]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

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

# Step 1: Delete old incorrect 【卡册主题】section (R95-R107: blank + title + header + 9 data + blank = 13 rows)
# Must delete from bottom up so row indices don't shift
# R95 (blank separator) through R107 (blank after section) = rows 95-107, 0-indexed: 94-106
print("Step 1: Deleting old 【卡册主题】 section (R95-R107)...")
resp = gws_batch_update([{
    'deleteDimension': {
        'range': {
            'sheetId': NEW_SHEET_ID,
            'dimension': 'ROWS',
            'startIndex': 94,   # R95 (0-indexed)
            'endIndex': 107     # R107 inclusive (0-indexed exclusive = 107)
        }
    }
}])
print(f"  {'OK' if resp else 'FAILED'}")

# After deletion, old R12-R13 are still at R12-R13
# Step 2: Delete duplicate title+header (R12-R13)
print("Step 2: Deleting duplicate title+header (R12-R13)...")
resp = gws_batch_update([{
    'deleteDimension': {
        'range': {
            'sheetId': NEW_SHEET_ID,
            'dimension': 'ROWS',
            'startIndex': 11,   # R12 (0-indexed)
            'endIndex': 13      # R13 inclusive
        }
    }
}])
print(f"  {'OK' if resp else 'FAILED'}")

# Step 3: Update section title to include card themes
print("Step 3: Updating section title...")
resp = gws_values_update(f"'{NEW_TAB}'!A1", [['【卡片清单】9 个卡册主题 + 81 张卡片']])
print(f"  {'OK' if resp else 'FAILED'}")

# Step 4: Fix original tab R83-R91 with correct IDs
EASTER_TAB = '卡册key（复活节）+本地化'
CORRECT_THEMES = [
    ['', '', '', '', '151105042', '复活节卡册主题-欢乐寻蛋'],
    ['', '', '', '', '151105043', '复活节卡册主题-彩绘时光'],
    ['', '', '', '', '151105044', '复活节卡册主题-春日花园'],
    ['', '', '', '', '151105045', '复活节卡册主题-金蛋工坊'],
    ['', '', '', '', '151105046', '复活节卡册主题-拳击冒险'],
    ['', '', '', '', '151105047', '复活节卡册主题-极速飞车'],
    ['', '', '', '', '151105048', '复活节卡册主题-矿洞寻宝'],
    ['', '', '', '', '151105049', '复活节卡册主题-彩蛋大亨'],
    ['', '', '', '', '151105050', '复活节卡册主题-异族探秘'],
]
print("Step 4: Fixing original tab R83-R91 with correct IDs (151105042-151105050)...")
resp = gws_values_update(f"'{EASTER_TAB}'!A83", CORRECT_THEMES)
print(f"  {'OK' if resp else 'FAILED'}")

print("\nCleanup complete!")
