"""
读取 Google Sheet 单元格背景色，推断各活动的时间区间
输出 JSON 格式：{活动名: {start: "MM-DD", end: "MM-DD", color: "#RRGGBB"}}
"""
import subprocess, json, os
from datetime import datetime, timedelta

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

def rgb_to_hex(r, g, b):
    return '#{:02X}{:02X}{:02X}'.format(
        int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

def is_white_or_default(color_obj):
    """接近白色或空 → 视为无标记"""
    if not color_obj:
        return True
    r = color_obj.get('red',   1.0)
    g = color_obj.get('green', 1.0)
    b = color_obj.get('blue',  1.0)
    return (r >= 0.98 and g >= 0.98 and b >= 0.98)

def fetch_grid(sheet_name):
    """用 includeGridData 拿到格子数据（含背景色）"""
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'ranges': [f"'{sheet_name}'!A1:AJ60"],
        'includeGridData': True,
        'fields': 'sheets.data.rowData.values(formattedValue,effectiveFormat.backgroundColor)'
    })
    r = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    data = json.loads(r.stdout)
    rows = data['sheets'][0]['data'][0].get('rowData', [])
    return rows

def parse_dates_from_header(rows):
    """从第2行提取日期列：col_idx -> 日期字符串"""
    date_cols = {}
    if len(rows) < 2:
        return date_cols
    header_cells = rows[1].get('values', [])
    for ci, cell in enumerate(header_cells):
        val = cell.get('formattedValue', '')
        if val and '-' in val and len(val) == 5:  # "MM-DD"
            date_cols[ci] = val
    return date_cols

def extract_activity_ranges(rows, date_cols, year, month_label):
    """逐行解析活动名 + 有颜色的日期格子 → 时间区间"""
    results = []
    DATA_START = 3  # 数据从第4行(index=3)开始
    LABEL_COL  = 0
    FUNC_COL   = 1
    CAT_COL    = 0  # 分类和名称同列，合并处理

    last_cat = ''
    for ri in range(DATA_START, len(rows)):
        row = rows[ri]
        cells = row.get('values', [])
        if not cells:
            continue

        def cv(idx):
            if idx >= len(cells):
                return ''
            return cells[idx].get('formattedValue', '') or ''

        label = cv(LABEL_COL).strip()
        func  = cv(FUNC_COL).strip()
        dev   = cv(2).strip()
        content = cv(3).strip()
        t_score = cv(4).strip()

        # 跳过非活动行（备注、特殊投放说明等）
        if not func or not dev:
            continue
        if label:
            last_cat = label
        display_name = f"{last_cat} | {func}" if last_cat else func

        # 找日期列中有颜色的格子
        colored_cols = []
        dominant_color = None
        for ci, date_str in date_cols.items():
            if ci >= len(cells):
                continue
            cell = cells[ci]
            bg = cell.get('effectiveFormat', {}).get('backgroundColor', {})
            if not is_white_or_default(bg):
                colored_cols.append((ci, date_str, bg))
                if dominant_color is None:
                    dominant_color = bg

        if not colored_cols:
            continue  # 无颜色标记，跳过

        # 取最早和最晚日期
        date_strs = [x[1] for x in colored_cols]
        start_str = min(date_strs)
        end_str   = max(date_strs)
        hex_color = rgb_to_hex(
            dominant_color.get('red',   0.5),
            dominant_color.get('green', 0.5),
            dominant_color.get('blue',  0.5)
        ) if dominant_color else '#888888'

        # 检查是否有分阶段标记（文字值）
        phases = []
        for ci, date_str, bg in colored_cols:
            text_val = cells[ci].get('formattedValue', '') if ci < len(cells) else ''
            if text_val and text_val.strip():
                phases.append((date_str, text_val.strip()))

        results.append({
            'month':   month_label,
            'cat':     last_cat,
            'name':    func,
            'display': display_name,
            'content': content,
            't_score': t_score,
            'start':   start_str,
            'end':     end_str,
            'hex':     hex_color,
            'phases':  phases,
        })

    return results

# ── 读取两个月 ───────────────────────────────────────────
print("读取7月...")
july_rows = fetch_grid(july_name)
july_dates = parse_dates_from_header(july_rows)
print(f"  日期列数量: {len(july_dates)}")
july_acts = extract_activity_ranges(july_rows, july_dates, 2026, '7月')

print("读取8月...")
aug_rows = fetch_grid(aug_name)
aug_dates = parse_dates_from_header(aug_rows)
print(f"  日期列数量: {len(aug_dates)}")
aug_acts = extract_activity_ranges(aug_rows, aug_dates, 2026, '8月')

all_acts = july_acts + aug_acts
print(f"\n共提取 {len(all_acts)} 条活动（有日期标记）")
for a in all_acts:
    print(f"  {a['month']} {a['display']:35s}  {a['start']} → {a['end']}  {a['hex']}  phases={a['phases']}")

with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', 'w', encoding='utf-8') as f:
    json.dump(all_acts, f, ensure_ascii=False, indent=2)
print("\n已写入 _tmp_acts_with_dates.json")
