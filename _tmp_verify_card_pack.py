# -*- coding: utf-8 -*-
import subprocess, json, os, sys

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

params = {
    'spreadsheetId': '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw',
    'range': "'卡册key（复活节）+本地化'!J2:L9"
}

r = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get',
     '--params', json.dumps(params, ensure_ascii=False)],
    capture_output=True, encoding='utf-8', errors='replace'
)

data = json.loads(r.stdout)
for row in data.get('values', []):
    key = row[0][:38] if len(row) > 0 else ''
    zh  = row[1][:20] if len(row) > 1 else ''
    en  = row[2][:30] if len(row) > 2 else ''
    print(f"{key:40s} | {zh:20s} | {en}")
