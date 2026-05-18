#!/usr/bin/env python3
"""写入单个活动的所有子表到 GSheet，写前自动备份页签"""

import json, subprocess, sys, io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

# 表 → {sheetId, tab, gid}
TABLES = {
    '2112': {'sid': '1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo', 'tab': 'activity_config_QA', 'gid': 1922183355},
    '2135': {'sid': '1Agp8e-FfSz0ixLIVFwUIjvlkU69gB7D39URWnjzRvbs', 'tab': 'activity_event_pkg\uff08qa\uff09'},
    '2011': {'sid': '1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY', 'tab': 'iap_config_x2qa'},
    '2013': {'sid': '1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E', 'tab': 'iap_template_x2\uff08qa\uff09'},
    '2121': {'sid': '1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4', 'tab': 'activity_special'},
    '2115': {'sid': '1rXVuN_j2C_4D1e29KhbpRt0AJOy2w681MPv_gMu3TgM', 'tab': 'activity_task_master\uff0827\u88c5\u5907\u6253\u9020bingo\uff09'},
    '2116': {'sid': '1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA', 'tab': 'activity_item_exchange\uff08\u7ebf\u4e0a\u7248\u672c\uff09'},
    '2124': {'sid': '11wgGaUdAG064VvyZAKZA-M6GO6WIBf2PP88yVmDlYjU', 'tab': 'activity_drop'},
    '2137': {'sid': '1vSQa-CuzSyziwTV5ynPmB8HxE2SXNnFxQ-eKQiWlNUY', 'tab': 'activity_asset_retake'},
    '2122': {'sid': '1P5bHlZdhuRlpYkJA6tvaZuK32V5RZFRvuQuuomMjiM4', 'tab': 'activity_rank_rule\uff08QA\uff09'},
}

def run_gws(args, json_body=None):
    cmd = [GWS] + args
    if json_body:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        return None, r.stdout[:300] + r.stderr[:200]
    return json.loads(r.stdout) if r.stdout.strip() else {}, None

def backup_tab(sid, tab):
    date_str = datetime.now().strftime('%m%d_%H%M')
    backup_name = f"{tab}_bak_{date_str}"
    # 先获取 gid
    resp, err = run_gws(['sheets', 'spreadsheets', 'get',
        '--params', json.dumps({'spreadsheetId': sid, 'fields': 'sheets.properties'})])
    if err:
        return None
    gid = None
    for s in resp.get('sheets', []):
        if s.get('properties', {}).get('title') == tab:
            gid = s['properties']['sheetId']
            break
    if gid is None:
        print(f"    tab '{tab}' not found, skip backup")
        return None
    resp2, err2 = run_gws(['sheets', 'spreadsheets', 'batchUpdate',
        '--params', json.dumps({'spreadsheetId': sid})],
        json_body={"requests": [{"duplicateSheet": {"sourceSheetId": gid, "newSheetName": backup_name}}]})
    if err2:
        print(f"    backup failed: {err2[:100]}")
        return None
    return backup_name

def write_tsv(sid, tab, tsv_file):
    rows = []
    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(line.rstrip('\n').split('\t'))
    if not rows:
        return 0
    success = 0
    for i in range(0, len(rows), 5):
        batch = rows[i:i+5]
        resp, err = run_gws(
            ['sheets', 'spreadsheets', 'values', 'append',
             '--params', json.dumps({
                 'spreadsheetId': sid,
                 'range': f"'{tab}'!A:AZ",
                 'valueInputOption': 'RAW',
                 'insertDataOption': 'INSERT_ROWS'
             })],
            json_body={"values": batch})
        if err:
            print(f"    write failed: {err[:100]}")
        else:
            success += len(batch)
    return success

def main():
    if len(sys.argv) < 2:
        print("用法: python write_activity.py <activity_id>")
        sys.exit(1)

    act_id = sys.argv[1]
    out_dir = Path(__file__).parent / f'output_{act_id}'
    if not out_dir.exists():
        print(f"output dir not found: {out_dir}")
        sys.exit(1)

    # 找所有 TSV 文件
    tsv_files = sorted(out_dir.glob('*.tsv'))
    print(f"=== 写入活动 {act_id} ===")

    # 检查哪些表已有备份（同一个 tab 只备份一次，跨活动复用）
    total = 0

    for tsv_file in tsv_files:
        table_id = tsv_file.stem
        if table_id not in TABLES:
            print(f"  {table_id}: 未知表，跳过")
            continue

        info = TABLES[table_id]
        sid = info['sid']
        tab = info['tab']
        n_rows = sum(1 for line in open(tsv_file, encoding='utf-8') if line.strip())

        # 检查是否已有 _bak_ 页签，有则跳过备份
        resp, _ = run_gws(['sheets', 'spreadsheets', 'get',
            '--params', json.dumps({'spreadsheetId': sid, 'fields': 'sheets.properties'})])
        has_backup = False
        if resp:
            for s in resp.get('sheets', []):
                t = s.get('properties', {}).get('title', '')
                if t.startswith(tab + '_bak_'):
                    has_backup = True
                    break
        if not has_backup:
            bak = backup_tab(sid, tab)
            if bak:
                print(f"  {table_id}: backup -> {bak}")

        # 写入
        written = write_tsv(sid, tab, tsv_file)
        total += written
        print(f"  {table_id}: {written}/{n_rows} 行写入 '{tab}'")

    print(f"\n=== 完成: {total} 行 ===")

if __name__ == '__main__':
    main()
