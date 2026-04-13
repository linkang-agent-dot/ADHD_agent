import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
SHEET = '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E'

params = json.dumps({'spreadsheetId': SHEET, 'includeGridData': False})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'get', '--params', params],
                   capture_output=True, text=True, encoding='utf-8')
d = json.loads(r.stdout)
sheets = d.get('sheets', [])
tab_names = [s['properties']['title'] for s in sheets]

with open(r'C:\ADHD_agent\tmp_tabs.json', 'w', encoding='utf-8') as f:
    json.dump(tab_names, f, ensure_ascii=False, indent=2)

# 只打印包含 qa/QA 或 复活/4月/easter 的
for t in tab_names:
    tl = t.lower()
    if any(kw in tl for kw in ['qa', 'easter', '复活', '4月', '大富翁', '赛车']):
        print(f"[MATCH] {t}")
    else:
        print(f"       {t}")
