"""GSheet 写入通用工具函数"""
import json, subprocess

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'


def run_gws(args, jb=None):
    cmd = [GWS] + args
    if jb:
        cmd.extend(['--json', json.dumps(jb, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def find_last_data_row(spreadsheet_id, tab, col='B'):
    """找最后一个有数据的行号（1-indexed）。

    不能用 len(values)！API 可能在空行处截断返回。
    必须遍历 ID 列找最后一个非空值的位置。
    """
    resp = run_gws(['sheets', 'spreadsheets', 'values', 'get',
        '--params', json.dumps({
            'spreadsheetId': spreadsheet_id,
            'range': f"'{tab}'!{col}:{col}"
        })])
    all_vals = (resp or {}).get('values', [])
    last = 0
    for i, v in enumerate(all_vals):
        if v and v[0].strip():
            last = i + 1  # 1-indexed
    return last


def get_sheet_gid(spreadsheet_id, tab):
    """获取页签的 sheetId (gid)"""
    resp = run_gws(['sheets', 'spreadsheets', 'get',
        '--params', json.dumps({'spreadsheetId': spreadsheet_id, 'fields': 'sheets.properties'})])
    for s in (resp or {}).get('sheets', []):
        if s.get('properties', {}).get('title') == tab:
            return s['properties']['sheetId']
    return None


def append_rows_safe(spreadsheet_id, tab, rows, id_col='B'):
    """安全追加行到表尾。

    1. 找最后数据行（不用 len）
    2. insertDimension 在数据行后面
    3. values.update 写入
    """
    if not rows:
        return 0

    gid = get_sheet_gid(spreadsheet_id, tab)
    if gid is None:
        print(f"  tab '{tab}' not found")
        return 0

    last_row = find_last_data_row(spreadsheet_id, tab, id_col)

    # insertDimension
    run_gws(['sheets', 'spreadsheets', 'batchUpdate',
        '--params', json.dumps({'spreadsheetId': spreadsheet_id})],
        jb={"requests": [{"insertDimension": {"range": {
            "sheetId": gid, "dimension": "ROWS",
            "startIndex": last_row, "endIndex": last_row + len(rows)},
            "inheritFromBefore": True}}]})

    # values.update 逐行
    ok = 0
    for i, row in enumerate(rows):
        safe_row = [c.replace('&', '+') for c in row]
        rng = f"'{tab}'!A{last_row + i + 1}:AZ{last_row + i + 1}"
        resp = run_gws(['sheets', 'spreadsheets', 'values', 'update',
            '--params', json.dumps({
                'spreadsheetId': spreadsheet_id,
                'range': rng,
                'valueInputOption': 'RAW'
            })],
            jb={"values": [safe_row]})
        if resp is not None:
            ok += 1
    return ok
