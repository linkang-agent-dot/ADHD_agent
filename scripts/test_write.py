# -*- coding: utf-8 -*-
"""Quick test: write a single row to the existing GSheet to diagnose failures."""
import subprocess, json, os, sys

NPM_DIR = os.path.join(os.environ.get('APPDATA', ''), 'npm')
RUN_GWS_JS = os.path.join(NPM_DIR, 'node_modules', '@googleworkspace', 'cli', 'run-gws.js')
GWS_CMD = os.path.join(NPM_DIR, 'gws.cmd')
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

SPREADSHEET_ID = '1zqKIZJNjwPX4IdhK7uxvBC0-X3d2Z0HZRvSq1WY8rqU'

def run_gws_node(args, json_body=None):
    cmd = ['node', RUN_GWS_JS] + args
    if json_body is not None:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    print(f"  CMD total chars: {sum(len(str(a)) for a in cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
    print(f"  Return: {r.returncode}")
    if r.stdout.strip():
        print(f"  Stdout: {r.stdout[:300]}")
    if r.stderr.strip():
        print(f"  Stderr: {r.stderr[:300]}")
    return r.returncode == 0

# Test 1: Simple write to activity_special A1
print("=== Test 1: Write simple row to activity_special ===")
params = json.dumps({"spreadsheetId": SPREADSHEET_ID, "range": "'activity_special'!A1", "valueInputOption": "RAW"})
body = {"values": [["test_type", "test_col1", "test_col2"]], "majorDimension": "ROWS"}
run_gws_node(['sheets', 'spreadsheets', 'values', 'update', '--params', params], body)

# Test 2: Read back what's in activity_special
print("\n=== Test 2: Read activity_special A1:C2 ===")
params2 = json.dumps({"spreadsheetId": SPREADSHEET_ID, "range": "'activity_special'!A1:C2"})
cmd = ['node', RUN_GWS_JS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params2]
r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
print(f"  Return: {r.returncode}")
print(f"  Data: {r.stdout[:500]}")

# Test 3: Write actual diff data for one row of activity_special
print("\n=== Test 3: Write real diff row ===")
REPO_DIR = r"C:\gdconfig"
diff_out = subprocess.run(
    ["git", "diff", "origin/dev...origin/dev_7days_v86", "--", "fo/config/activity_special.tsv"],
    capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO_DIR
).stdout
first_added = None
for line in diff_out.split('\n'):
    if line.startswith('+') and not line.startswith('+++'):
        content = line[1:]
        if content.strip():
            first_added = content
            break

if first_added:
    cells = first_added.split('\t')
    print(f"  First added row: {len(cells)} cols, {len(first_added)} chars")
    row = ["修改"] + cells
    params3 = json.dumps({"spreadsheetId": SPREADSHEET_ID, "range": "'activity_special'!A3", "valueInputOption": "RAW"})
    body3 = {"values": [row], "majorDimension": "ROWS"}
    json_str = json.dumps(body3, ensure_ascii=False)
    print(f"  JSON body length: {len(json_str)}")
    run_gws_node(['sheets', 'spreadsheets', 'values', 'update', '--params', params3], body3)
