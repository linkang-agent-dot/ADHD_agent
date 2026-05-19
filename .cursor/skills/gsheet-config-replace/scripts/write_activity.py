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
    '2115': {'sid': '1rXVuN_j2C_4D1e29KhbpRt0AJOy2w681MPv_gMu3TgM', 'tab': 'activity_task_master\uff08\u7ebf\u4e0a\uff09'},
    '2116': {'sid': '1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA', 'tab': 'activity_item_exchange\uff08\u7ebf\u4e0a\u7248\u672c\uff09'},
    '2124': {'sid': '11wgGaUdAG064VvyZAKZA-M6GO6WIBf2PP88yVmDlYjU', 'tab': 'activity_drop'},
    '2137': {'sid': '1vSQa-CuzSyziwTV5ynPmB8HxE2SXNnFxQ-eKQiWlNUY', 'tab': 'activity_asset_retake'},
    '2122': {'sid': '1P5bHlZdhuRlpYkJA6tvaZuK32V5RZFRvuQuuomMjiM4', 'tab': 'activity_rank_rule\uff08QA\uff09'},
    # B8: 补全所有涉及的表
    '2118': {'sid': '1bAwu8A-N4j0Wub6wQQ2AImeB958gSaWV-XdU87k8u60', 'tab': 'activity_rank_rewards'},
    '2130': {'sid': '1XfpgS-r7kTDk24t5mEE93uOy9u6wm_fub0txKMRDTwU', 'tab': 'activity_battle_pass\uff0824\u65b0\u683c\u5f0f-dev\uff09'},
    '2131': {'sid': '1CFoDVfINRdcjpuGpKbNz9f3WyFxIHW5dbayQDJy5evA', 'tab': 'ActivityBattlePassLevel\uff08master\uff09'},
    '2151': {'sid': '1X9fu7V3JFd1ZKoisbLjDpR8SAfngKso6lWjZ0-eTudg', 'tab': 'activity_monopoly_gacha_map_QA'},
    '1365': {'sid': '1euWfOkXNsn4sQwyRNaoCZ6-0_EGed9aToBUbDCOzi8w', 'tab': 'march_effect'},
    '1187': {'sid': '1lXRldN7kN_HsEYQ5FfNdawep23TD9J81Vj66yKRdjEk', 'tab': 'FurnitureBuild'},
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
    backup_name = f"_bak_{date_str}_{tab}"
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

def get_existing_ids(sid, tab, id_col=1):
    """读表中已有的 ID 集合（B1: 写前去重）"""
    col_letter = chr(ord('A') + id_col)
    resp, _ = run_gws(['sheets', 'spreadsheets', 'values', 'get',
        '--params', json.dumps({'spreadsheetId': sid, 'range': f"'{tab}'!{col_letter}:{col_letter}"})])
    return set(v[0].strip() for v in (resp or {}).get('values', []) if v and v[0].strip())


def get_id_col(table_id):
    """获取表的 ID 列位置"""
    id_cols = {'2115': 2, '2116': 2, '2122': 2, '2118': 3}
    return id_cols.get(table_id, 1)


def write_tsv(sid, tab, tsv_file, table_id=None):
    rows = []
    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(line.rstrip('\n').split('\t'))
    if not rows:
        return 0

    # B1: 写前去重 — 跳过 GSheet 中已有的行
    id_col = get_id_col(table_id) if table_id else 1
    existing = get_existing_ids(sid, tab, id_col)
    new_rows = []
    for row in rows:
        rid = row[id_col].strip() if len(row) > id_col else ''
        if rid and rid in existing:
            print(f"    跳过已存在: {rid}")
        else:
            new_rows.append(row)
    if not new_rows:
        print(f"    全部已存在，跳过写入")
        return 0
    rows = new_rows

    # B4: 校验列数 — 读表头确认列数，不足前补空列
    resp_h, _ = run_gws(['sheets', 'spreadsheets', 'values', 'get',
        '--params', json.dumps({'spreadsheetId': sid, 'range': f"'{tab}'!1:1"})])
    header_cols = len((resp_h or {}).get('values', [[]])[0])
    for i, row in enumerate(rows):
        if len(row) < header_cols:
            rows[i] = row + [''] * (header_cols - len(row))

    # 获取 gid
    resp_meta, _ = run_gws(['sheets', 'spreadsheets', 'get',
        '--params', json.dumps({'spreadsheetId': sid, 'fields': 'sheets.properties'})])
    sheet_gid = None
    for s in (resp_meta or {}).get('sheets', []):
        if s.get('properties', {}).get('title') == tab:
            sheet_gid = s['properties']['sheetId']
    if sheet_gid is None:
        print(f"    tab '{tab}' not found")
        return 0

    # 读 B 列找最后数据行
    resp_b, _ = run_gws(['sheets', 'spreadsheets', 'values', 'get',
        '--params', json.dumps({'spreadsheetId': sid, 'range': f"'{tab}'!B:B"})])
    all_b = (resp_b or {}).get('values', [])
    last_row = max((i+1 for i, b in enumerate(all_b) if b and b[0].strip()), default=0)

    # insertDimension 在表尾
    insert_at = last_row
    run_gws(['sheets', 'spreadsheets', 'batchUpdate',
        '--params', json.dumps({'spreadsheetId': sid})],
        json_body={"requests": [{"insertDimension": {"range": {
            "sheetId": sheet_gid, "dimension": "ROWS",
            "startIndex": insert_at, "endIndex": insert_at + len(rows)},
            "inheritFromBefore": True}}]})

    # values.update 分批写入
    success = 0
    start = insert_at + 1
    for i in range(0, len(rows), 5):
        batch = rows[i:i+5]
        safe_batch = [[c.replace('&', '+') for c in row] for row in batch]
        rng = f"'{tab}'!A{start+i}:AZ{start+i+len(batch)-1}"
        resp, err = run_gws(
            ['sheets', 'spreadsheets', 'values', 'batchUpdate',
             '--params', json.dumps({'spreadsheetId': sid, 'valueInputOption': 'RAW'})],
            json_body={"data": [{"range": rng, "values": safe_batch}]})
        if err:
            for j, row in enumerate(safe_batch):
                row_rng = f"'{tab}'!A{start+i+j}:AZ{start+i+j}"
                r2, e2 = run_gws(
                    ['sheets', 'spreadsheets', 'values', 'update',
                     '--params', json.dumps({'spreadsheetId': sid, 'range': row_rng, 'valueInputOption': 'RAW'})],
                    json_body={"values": [row]})
                if not e2:
                    success += 1
                else:
                    print(f"    row {start+i+j} failed")
        else:
            success += len(batch)
    return success

def main():
    if len(sys.argv) < 2:
        print("用法: python write_activity.py <activity_id> [--verify]")
        sys.exit(1)

    act_id = sys.argv[1]
    verify_only = '--verify' in sys.argv
    out_dir = Path(__file__).parent / f'output_{act_id}'
    if not out_dir.exists():
        print(f"output dir not found: {out_dir}")
        sys.exit(1)

    # B7: 检测上次是否崩溃（写入状态文件）
    state_file = out_dir / '_write_state.json'
    if state_file.exists() and not verify_only:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        if state.get('status') == 'in_progress':
            print(f"⚠️ 上次写入未完成（{state.get('last_table','?')}），进入验证模式")
            print(f"   先用 --verify 检查 GSheet 实际状态，确认后删除 {state_file} 再重跑")
            verify_only = True

    # 找所有 TSV 文件
    tsv_files = sorted(out_dir.glob('*.tsv'))
    print(f"=== {'验证' if verify_only else '写入'}活动 {act_id} ===")

    # B3: 备份前置 — 先备份所有涉及的表，再写入任何数据
    tables_to_write = []
    for tsv_file in tsv_files:
        table_id = tsv_file.stem
        if table_id not in TABLES:
            print(f"  {table_id}: 未知表，跳过")
            continue
        tables_to_write.append((table_id, tsv_file))

    # Phase 1: 全部备份
    for table_id, _ in tables_to_write:
        info = TABLES[table_id]
        sid = info['sid']
        tab = info['tab']
        resp, _ = run_gws(['sheets', 'spreadsheets', 'get',
            '--params', json.dumps({'spreadsheetId': sid, 'fields': 'sheets.properties'})])
        has_backup = False
        if resp:
            for s in resp.get('sheets', []):
                t = s.get('properties', {}).get('title', '')
                if t.startswith('_bak_') and tab in t:
                    has_backup = True
                    break
        if not has_backup:
            bak = backup_tab(sid, tab)
            if bak:
                print(f"  {table_id}: backup -> {bak}")

    # Phase 2: 逐表写入（备份已全部完成）
    total = 0
    for table_id, tsv_file in tables_to_write:
        info = TABLES[table_id]
        sid = info['sid']
        tab = info['tab']
        n_rows = sum(1 for line in open(tsv_file, encoding='utf-8') if line.strip())

        if verify_only:
            # B7: 验证模式 — 只检查已写入行数，不写入
            id_col = get_id_col(table_id)
            existing = get_existing_ids(sid, tab, id_col)
            rows = []
            with open(tsv_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        cells = line.strip().split('\t')
                        rid = cells[id_col].strip() if len(cells) > id_col else ''
                        if rid and rid in existing:
                            rows.append(rid)
            print(f"  {table_id}: {len(rows)}/{n_rows} 行已在 GSheet 中")
            total += len(rows)
            continue

        # 记录写入状态
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({'status': 'in_progress', 'last_table': table_id}, f)

        written = write_tsv(sid, tab, tsv_file, table_id=table_id)
        total += written
        print(f"  {table_id}: {written}/{n_rows} 行写入 '{tab}'")

    # B7: 写入完成，标记 done
    if not verify_only and state_file.exists():
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({'status': 'done', 'total': total}, f)

    print(f"\n=== {'验证' if verify_only else '写入'}完成: {total} 行 ===")

if __name__ == '__main__':
    main()
