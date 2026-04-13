# -*- coding: utf-8 -*-
import subprocess, json, os

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

params = {
    'spreadsheetId': '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw',
    'range': "'复活节-整理版'!A120:D145"
}

r = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get',
     '--params', json.dumps(params, ensure_ascii=False)],
    capture_output=True, encoding='utf-8', errors='replace'
)

rows = json.loads(r.stdout).get('values', [])
for i, row in enumerate(rows, start=120):
    cols = [c[:35] for c in row] + [''] * (4 - len(row))
    print(f"R{i}: {cols[0]} | {cols[1]} | {cols[2]} | {cols[3]}")
