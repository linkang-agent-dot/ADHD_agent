"""
用 client_secret.json + refresh_token 获取 access_token，直接调 Sheets API
"""
import subprocess, json, os, requests

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# 读 client_secret.json（真正的 client_id/secret）
with open(r'C:\Users\linkang\.config\gws\client_secret.json', encoding='utf-8') as f:
    cs = json.load(f)

# client_secret.json 格式：{"installed": {"client_id":..., "client_secret":..., ...}}
key = list(cs.keys())[0]  # "installed" or "web"
real_client_id = cs[key]['client_id']
real_client_secret = cs[key]['client_secret']
print(f"client_id: {real_client_id[:30]}...")

# refresh_token 来自 gws auth export
creds_raw = subprocess.run([gws, 'auth', 'export'],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
creds = json.loads(creds_raw)
refresh_token = creds['refresh_token']
print(f"refresh_token: {refresh_token[:30]}...")

# 换 access_token
token_resp = requests.post('https://oauth2.googleapis.com/token', data={
    'client_id':     real_client_id,
    'client_secret': real_client_secret,
    'refresh_token': refresh_token,
    'grant_type':    'refresh_token',
})
rj = token_resp.json()
if 'error' in rj:
    print("ERROR:", rj)
    exit(1)
access_token = rj['access_token']
print(f"access_token 获取成功（长度 {len(access_token)}）")

HEADERS = {'Authorization': f'Bearer {access_token}'}

# ── 获取 sheet 名 ────────────────────────────────────────
meta = requests.get(
    f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}',
    params={'fields': 'sheets.properties'},
    headers=HEADERS
).json()
gid_map = {s['properties']['sheetId']: s['properties']['title']
           for s in meta.get('sheets', [])}
july_name = gid_map[1053666315]
aug_name  = gid_map[1914018097]
print(f"7月: {july_name}")
print(f"8月: {aug_name}")

# ── 读取格子数据（含背景色）────────────────────────────────
def fetch_grid(sheet_name):
    resp = requests.get(
        f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}',
        params={
            'ranges':          f"'{sheet_name}'!A1:AJ60",
            'includeGridData': 'true',
            'fields':          'sheets.data.rowData.values(formattedValue,effectiveFormat.backgroundColor)',
        },
        headers=HEADERS
    ).json()
    if 'error' in resp:
        print("API ERROR:", resp['error'])
        return []
    return resp['sheets'][0]['data'][0].get('rowData', [])

def rgb_to_hex(color_obj):
    r = int(round(color_obj.get('red',   1.0) * 255))
    g = int(round(color_obj.get('green', 1.0) * 255))
    b = int(round(color_obj.get('blue',  1.0) * 255))
    return f'#{r:02X}{g:02X}{b:02X}'

def is_white_or_default(color_obj):
    if not color_obj:
        return True
    r = color_obj.get('red',   1.0)
    g = color_obj.get('green', 1.0)
    b = color_obj.get('blue',  1.0)
    return (r >= 0.95 and g >= 0.95 and b >= 0.95)

def parse_date_cols(rows):
    date_cols = {}
    if len(rows) < 2:
        return date_cols
    for ci, cell in enumerate(rows[1].get('values', [])):
        val = cell.get('formattedValue', '')
        if val and '-' in val and len(val) == 5:
            date_cols[ci] = val
    return date_cols

def extract_ranges(rows, date_cols, month_label):
    results = []
    last_cat = ''
    for ri in range(3, len(rows)):
        cells = rows[ri].get('values', [])
        if not cells:
            continue
        def cv(idx):
            return cells[idx].get('formattedValue', '') if idx < len(cells) else ''
        label   = cv(0).strip()
        func    = cv(1).strip()
        dev     = cv(2).strip()
        content = cv(3).strip()
        t_score = cv(4).strip()
        if not func or not dev:
            continue
        if label:
            last_cat = label
        colored = []
        for ci, date_str in date_cols.items():
            if ci >= len(cells):
                continue
            bg = cells[ci].get('effectiveFormat', {}).get('backgroundColor', {})
            if not is_white_or_default(bg):
                colored.append((ci, date_str, bg))
        if not colored:
            continue
        start_str = min(x[1] for x in colored)
        end_str   = max(x[1] for x in colored)
        hex_col   = rgb_to_hex(colored[0][2])
        phases = []
        for ci, date_str, _ in colored:
            txt = cells[ci].get('formattedValue', '') if ci < len(cells) else ''
            if txt and txt.strip():
                phases.append({'date': date_str, 'label': txt.strip()})
        results.append({
            'month': month_label, 'cat': last_cat, 'name': func,
            'content': content, 't_score': t_score,
            'start': f"2026-{start_str}", 'end': f"2026-{end_str}",
            'hex': hex_col, 'phases': phases,
        })
    return results

print("\n读取7月...")
july_rows  = fetch_grid(july_name)
july_dates = parse_date_cols(july_rows)
print(f"  日期列 {len(july_dates)} 个: {list(july_dates.values())}")
july_acts  = extract_ranges(july_rows, july_dates, '7月')

print("读取8月...")
aug_rows   = fetch_grid(aug_name)
aug_dates  = parse_date_cols(aug_rows)
print(f"  日期列 {len(aug_dates)} 个: {list(aug_dates.values())}")
aug_acts   = extract_ranges(aug_rows, aug_dates, '8月')

all_acts = july_acts + aug_acts
print(f"\n共 {len(all_acts)} 条有颜色标记的活动：")
for a in all_acts:
    print(f"  [{a['month']}] {a['cat']:12s} | {a['name']:28s} "
          f"{a['start'][5:]} → {a['end'][5:]}  {a['hex']}")

with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', 'w', encoding='utf-8') as f:
    json.dump(all_acts, f, ensure_ascii=False, indent=2)
print("\n已写入 _tmp_acts_with_dates.json")
