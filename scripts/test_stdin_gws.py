# -*- coding: utf-8 -*-
"""Test: call gws via stdin wrapper to bypass command line limits."""
import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
WRAPPER = os.path.join(os.path.dirname(__file__), 'gws_stdin.js')
SPREADSHEET_ID = '1hHEfazq6OghuTJlVPVxoO0VdApWitMIl0--F6ih0_U0'

params = json.dumps({
    "spreadsheetId": SPREADSHEET_ID,
    "range": "'activity_config'!A1:C1",
    "valueInputOption": "RAW"
})

body = {"values": [["test_stdin", "col_a", "col_b"]], "majorDimension": "ROWS"}

stdin_payload = json.dumps({
    "args": ['sheets', 'spreadsheets', 'values', 'update', '--params', params],
    "json": body
}, ensure_ascii=False)

print(f"Stdin payload length: {len(stdin_payload)}")

proc = subprocess.run(
    ['node', WRAPPER],
    input=stdin_payload,
    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30
)
print(f"Return code: {proc.returncode}")
print(f"Stdout: {proc.stdout[:500]}")
if proc.stderr:
    print(f"Stderr: {proc.stderr[:500]}")
