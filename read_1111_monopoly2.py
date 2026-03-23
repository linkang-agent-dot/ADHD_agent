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

# 读 R100-R300，找活动专用道具
data = gws_values_get(f"'{tab}'!A100:Z300")
if data and 'values' in data:
    rows = data['values']
    print(f"R100-R300 共 {len(rows)} 行\n")
    for i, row in enumerate(rows):
        row_num = 100 + i
        # 只打印有数据的行（跳过全空行）
        if any(c.strip() for c in row if c):
            print(f"R{row_num}: " + '\t'.join(str(c) for c in row))
else:
    print("无数据")
