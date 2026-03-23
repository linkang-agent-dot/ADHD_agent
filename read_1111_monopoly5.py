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

tab = "83异族大富翁"
# 读 600 - 800 找异族大富翁专属道具
data = gws_values_get(f"'{tab}'!A600:Z800")
if data and 'values' in data:
    rows = data['values']
    print(f"共 {len(rows)} 行")
    for i, row in enumerate(rows):
        row_num = 600 + i
        if any(c.strip() for c in row if c):
            id_col = row[0] if len(row) > 0 else ''
            comment = row[1] if len(row) > 1 else ''
            print(f"R{row_num}: {id_col}\t{comment}")
else:
    print("无数据 - 可能不到600行")
