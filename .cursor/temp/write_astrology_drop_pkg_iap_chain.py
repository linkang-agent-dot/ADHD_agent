import json
import os
import re
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

SHEETS = {
    "2121": "1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4",
    "2011": "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY",
    "2013": "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E",
    "2112": "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo",
}

TABS = {
    "2121": "activity_special",
    "2011": "iap_config_x2qa",
    "2013": "iap_template_x2（qa）",
    "2112": "activity_config_QA",
}


def call(args, body=None):
    cmd = [NODE, GWS_JS] + args
    if body is not None:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if res.returncode != 0:
        raise RuntimeError(res.stdout + res.stderr)
    return json.loads(res.stdout) if res.stdout.strip() else {}


def get_values(spreadsheet_id, range_name):
    params = json.dumps({"spreadsheetId": spreadsheet_id, "range": range_name}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def update_values(spreadsheet_id, range_name, values):
    params = json.dumps(
        {"spreadsheetId": spreadsheet_id, "range": range_name, "valueInputOption": "RAW"},
        ensure_ascii=False,
    )
    return call(["sheets", "spreadsheets", "values", "update", "--params", params], {"values": values})


def append_rows(spreadsheet_id, sheet_id, range_name, values):
    # values.update cannot write past current grid limits, so expand explicitly first.
    params = json.dumps({"spreadsheetId": spreadsheet_id}, ensure_ascii=False)
    call(
        ["sheets", "spreadsheets", "batchUpdate", "--params", params],
        {"requests": [{"appendDimension": {"sheetId": sheet_id, "dimension": "ROWS", "length": len(values)}}]},
    )
    return update_values(spreadsheet_id, range_name, values)


def get_sheet_ids(spreadsheet_id):
    params = json.dumps({"spreadsheetId": spreadsheet_id, "includeGridData": False}, ensure_ascii=False)
    data = call(["sheets", "spreadsheets", "get", "--params", params])
    return {s["properties"]["title"]: s["properties"]["sheetId"] for s in data.get("sheets", [])}


def find_row(rows, needle):
    for i, row in enumerate(rows, start=1):
        if any(str(cell) == str(needle) for cell in row):
            return i, row
    raise ValueError(f"not found: {needle}")


def max_id_in_col(rows, prefix):
    max_id = 0
    pat = re.compile(rf"^{prefix}\d+$")
    for row in rows:
        if not row:
            continue
        value = str(row[0])
        if pat.match(value):
            max_id = max(max_id, int(value))
    return max_id


def pad(row, length):
    return row + [""] * (length - len(row))


def main():
    # Read only the tabs involved in this chain.
    rows_2121 = get_values(SHEETS["2121"], f"{TABS['2121']}!A:P")
    rows_2011 = get_values(SHEETS["2011"], f"{TABS['2011']}!A:S")
    rows_2013 = get_values(SHEETS["2013"], f"{TABS['2013']}!A:AD")
    rows_2112 = get_values(SHEETS["2112"], f"{TABS['2112']}!A:AA")

    _, old_2121 = find_row(rows_2121, "212100316")
    _, old_2011 = find_row(rows_2011, "2011910065")
    old_2013_rows = [row for row in rows_2013 if len(row) > 3 and row[3] == "2011910065"]
    row_2112_idx, row_2112 = find_row(rows_2112, "21127360")

    if len(old_2013_rows) != 4:
        raise RuntimeError(f"expected 4 old 2013 rows for 2011910065, got {len(old_2013_rows)}")

    # Allocate IDs from current max in the target QA tabs.
    new_2121_id = max_id_in_col([r[1:2] for r in rows_2121 if len(r) > 1], "2121") + 1
    new_2011_id = max_id_in_col([r[1:2] for r in rows_2011 if len(r) > 1], "2011") + 1
    new_2013_start = max_id_in_col([r[1:2] for r in rows_2013 if len(r) > 1], "2013") + 1

    print("Allocated IDs:")
    print(f"  2121: {new_2121_id}")
    print(f"  2011: {new_2011_id}")
    print(f"  2013: {new_2013_start}-{new_2013_start + len(old_2013_rows) - 1}")

    # New 2011: copy old drop-to-pay IAP config, bind to new activity and astrology recharge activity.
    new_2011 = pad(old_2011[:], 19)
    new_2011[1] = str(new_2011_id)
    new_2011[2] = "占星节-掉落转付费礼包"
    new_2011[9] = json.dumps({"normal": [{"actv_id": 21127360}]}, separators=(",", ":"), ensure_ascii=False)
    new_2011[12] = json.dumps(
        [{"typ": "recharge_actv", "id": 211200093, "arg1": 1511018855, "val": 1}],
        separators=(",", ":"),
        ensure_ascii=False,
    )

    # New 2013 rows: copy four price tiers and point config_id to new 2011.
    new_2013_rows = []
    for offset, old in enumerate(old_2013_rows):
        row = pad(old[:], 30)
        row[1] = str(new_2013_start + offset)
        row[3] = str(new_2011_id)
        row[5] = str(row[5]).replace("掉落转付费礼包", "占星节-掉落转付费礼包")
        new_2013_rows.append(row)

    # New 2121: copy old discount component and point status to new 2011.
    new_2121 = pad(old_2121[:], 16)
    new_2121[1] = str(new_2121_id)
    new_2121[2] = "占星节-掉落转付费-礼包"
    new_2121[12] = json.dumps([{"typ": "iap", "id": new_2011_id}], separators=(",", ":"), ensure_ascii=False)

    # Update 2112 package activity component to new 2121 id.
    updated_2112 = pad(row_2112[:], 27)
    updated_2112[9] = json.dumps([{"typ": "discount", "id": new_2121_id}], separators=(",", ":"), ensure_ascii=False)

    sheet_ids_2011 = get_sheet_ids(SHEETS["2011"])
    sheet_ids_2013 = get_sheet_ids(SHEETS["2013"])
    sheet_ids_2121 = get_sheet_ids(SHEETS["2121"])

    next_2011_row = len(rows_2011) + 1
    next_2013_row = len(rows_2013) + 1
    next_2121_row = len(rows_2121) + 1

    print("Target ranges:")
    print(f"  2011: {TABS['2011']}!A{next_2011_row}:S{next_2011_row}")
    print(f"  2013: {TABS['2013']}!A{next_2013_row}:AD{next_2013_row + len(new_2013_rows) - 1}")
    print(f"  2121: {TABS['2121']}!A{next_2121_row}:P{next_2121_row}")
    print(f"  2112 update: {TABS['2112']}!A{row_2112_idx}:AA{row_2112_idx}")

    # Write in dependency order: 2013, 2011, 2121, then update 2112.
    append_rows(
        SHEETS["2013"],
        sheet_ids_2013[TABS["2013"]],
        f"{TABS['2013']}!A{next_2013_row}:AD{next_2013_row + len(new_2013_rows) - 1}",
        new_2013_rows,
    )
    append_rows(
        SHEETS["2011"],
        sheet_ids_2011[TABS["2011"]],
        f"{TABS['2011']}!A{next_2011_row}:S{next_2011_row}",
        [new_2011],
    )
    append_rows(
        SHEETS["2121"],
        sheet_ids_2121[TABS["2121"]],
        f"{TABS['2121']}!A{next_2121_row}:P{next_2121_row}",
        [new_2121],
    )
    update_values(
        SHEETS["2112"],
        f"{TABS['2112']}!A{row_2112_idx}:AA{row_2112_idx}",
        [updated_2112],
    )

    print("DONE")
    print(json.dumps({
        "new_2121": new_2121_id,
        "new_2011": new_2011_id,
        "new_2013": [new_2013_start + i for i in range(len(new_2013_rows))],
        "updated_2112_row": row_2112_idx,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
