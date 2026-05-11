# -*- coding: utf-8 -*-
"""
补写 goldegg vs dev_26festival 差异 GSheet 的剩余页签。
GSheet ID: 1FsA4HCVjIXbRff5SgumWqeiGKDzVWbi35fOu9Jwu5V4
已完成: activity_asset_retake, activity_config, activity_drop, activity_package, activity_special
待写入:
  - activity_task       → 超大表(10118行), 仅写摘要
  - activity_ui_template
  - get_access_group
  - iap_config
  - iap_template
  - item
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Reuse functions from create_diff_sheet.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cds", os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_diff_sheet.py")
)
cds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cds)

import time, json

SPREADSHEET_ID = "1FsA4HCVjIXbRff5SgumWqeiGKDzVWbi35fOu9Jwu5V4"
SOURCE = "0f42fafd8"
TARGET = "c05871134"

# All 11 tabs (index 0-10)
ALL_TABS = [
    "activity_asset_retake",   # 0 - done
    "activity_config",          # 1 - done
    "activity_drop",            # 2 - done
    "activity_package",         # 3 - done
    "activity_special",         # 4 - done
    "activity_task",            # 5 - LARGE: write summary only
    "activity_ui_template",     # 6
    "get_access_group",         # 7
    "iap_config",               # 8
    "iap_template",             # 9
    "item",                     # 10
]

SKIP_DONE = {"activity_asset_retake", "activity_config", "activity_drop",
             "activity_package", "activity_special"}

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

def write_activity_task_summary():
    """activity_task 超大表，只写一行摘要。"""
    sheet_name = "activity_task"
    tab_idx = ALL_TABS.index(sheet_name)
    print(f"  写入摘要: {sheet_name} (超大表，跳过明细)...")

    values = [
        ["变更类型", "说明"],
        ["摘要", "activity_task 共 10118 行修改（几乎全表），推测为新增列导致全表行偏移。请直接 git diff 查看具体字段变更。"],
    ]
    params = json.dumps({
        "spreadsheetId": SPREADSHEET_ID,
        "range": f"'{sheet_name}'!A1",
        "valueInputOption": "USER_ENTERED"
    })
    body = {"values": values, "majorDimension": "ROWS"}
    cds.run_gws(['sheets', 'spreadsheets', 'values', 'update', '--params', params], body)

    # orange header for summary row
    fmt = [
        {
            "repeatCell": {
                "range": {"sheetId": tab_idx, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {
                    "backgroundColor": cds.COLOR_HEADER,
                    "textFormat": {"bold": True},
                }},
                "fields": "userEnteredFormat(backgroundColor,textFormat.bold)"
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": tab_idx, "startRowIndex": 1, "endRowIndex": 2},
                "cell": {"userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.7},
                }},
                "fields": "userEnteredFormat.backgroundColor"
            }
        },
    ]
    cds.run_gws(
        ['sheets', 'spreadsheets', 'batchUpdate',
         '--params', json.dumps({"spreadsheetId": SPREADSHEET_ID})],
        {"requests": fmt}
    )
    print("  OK")


def write_remaining():
    """写入剩余 6 张小表."""
    remaining = [t for t in ALL_TABS if t not in SKIP_DONE and t != "activity_task"]
    all_fmt = []

    for sheet_name in remaining:
        tab_idx = ALL_TABS.index(sheet_name)
        filepath = f"fo/config/{sheet_name}.tsv"
        print(f"  写入: {sheet_name}...", end='', flush=True)

        header = cds.get_header(filepath, SOURCE)
        rows = cds.get_diff_data(filepath, SOURCE, TARGET, header_cols=len(header))

        if not rows:
            print(" (无差异，跳过)")
            continue

        header_row = ["变更类型"] + cds._cells_for_gsheet_write(header)
        values = [header_row]
        for row in rows:
            label = "新增" if row['type'] == 'added' else "修改"
            values.append([label] + cds._cells_for_gsheet_write(row['cells']))

        cds.write_values_chunked(SPREADSHEET_ID, sheet_name, values)
        print(f" OK ({len(rows)} 行)")

        fmt = cds.build_format_requests(tab_idx, rows, len(header) + 1)
        all_fmt.extend(fmt)
        time.sleep(0.5)

    if all_fmt:
        print(f"\n  应用着色 ({len(all_fmt)} 条)...")
        cds.apply_formatting(SPREADSHEET_ID, all_fmt)
        print("  着色完成")


if __name__ == '__main__':
    print("补写 goldegg diff GSheet 剩余页签")
    print(f"GSheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")

    write_activity_task_summary()
    time.sleep(2)
    write_remaining()

    print("\n完成！")
    print(f"链接: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
