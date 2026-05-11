import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

SHEETS = {
    "2121": "1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4",
    "2135": "1Agp8e-FfSz0ixLIVFwUIjvlkU69gB7D39URWnjzRvbs",
    "2011": "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY",
    "2013": "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E",
    "2112": "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo",
}


def gws(args, body=None):
    cmd = [NODE, GWS_JS] + args
    if body is not None:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return json.loads(result.stdout)


def read_values(spreadsheet_id, range_name):
    params = json.dumps({"spreadsheetId": spreadsheet_id, "range": range_name}, ensure_ascii=False)
    return gws(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def find_rows(spreadsheet_id, tabs, needle, range_suffix="A:Z"):
    matches = []
    for tab in tabs:
        try:
            rows = read_values(spreadsheet_id, f"{tab}!{range_suffix}")
        except Exception as exc:
            print(f"[WARN] read failed {tab}: {exc}")
            continue
        for idx, row in enumerate(rows, start=1):
            if any(needle in str(cell) for cell in row):
                matches.append((tab, idx, row))
    return matches


def main():
    print("=== 2121 header ===")
    header_2121 = read_values(SHEETS["2121"], "activity_special（掉落转付费）!A1:P6")
    for row in header_2121:
        print(json.dumps(row, ensure_ascii=False))

    candidates_2121 = [
        "activity_special（掉落转付费）",
        "activity_special",
        "26巨猿",
    ]
    rows_2121 = find_rows(SHEETS["2121"], candidates_2121, "212100316")
    print("=== 2121 rows for 212100316 ===")
    for tab, idx, row in rows_2121:
        print(json.dumps({"tab": tab, "row": idx, "values": row}, ensure_ascii=False))

    # Also locate the already-written 21127360 row and component cell range.
    rows_2112 = find_rows(SHEETS["2112"], ["activity_config_QA"], "21127360", "A:AA")
    print("\n=== 2112 rows for 21127360 ===")
    for tab, idx, row in rows_2112:
        print(json.dumps({"tab": tab, "row": idx, "values": row[:12]}, ensure_ascii=False))

    rows_2011 = find_rows(
        SHEETS["2011"],
        ["iap_config_x2qa", "iap_config_x2qa（掉落转付费）"],
        "2011910065",
        "A:S",
    )
    print("\n=== 2011 rows for 2011910065 ===")
    for tab, idx, row in rows_2011:
        print(json.dumps({"tab": tab, "row": idx, "values": row}, ensure_ascii=False))

    rows_2013 = find_rows(
        SHEETS["2013"],
        ["iap_template_x2（qa）", "iap_template_x2（掉落转付费）"],
        "2011910065",
        "A:AD",
    )
    print("\n=== 2013 rows for config_id 2011910065 ===")
    for tab, idx, row in rows_2013:
        print(json.dumps({"tab": tab, "row": idx, "values": row}, ensure_ascii=False))


if __name__ == "__main__":
    main()
