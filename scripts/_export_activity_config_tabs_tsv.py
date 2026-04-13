# -*- coding: utf-8 -*-
"""Export full activity_config tabs (by gid) to UTF-8 TSV for Google Sheets paste.

2112_x2_activity_config — spreadsheet 1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo
  - QA:   gid 1922183355  activity_config_QA
  - 线上: gid 1943943957  activity_config_Master（线上主页签-线上热更后记得同步qa页签）
"""
import csv
import json
import subprocess
from pathlib import Path

SPREADSHEET = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"
GIDS = (1922183355, 1943943957)
GID_TITLE_OVERRIDE: dict[int, str] = {
    1943943957: "activity_config_Master（线上主页签-线上热更后记得同步qa页签）",
}
CELL_TAIL = "A1:AB25000"
# Rows 1–7: p2_title + fwcli meta; row 8+ = data（与 IAP 表不覆盖前 7 行一致）
META_ROWS = 7


def _run_gws_json(cmd: str) -> dict:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:4000] or str(p.returncode))
    return json.loads(p.stdout)


def _sheet_titles_by_gid() -> dict[int, str]:
    cmd = (
        "gws sheets spreadsheets get --params "
        + json.dumps(json.dumps({"spreadsheetId": SPREADSHEET}))
        + " --format json"
    )
    data = _run_gws_json(cmd)
    out: dict[int, str] = {}
    for s in data.get("sheets", []):
        props = s.get("properties", {})
        sid = props.get("sheetId")
        title = props.get("title") or ""
        if sid is not None:
            out[int(sid)] = title
    return out


def _a1_range(sheet_title: str) -> str:
    esc = sheet_title.replace("'", "''")
    return f"'{esc}'!{CELL_TAIL}"


def _read_values(range_a1: str) -> list[list]:
    # Do not json.dumps(range): API rejects \uXXXX escapes in A1 range string.
    cmd = (
        f'gws sheets +read --spreadsheet {SPREADSHEET} '
        f'--range "{range_a1}" --format json'
    )
    data = _run_gws_json(cmd)
    return data.get("values") or []


def _write_tsv(path: Path, rows: list[list]) -> None:
    maxc = max((len(r) for r in rows), default=0)

    def pad(r: list) -> list:
        return list(r) + [""] * (maxc - len(r))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        for r in rows:
            w.writerow(pad(r))


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    by_gid = _sheet_titles_by_gid()
    for gid in GIDS:
        title = GID_TITLE_OVERRIDE.get(gid) or by_gid.get(gid)
        if not title:
            print("missing gid", gid)
            continue
        rng = _a1_range(title)
        print("reading", gid, "...")
        rows = _read_values(rng)
        slug = "activity_config_QA" if gid == 1922183355 else "activity_config_online"
        out_full = base / f"{slug}_full_paste.tsv"
        _write_tsv(out_full, rows)
        only = rows[META_ROWS:] if len(rows) > META_ROWS else []
        out_only = base / f"{slug}_only.tsv"
        _write_tsv(out_only, only)
        print(
            "written",
            out_full,
            "rows",
            len(rows),
            "| only",
            out_only,
            "rows",
            len(only),
            "max_cols",
            max((len(r) for r in rows), default=0),
        )


if __name__ == "__main__":
    main()
