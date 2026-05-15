#!/usr/bin/env python3
"""将 1111.md 中的 TSV 行写入 X2 1111 item 表"""

import json, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs'
TAB = 'item'
GID = 0
INSERT_AT = 2195  # 0-indexed: row 2195 = after row 2194

def run_gws(args, json_body=None):
    cmd = [GWS] + args
    if json_body:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f"ERROR: {r.stderr[:300]}")
        return None
    return json.loads(r.stdout) if r.stdout.strip() else {}

# 读 TSV
tsv_file = r'C:\ADHD_agent\.cursor\config-library\cases\2026_pioneer_reskin_from_astrology\1111.md'
rows = []
in_tsv = False
with open(tsv_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip() == '```tsv':
            in_tsv = True
            continue
        if line.strip() == '```' and in_tsv:
            break
        if in_tsv and line.strip():
            cells = line.rstrip('\n').split('\t')
            rows.append(cells)

print(f"读取 {len(rows)} 行 TSV")

if not rows:
    print("无数据")
    sys.exit(1)

# Step 1+2: 直接 append 到表尾（分批，每批5行）
print(f"写入 {len(rows)} 行到 {TAB} 表尾...")
batch_size = 5
success = 0
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    range_str = f"'{TAB}'!A:AC"

    resp = run_gws(
        ['sheets', 'spreadsheets', 'values', 'append',
         '--params', json.dumps({
             'spreadsheetId': SHEET_ID,
             'range': range_str,
             'valueInputOption': 'RAW',
             'insertDataOption': 'INSERT_ROWS'
         })],
        json_body={
            "values": batch
        }
    )
    if resp is not None:
        success += len(batch)
        print(f"  批次 {i//batch_size+1}: {len(batch)} 行")
    else:
        print(f"  批次 {i//batch_size+1} 失败")

print(f"\n✅ 写入完成: {success}/{len(rows)} 行")

# Step 3: 验证
print(f"\nStep 3: 验证...")
verify = run_gws(
    ['sheets', 'spreadsheets', 'values', 'get',
     '--params', json.dumps({
         'spreadsheetId': SHEET_ID,
         'range': f"'{TAB}'!B{INSERT_AT+1}:B{INSERT_AT+len(rows)}"
     })]
)
if verify:
    ids = [r[0] for r in verify.get('values', []) if r]
    print(f"  读回 {len(ids)} 行，ID 范围: {ids[0] if ids else '?'} ~ {ids[-1] if ids else '?'}")
    if len(ids) == len(rows):
        print(f"  ✅ 行数匹配")
    else:
        print(f"  ⚠️ 行数不匹配: 期望 {len(rows)}，实际 {len(ids)}")
