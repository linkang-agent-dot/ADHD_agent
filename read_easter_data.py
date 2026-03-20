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
        print(f"ERROR reading {range_name}: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"JSON parse error for {range_name}: {result.stdout[:200]}", file=sys.stderr)
        return None

full_range = f"'{TAB_NAME}'!A1:P210"
print(f"Reading {full_range} ...")
data = gws_values_get(full_range)

if data and 'values' in data:
    rows = data['values']
    print(f"Total rows: {len(rows)}")
    
    with open('easter_dump.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("Saved to easter_dump.json")
    
    with open('easter_dump.txt', 'w', encoding='utf-8') as f:
        for i, row in enumerate(rows):
            padded = [c if c else '' for c in row]
            f.write(f"R{i+1}: {padded}\n")
    print("Saved to easter_dump.txt")
else:
    print("No data returned!")
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))
