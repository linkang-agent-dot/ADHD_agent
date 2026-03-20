import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
NEW_TAB = '复活节-整理版'

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

# Read all data from new tab
data = gws_values_get(f"'{NEW_TAB}'!A1:F260")
if not data or 'values' not in data:
    print("ERROR: Could not read new tab!")
    sys.exit(1)

rows = data['values']
print(f"New tab has {len(rows)} rows\n")

with open('verify_output.txt', 'w', encoding='utf-8') as f:
    for i, row in enumerate(rows):
        line = f"R{i+1}: {row}"
        f.write(line + '\n')

# Identify sections by title rows
title_rows = []
for i, row in enumerate(rows):
    if row and len(row) > 0 and row[0].startswith('【'):
        title_rows.append((i+1, row[0]))
        print(f"  Section at R{i+1}: {row[0]}")

print(f"\nFound {len(title_rows)} sections")

# Verify section data counts
expected = {
    '【卡片清单】': 81,
    '【卡包本地化】': 24,
    '【卡包描述': 22,
    '【图片描述': 6,
    '【卡组/卡片': 98,
    '【大富翁': 9,
}

for i, (row_num, title) in enumerate(title_rows):
    next_section_start = title_rows[i+1][0] - 1 if i + 1 < len(title_rows) else len(rows)
    data_start = row_num + 1  # header row is row_num+1, data starts at row_num+2
    data_rows = next_section_start - data_start
    
    for prefix, expected_count in expected.items():
        if title.startswith(prefix):
            status = "OK" if data_rows == expected_count else f"MISMATCH (expected {expected_count})"
            print(f"  {title}: {data_rows} data rows -> {status}")
            break

# Spot-check specific cells
checks = [
    (3, 'R3 (first card)', ['彩蛋节泛用主题1', '1', '满筐快乐', '151104889', '复活节卡包-满筐快乐']),
    (83, 'R83 (last card)', ['', '9', '巅峰对决', '151104969', '复活节卡包-巅峰对决']),
]

print("\nSpot checks:")
for row_idx, desc, expected_vals in checks:
    actual = rows[row_idx - 1] if row_idx <= len(rows) else []
    match = actual == expected_vals
    print(f"  {desc}: {'OK' if match else 'MISMATCH'}")
    if not match:
        print(f"    Expected: {expected_vals}")
        print(f"    Actual:   {actual}")

print("\nSaved full dump to verify_output.txt")
