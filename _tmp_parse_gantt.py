import json

with open(r'C:\ADHD_agent\_tmp_gantt_colors.json', encoding='utf-8') as f:
    color_data = json.load(f)

with open(r'C:\ADHD_agent\_tmp_gantt_data.json', encoding='utf-8') as f:
    text_data = json.load(f)

# Helper: detect if a cell has a non-white, non-empty background color
def is_colored(bg):
    if not bg:
        return False
    r = bg.get('red', 1.0)
    g = bg.get('green', 1.0)
    b = bg.get('blue', 1.0)
    # white = (1,1,1), near-white threshold
    return not (r > 0.95 and g > 0.95 and b > 0.95)

def color_to_name(bg):
    if not bg:
        return 'white'
    r = bg.get('red', 1.0)
    g = bg.get('green', 1.0)
    b = bg.get('blue', 1.0)
    # Simple color categorization
    if r > 0.8 and g < 0.5 and b < 0.5:
        return 'red'
    elif r > 0.8 and g > 0.6 and b < 0.4:
        return 'orange'
    elif r > 0.8 and g > 0.8 and b < 0.4:
        return 'yellow'
    elif r < 0.5 and g > 0.6 and b < 0.5:
        return 'green'
    elif r < 0.4 and g < 0.6 and b > 0.7:
        return 'blue'
    elif r > 0.6 and g < 0.4 and b > 0.6:
        return 'purple'
    elif r < 0.7 and g > 0.7 and b > 0.7:
        return 'cyan'
    elif r > 0.6 and g > 0.6 and b > 0.6:
        return 'gray'
    else:
        return f'rgb({r:.2f},{g:.2f},{b:.2f})'

# Sheet configs: how many gantt cols, offset of gantt start in the range
SHEET_CONFIGS = {
    'X2前期节日循环': {'gantt_weeks': 7, 'row_offset': 0, 'range_start_col': 7},   # range starts at H(col7), gantt at col8(I=1st week)
    'X2-5月占星节':   {'gantt_weeks': 7, 'row_offset': 0, 'range_start_col': 6},   # range starts at G(col6)
    'X2-6月拓荒节':   {'gantt_weeks': 7, 'row_offset': 0, 'range_start_col': 6},
    'X2-7月烟火庆典': {'gantt_weeks': 10,'row_offset': 0, 'range_start_col': 6},
}

print("=" * 80)
for sheet_name, cfg in SHEET_CONFIGS.items():
    text_rows = text_data.get(sheet_name, [])
    sheet_color = color_data.get(sheet_name, {})
    
    # Get rowData from color response
    row_data = []
    sheets_arr = sheet_color.get('sheets', [])
    if sheets_arr:
        data_arr = sheets_arr[0].get('data', [])
        if data_arr:
            row_data = data_arr[0].get('rowData', [])
    
    print(f"\n{'='*60}")
    print(f"[{sheet_name}]")
    print(f"{'='*60}")
    
    # Find header row (row 3 in text, index 2)
    if len(text_rows) >= 3:
        header = text_rows[2]
        print(f"列头: {header}")
    
    # Gantt column indices in text_rows (0-based within each row)
    # Header shows: 分类, 功能修改, 负责人, 开发内容, T级评价, 策划案, 美需链接, 1, 2, 3...
    # Find where "1" starts
    gantt_start_idx = None
    if len(text_rows) >= 3:
        for i, h in enumerate(text_rows[2]):
            if h == '1':
                gantt_start_idx = i
                break
    
    if gantt_start_idx is None:
        # For X2前期节日循环 the header is different
        # 分类, 付费模块, 功能修改, 负责人, 交接后负责人, 活动id, 数值, 美术修改链接, 1, 2...
        for i, h in enumerate(text_rows[2] if len(text_rows) >= 3 else []):
            if h == '1':
                gantt_start_idx = i
                break
    
    n_weeks = cfg['gantt_weeks']
    print(f"甘特周数: {n_weeks}  | 甘特起始列索引: {gantt_start_idx}")
    
    # Parse gantt from color data
    # row_data corresponds to range starting at range_start_col
    # So color col_idx 0 = text col gantt_start_idx - range_start_col + (offset for value/link cols)
    
    # Actually let's just scan all rows and check colors in gantt columns
    gantt_results = []
    
    for row_idx, text_row in enumerate(text_rows):
        if row_idx < 3:  # skip title, 优化方向, header rows
            continue
        if not text_row:
            continue
        
        # Get module name
        module = ''
        for cell in text_row[:3]:
            if cell.strip():
                module = cell.strip()
                break
        if not module:
            continue
        
        # Try to get gantt from color data
        # color row_data[row_idx] corresponds to the range rows
        week_schedule = []
        if row_idx < len(row_data):
            cells = row_data[row_idx].get('values', [])
            # cells[0] = range_start_col, cells[n] = range_start_col + n
            # gantt cells start at: gantt_start_idx - range_start_col (within the range)
            if gantt_start_idx is not None:
                gantt_offset = gantt_start_idx - cfg['range_start_col']
                for w in range(n_weeks):
                    cell_idx = gantt_offset + w
                    if 0 <= cell_idx < len(cells):
                        cell = cells[cell_idx]
                        bg = cell.get('userEnteredFormat', {}).get('backgroundColor', {})
                        colored = is_colored(bg)
                        color_name = color_to_name(bg) if colored else ''
                        week_schedule.append(f'W{w+1}:{color_name if colored else "·"}')
                    else:
                        week_schedule.append(f'W{w+1}:?')
        
        # Also get dev type and T-grade
        dev_type = text_row[3] if len(text_row) > 3 else ''
        t_grade = text_row[4] if len(text_row) > 4 else ''
        
        gantt_str = ' '.join(week_schedule) if week_schedule else '(无颜色数据)'
        gantt_results.append({
            'module': module,
            'dev': dev_type,
            'grade': t_grade,
            'gantt': week_schedule
        })
        print(f"  {module:<20} [{dev_type:<6}] [{t_grade:<8}]  {gantt_str}")

print("\n解析完成")
