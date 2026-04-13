"""Scan activity_config.tsv JSON-typed cells for invalid JSON / trailing garbage (Newtonsoft-style).

用法：
  python _scan_activity_config_json.py
  python _scan_activity_config_json.py "D:\\path\\to\\activity_config.tsv"
"""
import argparse
import csv
import json
from pathlib import Path

DEFAULT_TSV = Path(r"D:\UGit\x2gdconf\fo\config\activity_config.tsv")
# fwcli_type row 3 (1-based line 3): JSON-ish columns
JSON_HINT = ("MAP", "ARR", "CVal", "CGroup", "CRule", "ARR,C")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv", nargs="?", type=Path, default=DEFAULT_TSV)
    args = ap.parse_args()
    tsv = args.tsv
    if not tsv.is_file():
        print(f"文件不存在: {tsv}")
        return

    with tsv.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))

    if len(rows) < 8:
        print("too few rows")
        return

    titles = rows[0]
    fw_types = rows[2]

    json_cols = []
    for i, (t, typ) in enumerate(zip(titles, fw_types)):
        if not typ:
            continue
        if any(h in typ for h in JSON_HINT):
            json_cols.append((i, titles[i], typ))

    dec = json.JSONDecoder()
    problems = []

    for ri, row in enumerate(rows[7:], start=8):
        if not row or (len(row) >= 2 and not row[1].strip()):
            continue
        row_id = row[1].strip() if len(row) > 1 else "?"
        for ci, colname, _typ in json_cols:
            if ci >= len(row):
                continue
            raw = row[ci].strip()
            if not raw:
                continue
            s = raw
            # TSV already unescaped by csv.reader
            try:
                obj, end = dec.raw_decode(s)
            except json.JSONDecodeError as e:
                problems.append(
                    {
                        "line": ri,
                        "id": row_id,
                        "column": colname,
                        "error": str(e),
                        "snippet": s[:120] + ("..." if len(s) > 120 else ""),
                    }
                )
                continue
            rest = s[end:].strip()
            if rest:
                problems.append(
                    {
                        "line": ri,
                        "id": row_id,
                        "column": colname,
                        "error": f"trailing_after_json: {rest[:80]!r}",
                        "snippet": s[:200] + ("..." if len(s) > 200 else ""),
                    }
                )

    print(f"File: {tsv}")
    print(f"Scanned data rows from line 8, JSON columns: {len(json_cols)}")
    if not problems:
        print("OK: no JSON parse errors or trailing garbage")
        return
    print(f"FOUND {len(problems)} issue(s):\n")
    for p in problems:
        print(
            f"  line {p['line']}  Id={p['id']}  col={p['column']}\n"
            f"    {p['error']}\n"
            f"    {p['snippet']}\n"
        )


if __name__ == "__main__":
    main()
