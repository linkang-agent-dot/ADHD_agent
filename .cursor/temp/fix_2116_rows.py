import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

SHEET_ID = "1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA"
TAB = "activity_item_exchange（线上版本）"


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


def get_sheet_id():
    params = json.dumps({"spreadsheetId": SHEET_ID, "includeGridData": False}, ensure_ascii=False)
    data = call(["sheets", "spreadsheets", "get", "--params", params])
    for sheet in data["sheets"]:
        if sheet["properties"]["title"] == TAB:
            return sheet["properties"]["sheetId"]
    raise RuntimeError("tab not found")


def batch_update(body):
    params = json.dumps({"spreadsheetId": SHEET_ID}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "batchUpdate", "--params", params], body)


def update_values(range_name, values):
    params = json.dumps({"spreadsheetId": SHEET_ID, "range": range_name, "valueInputOption": "RAW"}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "update", "--params", params], {"values": values})


def make_give(item_id, val):
    return json.dumps([{"asset": {"typ": "item", "id": item_id, "val": val}, "setting": {"serial_number": 1}}], separators=(",", ":"))


def make_get(item_id, val):
    return json.dumps([{"asset": {"typ": "item", "id": item_id, "val": val}, "setting": {"serial_number": 1}}], separators=(",", ":"))


rows_2116 = [
    ["", "33", "21161748", "2026-占星节-掉落转付费", make_give(111111119, 12), make_get(11111048, 1), "8001", "15"],
    ["", "33", "21161749", "2026-占星节-掉落转付费", make_give(111111119, 10), make_get(11119473, 1), "8002", "20"],
    ["", "33", "21161750", "2026-占星节-掉落转付费", make_give(111111119, 20), make_get(11116304, 1), "8003", "15"],
    ["", "33", "21161751", "2026-占星节-掉落转付费", make_give(111111119, 2), make_get(11111055, 1), "8004", "35"],
    ["", "33", "21161752", "2026-占星节-掉落转付费", make_give(111111119, 5), make_get(11118501, 1), "8005", "50"],
    ["", "33", "21161753", "2026-占星节-掉落转付费", make_give(111111119, 15), make_get(11116604, 1), "8006", "22"],
    ["", "33", "21161754", "2026-占星节-掉落转付费", make_give(111111118, 2), make_get(11119453, 1), "8007", "250"],
    ["", "33", "21161755", "2026-占星节-掉落转付费", make_give(111111118, 10), make_get(11114003, 1), "8008", "15"],
    ["", "33", "21161756", "2026-占星节-掉落转付费", make_give(111111118, 20), make_get(11117024, 1), "8009", "5"],
    ["", "33", "21161757", "2026-占星节-掉落转付费", make_give(111111118, 5), make_get(11111156, 1), "8010", "20"],
]


def main():
    sheet_gid = get_sheet_id()

    # Delete the accidental row 8 containing only 21161748 near the header.
    row8 = get_values(f"{TAB}!A8:H8")
    if row8 and len(row8[0]) > 2 and row8[0][2] == "21161748":
        batch_update({
            "requests": [{
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_gid,
                        "dimension": "ROWS",
                        "startIndex": 7,
                        "endIndex": 8,
                    }
                }
            }]
        })
        print("deleted accidental row 8")
    else:
        print("row 8 did not contain accidental 21161748; skip delete")

    # Re-read C column after deletion to find the true tail.
    col_c = get_values(f"{TAB}!C:C")
    last_row = len(col_c)
    next_row = last_row + 1
    print(f"last row after delete: {last_row}; append at {next_row}")

    batch_update({
        "requests": [{
            "appendDimension": {
                "sheetId": sheet_gid,
                "dimension": "ROWS",
                "length": len(rows_2116),
            }
        }]
    })
    target = f"{TAB}!A{next_row}:H{next_row + len(rows_2116) - 1}"
    update_values(target, rows_2116)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
