import subprocess
import json
import os

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

# Check new tab R82-R100
NEW_TAB = '复活节-整理版'
print("=== 新页签 R82-R100 (卡册主题区域) ===")
data = gws_values_get(f"'{NEW_TAB}'!A82:F100")
if data and 'values' in data:
    for i, row in enumerate(data['values']):
        print(f"R{82+i}: {row}")

# Check original tab R83-R91
EASTER_TAB = '卡册key（复活节）+本地化'
print("\n=== 原页签 R83-R91 ===")
data2 = gws_values_get(f"'{EASTER_TAB}'!A83:G91")
if data2 and 'values' in data2:
    for i, row in enumerate(data2['values']):
        print(f"R{83+i}: {row}")

# Also check the section titles to make sure all 7 sections are present
print("\n=== 所有分区标题 ===")
data3 = gws_values_get(f"'{NEW_TAB}'!A1:A270")
if data3 and 'values' in data3:
    for i, row in enumerate(data3['values']):
        if row and row[0].startswith('【'):
            print(f"R{i+1}: {row[0]}")
