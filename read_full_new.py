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
data = gws_values_get(f"'{NEW_TAB}'!A1:F280")
if data and 'values' in data:
    rows = data['values']
    with open('new_tab_full.txt', 'w', encoding='utf-8') as f:
        for i, row in enumerate(rows):
            line = f"R{i+1}: {row}"
            f.write(line + '\n')
    print(f"Total rows: {len(rows)}")
    print("Saved to new_tab_full.txt")
