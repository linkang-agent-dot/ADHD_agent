# -*- coding: utf-8 -*-
"""读取整理版页签，找卡包本地化区域"""
import subprocess, json, os

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

params = {
    'spreadsheetId': '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw',
    'range': "'复活节-整理版'!A85:D130"   # 卡包本地化区域约在 R93+
}

r = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get',
     '--params', json.dumps(params, ensure_ascii=False)],
    capture_output=True, encoding='utf-8', errors='replace'
)

rows = json.loads(r.stdout).get('values', [])
for i, row in enumerate(rows, start=85):
    c0 = row[0] if len(row) > 0 else ''
    c1 = row[1] if len(row) > 1 else ''
    c2 = row[2] if len(row) > 2 else ''
    print(f"R{i}: {c0[:40]} | {c1[:30]} | {c2[:30]}")
