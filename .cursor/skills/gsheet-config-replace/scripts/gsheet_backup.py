#!/usr/bin/env python3
"""GSheet 页签备份工具：写入前调用，复制当前页签为 _backup_{日期}"""

import json, subprocess, sys, io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'


def run_gws(args, json_body=None):
    cmd = [GWS] + args
    if json_body:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        return None, r.stdout[:300]
    return json.loads(r.stdout) if r.stdout.strip() else {}, None


def backup_sheet(spreadsheet_id: str, sheet_gid: int, sheet_name: str) -> str:
    """复制页签为备份，返回备份页签名"""
    date_str = datetime.now().strftime('%m%d_%H%M')
    backup_name = f"{sheet_name}_backup_{date_str}"

    resp, err = run_gws(
        ['sheets', 'spreadsheets', 'batchUpdate',
         '--params', json.dumps({'spreadsheetId': spreadsheet_id})],
        json_body={
            "requests": [{
                "duplicateSheet": {
                    "sourceSheetId": sheet_gid,
                    "newSheetName": backup_name
                }
            }]
        }
    )

    if err:
        print(f"  backup 失败: {err}")
        return None

    print(f"  backup 已创建: {backup_name}")
    return backup_name


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python gsheet_backup.py <spreadsheet_id> <sheet_gid> <sheet_name>")
        sys.exit(1)

    sid, gid, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    result = backup_sheet(sid, gid, name)
    if result:
        print(f"OK: {result}")
    else:
        sys.exit(1)
