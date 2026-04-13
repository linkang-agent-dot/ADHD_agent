"""
读取 Google Sheet 单元格背景色，提取每行活动的真实时间区间
"""
import subprocess, json, os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# ── 获取 sheet 名 ────────────────────────────────────────
meta = json.loads(subprocess.run(
    [gws, 'sheets', 'spreadsheets', 'get', '--params',
     json.dumps({'spreadsheetId': SHEET_ID, 'fields': 'sheets.properties'})],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout)
gid_map = {s['properties']['sheetId']: s['properties']['title']
           for s in meta.get('sheets', [])}
july_name = gid_map[1053666315]
aug_name  = gid_map[1914018097]
print(f"7月: {july_name}")
print(f"8月: {aug_name}")

def fetch_grid(sheet_name):
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'ranges': f"'{sheet_name}'!A1:AJ60",
        'includeGridData': 'true',
    })
    r = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    resp = json.loads(r.stdout)
    if 'error' in resp:
        print("ERROR:", resp['error'])
        return []
    return resp['sheets'][0]['data'][0].get('rowData', [])

def is_white(bg):
    if not bg:
        return True
    return bg.get('red', 1) >= 0.95 and bg.get('green', 1) >= 0.95 and bg.get('blue', 1) >= 0.95

def rgb_to_hex(bg):
    r = int(round(bg.get('red',   1) * 255))
    g = int(round(bg.get('green', 1) * 255))
    b = int(round(bg.get('blue',  1) * 255))
    return f'#{r:02X}{g:02X}{b:02X}'

def parse_date_cols(rows):
    """第2行（index=1）解析日期列"""
    date_cols = {}
    if len(rows) < 2:
        return date_cols
    for ci, cell in enumerate(rows[1].get('values', [])):
        val = cell.get('formattedValue', '')
        # 匹配 MM-DD 格式
        if val and len(val) == 5 and val[2] == '-':
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

        # 找有非白色背景的日期格子
        colored = []
        for ci, date_str in date_cols.items():
            if ci >= len(cells):
                continue
            bg = cells[ci].get('effectiveFormat', {}).get('backgroundColor', {})
            if not is_white(bg):
                colored.append({
                    'col': ci,
                    'date': date_str,
                    'bg': bg,
                    'hex': rgb_to_hex(bg),
                    'text': (cells[ci].get('formattedValue', '') or '').strip(),
                })

        if not colored:
            continue

        # 找主色（出现最多的）
        from collections import Counter
        color_counts = Counter(c['hex'] for c in colored)
        dominant_hex = color_counts.most_common(1)[0][0]

        # 取最早和最晚日期
        dates = [c['date'] for c in colored]
        start_str = min(dates)
        end_str   = max(dates)

        # 找分段标记（有文字的格子）
        phases = [{'date': c['date'], 'label': c['text']}
                  for c in colored if c['text']]

        # 检测是否有多段（颜色变化可能表示分期）
        segments = []
        if len(set(c['hex'] for c in colored)) > 1:
            # 按日期排序，找颜色切换点
            sorted_c = sorted(colored, key=lambda x: x['date'])
            cur_color = sorted_c[0]['hex']
            seg_start = sorted_c[0]['date']
            for c in sorted_c[1:]:
                if c['hex'] != cur_color:
                    segments.append({'start': seg_start, 'end': sorted_c[sorted_c.index(c)-1]['date'], 'hex': cur_color})
                    cur_color = c['hex']
                    seg_start = c['date']
            segments.append({'start': seg_start, 'end': sorted_c[-1]['date'], 'hex': cur_color})

        results.append({
            'month':    month_label,
            'cat':      last_cat,
            'name':     func,
            'content':  content,
            't_score':  t_score,
            'start':    f"2026-{start_str}",
            'end':      f"2026-{end_str}",
            'hex':      dominant_hex,
            'phases':   phases,
            'segments': segments,
            'colored_count': len(colored),
        })
    return results

# ── 读取 ─────────────────────────────────────────────────
print("读取7月...")
july_rows  = fetch_grid(july_name)
july_dates = parse_date_cols(july_rows)
print(f"  找到 {len(july_dates)} 个日期列: {list(july_dates.values())}")
july_acts  = extract_ranges(july_rows, july_dates, '7月')

print("读取8月...")
aug_rows   = fetch_grid(aug_name)
aug_dates  = parse_date_cols(aug_rows)
print(f"  找到 {len(aug_dates)} 个日期列: {list(aug_dates.values())}")
aug_acts   = extract_ranges(aug_rows, aug_dates, '8月')

all_acts = july_acts + aug_acts
print(f"\n共提取 {len(all_acts)} 条有颜色标记的活动：")
for a in all_acts:
    segs = f"  分段:{[(s['start'][5:]+'-'+s['end'][5:]) for s in a['segments']]}" if a['segments'] else ''
    print(f"  [{a['month']}] {a['cat']:14s} | {a['name']:28s} "
          f"{a['start'][5:]}→{a['end'][5:]}  {a['hex']}  格{a['colored_count']:2d}  {segs}")

with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', 'w', encoding='utf-8') as f:
    json.dump(all_acts, f, ensure_ascii=False, indent=2)
print("\n已写入 _tmp_acts_with_dates.json")
