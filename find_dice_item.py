import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws'

def gws_values_get(range_name):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': range_name})
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None

tab = "83异族大富翁"
# 搜索所有行，找 11112765
for start in range(1, 1200, 200):
    end = start + 200
    data = gws_values_get(f"'{tab}'!A{start}:Z{end}")
    if not data or 'values' not in data:
        break
    for i, row in enumerate(data['values']):
        if row and row[0].strip() == '11112765':
            row_num = start + i
            print(f"找到！R{row_num}:")
            print('\t'.join(str(c) for c in row))
            sys.exit(0)

print("未找到 11112765")
