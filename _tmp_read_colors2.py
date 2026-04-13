"""
用 refresh_token 换 access_token，直接调 Sheets API 读背景色
"""
import subprocess, json, os, requests
from datetime import datetime

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# ── 1. 获取 access_token ─────────────────────────────────
creds_raw = subprocess.run([gws, 'auth', 'export'],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
creds = json.loads(creds_raw)

token_resp = requests.post('https://oauth2.googleapis.com/token', data={
    'client_id':     creds['client_id'],
    'client_secret': creds['client_secret'],
    'refresh_token': creds['refresh_token'],
    'grant_type':    'refresh_token',
})
access_token = token_resp.json()['access_token']
print(f"access_token 获取成功（长度 {len(access_token)}）")

HEADERS = {'Authorization': f'Bearer {access_token}'}

# ── 2. 获取所有 sheet 名 ─────────────────────────────────
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

# ── 3. 读取格子数据（含背景色）────────────────────────────
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
    """从第2行（index=1）提取列索引→日期字符串映射"""
    date_cols = {}
    if len(rows) < 2:
        return date_cols
    for ci, cell in enumerate(rows[1].get('values', [])):
        val = cell.get('formattedValue', '')
        if val and '-' in val and len(val) == 5:
            date_cols[ci] = val
    return date_cols

def extract_ranges(rows, date_cols, month_label, year=2026):
    results = []
    last_cat = ''
    DATA_START = 3

    for ri in range(DATA_START, len(rows)):
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

        # 找有颜色的日期格子
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
        dom_color = colored[0][2]
        hex_col   = rgb_to_hex(dom_color)

        # 分阶段文字标记
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

# ── 4. 执行 ──────────────────────────────────────────────
print("\n读取7月格子...")
july_rows  = fetch_grid(july_name)
july_dates = parse_date_cols(july_rows)
print(f"  日期列: {len(july_dates)} 列 → {list(july_dates.values())[:5]}...")
july_acts  = extract_ranges(july_rows, july_dates, '7月')

print("读取8月格子...")
aug_rows   = fetch_grid(aug_name)
aug_dates  = parse_date_cols(aug_rows)
print(f"  日期列: {len(aug_dates)} 列 → {list(aug_dates.values())[:5]}...")
aug_acts   = extract_ranges(aug_rows, aug_dates, '8月')

all_acts = july_acts + aug_acts
print(f"\n共提取 {len(all_acts)} 条有日期标记的活动：")
for a in all_acts:
    print(f"  [{a['month']}] {a['cat']:12s} | {a['name']:25s} "
          f"{a['start'][5:]} → {a['end'][5:]}  {a['hex']}")

with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', 'w', encoding='utf-8') as f:
    json.dump(all_acts, f, ensure_ascii=False, indent=2)
print("\n已写入 _tmp_acts_with_dates.json")
