import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

ACTIVITY_CONFIG_SHEET = '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E'

def read_tab_range(tab_title, start_row, end_row):
    params = json.dumps({'spreadsheetId': ACTIVITY_CONFIG_SHEET, 'range': f"'{tab_title}'!A{start_row}:C{end_row}"})
    r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0 or not r.stdout:
        return []
    try:
        return json.loads(r.stdout).get('values', [])
    except:
        return []

# 这些页签只是在 master 基础上追加新行，新行 ID 一定 > 当前 master 最大 ID (21127274)
MASTER_MAX_ID = 21127274

tabs = ['86赛车', '86异族大富翁', '85大富翁组合', '85节日卡册', '85彩蛋交换', '86挖孔', '86前期月卡', '86连胜7日']

result = {}
for tab in tabs:
    # master 有 1208 行，新内容在 1209 行之后，读到 1500 行足够
    rows = read_tab_range(tab, 1209, 1500)
    new_entries = []
    for row in rows:
        if row and len(row) >= 2 and row[0].isdigit():
            try:
                if int(row[0]) > MASTER_MAX_ID:
                    new_entries.append({
                        'id': row[0],
                        'comment': row[1] if len(row) > 1 else '',
                        'constant': row[2] if len(row) > 2 else ''
                    })
            except:
                pass
    result[tab] = new_entries

with open(r'C:\ADHD_agent\tmp_new_entries.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Saved.")
