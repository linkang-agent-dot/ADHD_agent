"""
重新读取7月/8月排期表完整文字数据，用于核对报告
"""
import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

meta = json.loads(subprocess.run(
    [gws, 'sheets', 'spreadsheets', 'get', '--params',
     json.dumps({'spreadsheetId': SHEET_ID, 'fields': 'sheets.properties'})],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout)
gid_map = {s['properties']['sheetId']: s['properties']['title']
           for s in meta.get('sheets', [])}
july_name = gid_map[1053666315]
aug_name  = gid_map[1914018097]

def read_values(sheet_name):
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'ranges': f"'{sheet_name}'!A1:BJ60",
        'includeGridData': 'true',
    })
    r = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    resp = json.loads(r.stdout)
    return resp['sheets'][0]['data'][0].get('rowData', [])

def is_white(bg):
    if not bg: return True
    return bg.get('red',1)>=0.95 and bg.get('green',1)>=0.95 and bg.get('blue',1)>=0.95

def parse_date_cols(rows):
    date_cols = {}
    if len(rows) < 2: return date_cols
    for ci, cell in enumerate(rows[1].get('values', [])):
        val = cell.get('formattedValue', '')
        if val and len(val)==5 and val[2]=='-':
            date_cols[ci] = val
    return date_cols

def extract_all(rows, date_cols, month):
    result = []
    last_cat = ''
    for ri in range(3, len(rows)):
        cells = rows[ri].get('values', [])
        if not cells: continue
        def cv(idx): return cells[idx].get('formattedValue','') if idx<len(cells) else ''
        label=cv(0).strip(); func=cv(1).strip(); dev=cv(2).strip()
        content=cv(3).strip(); t=cv(4).strip(); plan=cv(5).strip(); art=cv(6).strip()
        if not func: continue
        if label: last_cat = label
        if not dev and func and '→' not in func and func not in ('特殊投放美需内容','对应活动'):
            continue

        colored = []
        for ci, ds in date_cols.items():
            if ci >= len(cells): continue
            bg = cells[ci].get('effectiveFormat',{}).get('backgroundColor',{})
            if not is_white(bg):
                txt = (cells[ci].get('formattedValue','') or '').strip()
                colored.append({'date': ds, 'text': txt})

        phases = [c for c in colored if c['text']]
        start = min(c['date'] for c in colored) if colored else ''
        end   = max(c['date'] for c in colored) if colored else ''

        result.append({
            'month': month, 'cat': last_cat, 'name': func,
            'dev': dev, 'content': content, 't': t,
            'plan': plan, 'art': art,
            'start': start, 'end': end,
            'phases': phases,
            'has_color': bool(colored),
        })
    return result

print("读取7月...")
july_rows  = read_values(july_name)
july_dates = parse_date_cols(july_rows)
july_all   = extract_all(july_rows, july_dates, '7月')

print("读取8月...")
aug_rows  = read_values(aug_name)
aug_dates = parse_date_cols(aug_rows)
aug_all   = extract_all(aug_rows, aug_dates, '8月')

with open(r'C:\ADHD_agent\_tmp_recheck.json', 'w', encoding='utf-8') as f:
    json.dump(july_all + aug_all, f, ensure_ascii=False, indent=2)

for month, items in [('7月', july_all), ('8月', aug_all)]:
    print(f"\n{'='*60}")
    print(f"{month} | 共 {len(items)} 条活动")
    print(f"{'='*60}")
    for a in items:
        color_mark = f"{a['start']}→{a['end']}" if a['has_color'] else '(无色块)'
        plan_mark = '' if a['plan'] in ('-','') else f" [策划案:{'有' if a['plan'] else '无'}]"
        art_mark  = '' if a['art']  in ('-','待补充','') else ''
        art_warn  = ' [美需:待补充]' if a['art'] == '待补充' else ''
        phase_str = '  阶段:' + '/'.join(p['text'][:8] for p in a['phases']) if a['phases'] else ''
        print(f"  {a['cat']:20s} | {a['name']:28s} | {a['content']:4s} | T:{a['t']:8s} | {color_mark}{phase_str}{art_warn}")

print("\n已写入 _tmp_recheck.json")
