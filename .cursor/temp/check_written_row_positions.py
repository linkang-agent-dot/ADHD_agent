import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}


def call(args):
    res = subprocess.run([NODE, GWS_JS] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if res.returncode != 0:
        raise RuntimeError(res.stdout + res.stderr)
    return json.loads(res.stdout) if res.stdout.strip() else {}


def get_values(sheet_id, range_name):
    params = json.dumps({"spreadsheetId": sheet_id, "range": range_name}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def get_titles(sheet_id):
    params = json.dumps({"spreadsheetId": sheet_id, "includeGridData": False}, ensure_ascii=False)
    data = call(["sheets", "spreadsheets", "get", "--params", params])
    return [s["properties"]["title"] for s in data.get("sheets", [])]


def find_rows(sheet_id, tab, col, ids):
    values = get_values(sheet_id, f"{tab}!{col}:{col}")
    found = {}
    for idx, row in enumerate(values, start=1):
        if not row:
            continue
        val = str(row[0])
        if val in ids:
            found[val] = idx
    return found


def read_window(sheet_id, tab, start, end, cols):
    first_col, last_col = cols.split(":")
    return get_values(sheet_id, f"{tab}!{first_col}{start}:{last_col}{end}")


def print_table(name, found):
    print(f"\n=== {name} ===")
    for k in sorted(found, key=lambda x: int(x)):
        print(f"{k}: row {found[k]}")


def main():
    tables = {
        "2116": {
            "sheet": "1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA",
            "ids": [str(i) for i in range(21161748, 21161758)],
            "col": "C",
        },
        "2112": {
            "sheet": "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo",
            "tab": "activity_config_QA",
            "ids": ["21127359", "21127360", "21127361"],
            "col": "B",
        },
        "2111": {
            "sheet": "1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk",
            "tab": "activity_calendar_x2（QA）",
            "ids": ["211110567", "211110568", "211110569"],
            "col": "B",
        },
        "2013": {
            "sheet": "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E",
            "tab": "iap_template_x2（qa）",
            "ids": ["2013920111", "2013920112", "2013920113", "2013920114"],
            "col": "B",
        },
        "2011": {
            "sheet": "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY",
            "tab": "iap_config_x2qa",
            "ids": ["2011920111"],
            "col": "B",
        },
        "2121": {
            "sheet": "1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4",
            "tab": "activity_special",
            "ids": ["212101117"],
            "col": "B",
        },
    }

    # 2116 was appended by +append to the first tab; detect exact tab containing all IDs.
    t2116 = tables["2116"]
    tabs_2116 = get_titles(t2116["sheet"])
    best_tab = None
    best_found = {}
    for tab in tabs_2116:
        try:
            found = find_rows(t2116["sheet"], tab, t2116["col"], set(t2116["ids"]))
        except Exception:
            continue
        if len(found) > len(best_found):
            best_tab, best_found = tab, found
    t2116["tab"] = best_tab

    for name, cfg in tables.items():
        found = best_found if name == "2116" else find_rows(cfg["sheet"], cfg["tab"], cfg["col"], set(cfg["ids"]))
        print_table(f"{name} / {cfg['tab']}", found)

        if found:
            min_row = min(found.values())
            max_row = max(found.values())
            start = max(1, min_row - 2)
            end = max_row + 2
            cols = {
                "2116": "A:H",
                "2112": "A:J",
                "2111": "A:F",
                "2013": "A:D",
                "2011": "A:M",
                "2121": "A:M",
            }[name]
            window = read_window(cfg["sheet"], cfg["tab"], start, end, cols)
            print(f"window {start}:{end} {cols}:")
            for i, row in enumerate(window, start=start):
                print(f"  row {i}: {json.dumps(row, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
