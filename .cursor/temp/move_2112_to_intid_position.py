import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

SHEET_ID = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"
TAB = "activity_config_QA"
TARGET_IDS = {"21127359", "21127360", "21127361"}


def call(args, body=None):
    cmd = [NODE, GWS_JS] + args
    if body is not None:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if res.returncode != 0:
        raise RuntimeError(res.stdout + res.stderr)
    return json.loads(res.stdout) if res.stdout.strip() else {}


def get_values(range_name):
    params = json.dumps({"spreadsheetId": SHEET_ID, "range": range_name}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def update_values(range_name, values):
    params = json.dumps({"spreadsheetId": SHEET_ID, "range": range_name, "valueInputOption": "RAW"}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "update", "--params", params], {"values": values})


def batch_update(body):
    params = json.dumps({"spreadsheetId": SHEET_ID}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "batchUpdate", "--params", params], body)


def get_sheet_gid():
    params = json.dumps({"spreadsheetId": SHEET_ID, "includeGridData": False}, ensure_ascii=False)
    data = call(["sheets", "spreadsheets", "get", "--params", params])
    for sheet in data["sheets"]:
        if sheet["properties"]["title"] == TAB:
            return sheet["properties"]["sheetId"]
    raise RuntimeError("tab not found")


def main():
    gid = get_sheet_gid()
    rows = get_values(f"{TAB}!A:AA")
    found = []
    row_21127358 = None
    for idx, row in enumerate(rows, start=1):
        if len(row) > 1:
            if row[1] == "21127358":
                row_21127358 = idx
            if row[1] in TARGET_IDS:
                found.append((idx, row))

    if row_21127358 is None:
        raise RuntimeError("cannot find 21127358")
    if [i for i, _ in found] != [1467, 1468, 1469]:
        raise RuntimeError(f"unexpected current rows for targets: {[i for i, _ in found]}")

    moving_rows = [row + [""] * (27 - len(row)) for _, row in found]
    print(f"moving rows {[i for i, _ in found]} to after row {row_21127358}")

    # Delete current misplaced rows first. They are below the target, so target row remains stable.
    batch_update({
        "requests": [{
            "deleteDimension": {
                "range": {
                    "sheetId": gid,
                    "dimension": "ROWS",
                    "startIndex": 1466,  # row 1467, 0-based inclusive
                    "endIndex": 1469,    # row 1469, exclusive
                }
            }
        }]
    })

    # Insert 3 rows before the current row after 21127358.
    insert_at = row_21127358  # 0-based index equal to 1-based row after 21127358
    batch_update({
        "requests": [{
            "insertDimension": {
                "range": {
                    "sheetId": gid,
                    "dimension": "ROWS",
                    "startIndex": insert_at,
                    "endIndex": insert_at + 3,
                },
                "inheritFromBefore": True,
            }
        }]
    })

    target_range = f"{TAB}!A{row_21127358 + 1}:AA{row_21127358 + 3}"
    update_values(target_range, moving_rows)
    print(f"moved to {target_range}")


if __name__ == "__main__":
    main()
