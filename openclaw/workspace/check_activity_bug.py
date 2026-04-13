import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
OUTPUT = 'c:/ADHD_agent/openclaw/workspace/easter_extend.txt'

def gws_values(sid, rng):
    params = json.dumps({'spreadsheetId': sid, 'range': rng})
    r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                       capture_output=True, text=True, encoding='utf-8')
    return json.loads(r.stdout).get('values', [])

lines = []

# ===== 2148: 查科技节挖矿(214845) 和 科技节大富翁(214846?) 有涂饰功能的行 =====
lines.append("=== 2148: 搜索有涂饰功能的行 (col5!=0) ===")
rows = gws_values('1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw', 'event_decroation_level!A:X')
for i, row in enumerate(rows):
    if i == 0: continue
    try:
        paint_col = str(row[5]).strip() if len(row) > 5 else '0'
        if paint_col != '0' and paint_col != '':
            lines.append(f"row {i}: " + "\t".join(f"[{j}]{c}" for j, c in enumerate(row[:20])))
    except: pass

# ===== 2171表的全部内容 =====
lines.append("\n=== 2171 全表 ===")
tabs_r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'get', '--params',
    json.dumps({'spreadsheetId': '1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4', 'fields': 'sheets.properties'})],
    capture_output=True, text=True, encoding='utf-8')
tabs = [(s['properties']['sheetId'], s['properties']['title'])
        for s in json.loads(tabs_r.stdout).get('sheets', [])]
lines.append(f"tabs: {tabs}")
rows2171 = gws_values('1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4', f"'{tabs[0][1]}'!A:F")
if rows2171:
    lines.append("HEADER: " + "\t".join(f"[{i}]{c}" for i, c in enumerate(rows2171[0])))
for i, row in enumerate(rows2171[1:], 1):
    lines.append(f"  row {i}: " + "\t".join(str(c) for c in row))

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"Done → {OUTPUT}")
