import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
SHEET = '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E'

# 先读 QA 页签前几行，看列结构
params = json.dumps({'spreadsheetId': SHEET, 'range': "QA!A1:E5"})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                   capture_output=True, text=True, encoding='utf-8')
header_rows = json.loads(r.stdout).get('values', [])
print("=== Header ===")
for row in header_rows:
    print(row)

# 读全部 QA 行（A:F）
params2 = json.dumps({'spreadsheetId': SHEET, 'range': "QA!A1:F2000"})
r2 = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params2],
                    capture_output=True, text=True, encoding='utf-8')
all_rows = json.loads(r2.stdout).get('values', [])
print(f"\nTotal rows: {len(all_rows)}")

# 筛选关键词
keywords = ['4月', '复活节', 'easter', 'Easter', '2026', '大富翁', '赛车', '异族']
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
