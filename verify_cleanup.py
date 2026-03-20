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

NEW_TAB = '复活节-整理版'
print("=== 整理版 R1-R15 (卡册主题+卡片开头) ===")
data = gws_values_get(f"'{NEW_TAB}'!A1:F15")
if data and 'values' in data:
    for i, row in enumerate(data['values']):
        print(f"R{i+1}: {row}")

print("\n=== 整理版 R80-R100 (卡片尾部 → 下一分区) ===")
data2 = gws_values_get(f"'{NEW_TAB}'!A80:F100")
if data2 and 'values' in data2:
    for i, row in enumerate(data2['values']):
        print(f"R{80+i}: {row}")

print("\n=== 所有分区标题 ===")
data3 = gws_values_get(f"'{NEW_TAB}'!A1:A270")
if data3 and 'values' in data3:
    for i, row in enumerate(data3['values']):
        if row and row[0] and row[0].startswith('【'):
            print(f"R{i+1}: {row[0]}")

# Also verify original tab
EASTER_TAB = '卡册key（复活节）+本地化'
print("\n=== 原页签 R83-R91 (已修正 ID) ===")
data4 = gws_values_get(f"'{EASTER_TAB}'!E83:F91")
if data4 and 'values' in data4:
    for i, row in enumerate(data4['values']):
        print(f"R{83+i}: {row}")
