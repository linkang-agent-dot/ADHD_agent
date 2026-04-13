"""Create April 2026 Easter activity schedule sheet in the template spreadsheet.
Updates the existing 2026复活节 sheet with correct April data.
"""
import subprocess
import json
import sys

TEMPLATE_SPREADSHEET_ID = '1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8'
# Update existing 复活节 sheet
SHEET_NAME = '2026复活节上线checklist+甘特图（正式）'

def run_gws(cmd_str, json_body=None, params=None):
    """Run gws command and return parsed result."""
    cmd = 'gws ' + cmd_str
    if params:
        cmd += ' --params ' + json.dumps(json.dumps(params))
    if json_body:
        cmd += ' --json ' + json.dumps(json.dumps(json_body, ensure_ascii=False))
    
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    
    if not stdout.strip():
        return None, f'No output. Stderr: {stderr[:300]}'
    
    try:
        return json.loads(stdout, strict=False), None
    except Exception as e:
        return None, f'Parse error: {e}\nStdout: {stdout[:300]}'


def run_gws_v2(cmd_parts, json_body=None, params=None):
    """Run gws command using temp files for JSON to avoid quoting issues."""
    import tempfile, os
    
    full_cmd = ['gws'] + cmd_parts
    
    if params:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(params, f)
            params_file = f.name
        # Read back to verify
        # Use @file syntax or pass directly
        # Actually, let's write to a temp file and read with @ prefix
    
    # Build command string for PowerShell
    cmd_str = ' '.join(full_cmd)
    
    if params:
        params_json = json.dumps(params)
        cmd_str += f' --params {json.dumps(params_json)}'
    
    if json_body:
        body_json = json.dumps(json_body, ensure_ascii=False)
        cmd_str += f' --json {json.dumps(body_json)}'
    
    result = subprocess.run(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    
    if stdout.strip():
        try:
            return json.loads(stdout, strict=False), None
        except Exception as e:
            return None, f'Parse error: {e}\nStdout: {stdout[:500]}'
    return None, f'No output. Stderr: {stderr[:300]}'


GWS_PS1 = r'C:\Users\linkang\AppData\Roaming\npm\gws.ps1'

def run_gws_with_file(cmd_parts, json_body=None, params_dict=None):
    """Run gws command using PowerShell to handle Unicode correctly."""
    import tempfile, os
    
    # Build the gws command arguments
    gws_args = cmd_parts[:]
    
    if params_dict:
        params_json = json.dumps(params_dict, ensure_ascii=False)
        gws_args += ['--params', params_json]
    
    body_file = None
    if json_body:
        # Write body to a temp file to avoid command line length/encoding issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, 
                                          encoding='utf-8', newline='') as f:
            json.dump(json_body, f, ensure_ascii=False)
            body_file = f.name
        gws_args += ['--json', f'$(Get-Content -Raw -Encoding UTF8 "{body_file}")']
    
    # Build PowerShell command
    ps_cmd_parts = [f'& "{GWS_PS1}"'] + [f'"{a}"' if ' ' in str(a) or '"' in str(a) else str(a) for a in gws_args]
    ps_cmd = ' '.join(ps_cmd_parts)
    
    full_cmd = f'powershell.exe -NoProfile -Command "{ps_cmd.replace(chr(34), chr(92)+chr(34))}"'
    
    # Use a simpler approach: write a PS1 script and run it
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, 
                                      encoding='utf-8', newline='') as f:
        if body_file:
            f.write(f'$body = Get-Content -Raw -Encoding UTF8 "{body_file}"\n')
            args_str = ' '.join([f'"{a}"' if ' ' in str(a) else str(a) for a in gws_args[:-1]])
            f.write(f'& "{GWS_PS1}" {args_str} --json $body\n')
        else:
            args_str = ' '.join([f'"{a}"' if ' ' in str(a) else str(a) for a in gws_args])
            f.write(f'& "{GWS_PS1}" {args_str}\n')
        ps1_file = f.name
    
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-File', ps1_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
    finally:
        os.unlink(ps1_file)
        if body_file:
            os.unlink(body_file)
    
    if stdout.strip():
        try:
            return json.loads(stdout, strict=False), None
        except Exception as e:
            return None, f'Parse error: {e}\nStdout: {stdout[:500]}\nStderr: {stderr[:300]}'
    return None, f'No output. RetCode: {result.returncode}\nStderr: {stderr[:300]}'


# ===== April 2026 date structure =====
# April 1, 2026 = Wednesday

def get_weekday(day_in_april):
    """Get Chinese weekday for given day of April 2026."""
    # April 1 = Wednesday = 2 (Mon=0, Tue=1, Wed=2, ...)
    names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    idx = (day_in_april - 1 + 2) % 7
    return names[idx]

april_days = list(range(1, 31))
april_weekdays_list = [get_weekday(d) for d in april_days]
april_dates_list = [f'4-{d}' for d in april_days]

# 12 empty prefix columns (A-L)
HEADER_COLS = 12
prefix = [''] * HEADER_COLS

# ===== Activities =====
# [name, id, person, check, cross_server, upload, server_cnt, test_check, tester, count_col, blank, schedule_label]
activities = [
    # 累充类
    ['主城特效累充bingo',        '', 'liusiyi', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '2', '', ''],
    ['主城特效累充-联盟版',       '', 'liusiyi', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['主城特效累充-服务器版',      '', 'liusiyi', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 大富翁皮肤抽奖
    ['异族大富翁-第二期-皮肤抽奖', '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['大富翁配套充值活动',         '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['每日异族大富翁礼包',         '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 赛车/行军特效抽奖
    ['赛车优化-行军特效抽奖',      '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['每日赛车礼包',              '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 节日BP
    ['节日BP',                   '', 'minghao', 'FALSE', '跨服-全服',  'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 强消耗
    ['强消耗扭蛋',                '', 'minghao', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['强消耗对对碰-任务形式',      '', 'linkang', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 装饰/大富翁
    ['大富翁-节日装饰',           '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['大富翁-团队合作子活动',      '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 小游戏
    ['挖孔优化',                  '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['挖矿',                     '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['挖矿新增砍价礼包',          '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['挖孔',                     '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 活跃类带小额付费
    ['掉落转付费',                '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['7日',                      '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['bingo',                    '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 中小R付费
    ['行军特效-付费率',            '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['行军表情-付费率',            '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 预购
    ['预购连锁礼包',              '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 月常类
    ['订阅卡累充',                '', 'linkang', 'FALSE', '单服',      'FALSE', '', 'FALSE', '#N/A', '1', '', ''],
    ['贬值商店',                  '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '0', '', ''],
    # 礼包付费
    ['抢购礼包',                  '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['挂机BP',                   '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['团购礼包',                  '', 'minghao', 'FALSE', '单服',      'FALSE', '', 'FALSE', '#N/A', '1', '', ''],
    # 活跃
    ['巨猿',                     '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['签到',                     '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 节日卡包
    ['节日卡包系统',              '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
]

# ===== Build rows =====
row1 = ['分组查看这个链接', 'https://anasta0910-glitch.github.io/yych-tools/#/server-organizer?s=pniket'] + [''] * 28 + ['合服']
row2 = ['']
row3 = ['节日活动名', '活动ID-2111', '活动上线负责人', '检查', '跨服', '上线', '上线总服务器数量', '互测check', '互测负责人', '活动条数', '', '活动排期'] + [str(d) for d in april_days]
row4 = prefix + [str(d) for d in april_days]
row5 = prefix + april_weekdays_list
row6 = prefix + april_dates_list

# Merge header + schedule days
row3 = ['节日活动名', '活动ID-2111', '活动上线负责人', '检查', '跨服', '上线', '上线总服务器数量', '互测check', '互测负责人', '活动条数', '', '活动排期']
row4_full = prefix + [str(d) for d in april_days]
row5_full = prefix + april_weekdays_list
row6_full = prefix + april_dates_list

activity_rows = []
for act in activities:
    row = act + [''] * 30  # 30 empty schedule day cells
    activity_rows.append(row)

all_rows = [
    row1,   # Row 1: Title/link
    row2,   # Row 2: Empty
    row3,   # Row 3: Column headers (A-L only)
    row4_full,  # Row 4: Day numbers (1-30)
    row5_full,  # Row 5: Weekdays
    row6_full,  # Row 6: Month-day (4-1 to 4-30)
] + activity_rows


def get_sheet_id(spreadsheet_id, sheet_name):
    data, err = run_gws_with_file(
        ['sheets', 'spreadsheets', 'get'],
        params_dict={'spreadsheetId': spreadsheet_id}
    )
    if err:
        return None, err
    sheets = data.get('sheets', [])
    for s in sheets:
        if s.get('properties', {}).get('title') == sheet_name:
            return s['properties']['sheetId'], None
    return None, f'Sheet not found: {sheet_name}'


def clear_range(spreadsheet_id, range_name):
    """Clear a range."""
    data, err = run_gws_with_file(
        ['sheets', 'spreadsheets', 'values', 'clear'],
        params_dict={
            'spreadsheetId': spreadsheet_id,
            'range': range_name
        }
    )
    return data, err


def write_values(spreadsheet_id, range_name, values):
    """Write values to a range."""
    body = {
        'range': range_name,
        'majorDimension': 'ROWS',
        'values': values
    }
    data, err = run_gws_with_file(
        ['sheets', 'spreadsheets', 'values', 'update'],
        json_body=body,
        params_dict={
            'spreadsheetId': spreadsheet_id,
            'range': range_name,
            'valueInputOption': 'USER_ENTERED'
        }
    )
    return data, err


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'check'
    
    sys.stdout.reconfigure(encoding='utf-8')
    
    if action == 'check':
        print(f'Sheet to update: {SHEET_NAME}')
        print(f'Total rows to write: {len(all_rows)}')
        print(f'Row 3 (header): {row3}')
        print(f'Row 4 (days 1-5): {row4_full[12:17]}')
        print(f'Row 5 (weekdays 1-5): {row5_full[12:17]}')
        print(f'Row 6 (dates 1-5): {row6_full[12:17]}')
        print(f'First activity: {activity_rows[0][:12]}')
        print(f'Total activities: {len(activities)}')
    
    elif action == 'get_sheet_id':
        sid, err = get_sheet_id(TEMPLATE_SPREADSHEET_ID, SHEET_NAME)
        if err:
            print(f'Error: {err}')
        else:
            print(f'Sheet ID: {sid}')
    
    elif action == 'clear':
        range_name = f"'{SHEET_NAME}'!A1:BJ100"
        print(f'Clearing range {range_name}...')
        data, err = clear_range(TEMPLATE_SPREADSHEET_ID, range_name)
        if err:
            print(f'Clear error: {err}')
        else:
            print('Cleared.')
    
    elif action == 'write':
        chunk_size = 10
        for start in range(0, len(all_rows), chunk_size):
            chunk = all_rows[start:start+chunk_size]
            chunk_range = f"'{SHEET_NAME}'!A{start+1}"
            data, err = write_values(TEMPLATE_SPREADSHEET_ID, chunk_range, chunk)
            if err:
                print(f'Write error at row {start+1}: {err}')
                sys.exit(1)
            print(f'Written rows {start+1}-{start+len(chunk)}')
        print('Done writing!')
    
    elif action == 'full':
        print('=== Step 1: Clear existing data ===')
        range_name = f"'{SHEET_NAME}'!A1:BJ100"
        data, err = clear_range(TEMPLATE_SPREADSHEET_ID, range_name)
        if err:
            print(f'Clear error: {err}')
            sys.exit(1)
        print('Cleared.')
        
        print('\n=== Step 2: Write new data ===')
        chunk_size = 10
        for start in range(0, len(all_rows), chunk_size):
            chunk = all_rows[start:start+chunk_size]
            chunk_range = f"'{SHEET_NAME}'!A{start+1}"
            data, err = write_values(TEMPLATE_SPREADSHEET_ID, chunk_range, chunk)
            if err:
                print(f'Write error at row {start+1}: {err}')
                sys.exit(1)
            print(f'Written rows {start+1}-{start+len(chunk)}')
        
        print('\n=== Done! ===')
        print(f'Sheet URL: https://docs.google.com/spreadsheets/d/{TEMPLATE_SPREADSHEET_ID}/edit#gid=1308571090')
