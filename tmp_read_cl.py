import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
SHEET = '1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E'

params = json.dumps({'spreadsheetId': SHEET, 'range': '复活节checklist!A1:F50'})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                   capture_output=True, text=True, encoding='utf-8')
rows = json.loads(r.stdout).get('values', [])
with open(r'C:\ADHD_agent\tmp_cl.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print(f"Total rows: {len(rows)}")
for i, row in enumerate(rows):
    print(f"R{i+1}: {row}")
