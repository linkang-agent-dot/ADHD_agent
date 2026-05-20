#!/usr/bin/env python3
import json, subprocess, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

item_map = {'11119497': '111111314', '11119517': '111111315'}
sorted_items = sorted(item_map.items(), key=lambda x: len(x[0]), reverse=True)

def safe_replace(text):
    result = text
    phs = {}
    for i, (old, new) in enumerate(sorted_items):
        ph = f'__PH{i}__'
        phs[ph] = new
        result = re.sub(r'(?<![0-9])' + re.escape(old) + r'(?![0-9])', ph, result)
    for ph, new in phs.items():
        result = result.replace(ph, new)
    return result

def run_gws(args, jb=None):
    cmd = [GWS] + args
    if jb: cmd.extend(['--json', json.dumps(jb, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

# 1. 新建 2011
SID_2011 = '1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY'
r = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID_2011, 'range': "'iap_config_x2qa'!A:T"})])
rows = (r or {}).get('values', [])
src = next((r for r in rows if len(r)>1 and r[1].strip() == '2011920111'), None)
max_id = max(int(r[1]) for r in rows if len(r)>1 and r[1].strip().isdigit())
new_2011_id = str(max_id + 1)
print(f'新 2011: {new_2011_id}')

new_2011 = list(src)
new_2011[1] = new_2011_id
new_2011[2] = new_2011[2].replace('占星节', '拓荒节')
new_2011[9] = new_2011[9].replace('21127360', '21127370')
new_2011[12] = re.sub(r'"id":\d+', '"id":21127380', new_2011[12], count=1)
for j in range(len(new_2011)):
    new_2011[j] = safe_replace(new_2011[j])

r_meta = run_gws(['sheets', 'spreadsheets', 'get',
    '--params', json.dumps({'spreadsheetId': SID_2011, 'fields': 'sheets.properties'})])
gid = next(s['properties']['sheetId'] for s in (r_meta or {}).get('sheets',[]) if s.get('properties',{}).get('title')=='iap_config_x2qa')
last = len(rows)
run_gws(['sheets', 'spreadsheets', 'batchUpdate', '--params', json.dumps({'spreadsheetId': SID_2011})],
    jb={"requests": [{"insertDimension": {"range": {"sheetId": gid, "dimension": "ROWS", "startIndex": last, "endIndex": last+1}, "inheritFromBefore": True}}]})
run_gws(['sheets', 'spreadsheets', 'values', 'update',
    '--params', json.dumps({'spreadsheetId': SID_2011, 'range': f"'iap_config_x2qa'!A{last+1}:T{last+1}", 'valueInputOption': 'RAW'})],
    jb={"values": [new_2011]})
print('2011 写入 ✓')

# 2. 新建 2013
SID_2013 = '1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E'
r2 = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID_2013, 'range': "'iap_template_x2（qa）'!B:AE"})])
rows_2013 = (r2 or {}).get('values', [])
src_2013 = [r for r in rows_2013 if len(r)>2 and r[2].strip() == '2011920111']
print(f'源 2013: {len(src_2013)} 行')
max_2013 = max(int(r[0]) for r in rows_2013 if r and r[0].strip().isdigit())
next_2013 = max_2013 + 1

new_rows_2013 = []
for row in src_2013:
    new_row = list(row)
    new_row[0] = str(next_2013)
    next_2013 += 1
    new_row[2] = new_2011_id
    for j in range(len(new_row)):
        new_row[j] = safe_replace(new_row[j])
    if len(new_row) > 3:
        new_row[3] = new_row[3].replace('占星', '拓荒')
    new_rows_2013.append(new_row)

r_meta2 = run_gws(['sheets', 'spreadsheets', 'get',
    '--params', json.dumps({'spreadsheetId': SID_2013, 'fields': 'sheets.properties'})])
gid2 = next(s['properties']['sheetId'] for s in (r_meta2 or {}).get('sheets',[]) if 'iap_template_x2' in s.get('properties',{}).get('title',''))
last2 = len(rows_2013)
run_gws(['sheets', 'spreadsheets', 'batchUpdate', '--params', json.dumps({'spreadsheetId': SID_2013})],
    jb={"requests": [{"insertDimension": {"range": {"sheetId": gid2, "dimension": "ROWS", "startIndex": last2, "endIndex": last2+len(new_rows_2013)}, "inheritFromBefore": True}}]})
ok = 0
for i, row in enumerate(new_rows_2013):
    resp = run_gws(['sheets', 'spreadsheets', 'values', 'update',
        '--params', json.dumps({'spreadsheetId': SID_2013, 'range': f"'iap_template_x2（qa）'!B{last2+i+1}:AE{last2+i+1}", 'valueInputOption': 'RAW'})],
        jb={"values": [row]})
    if resp: ok += 1
print(f'2013 写入 {ok}/{len(new_rows_2013)}')

# 3. 更新 2121 212101117 status → 新 2011
SID_2121 = '1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4'
r3 = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID_2121, 'range': "'activity_special'!B:M"})])
for i, row in enumerate((r3 or {}).get('values', [])):
    if row and row[0].strip() == '212101117':
        row_num = i + 1
        status = row[11] if len(row) > 11 else ''
        new_status = re.sub(r'(?<![0-9])2011920111(?![0-9])', new_2011_id, status)
        run_gws(['sheets', 'spreadsheets', 'values', 'update',
            '--params', json.dumps({'spreadsheetId': SID_2121, 'range': f"'activity_special'!M{row_num}", 'valueInputOption': 'RAW'})],
            jb={"values": [[new_status]]})
        print(f'2121 discount: 2011920111 → {new_2011_id} ✓')
        break

# 4. 更新 2122 累充排名 score_rule 加入新 2011
SID_2122 = '1P5bHlZdhuRlpYkJA6tvaZuK32V5RZFRvuQuuomMjiM4'
r4 = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID_2122, 'range': "'activity_rank_rule（QA）'!C:E"})])
for i, row in enumerate((r4 or {}).get('values', [])):
    if row and row[0].strip() == '21223205':
        row_num = i + 1
        score = row[2] if len(row) > 2 else '[]'
        score_obj = json.loads(score)
        ids_list = score_obj[0]['ids']
        new_id_int = int(new_2011_id)
        if new_id_int not in ids_list:
            ids_list.append(new_id_int)
            new_score = json.dumps(score_obj, ensure_ascii=False, separators=(',', ':'))
            run_gws(['sheets', 'spreadsheets', 'values', 'update',
                '--params', json.dumps({'spreadsheetId': SID_2122, 'range': f"'activity_rank_rule（QA）'!E{row_num}", 'valueInputOption': 'RAW'})],
                jb={"values": [[new_score]]})
            print(f'2122 score_rule: +{new_2011_id}（共{len(ids_list)}个）✓')
        break

print(f'\n完成。新 2011={new_2011_id}')
