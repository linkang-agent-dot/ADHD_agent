# -*- coding: utf-8 -*-
"""Debug: check special chars + actual write failures."""
import subprocess, json, os

REPO_DIR = r"C:\gdconfig"
NPM_DIR = os.path.join(os.environ.get('APPDATA', ''), 'npm')
RUN_GWS_JS = os.path.join(NPM_DIR, 'node_modules', '@googleworkspace', 'cli', 'run-gws.js')
GWS_CMD = os.path.join(NPM_DIR, 'gws.cmd')
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

SPECIAL = set('|<>&^\'"')

files = [
    'fo/config/activity_asset_retake.tsv',
    'fo/config/activity_config.tsv',
    'fo/config/activity_package.tsv',
    'fo/config/activity_special.tsv',
    'fo/config/activity_task.tsv',
    'fo/config/activity_ui_module.tsv',
    'fo/config/activity_ui_template.tsv',
    'fo/config/display_key.tsv',
    'fo/config/get_access_group.tsv',
    'fo/config/iap_config.tsv',
    'fo/config/iap_template.tsv',
    'fo/config/item.tsv',
]

print("=== Check 1: Special chars in diff data ===")
for f in files:
    diff = subprocess.run(
        ['git', 'diff', 'origin/dev...origin/dev_7days_v86', '--', f],
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO_DIR
    ).stdout
    found = set()
    max_row_json = 0
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            content = line[1:]
            if content.strip():
                for ch in content:
                    if ch in SPECIAL:
                        found.add(ch)
                row_json = json.dumps(["修改"] + content.split('\t'), ensure_ascii=False)
                if len(row_json) > max_row_json:
                    max_row_json = len(row_json)
    name = os.path.basename(f).replace('.tsv', '')
    print(f"  {name}: special={found or 'none'}, max_row_json={max_row_json}")

print("\n=== Check 2: Test gws.cmd vs node for activity_special ===")
SPREADSHEET_ID = '1zqKIZJNjwPX4IdhK7uxvBC0-X3d2Z0HZRvSq1WY8rqU'

diff = subprocess.run(
    ['git', 'diff', 'origin/dev...origin/dev_7days_v86', '--', 'fo/config/activity_special.tsv'],
    capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO_DIR
).stdout

rows = []
for line in diff.split('\n'):
    if line.startswith('+') and not line.startswith('+++'):
        content = line[1:]
        if content.strip():
            rows.append(["修改"] + content.split('\t'))

chunk = rows[:3]
body = {"values": chunk, "majorDimension": "ROWS"}
params = json.dumps({"spreadsheetId": SPREADSHEET_ID, "range": "'activity_special'!A5", "valueInputOption": "RAW"})
body_json = json.dumps(body, ensure_ascii=False)
print(f"  Body JSON len: {len(body_json)}")

print("\n  --- Via gws.cmd ---")
cmd1 = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body_json]
total_cmd_len = sum(len(a) for a in cmd1) + len(cmd1) - 1
print(f"  Total cmd chars: {total_cmd_len}")
try:
    r1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
    print(f"  Return: {r1.returncode}")
    print(f"  Stdout: {r1.stdout[:200]}")
    if r1.stderr:
        print(f"  Stderr: {r1.stderr[:200]}")
except OSError as e:
    print(f"  OSError: {e}")

print("\n  --- Via node direct ---")
cmd2 = ['node', RUN_GWS_JS, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body_json]
r2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
print(f"  Return: {r2.returncode}")
print(f"  Stdout: {r2.stdout[:200]}")
if r2.stderr:
    print(f"  Stderr: {r2.stderr[:200]}")
