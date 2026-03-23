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
        print(f"ERROR: {result.stderr[:300]}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return None

# 先获取所有页签名称
def get_sheet_names():
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'fields': 'sheets.properties'})
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[:300]}", file=sys.stderr)
        return []
    data = json.loads(result.stdout)
    return [(s['properties']['title'], s['properties']['sheetId']) for s in data.get('sheets', [])]

print("=== 获取页签列表 ===")
sheets = get_sheet_names()
for title, sid in sheets:
    print(f"  [{sid}] {title}")

# 读取默认页签前100行（A1:Z100）
print("\n=== 读取第一个页签前5行 ===")
if sheets:
    first_sheet = sheets[0][0]
    data = gws_values_get(f"'{first_sheet}'!A1:Z5")
    if data and 'values' in data:
        for row in data['values']:
            print('\t'.join(str(c) for c in row))
