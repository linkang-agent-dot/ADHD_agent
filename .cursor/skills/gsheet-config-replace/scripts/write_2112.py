#!/usr/bin/env python3
import json, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo'
TAB = 'activity_config_QA'

def run_gws(args, json_body=None):
    cmd = [GWS] + args
    if json_body:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f"ERROR: {r.stdout[:300]}")
        return None
    return json.loads(r.stdout) if r.stdout.strip() else {}

# 合并 4 个活动的 2112 TSV
rows = []
for d in ['output_21127362','output_21127363','output_21127364','output_21127365']:
    with open(f'{d}/2112.tsv', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(line.rstrip('\n').split('\t'))

print(f"共 {len(rows)} 行 2112")
for r in rows:
    idx = 1 if r[0]=='' else 0
    print(f"  {r[idx]}: {r[idx+1]}")

# append 写入
success = 0
for i in range(0, len(rows), 2):
    batch = rows[i:i+2]
    resp = run_gws(
        ['sheets', 'spreadsheets', 'values', 'append',
         '--params', json.dumps({
             'spreadsheetId': SHEET_ID,
             'range': f"'{TAB}'!A:AA",
             'valueInputOption': 'RAW',
             'insertDataOption': 'INSERT_ROWS'
         })],
        json_body={"values": batch}
    )
    if resp is not None:
        success += len(batch)
        print(f"  batch {i//2+1}: {len(batch)} rows OK")
    else:
        print(f"  batch {i//2+1} FAILED")

print(f"\n写入完成: {success}/{len(rows)}")

# 验证
print("\n验证:")
resp = run_gws(
    ['sheets', 'spreadsheets', 'values', 'get',
     '--params', json.dumps({
         'spreadsheetId': SHEET_ID,
         'range': f"'{TAB}'!B1470:C1475"
     })]
)
if resp:
    for r in resp.get('values', []):
        print(f"  {r[0]} | {r[1][:40] if len(r)>1 else ''}")
