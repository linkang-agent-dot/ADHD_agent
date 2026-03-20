import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
TAB_NAME = '卡册key（复活节）+本地化'

def gws_values_get(range_name):
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'range': range_name
    })
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

# Read original tab - wider range to capture all columns including B
data = gws_values_get(f"'{TAB_NAME}'!A1:H15")
if data and 'values' in data:
    rows = data['values']
    with open('check_missing_output.txt', 'w', encoding='utf-8') as f:
        for i, row in enumerate(rows):
            line = f"R{i+1} (len={len(row)}): {row}"
            f.write(line + '\n')
            print(line)

# Also check the new tab's section 1 header area
NEW_TAB = '复活节-整理版'
data2 = gws_values_get(f"'{NEW_TAB}'!A1:F15")
if data2 and 'values' in data2:
    rows2 = data2['values']
    print("\n--- New tab section 1 ---")
    for i, row in enumerate(rows2):
        print(f"R{i+1}: {row}")
