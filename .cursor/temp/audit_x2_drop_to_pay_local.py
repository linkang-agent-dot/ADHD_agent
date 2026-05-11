from pathlib import Path
import json
import re
from collections import Counter

ROOT = Path(r"D:\UGit\x2gdconf")

FILES = {
    "2116": ROOT / "fo/config/activity_item_exchange.tsv",
    "2112": ROOT / "fo/config/activity_config.tsv",
    "2111": ROOT / "fo/json/ActivityCalendar.tsv",
    "2013": ROOT / "fo/config/iap_template.tsv",
    "2011": ROOT / "fo/config/iap_config.tsv",
    "2121": ROOT / "fo/config/activity_special.tsv",
}

TARGETS = {
    "2116": [str(i) for i in range(21161748, 21161758)],
    "2112": ["21127359", "21127360", "21127361"],
    "2111": ["211110567", "211110568", "211110569"],
    "2013": ["2013920111", "2013920112", "2013920113", "2013920114"],
    "2011": ["2011920111"],
    "2121": ["212101117"],
}


def read_tsv(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    return [line.split("\t") for line in text.splitlines()]


def id_col(rows):
    for row in rows[:8]:
        for i, cell in enumerate(row):
            if cell == "Id":
                return i
    # fallback for generated config files
    return 1


def rows_by_id(rows, col):
    out = {}
    dups = []
    seen = {}
    for idx, row in enumerate(rows, start=1):
        if len(row) <= col:
            continue
        v = row[col]
        if v.isdigit():
            if v in seen:
                dups.append((v, seen[v], idx))
            seen[v] = idx
            out[v] = (idx, row)
    return out, dups


def parse_json_cell(value, default=None):
    try:
        return json.loads(value)
    except Exception:
        return default


def check_order(table, ids, mapping):
    result = []
    numeric = sorted((int(k), v[0]) for k, v in mapping.items())
    by_id = {i: n for n, (i, _) in enumerate(numeric)}
    by_row = sorted((i, row) for i, row in numeric)
    row_positions = {i: n for n, (i, _) in enumerate(by_row)}
    for target in ids:
        tid = int(target)
        if target not in mapping:
            result.append((target, "MISSING", None))
            continue
        id_idx = by_id[tid]
        row_idx = row_positions[tid]
        prev_id = numeric[id_idx - 1] if id_idx > 0 else None
        next_id = numeric[id_idx + 1] if id_idx + 1 < len(numeric) else None
        prev_row = by_row[row_idx - 1] if row_idx > 0 else None
        next_row = by_row[row_idx + 1] if row_idx + 1 < len(by_row) else None
        ok = prev_id == prev_row and next_id == next_row
        result.append((target, "OK" if ok else "ORDER_WARN", {
            "row": mapping[target][0],
            "prev_row": prev_row,
            "next_row": next_row,
            "prev_id": prev_id,
            "next_id": next_id,
        }))
    return result


def get(mapping, tid):
    item = mapping.get(str(tid))
    return item[1] if item else None


def main():
    all_maps = {}
    print("=== LOCAL TARGET EXISTENCE / ORDER ===")
    for table, path in FILES.items():
        rows = read_tsv(path)
        col = id_col(rows)
        mapping, dups = rows_by_id(rows, col)
        all_maps[table] = (rows, col, mapping, dups)
        print(f"\n[{table}] {path.relative_to(ROOT)} id_col={col}")
        for tid, status, detail in check_order(table, TARGETS[table], mapping):
            print(f"  {tid}: {status} {detail}")
        target_dups = [d for d in dups if d[0] in TARGETS[table]]
        print(f"  target_duplicates: {target_dups or 'none'}")

    print("\n=== LOCAL CHAIN CHECK ===")
    m2112 = all_maps["2112"][2]
    m2121 = all_maps["2121"][2]
    m2011 = all_maps["2011"][2]
    m2013 = all_maps["2013"][2]
    m2116 = all_maps["2116"][2]
    m2111 = all_maps["2111"][2]

    # 2111 -> 2112
    expected_calendar = {
        "211110567": "21127361",
        "211110568": "21127359",
        "211110569": "21127360",
    }
    for cal_id, actv_id in expected_calendar.items():
        row = get(m2111, cal_id)
        actual = row[2] if row and len(row) > 2 else None
        print(f"  2111 {cal_id} -> {actual}; expected {actv_id}; ok={actual == actv_id}")

    # 2112 package -> 2121
    row_21127360 = get(m2112, "21127360")
    comp_21127360 = parse_json_cell(row_21127360[9], []) if row_21127360 else []
    print(f"  2112 21127360 components={comp_21127360}")
    print(f"  expect discount 212101117 ok={comp_21127360 == [{'typ':'discount','id':212101117}]}")

    # 2121 -> 2011
    row_2121 = get(m2121, "212101117")
    status_2121 = parse_json_cell(row_2121[12], []) if row_2121 and len(row_2121) > 12 else []
    print(f"  2121 212101117 status={status_2121}; expect iap 2011920111 ok={status_2121 == [{'typ':'iap','id':2011920111}]}")

    # 2011 -> actv + recharge
    row_2011 = get(m2011, "2011920111")
    time_info = parse_json_cell(row_2011[9], {}) if row_2011 and len(row_2011) > 9 else {}
    iap_status = parse_json_cell(row_2011[12], []) if row_2011 and len(row_2011) > 12 else []
    print(f"  2011 2011920111 time_info={time_info}; expect actv_id=21127360 ok={time_info == {'normal':[{'actv_id':21127360}]}}")
    print(f"  2011 2011920111 iap_status={iap_status}; expect recharge 211200093 ok={iap_status == [{'typ':'recharge_actv','id':211200093,'arg1':1511018855,'val':1}]}")

    # 2013 -> 2011
    for tid in TARGETS["2013"]:
        row = get(m2013, tid)
        cfg_id = row[3] if row and len(row) > 3 else None
        print(f"  2013 {tid} -> config_id {cfg_id}; expected 2011920111; ok={cfg_id == '2011920111'}")

    # 2112 main exchanges -> 2116
    row_main = get(m2112, "21127361")
    comps = parse_json_cell(row_main[9], []) if row_main else []
    exchange_ids = [str(x.get("id")) for x in comps if isinstance(x, dict) and x.get("typ") == "exchange"]
    expected_exchange = TARGETS["2116"]
    print(f"  2112 21127361 exchange_ids={exchange_ids}")
    print(f"  expect all 2116 ok={exchange_ids == expected_exchange and all(e in m2116 for e in expected_exchange)}")


if __name__ == "__main__":
    main()
