# -*- coding: utf-8 -*-
"""Read back data from the GSheet to verify what's actually there."""
import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
WRAPPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gws_stdin.js')
SPREADSHEET_ID = '1Yq1xsC27Ho7yURQLSdG54qF7HXsEDgmLj2e9gZkjg-g'

def read_sheet(sheet_name, range_str):
    params = json.dumps({"spreadsheetId": SPREADSHEET_ID, "range": f"'{sheet_name}'!{range_str}"})
    stdin_payload = json.dumps({
        "args": ['sheets', 'spreadsheets', 'values', 'get', '--params', params],
        "json": None
    })
    r = subprocess.run(['node', WRAPPER], input=stdin_payload,
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            return data.get('values', [])
        except:
            pass
    return []

sheets = ['activity_config', 'activity_package', 'activity_asset_retake', 'activity_task']
for s in sheets:
    print(f"\n=== {s} ===")
    rows = read_sheet(s, 'A1:D5')
    for i, row in enumerate(rows):
        print(f"  Row{i}: {row[:4]}")
