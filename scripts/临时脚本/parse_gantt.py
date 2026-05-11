import subprocess, json, sys, os, datetime
sys.stdout.reconfigure(encoding='utf-8')

gws_path = os.path.expanduser('~/AppData/Roaming/npm/gws.cmd')
params = json.dumps({
    'spreadsheetId': '1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8',
    'ranges': "'2026科技节上线checklist+甘特图（正式）'!A7:AH51",
    'includeGridData': True,
    'fields': 'sheets.data.rowData.values.effectiveFormat.backgroundColor,sheets.data.rowData.values.formattedValue'
})
result = subprocess.run([gws_path, 'sheets', 'spreadsheets', 'get', '--params', params], capture_output=True, encoding='utf-8')
data = json.loads(result.stdout)
rows = data['sheets'][0]['data'][0]['rowData']

dates = ['3-12','3-13','3-14','3-15','3-16','3-17','3-18','3-19','3-20','3-21','3-22','3-23','3-24','3-25','3-26','3-27','3-28','3-29','3-30','3-31','4-1','4-2']

for idx in range(len(rows)):
    row = rows[idx]
    cells = row.get('values', [])
    name = cells[0].get('formattedValue','') if len(cells) > 0 else ''
    aid = cells[1].get('formattedValue','') if len(cells) > 1 else ''
    if not name or not aid:
        continue

    segments = []
    cur_start = None
    cur_color = None
    cur_text = ''

    for j in range(12, min(len(cells), 12+22)):
        cell = cells[j]
        bg = cell.get('effectiveFormat', {}).get('backgroundColor', {})
        r = bg.get('red', 1.0)
        g = bg.get('green', 1.0)
        b = bg.get('blue', 1.0)
        fv = cell.get('formattedValue', '')
        is_colored = not (r > 0.95 and g > 0.95 and b > 0.95)
        color_hex = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}' if is_colored else None

        if is_colored:
            if cur_start is None:
                cur_start = j - 12
                cur_color = color_hex
                cur_text = fv
            elif color_hex != cur_color:
                segments.append((dates[cur_start], dates[j-1-12], cur_color, cur_text))
                cur_start = j - 12
                cur_color = color_hex
                cur_text = fv
            else:
                if fv:
                    if cur_text:
                        cur_text += ' ' + fv
                    else:
                        cur_text = fv
        else:
            if cur_start is not None:
                segments.append((dates[cur_start], dates[j-1-12], cur_color, cur_text))
                cur_start = None
                cur_color = None
                cur_text = ''

    if cur_start is not None:
        last_idx = min(len(dates)-1, len(cells)-12-1)
        if last_idx >= cur_start:
            segments.append((dates[cur_start], dates[last_idx], cur_color, cur_text))

    if segments:
        seg_str = ' | '.join([f'{s}~{e} [{c}] {t}' for s,e,c,t in segments])
        print(f'{aid} {name}: {seg_str}')
