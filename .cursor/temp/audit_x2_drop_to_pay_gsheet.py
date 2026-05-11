import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

SHEETS = {
    "2116": ("1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA", "activity_item_exchange（线上版本）", 2, "A:H"),
    "2112": ("1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo", "activity_config_QA", 1, "A:AA"),
    "2111": ("1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk", "activity_calendar_x2（QA）", 1, "A:F"),
    "2013": ("1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E", "iap_template_x2（qa）", 1, "A:AD"),
    "2011": ("1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY", "iap_config_x2qa", 1, "A:S"),
    "2121": ("1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4", "activity_special", 1, "A:P"),
}

TARGETS = {
    "2116": [str(i) for i in range(21161748, 21161758)],
    "2112": ["21127359", "21127360", "21127361"],
    "2111": ["211110567", "211110568", "211110569"],
    "2013": ["2013920111", "2013920112", "2013920113", "2013920114"],
    "2011": ["2011920111"],
    "2121": ["212101117"],
}


def call(args):
    res = subprocess.run([NODE, GWS_JS] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if res.returncode != 0:
        raise RuntimeError(res.stdout + res.stderr)
    return json.loads(res.stdout) if res.stdout.strip() else {}


def get_values(sheet, range_name):
    params = json.dumps({"spreadsheetId": sheet, "range": range_name}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def parse_json(value, default=None):
    try:
        return json.loads(value)
    except Exception:
        return default


def numeric_map(rows, id_col):
    mapping, seen, dups = {}, {}, []
    for idx, row in enumerate(rows, start=1):
        if len(row) <= id_col:
            continue
        v = str(row[id_col])
        if v.isdigit():
            if v in seen:
                dups.append((v, seen[v], idx))
            seen[v] = idx
            mapping[v] = (idx, row)
    return mapping, dups


def check_order(mapping, targets):
    nums = sorted((int(k), v[0]) for k, v in mapping.items())
    by_id = {v: i for i, (v, _) in enumerate(nums)}
    by_row_list = sorted(nums, key=lambda x: x[1])
    by_row = {v: i for i, (v, _) in enumerate(by_row_list)}
    for t in targets:
        if t not in mapping:
            print(f"  {t}: MISSING")
            continue
        v = int(t)
        i, r = by_id[v], by_row[v]
        prev_id = nums[i - 1] if i > 0 else None
        next_id = nums[i + 1] if i + 1 < len(nums) else None
        prev_row = by_row_list[r - 1] if r > 0 else None
        next_row = by_row_list[r + 1] if r + 1 < len(by_row_list) else None
        print(f"  {t}: row={mapping[t][0]}, order_ok={prev_id == prev_row and next_id == next_row}, prev={prev_row}, next={next_row}")


def main():
    maps = {}
    print("=== GSHEET TARGET EXISTENCE / ORDER ===")
    for table, (sheet, tab, id_col, cols) in SHEETS.items():
        rows = get_values(sheet, f"{tab}!{cols}")
        mapping, dups = numeric_map(rows, id_col)
        maps[table] = mapping
        print(f"\n[{table}] {tab}")
        check_order(mapping, TARGETS[table])
        print(f"  target_duplicates: {[d for d in dups if d[0] in TARGETS[table]] or 'none'}")

    print("\n=== GSHEET CHAIN CHECK ===")
    m2111, m2112, m2121 = maps["2111"], maps["2112"], maps["2121"]
    m2011, m2013, m2116 = maps["2011"], maps["2013"], maps["2116"]
    for cal_id, actv_id in {"211110567": "21127361", "211110568": "21127359", "211110569": "21127360"}.items():
        row = m2111.get(cal_id, (None, []))[1]
        actual = row[2] if len(row) > 2 else None
        print(f"  2111 {cal_id} -> {actual}; expected {actv_id}; ok={actual == actv_id}")
    row = m2112["21127360"][1]
    comp = parse_json(row[9], [])
    print(f"  2112 21127360 components={comp}; ok={comp == [{'typ':'discount','id':212101117}]}")
    row = m2121["212101117"][1]
    status = parse_json(row[12], [])
    print(f"  2121 212101117 status={status}; ok={status == [{'typ':'iap','id':2011920111}]}")
    row = m2011["2011920111"][1]
    time_info = parse_json(row[9], {})
    iap_status = parse_json(row[12], [])
    print(f"  2011 2011920111 time_info={time_info}; ok={time_info == {'normal':[{'actv_id':21127360}]}}")
    print(f"  2011 2011920111 iap_status={iap_status}; ok={iap_status == [{'typ':'recharge_actv','id':211200093,'arg1':1511018855,'val':1}]}")
    for tid in TARGETS["2013"]:
        row = m2013[tid][1]
        print(f"  2013 {tid} -> {row[3] if len(row) > 3 else None}; ok={len(row)>3 and row[3]=='2011920111'}")
    row = m2112["21127361"][1]
    comps = parse_json(row[9], [])
    exchange_ids = [str(x.get("id")) for x in comps if isinstance(x, dict) and x.get("typ") == "exchange"]
    print(f"  2112 21127361 exchange_ids={exchange_ids}; ok={exchange_ids == TARGETS['2116'] and all(x in m2116 for x in TARGETS['2116'])}")


if __name__ == "__main__":
    main()
