import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# includeGridData 通过 gws 来用
params = json.dumps({
    'spreadsheetId': SHEET_ID,
    'includeGridData': True,
    'ranges': ['Sheet1!A1:J5'],
})
r = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
    capture_output=True, text=True, encoding='utf-8', errors='replace')
resp = json.loads(r.stdout)
print("Top-level keys:", list(resp.keys()))

# 如果没有 sheets，看看能不能直接获取 token
# 尝试用 gws 执行任意 HTTP 请求
r2 = subprocess.run([gws, '--help'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r2.stdout[:500])
