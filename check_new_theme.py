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

# Read the card theme section area broadly (R83-R100) to see what user added
print("=== 整理版 R82-R105 ===")
data = gws_values_get(f"'{NEW_TAB}'!A82:F105")
if data and 'values' in data:
    for i, row in enumerate(data['values']):
        print(f"R{82+i}: {row}")

# Also check if user added content at the end or other areas
print("\n=== 整理版 所有分区标题 ===")
data2 = gws_values_get(f"'{NEW_TAB}'!A1:A280")
if data2 and 'values' in data2:
    for i, row in enumerate(data2['values']):
        if row and row[0] and (row[0].startswith('【') or '主题' in row[0] or '卡组' in row[0]):
            print(f"R{i+1}: {row[0]}")
