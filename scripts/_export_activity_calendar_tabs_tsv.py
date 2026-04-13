# -*- coding: utf-8 -*-
"""Export full ActivityCalendar tabs (by gid) to UTF-8 TSV for Google Sheets paste.

2111_x2_ActivityCalendar — spreadsheet 1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk
  - QA:     gid 681415886  activity_calendar_x2（QA）
  - 线上:   gid 1459407900 activity_calendar_x2（线上）
"""
import csv
import json
import subprocess
from pathlib import Path

SPREADSHEET = "1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk"
# 先 线上 后 QA，与常用「对齐到线上」顺序一致
GIDS = (1459407900, 681415886)
# gws get may mangle CJK; names from 2111_x2_ActivityCalendar tab bar
GID_TITLE_OVERRIDE: dict[int, str] = {
    1459407900: "activity_calendar_x2（线上）",
    681415886: "activity_calendar_x2（QA）",
}
# Snippet shows A–K (11 cols); cap rows
CELL_TAIL = "A1:K25000"
# Rows 1–6: fwcli_name/type/template/group/check/desc; row 7+ = data (paste into existing meta)
META_ROWS = 6


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
    cmd = (
        f"gws sheets +read --spreadsheet {SPREADSHEET} "
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
        slug = (
            "activity_calendar_x2_online"
            if gid == 1459407900
            else "activity_calendar_x2_QA"
        )
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
