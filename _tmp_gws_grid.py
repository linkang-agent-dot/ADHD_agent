"""
直接通过 Node.js 调用 gws 内部 token，或者用 gws 调真实 API
"""
import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# 用 gws spreadsheets get，传 includeGridData 为字符串 'true'
# gid 1053666315 对应 7月，只读 A1:J6 先验证
july_name = 'X2-7\u6708\u70df\u706b\u5e86\u5178'

params = json.dumps({
    'spreadsheetId': SHEET_ID,
    'ranges': f"'{july_name}'!A1:J6",
    'includeGridData': 'true',
})
r = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
    capture_output=True, text=True, encoding='utf-8', errors='replace')
resp = json.loads(r.stdout)
print("keys:", list(resp.keys()))
if 'error' in resp:
    print("error:", resp['error'])
elif 'sheets' in resp:
    rows = resp['sheets'][0]['data'][0].get('rowData', [])
    print(f"行数: {len(rows)}")
    for i, row in enumerate(rows[:4]):
        cells = row.get('values', [])
        print(f"行{i}:")
        for j, c in enumerate(cells[:8]):
            bg = c.get('effectiveFormat', {}).get('backgroundColor', {})
            fv = c.get('formattedValue', '')
            if fv or (bg and not (bg.get('red',1)>=0.95 and bg.get('green',1)>=0.95 and bg.get('blue',1)>=0.95)):
                print(f"  [{j}] '{fv}' bg={bg}")
