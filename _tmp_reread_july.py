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

def fetch_grid(sheet_name):
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

def extract(rows, date_cols):
    results = []
    last_cat = ''
    for ri in range(3, len(rows)):
        cells = rows[ri].get('values', [])
        if not cells: continue
        def cv(idx): return cells[idx].get('formattedValue','') if idx<len(cells) else ''
        label=cv(0).strip(); func=cv(1).strip(); dev=cv(2).strip()
        content=cv(3).strip(); t=cv(4).strip(); plan=cv(5).strip(); art=cv(6).strip()
        if not func or not dev: continue
        if label: last_cat = label
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
        results.append({
            'cat': last_cat, 'name': func, 'content': content, 't': t,
            'plan': plan, 'art': art,
            'start': start, 'end': end, 'phases': phases,
            'has_color': bool(colored),
        })
    return results

rows  = fetch_grid(july_name)
dates = parse_date_cols(rows)
acts  = extract(rows, dates)

print(f"7月共 {len(acts)} 条：")
for a in [x for x in acts if x['has_color']]:
    phase_str = '  [' + ' / '.join(p['text'][:12] for p in a['phases']) + ']' if a['phases'] else ''
    print(f"  {a['cat']:22s} | {a['name']:28s} | {a['content']:4s} | T:{a['t']:8s} | {a['start']}→{a['end']}{phase_str}")

with open(r'C:\ADHD_agent\_tmp_july_v2.json', 'w', encoding='utf-8') as f:
    json.dump(acts, f, ensure_ascii=False, indent=2)
print("\n已写入 _tmp_july_v2.json")
