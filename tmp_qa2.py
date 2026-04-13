import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
SHEET = '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E'

# 先看 header
params = json.dumps({'spreadsheetId': SHEET, 'range': "activity_config_qa!A1:G3"})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                   capture_output=True, text=True, encoding='utf-8')
header_rows = json.loads(r.stdout).get('values', [])
print("=== Header ===")
for row in header_rows:
    print(row)

# 读全部
params2 = json.dumps({'spreadsheetId': SHEET, 'range': "activity_config_qa!A1:G3000"})
r2 = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params2],
                    capture_output=True, text=True, encoding='utf-8')
all_rows = json.loads(r2.stdout).get('values', [])
print(f"Total rows: {len(all_rows)}")

# 筛选复活节/4月/大富翁/赛车/异族
keywords = ['4月', '复活节', 'easter', 'Easter', '大富翁', '赛车', '异族', '彩蛋']
matched = []
for i, row in enumerate(all_rows):
    row_text = ' '.join(row)
    if any(kw in row_text for kw in keywords):
        matched.append({'row': i+1, 'data': row})

print(f"\n=== Matched ({len(matched)}) ===")
for m in matched:
    print(f"R{m['row']}: {m['data']}")

with open(r'C:\ADHD_agent\tmp_qa_matched.json', 'w', encoding='utf-8') as f:
    json.dump(matched, f, ensure_ascii=False, indent=2)
