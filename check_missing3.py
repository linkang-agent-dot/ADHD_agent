import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'

def gws_values_get(range_name):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': range_name})
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

# Check the 科技节 tab for reference - see if card groups have separate IDs
TECH_TAB = '卡册key（科技节）'
print("=== 科技节 R1-R15 (Col A-H) ===")
data = gws_values_get(f"'{TECH_TAB}'!A1:H15")
if data and 'values' in data:
    for i, row in enumerate(data['values']):
        print(f"R{i+1}: {row}")

# Check 科技节 R83-R96 area for card group theme entries
print("\n=== 科技节 R82-R97 ===")
data2 = gws_values_get(f"'{TECH_TAB}'!A82:H97")
if data2 and 'values' in data2:
    for i, row in enumerate(data2['values']):
        if any(c for c in row if c):
            print(f"R{82+i}: {row}")
        else:
            print(f"R{82+i}: (empty)")

# Also read the new tab to see what R1-R15 looks like
NEW_TAB = '复活节-整理版'
print("\n=== 新页签 R1-R15 ===")
data3 = gws_values_get(f"'{NEW_TAB}'!A1:F15")
if data3 and 'values' in data3:
    for i, row in enumerate(data3['values']):
        print(f"R{i+1}: {row}")

# Check original Easter tab Col A-H for rows where Col B has data
EASTER_TAB = '卡册key（复活节）+本地化'
print("\n=== 复活节原Tab, check all non-empty Col B (卡组主题图) ===")
data4 = gws_values_get(f"'{EASTER_TAB}'!B1:B100")
if data4 and 'values' in data4:
    for i, row in enumerate(data4['values']):
        if row and row[0]:
            print(f"R{i+1} Col B: {row[0]}")
