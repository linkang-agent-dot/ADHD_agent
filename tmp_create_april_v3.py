"""Create April 2026 Easter activity schedule - using cmd.exe approach."""
import subprocess
import json
import sys
import os

TEMPLATE_SPREADSHEET_ID = '1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8'
SHEET_NAME = '2026复活节上线checklist+甘特图（正式）'
SHEET_ID = 1308571090  # Known from metadata


def run_gws_cmd(args, params=None, json_body=None):
    """Run gws via cmd.exe with shell=True. Uses ASCII-escaped JSON to avoid encoding issues."""
    cmd = 'gws ' + ' '.join(args)
    
    if params:
        params_str = json.dumps(params, ensure_ascii=True)
        # Escape for cmd.exe: inner double quotes need to be escaped
        params_escaped = params_str.replace('"', '\\"')
        cmd += f' --params "{params_escaped}"'
    
    if json_body:
        body_str = json.dumps(json_body, ensure_ascii=True)  # Use ASCII escaping for Unicode
        body_escaped = body_str.replace('"', '\\"')
        cmd += f' --json "{body_escaped}"'
    
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    return stdout, stderr


def clear_range(spreadsheet_id, range_str):
    """Clear a range. Range string should use sheet name safely."""
    stdout, stderr = run_gws_cmd(
        ['sheets', 'spreadsheets', 'values', 'clear'],
        params={'spreadsheetId': spreadsheet_id, 'range': range_str}
    )
    return stdout, stderr


def batch_update_values(spreadsheet_id, data_entries, value_input_option='USER_ENTERED'):
    """Write multiple ranges of data."""
    body = {
        'valueInputOption': value_input_option,
        'data': data_entries
    }
    stdout, stderr = run_gws_cmd(
        ['sheets', 'spreadsheets', 'values', 'batchUpdate'],
        params={'spreadsheetId': spreadsheet_id},
        json_body=body
    )
    return stdout, stderr


# ===== April 2026 data =====
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
    ['异族大富翁-第二期-皮肤抽奖', '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['大富翁配套充值活动',          '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['每日异族大富翁礼包',          '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 赛车/行军特效
    ['赛车优化-行军特效抽奖',       '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['每日赛车礼包',               '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 节日BP
    ['节日BP',                    '', 'minghao', 'FALSE', '跨服-全服',  'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 强消耗
    ['强消耗扭蛋',                 '', 'minghao', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['强消耗对对碰-任务形式',       '', 'linkang', 'FALSE', '跨服-分组', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 装饰/大富翁
    ['大富翁-节日装饰',            '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['大富翁-团队合作子活动',       '', 'minghao', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 小游戏
    ['挖孔优化',                   '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['挖矿',                      '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['挖矿新增砍价礼包',           '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['挖孔',                      '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 活跃类带小额付费
    ['掉落转付费',                 '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['7日',                       '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['bingo',                     '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 中小R付费
    ['行军特效-付费率',             '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    ['行军表情-付费率',             '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 预购
    ['预购连锁礼包',               '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '',  '', ''],
    # 月常类
    ['订阅卡累充',                 '', 'linkang', 'FALSE', '单服',      'FALSE', '', 'FALSE', '#N/A', '1', '', ''],
    ['贬值商店',                   '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '0', '', ''],
    # 礼包付费
    ['抢购礼包',                   '', 'liusiyi', 'FALSE', '跨服-全服', 'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['挂机BP',                    '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['团购礼包',                   '', 'minghao', 'FALSE', '单服',      'FALSE', '', 'FALSE', '#N/A', '1', '', ''],
    # 活跃
    ['巨猿',                      '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    ['签到',                      '', 'liusiyi', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
    # 节日卡包
    ['节日卡包系统',               '', 'linkang', 'FALSE', '单服',      'TRUE',  '', 'FALSE', '#N/A', '1', '', ''],
]

row1  = ['分组查看这个链接', 'https://anasta0910-glitch.github.io/yych-tools/#/server-organizer?s=pniket'] + [''] * 28 + ['合服']
row2  = ['']
row3  = ['节日活动名', '活动ID-2111', '活动上线负责人', '检查', '跨服', '上线', '上线总服务器数量', '互测check', '互测负责人', '活动条数', '', '活动排期']
row4  = prefix + [str(d) for d in april_days]
row5  = prefix + april_weekdays_list
row6  = prefix + april_dates_list

activity_rows = [act + [''] * 30 for act in activities]
all_rows = [row1, row2, row3, row4, row5, row6] + activity_rows


def build_data_entries(sheet_name, rows):
    """Build batchUpdate data entries for all rows."""
    entries = []
    for i, row in enumerate(rows):
        row_num = i + 1
        range_str = f"'{sheet_name}'!A{row_num}"
        entries.append({
            'range': range_str,
            'majorDimension': 'ROWS',
            'values': [row]
        })
    return entries


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'check'
    sys.stdout.reconfigure(encoding='utf-8')
    
    if action == 'check':
        print(f'Sheet: {SHEET_NAME}')
        print(f'Total rows: {len(all_rows)}')
        print(f'Row 4 (days 1-5 + prefix): {row4[:15]}...')
        print(f'Row 5 (weekdays 1-5): {row5[12:17]}')
        print(f'Row 6 (dates 1-5): {row6[12:17]}')
        print(f'Activity count: {len(activities)}')
        # Test JSON encoding
        test = {'test': '主城特效累充bingo'}
        print(f'ASCII JSON: {json.dumps(test, ensure_ascii=True)}')
    
    elif action == 'test_clear':
        print('Testing clear...')
        # Use A1 notation that avoids Chinese in range spec (just use column range)
        range_str = f"'{SHEET_NAME}'!A1:BJ100"
        stdout, stderr = clear_range(TEMPLATE_SPREADSHEET_ID, range_str)
        print(f'Stdout: {stdout[:400]}')
        if stderr:
            print(f'Stderr: {stderr[:200]}')
    
    elif action == 'test_write':
        print('Testing write of first 2 rows...')
        test_rows = [row1, row2]
        entries = build_data_entries(SHEET_NAME, test_rows)
        stdout, stderr = batch_update_values(TEMPLATE_SPREADSHEET_ID, entries)
        print(f'Stdout: {stdout[:400]}')
        if stderr:
            print(f'Stderr: {stderr[:200]}')
    
    elif action == 'full':
        print(f'=== Step 1: Clear {SHEET_NAME} ===')
        range_str = f"'{SHEET_NAME}'!A1:BJ100"
        stdout, stderr = clear_range(TEMPLATE_SPREADSHEET_ID, range_str)
        if '"clearedRange"' in stdout:
            print(f'Cleared. Range: {json.loads(stdout, strict=False).get("clearedRange","")}')
        else:
            print(f'Clear result: {stdout[:200]}')
            if 'error' in stdout.lower():
                print('Clear failed, proceeding anyway...')
        
        print(f'\n=== Step 2: Write {len(all_rows)} rows ===')
        # Write in batches to avoid command line length limits
        batch_size = 15
        for start in range(0, len(all_rows), batch_size):
            chunk = all_rows[start:start+batch_size]
            entries = []
            for i, row in enumerate(chunk):
                row_num = start + i + 1
                range_str = f"'{SHEET_NAME}'!A{row_num}"
                entries.append({
                    'range': range_str,
                    'majorDimension': 'ROWS',
                    'values': [row]
                })
            stdout, stderr = batch_update_values(TEMPLATE_SPREADSHEET_ID, entries)
            if '"totalUpdatedRows"' in stdout:
                result = json.loads(stdout, strict=False)
                print(f'Rows {start+1}-{start+len(chunk)}: {result.get("totalUpdatedRows",0)} rows updated')
            elif 'error' in stdout.lower():
                print(f'ERROR at rows {start+1}-{start+len(chunk)}: {stdout[:200]}')
                sys.exit(1)
            else:
                print(f'Rows {start+1}-{start+len(chunk)}: {stdout[:100]}')
        
        print(f'\n=== Done! ===')
        print(f'URL: https://docs.google.com/spreadsheets/d/{TEMPLATE_SPREADSHEET_ID}/edit#gid={SHEET_ID}')
