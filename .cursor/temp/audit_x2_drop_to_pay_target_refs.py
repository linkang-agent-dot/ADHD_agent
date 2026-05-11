from pathlib import Path
import json
import re
from collections import defaultdict

ROOT = Path(r"D:\UGit\x2gdconf")
TARGET_FILES = {
    "fo/config/activity_item_exchange.tsv": {"21161748","21161749","21161750","21161751","21161752","21161753","21161754","21161755","21161756","21161757"},
    "fo/config/activity_config.tsv": {"21127359","21127360","21127361"},
    "fo/json/ActivityCalendar.tsv": {"211110567","211110568","211110569"},
    "fo/config/iap_template.tsv": {"2013920111","2013920112","2013920113","2013920114"},
    "fo/config/iap_config.tsv": {"2011920111"},
    "fo/config/activity_special.tsv": {"212101117"},
}

ID_RE = re.compile(r"\b\d{8,10}\b")


def read_rows(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()]


def find_id_col(rows):
    for row in rows[:8]:
        for i, cell in enumerate(row):
            if cell == "Id":
                return i
    return 1


def build_id_index():
    ids = defaultdict(list)
    for folder in [ROOT / "fo/config", ROOT / "fo/json"]:
        for path in folder.glob("*.tsv"):
            rows = read_rows(path)
            col = find_id_col(rows)
            for line_no, row in enumerate(rows, 1):
                if len(row) > col and row[col].isdigit():
                    ids[row[col]].append((str(path.relative_to(ROOT)), line_no))
    return ids


def json_columns(rows):
    # Use fwcli_type row to identify MAP / ARR columns.
    for row in rows[:8]:
        if row and row[0] == "fwcli_type":
            return [i for i, v in enumerate(row) if "MAP" in v or "ARR" in v]
    return []


def main():
    id_index = build_id_index()
    problems = []
    print("=== TARGET ROW STRUCTURE / JSON / XREF ===")
    for rel, targets in TARGET_FILES.items():
        path = ROOT / rel
        rows = read_rows(path)
        id_col = find_id_col(rows)
        header_len = len(rows[0])
        jcols = json_columns(rows)
        found = {}
        for line_no, row in enumerate(rows, 1):
            if len(row) > id_col and row[id_col] in targets:
                found[row[id_col]] = (line_no, row)

        print(f"\n[{rel}] header_cols={header_len}, id_col={id_col}")
        missing = sorted(targets - set(found))
        print(f"  missing={missing or 'none'}")
        if missing:
            problems.append((rel, "missing", missing))

        for tid in sorted(targets, key=int):
            if tid not in found:
                continue
            line_no, row = found[tid]
            col_ok = len(row) == header_len
            if not col_ok:
                problems.append((rel, tid, f"col_count {len(row)} != {header_len}"))
            json_bad = []
            for c in jcols:
                if c >= len(row):
                    continue
                val = row[c]
                if val in ("", "NULL"):
                    continue
                try:
                    json.loads(val)
                except Exception as exc:
                    json_bad.append((c, val[:80], str(exc)))
            if json_bad:
                problems.append((rel, tid, f"bad_json {json_bad}"))

            refs = set(ID_RE.findall("\t".join(row)))
            # Ignore self row ID and obvious product ids are still checked if present in index.
            unresolved = []
            for ref in sorted(refs):
                if ref == tid:
                    continue
                # Some short ids are not table IDs, but our regex is 8-10 digits; check existence.
                if ref not in id_index:
                    unresolved.append(ref)
            if unresolved:
                problems.append((rel, tid, f"unresolved_refs {unresolved}"))
            print(f"  {tid}: row={line_no}, cols_ok={col_ok}, json_ok={not json_bad}, unresolved_refs={unresolved or 'none'}")

    print("\n=== RESULT ===")
    if problems:
        for p in problems:
            print("PROBLEM", p)
        raise SystemExit(1)
    print("OK: all target rows passed structure/json/xref checks")


if __name__ == "__main__":
    main()
