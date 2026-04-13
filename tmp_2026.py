import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
SHEET = '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E'

# 读全部 QA 行（A:G）
params = json.dumps({'spreadsheetId': SHEET, 'range': "activity_config_qa!A1:G2000"})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                   capture_output=True, text=True, encoding='utf-8')
all_rows = json.loads(r.stdout).get('values', [])

# 取 ID > 21127600 的所有条目（2026年新增）
new_entries = []
for row in all_rows:
    if not row or not row[0].isdigit():
        continue
    try:
        rid = int(row[0])
        if rid > 21127600:
            new_entries.append({
                'id': row[0],
                'comment': row[1] if len(row) > 1 else '',
                'constant': row[2] if len(row) > 2 else '',
            })
    except:
        pass

with open(r'C:\ADHD_agent\tmp_2026_entries.json', 'w', encoding='utf-8') as f:
    json.dump(new_entries, f, ensure_ascii=False, indent=2)

print(f"2026 new entries: {len(new_entries)}")
for e in new_entries:
    print(f"{e['id']}  {e['comment'][:30] if e['comment'] else '?':30s}  {e['constant']}")
