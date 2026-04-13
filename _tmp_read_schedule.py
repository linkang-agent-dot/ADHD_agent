import subprocess, json, os, sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# 先获取所有 sheet 名
params = json.dumps({'spreadsheetId': SHEET_ID, 'fields': 'sheets.properties'})
result = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
data = json.loads(result.stdout)

gid_map = {}
for s in data.get('sheets', []):
    p = s['properties']
    gid_map[p['sheetId']] = p['title']

july_name = gid_map.get(1053666315, '')
aug_name = gid_map.get(1914018097, '')
print(f"7月 sheet: {july_name}")
print(f"8月 sheet: {aug_name}")

def read_sheet(name, max_rows=200):
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'range': f"'{name}'!A1:AJ{max_rows}"
    })
    r = subprocess.run([gws, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout)

july_data = read_sheet(july_name)
aug_data = read_sheet(aug_name)

# 输出到文件
with open('C:\\ADHD_agent\\_tmp_july_sched.json', 'w', encoding='utf-8') as f:
    json.dump(july_data, f, ensure_ascii=False, indent=2)
with open('C:\\ADHD_agent\\_tmp_aug_sched.json', 'w', encoding='utf-8') as f:
    json.dump(aug_data, f, ensure_ascii=False, indent=2)

print("done")
