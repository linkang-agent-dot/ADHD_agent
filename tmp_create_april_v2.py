"""Create April 2026 Easter activity schedule - using PowerShell file approach for Unicode."""
import subprocess
import json
import sys
import tempfile
import os

TEMPLATE_SPREADSHEET_ID = '1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8'
SHEET_NAME = '2026复活节上线checklist+甘特图（正式）'
SHEET_ID = 1308571090  # Known from earlier metadata read

GWS_PS1 = r'C:\Users\linkang\AppData\Roaming\npm\gws.ps1'

def run_ps1_script(ps1_content):
    """Run a PowerShell script and return (stdout_bytes, stderr_bytes)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, 
                                      encoding='utf-8', newline='') as f:
        f.write(ps1_content)
        ps1_file = f.name
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-File', ps1_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout, result.stderr
    finally:
        os.unlink(ps1_file)

def clear_range(sheet_name, range_addr):
    """Clear a range using PowerShell + gws."""
    range_spec = f"'{sheet_name}'!{range_addr}"
    params_json = json.dumps({
        'spreadsheetId': TEMPLATE_SPREADSHEET_ID,
        'range': range_spec
    }, ensure_ascii=False)
    
    ps1 = f'''
$params = @"
{params_json}
"@
& "{GWS_PS1}" sheets spreadsheets values clear --params $params
'''
    stdout, stderr = run_ps1_script(ps1)
    return stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')

def write_values_batch(sheet_name, row_data_list):
    """Write all rows using batchUpdate for efficiency."""
    # Prepare the ranges and values
    data_entries = []
    for start_row, rows in row_data_list:
        for i, row in enumerate(rows):
            range_spec = f"'{sheet_name}'!A{start_row + i}"
            data_entries.append({
                'range': range_spec,
                'majorDimension': 'ROWS',
                'values': [row]
            })
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data_entries
    }
    
    # Write body to temp file
    body_file = tempfile.mktemp(suffix='.json')
    with open(body_file, 'w', encoding='utf-8') as f:
        json.dump(body, f, ensure_ascii=False)
    
    params_json = json.dumps({
        'spreadsheetId': TEMPLATE_SPREADSHEET_ID
    }, ensure_ascii=False)
    
    ps1 = f'''
$params = @"
{params_json}
"@
$body = Get-Content -Raw -Encoding UTF8 "{body_file}"
& "{GWS_PS1}" sheets spreadsheets values batchUpdate --params $params --json $body
'''
    
    stdout, stderr = run_ps1_script(ps1)
    os.unlink(body_file)
    
    return stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')

def write_values_single(sheet_name, start_row, rows):
    """Write rows to sheet starting at start_row using values batchUpdate."""
    data_entries = []
    range_spec = f"'{sheet_name}'!A{start_row}"
    data_entries.append({
        'range': range_spec,
        'majorDimension': 'ROWS',
        'values': rows
    })
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data_entries
    }
    
    body_file = tempfile.mktemp(suffix='.json')
    with open(body_file, 'w', encoding='utf-8') as f:
        json.dump(body, f, ensure_ascii=False)
    
    params_json = json.dumps({
        'spreadsheetId': TEMPLATE_SPREADSHEET_ID
    }, ensure_ascii=False)
    
    ps1 = f'''
$params = @"
{params_json}
"@
$body = Get-Content -Raw -Encoding UTF8 "{body_file}"
& "{GWS_PS1}" sheets spreadsheets values batchUpdate --params $params --json $body
'''
    
    stdout, stderr = run_ps1_script(ps1)
    
    try:
        os.unlink(body_file)
    except:
        pass
    
    return stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')


# ===== Build April 2026 schedule data =====

def get_weekday(day_in_april):
    """April 1, 2026 = Wednesday."""
    names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    idx = (day_in_april - 1 + 2) % 7
    return names[idx]

april_days = list(range(1, 31))
april_weekdays_list = [get_weekday(d) for d in april_days]
april_dates_list = [f'4-{d}' for d in april_days]

HEADER_COLS = 12
prefix = [''] * HEADER_COLS

activities = [
    # 累充类
    ['主城特效累充bingo',         '', 'liusiyi', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '2', '', ''],
    ['主城特效累充-联盟版',        '', 'liusiyi', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['主城特效累充-服务器版',       '', 'liusiyi', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 大富翁皮肤抽奖
    ['异族大富翁-第二期-皮肤抽奖', '', 'minghao', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['大富翁配套充值活动',          '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['每日异族大富翁礼包',          '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 赛车/行军特效
    ['赛车优化-行军特效抽奖',       '', 'minghao', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['每日赛车礼包',               '', 'minghao', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 节日BP
    ['节日BP',                    '', 'minghao', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 强消耗
    ['强消耗扭蛋',                 '', 'minghao', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['强消耗对对碰-任务形式',       '', 'linkang', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 装饰/大富翁
    ['大富翁-节日装饰',            '', 'minghao', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['大富翁-团队合作子活动',       '', 'minghao', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 小游戏
    ['挖孔优化',                   '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['挖矿',                      '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['挖矿新增砍价礼包',           '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['挖孔',                      '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 活跃类带小额付费
    ['掉落转付费',                 '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['7日',                       '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['bingo',                     '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 中小R付费
    ['行军特效-付费率',             '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['行军表情-付费率',             '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 预购
    ['预购连锁礼包',               '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 月常类
    ['订阅卡累充',                 '', 'linkang', 'FALSE', '单服',     'FALSE', '', 'FALSE', '#N/A', '1', '', ''],
    ['贬值商店',                   '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '0', '', ''],
    # 礼包付费
    ['抢购礼包',                   '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['挂机BP',                    '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['团购礼包',                   '', 'minghao', 'FALSE', '单服',     'FALSE', '', 'FALSE', '#N/A', '1', '', ''],
    # 活跃
    ['巨猿',                      '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['签到',                      '', 'liusiyi', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 节日卡包
    ['节日卡包系统',               '', 'linkang', 'FALSE', '单服',     'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
]

row1  = ['分组查看这个链接', 'https://anasta0910-glitch.github.io/yych-tools/#/server-organizer?s=pniket'] + [''] * 28 + ['合服']
row2  = ['']
row3  = ['节日活动名', '活动ID-2111', '活动上线负责人', '检查', '跨服', '上线', '上线总服务器数量', '互测check', '互测负责人', '活动条数', '', '活动排期']
row4  = prefix + [str(d) for d in april_days]
row5  = prefix + april_weekdays_list
row6  = prefix + april_dates_list

activity_rows = [act + [''] * 30 for act in activities]

all_rows = [row1, row2, row3, row4, row5, row6] + activity_rows


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'check'
    sys.stdout.reconfigure(encoding='utf-8')
    
    if action == 'check':
        print(f'Sheet: {SHEET_NAME}')
        print(f'Total rows: {len(all_rows)}')
        print(f'Row 5 sample: {row5[10:15]}')
        print(f'Row 6 sample: {row6[10:15]}')
        print(f'Activity count: {len(activities)}')
    
    elif action == 'test_clear':
        print('Testing clear...')
        stdout, stderr = clear_range(SHEET_NAME, 'A1:BJ100')
        print(f'Stdout: {stdout[:300]}')
        if stderr:
            print(f'Stderr: {stderr[:200]}')
    
    elif action == 'clear':
        print(f'Clearing {SHEET_NAME}...')
        stdout, stderr = clear_range(SHEET_NAME, 'A1:BJ100')
        if 'error' in stdout.lower():
            print(f'Clear error: {stdout[:300]}')
            sys.exit(1)
        print('Cleared.')
    
    elif action == 'write':
        print(f'Writing {len(all_rows)} rows to {SHEET_NAME}...')
        chunk_size = 8
        for start in range(0, len(all_rows), chunk_size):
            chunk = all_rows[start:start+chunk_size]
            stdout, stderr = write_values_single(SHEET_NAME, start+1, chunk)
            if 'error' in stdout.lower():
                print(f'Error at row {start+1}: {stdout[:300]}')
                sys.exit(1)
            print(f'Rows {start+1}-{start+len(chunk)} OK')
        print('All rows written!')
    
    elif action == 'full':
        print(f'=== Clearing {SHEET_NAME} ===')
        stdout, stderr = clear_range(SHEET_NAME, 'A1:BJ100')
        if 'error' in stdout.lower() and 'clearedRange' not in stdout:
            print(f'Clear error: {stdout[:300]}')
            sys.exit(1)
        print(f'Clear result: {stdout[:100]}')
        
        print(f'\n=== Writing {len(all_rows)} rows ===')
        chunk_size = 8
        for start in range(0, len(all_rows), chunk_size):
            chunk = all_rows[start:start+chunk_size]
            stdout, stderr = write_values_single(SHEET_NAME, start+1, chunk)
            if 'error' in stdout.lower() and 'updatedRange' not in stdout:
                print(f'Error at row {start+1}: {stdout[:300]}')
                sys.exit(1)
            print(f'Rows {start+1}-{start+len(chunk)} OK')
        
        print(f'\n=== Done! ===')
        print(f'URL: https://docs.google.com/spreadsheets/d/{TEMPLATE_SPREADSHEET_ID}/edit#gid={SHEET_ID}')
