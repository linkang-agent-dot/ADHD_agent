import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# 探索 gws sheets 的子命令
r = subprocess.run([gws, 'sheets', '--help'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print("=== sheets --help ===")
print(r.stdout[:2000])
print(r.stderr[:500])

# 试 spreadsheets get 无 fields 参数
params = json.dumps({'spreadsheetId': SHEET_ID, 'includeGridData': True,
                     'ranges': ["'X2-7\u6708\u70df\u706b\u5e86\u5178'!A1:J5"]})
r2 = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\n=== raw response (first 3000 chars) ===")
print(r2.stdout[:3000])
print(r2.stderr[:500])
