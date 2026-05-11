import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

TABLES = [
    ("2116", "1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA", "activity_item_exchange（线上版本）", "C", [*range(21161748, 21161758)]),
    ("2112", "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo", "activity_config_QA", "B", [21127359, 21127360, 21127361]),
    ("2111", "1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk", "activity_calendar_x2（QA）", "B", [211110567, 211110568, 211110569]),
    ("2013", "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E", "iap_template_x2（qa）", "B", [2013920111, 2013920112, 2013920113, 2013920114]),
    ("2011", "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY", "iap_config_x2qa", "B", [2011920111]),
    ("2121", "1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4", "activity_special", "B", [212101117]),
]


def call(args):
    res = subprocess.run([NODE, GWS_JS] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if res.returncode != 0:
        raise RuntimeError(res.stdout + res.stderr)
    return json.loads(res.stdout)


def get_values(sheet_id, range_name):
    params = json.dumps({"spreadsheetId": sheet_id, "range": range_name}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def numeric_rows(values):
    out = []
    for row_no, row in enumerate(values, start=1):
        if not row:
            continue
        s = str(row[0]).strip()
        if s.isdigit():
            out.append((int(s), row_no))
    return out


def main():
    for table, sheet, tab, col, targets in TABLES:
        ids = numeric_rows(get_values(sheet, f"{tab}!{col}:{col}"))
        id_to_row = {i: r for i, r in ids}
        print(f"\n=== {table} / {tab} ===")
        for t in targets:
            row = id_to_row.get(t)
            if not row:
                print(f"{t}: MISSING")
                continue
            # Neighbor in actual sheet row order.
            sorted_by_row = sorted(ids, key=lambda x: x[1])
            idx = next(i for i, (v, r) in enumerate(sorted_by_row) if v == t and r == row)
            prev_row = sorted_by_row[idx - 1] if idx > 0 else None
            next_row = sorted_by_row[idx + 1] if idx + 1 < len(sorted_by_row) else None
            # Neighbor in numeric id order.
            sorted_by_id = sorted(ids, key=lambda x: x[0])
            id_idx = next(i for i, (v, r) in enumerate(sorted_by_id) if v == t and r == row)
            prev_id = sorted_by_id[id_idx - 1] if id_idx > 0 else None
            next_id = sorted_by_id[id_idx + 1] if id_idx + 1 < len(sorted_by_id) else None
            ok = (prev_row == prev_id and next_row == next_id)
            print(f"{t}: row={row}, row_prev={prev_row}, row_next={next_row}, id_prev={prev_id}, id_next={next_id}, order_ok={ok}")


if __name__ == "__main__":
    main()
