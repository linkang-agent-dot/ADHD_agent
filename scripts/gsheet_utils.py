# -*- coding: utf-8 -*-
"""GSheet 读写统一工具 —— 固化所有已知坑的解法。GSheet 操作一律走这里，别再现写一次性脚本。

为什么需要它（每条 = 一个反复踩的坑，memory 有反馈）：
  1. 传输层用 node + gws_stdin.js（stdin 传 payload），不用 gws.cmd ——
     gws.cmd 的角括号 <> 会被 CMD 当重定向破坏 JSON（feedback_gws_angle_bracket）；
     stdin 还绕过命令行长度限制。
  2. raw stdout 本身就是 UTF-8，直接 .decode('utf-8') —— 不要试 gbk。
     中文"乱码"只发生在 print 到 Windows 控制台时，所以读结果用 dump_tabs 写文件再看
     （feedback_gws_gbk_search）。
  3. 读用 single get，不用 values.batchGet —— batchGet 的 ranges 数组里中文页签名
     会被 gws CLI 序列化破坏，报 "Unable to parse range"。
  4. 改单元格用 find_row_by_value 按内容定位，别手算行号 —— 手算易错位
     （大富翁验收 #14/#15 被改到错行的教训）。
  5. 写禁 append INSERT_ROWS（会插到表头）；找末行遍历 ID 列不用 len(values)（空行截断）；
     删行从后往前；写前先 backup_tab 备份（feedback_gsheet_write_safety）。

用法（库）：
  import sys; sys.path.insert(0, r'C:\\ADHD_agent\\scripts'); import gsheet_utils as gs
  gs.list_tabs(SID)                               # [(gid,title,rows,cols),...]
  gs.get_values(SID, '页签', 'A1:K90')             # 读 → 二维数组（空范围 []）
  gs.dump_tabs(SID, [('页签','A1:I90')], out)      # dump 多页签到 UTF-8 文件（带坐标）
  gs.find_row_by_value(SID, '页签', 'B', '某项')    # 按内容定位行号(1-indexed)，防错位
  gs.update_cell(SID, '页签', 'B17', '新值')        # 改单格
  gs.update_range(SID, '页签', 'A48:K64', rows2d)  # 写矩形
  gs.backup_tab(SID, '页签')                       # 备份 → _bak_MMDD_页签（写前必做）
  gs.delete_rows(SID, '页签', [(218,227),(2,139)]) # 删行（闭区间·自动从后往前）
  gs.ensure_grid(SID, '页签', rows=72, cols=11)    # 扩展行列（写超范围前调）

用法（命令行只读速查）：
  python gsheet_utils.py tabs <SID>
  python gsheet_utils.py dump <SID> "<页签>!A1:K90" [out.txt]
"""
import json, subprocess, os, sys, datetime

WRAPPER = r'C:\ADHD_agent\scripts\gws_stdin.js'
os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')


# ---------- 底层 ----------
def _call(args, jb=None):
    """node+gws_stdin.js，stdin 传 payload。返回 (rc, text, err)。raw stdout 是 UTF-8。"""
    payload = {"args": args}
    if jb is not None:
        payload["json"] = jb
    p = subprocess.run(['node', WRAPPER],
                       input=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                       capture_output=True, timeout=120)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def run_gws(args, jb=None):
    """成功返回解析后的 dict，失败返回 None（兼容旧调用方）。"""
    rc, text, err = _call(args, jb)
    if rc == 0 and text.strip():
        try:
            return json.loads(text)
        except Exception:
            return None
    return None


def _col_letter(i):
    s = ''; i += 1
    while i:
        i, r = divmod(i - 1, 26); s = chr(65 + r) + s
    return s


# ---------- 读 ----------
def get_values(spreadsheet_id, tab, a1):
    """读范围 → 二维数组（空范围 []）。single get，避 batchGet 数组中文 bug。"""
    resp = run_gws(['sheets', 'spreadsheets', 'values', 'get', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id, 'range': f"'{tab}'!{a1}"})])
    return (resp or {}).get('values', [])


def list_tabs(spreadsheet_id):
    """[(gid, title, rowCount, colCount), ...]。fields 限定避免响应过大被截断。"""
    resp = run_gws(['sheets', 'spreadsheets', 'get', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id,
                    'fields': 'sheets.properties(sheetId,title,gridProperties)'})])
    out = []
    for s in (resp or {}).get('sheets', []):
        p = s['properties']; g = p.get('gridProperties', {})
        out.append((p['sheetId'], p['title'], g.get('rowCount'), g.get('columnCount')))
    return out


def dump_tabs(spreadsheet_id, specs, out_path):
    """多页签 dump 成带坐标的 UTF-8 文本（避控制台乱码）。specs=[(tab,a1),...]。返回路径。"""
    lines = []
    for tab, a1 in specs:
        rows = get_values(spreadsheet_id, tab, a1)
        lines.append(f"\n{'='*70}\n■ {tab}!{a1}  ({len(rows)} 行)\n{'='*70}")
        for ri, row in enumerate(rows, 1):
            if not any(str(c).strip() for c in row):
                continue
            lines.append(" | ".join(f"{_col_letter(ci)}{ri}={str(c).strip()}"
                                    for ci, c in enumerate(row) if str(c).strip()))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    return out_path


# ---------- 定位（防行号错位）----------
def find_row_by_value(spreadsheet_id, tab, col, value, exact=True):
    """某列找内容=value 的行号(1-indexed)，找不到返回 None。改单元格前用它定位，别手算行号。"""
    vals = get_values(spreadsheet_id, tab, f"{col}:{col}")
    for i, v in enumerate(vals):
        cell = (v[0] if v else '').strip()
        if (cell == value) if exact else (value in cell):
            return i + 1
    return None


def find_last_data_row(spreadsheet_id, tab, col='B'):
    """最后一个非空行号(1-indexed)。不能用 len(values)（中间空行会截断返回）。"""
    vals = get_values(spreadsheet_id, tab, f"{col}:{col}")
    last = 0
    for i, v in enumerate(vals):
        if v and v[0].strip():
            last = i + 1
    return last


def get_sheet_gid(spreadsheet_id, tab):
    for gid, title, *_ in list_tabs(spreadsheet_id):
        if title == tab:
            return gid
    return None


# ---------- 写 ----------
def update_range(spreadsheet_id, tab, a1, rows):
    """写矩形（single range RAW，中文 OK）。rows=二维数组。返回 bool。"""
    rc, text, err = _call(['sheets', 'spreadsheets', 'values', 'update', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id, 'range': f"'{tab}'!{a1}",
                    'valueInputOption': 'RAW'})],
        jb={"values": rows, "majorDimension": "ROWS"})
    return rc == 0 and '"error"' not in text


def update_cell(spreadsheet_id, tab, a1cell, value):
    return update_range(spreadsheet_id, tab, a1cell, [[value]])


def append_rows_safe(spreadsheet_id, tab, rows, id_col='B'):
    """安全追加到表尾：找末行(遍历ID列)→insertDimension→values.update。禁 append INSERT_ROWS。"""
    if not rows:
        return 0
    gid = get_sheet_gid(spreadsheet_id, tab)
    if gid is None:
        return 0
    last_row = find_last_data_row(spreadsheet_id, tab, id_col)
    _call(['sheets', 'spreadsheets', 'batchUpdate', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id})],
        jb={"requests": [{"insertDimension": {"range": {
            "sheetId": gid, "dimension": "ROWS",
            "startIndex": last_row, "endIndex": last_row + len(rows)},
            "inheritFromBefore": True}}]})
    ok = 0
    for i, row in enumerate(rows):
        if update_range(spreadsheet_id, tab, f"A{last_row+i+1}:AZ{last_row+i+1}", [row]):
            ok += 1
    return ok


# ---------- 删行 ----------
def delete_rows(spreadsheet_id, tab, ranges_1based):
    """删多个行区间。ranges_1based=[(start,end),...] 闭区间(1-indexed)。自动从后往前删防偏移。"""
    gid = get_sheet_gid(spreadsheet_id, tab)
    if gid is None:
        return False
    reqs = [{"deleteDimension": {"range": {"sheetId": gid, "dimension": "ROWS",
             "startIndex": s - 1, "endIndex": e}}}
            for s, e in sorted(ranges_1based, reverse=True)]
    rc, text, err = _call(['sheets', 'spreadsheets', 'batchUpdate', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id})], jb={"requests": reqs})
    return rc == 0 and '"error"' not in text


# ---------- 备份 / 网格 ----------
def backup_tab(spreadsheet_id, tab, date=None):
    """duplicateSheet → _bak_{MMDD}_{tab}（写前必做，可回滚）。返回 bool。"""
    gid = get_sheet_gid(spreadsheet_id, tab)
    if gid is None:
        return False
    date = date or datetime.date.today().strftime('%m%d')
    idx = len(list_tabs(spreadsheet_id))
    rc, text, err = _call(['sheets', 'spreadsheets', 'batchUpdate', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id})],
        jb={"requests": [{"duplicateSheet": {"sourceSheetId": gid,
            "insertSheetIndex": idx, "newSheetName": f"_bak_{date}_{tab}"}}]})
    return rc == 0 and '"error"' not in text


def ensure_grid(spreadsheet_id, tab, rows=None, cols=None):
    """扩展页签行/列数（写超出当前范围前调）。返回 bool。"""
    gid = get_sheet_gid(spreadsheet_id, tab)
    if gid is None:
        return False
    gp = {}
    if rows: gp['rowCount'] = rows
    if cols: gp['columnCount'] = cols
    rc, text, err = _call(['sheets', 'spreadsheets', 'batchUpdate', '--params',
        json.dumps({'spreadsheetId': spreadsheet_id})],
        jb={"requests": [{"updateSheetProperties": {
            "properties": {"sheetId": gid, "gridProperties": gp},
            "fields": ",".join(f"gridProperties.{k}" for k in gp)}}]})
    return rc == 0 and '"error"' not in text


# ---------- 新建表 ----------
def create_spreadsheet(title, tabs=None):
    """新建 GSheet。tabs=页签名列表(可选,默认1个Sheet1)。返回 (spreadsheet_id, url)，失败 (None, None)。"""
    body = {"properties": {"title": title}}
    if tabs:
        body["sheets"] = [{"properties": {"title": t}} for t in tabs]
    rc, text, err = _call(['sheets', 'spreadsheets', 'create', '--params', '{}'], jb=body)
    if rc != 0 or not text.strip():
        return None, None
    try:
        r = json.loads(text)
    except Exception:
        return None, None
    sid = r.get("spreadsheetId")
    return sid, r.get("spreadsheetUrl", f"https://docs.google.com/spreadsheets/d/{sid}" if sid else None)


# ---------- CLI（只读速查）----------
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'tabs':
        for gid, title, r, c in list_tabs(sys.argv[2]):
            print(f"gid={gid}\t{r}x{c}\t{title}")
    elif cmd == 'dump':
        sid = sys.argv[2]
        tab, a1 = sys.argv[3].split('!', 1)
        tab = tab.strip("'")
        out = sys.argv[4] if len(sys.argv) > 4 else 'gs_dump.txt'
        print("written", dump_tabs(sid, [(tab, a1)], out))
    else:
        print("usage: gsheet_utils.py tabs <SID> | dump <SID> \"<tab>!A1:K90\" [out.txt]")
