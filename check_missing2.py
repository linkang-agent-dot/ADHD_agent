import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
TAB_NAME = '卡册key（复活节）+本地化'

def gws_values_get(range_name):
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'range': range_name
    })
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

# Check R83-R96 area (was empty before, maybe now has card group theme data)
print("=== R80-R100 (空白区 + 卡组详表前) ===")
data = gws_values_get(f"'{TAB_NAME}'!A80:P100")
if data and 'values' in data:
    for i, row in enumerate(data['values']):
        if any(c for c in row if c):
            print(f"R{80+i}: {row}")

# Check Col B specifically for all card group theme rows
print("\n=== Col A:B for R1-R82 (check 卡组主题图 column) ===")
data2 = gws_values_get(f"'{TAB_NAME}'!A1:B82")
if data2 and 'values' in data2:
    for i, row in enumerate(data2['values']):
        if len(row) > 1 and row[1]:
            print(f"R{i+1}: A={row[0]}, B={row[1]}")
        elif row[0]:
            print(f"R{i+1}: A={row[0]}, B=(empty)")

# Also read wider range to check for any 1511 IDs we might have missed
print("\n=== Search for '1511' in full original tab ===")
data3 = gws_values_get(f"'{TAB_NAME}'!A1:Z210")
if data3 and 'values' in data3:
    for i, row in enumerate(data3['values']):
        for j, cell in enumerate(row):
            if cell and '1511' in str(cell) and j != 5 and j != 6:
                col_letter = chr(65 + j) if j < 26 else f"Col{j}"
                print(f"R{i+1} {col_letter}(idx{j}): {cell}")
