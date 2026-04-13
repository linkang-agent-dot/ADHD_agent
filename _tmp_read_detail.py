import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

def read_sheet_raw(name):
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'range': f"'{name}'!A1:AJ60"
    })
    r = subprocess.run([gws, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout).get('values', [])

# 获取 sheet 名
meta = json.loads(subprocess.run(
    [gws, 'sheets', 'spreadsheets', 'get', '--params',
     json.dumps({'spreadsheetId': SHEET_ID, 'fields': 'sheets.properties'})],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout)

gid_map = {s['properties']['sheetId']: s['properties']['title']
           for s in meta.get('sheets', [])}

july_name = gid_map[1053666315]
aug_name  = gid_map[1914018097]

for month, name in [('7月', july_name), ('8月', aug_name)]:
    rows = read_sheet_raw(name)
    print(f"\n{'='*60}")
    print(f"{month} - {name}")
    print(f"{'='*60}")
    # 打印日期行
    if len(rows) > 1:
        print(f"日期行: {rows[1]}")
    if len(rows) > 2:
        print(f"序号行: {rows[2]}")
    print(f"\n--- 活动行（行索引:值列表）---")
    for i, row in enumerate(rows):
        if i < 3:
            continue
        if not row or not row[0].strip():
            continue
        # 打印完整行
        print(f"行{i:2d}: {row}")
