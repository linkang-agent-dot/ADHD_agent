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

# Re-read Easter original tab R80-R100 to see if user added theme entries
EASTER_TAB = '卡册key（复活节）+本地化'
print("=== 复活节原Tab R80-R100 (检查是否已补充卡册主题) ===")
data = gws_values_get(f"'{EASTER_TAB}'!A80:P100")
if data and 'values' in data:
    for i, row in enumerate(data['values']):
        print(f"R{80+i}: {row}")

# Also read the 科技节 R83-R91 for reference
TECH_TAB = '卡册key（科技节）'
print("\n=== 科技节 R83-R91 (卡册主题参考) ===")
data2 = gws_values_get(f"'{TECH_TAB}'!A83:H91")
if data2 and 'values' in data2:
    for i, row in enumerate(data2['values']):
        print(f"R{83+i}: {row}")
