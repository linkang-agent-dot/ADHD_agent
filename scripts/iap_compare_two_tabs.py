# -*- coding: utf-8 -*-
"""对比同一 spreadsheet 下两个 iap 页签（按 gid 或 sheet 名）。"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

SPREADSHEET_ID = "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY"
RANGE_ = "A1:U5000"
GWS = os.path.join(os.environ.get("APPDATA", ""), "npm", "gws.cmd")
ROOT = Path(__file__).resolve().parent
GWS_STDIN = ROOT / "gws_stdin.js"
OUT = Path(__file__).resolve().parents[1] / "iap_two_tabs_diff.md"

# 用户给的两个 gid
GID_A = 1032886231
GID_B = 1202421075

os.environ["GOOGLE_WORKSPACE_PROJECT_ID"] = "calm-repeater-489707-n1"


def gws_get_json(args: list[str]) -> dict:
    stdin_payload = json.dumps({"args": args, "json": None}, ensure_ascii=False)
    r = subprocess.run(
        ["node", str(GWS_STDIN)],
        input=stdin_payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def sheet_title_by_gid(gid: int) -> str:
    params = json.dumps(
        {
            "spreadsheetId": SPREADSHEET_ID,
            "fields": "sheets(properties(sheetId,title))",
        },
        separators=(",", ":"),
    )
    d = gws_get_json(["sheets", "spreadsheets", "get", "--params", params])
    for s in d.get("sheets", []):
        p = s.get("properties", {})
        if p.get("sheetId") == gid:
            return p.get("title") or ""
    raise SystemExit(f"gid {gid} not found")


def values_get(tab_title: str) -> list[list]:
    esc = tab_title.replace("'", "''")
    params = json.dumps(
        {"spreadsheetId": SPREADSHEET_ID, "range": f"'{esc}'!{RANGE_}"},
        separators=(",", ":"),
    )
    d = gws_get_json(["sheets", "spreadsheets", "values", "get", "--params", params])
    return d.get("values") or []


def norm_row(r: list) -> list[str]:
    return [("" if c is None else str(c).strip()) for c in r]


def main() -> None:
    title_a = sheet_title_by_gid(GID_A)
    title_b = sheet_title_by_gid(GID_B)
    print(f"A ({GID_A}): {title_a!r}")
    print(f"B ({GID_B}): {title_b!r}")

    va = values_get(title_a)
    vb = values_get(title_b)
    header_rows = 7

    def data_rows(vals: list) -> list[list[str]]:
        out = []
        for i, row in enumerate(vals):
            if i < header_rows:
                continue
            nr = norm_row(row)
            while len(nr) < 21:
                nr.append("")
            out.append(nr)
        return out

    da = data_rows(va)
    db = data_rows(vb)
    col_names = norm_row(va[1]) if len(va) > 1 else []

    def key_row(r: list[str]) -> tuple[str, str]:
        return (r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else "")

    from collections import defaultdict

    by_a: dict[tuple[str, str], list] = defaultdict(list)
    by_b: dict[tuple[str, str], list] = defaultdict(list)
    for r in da:
        by_a[key_row(r)].append(r)
    for r in db:
        by_b[key_row(r)].append(r)

    keys = sorted(set(by_a) | set(by_b), key=lambda k: (k[0], k[1]))
    only_a = [k for k in keys if k not in by_b]
    only_b = [k for k in keys if k not in by_a]
    cell_diffs: list[dict] = []

    for k in keys:
        la, lb = by_a.get(k, []), by_b.get(k, [])
        if not la or not lb or len(la) != len(lb):
            continue
        for ra, rb in zip(la, lb):
            for ci, (a, b) in enumerate(zip(ra, rb)):
                if a != b:
                    cname = col_names[ci] if ci < len(col_names) else f"col{ci}"
                    cell_diffs.append(
                        {"key": k, "col": cname, "a": a, "b": b}
                    )

    lines = [
        f"# iap 两页签差异（供人工核对）",
        "",
        f"**表**：`{SPREADSHEET_ID}`",
        f"**A**（gid `{GID_A}`）：`{title_a}`",
        f"**B**（gid `{GID_B}`）：`{title_b}`",
        f"**范围**：`{RANGE_}`（前 7 行为 meta，之后为数据）",
        "",
        f"- A 数据行：**{len(da)}**；B 数据行：**{len(db)}**",
        f"- 仅 A 有（B 无此 Id+PkgDesc）：**{len(only_a)}**",
        f"- 仅 B 有（A 无此 Id+PkgDesc）：**{len(only_b)}**",
        f"- 同键同重复次数下单元格不同：**{len(cell_diffs)}** 处",
        "",
        "---",
        "",
        "## 一、仅 A 有",
        "",
        "| Id | PkgDesc |",
        "|------|---------|",
    ]
    for bid, desc in only_a:
        lines.append(f"| {bid} | {desc.replace('|', '\\|')} |")
    lines += ["", "---", "", "## 二、仅 B 有", "", "| Id | PkgDesc |", "|------|---------|"]
    for bid, desc in only_b:
        lines.append(f"| {bid} | {desc.replace('|', '\\|')} |")

    esc_a = title_a.replace("|", "\\|")
    esc_b = title_b.replace("|", "\\|")
    lines += [
        "",
        "---",
        "",
        "## 三、两边都有但单元格不同",
        "",
        f"| Id | PkgDesc | 列 | A：`{esc_a}` | B：`{esc_b}` |",
        "|----|---------|-----|----------------|----------------|",
    ]
    for d in cell_diffs:
        bid, desc = d["key"]
        ae = d["a"].replace("|", "\\|")[:400]
        be = d["b"].replace("|", "\\|")[:400]
        if len(d["a"]) > 400:
            ae += "…"
        if len(d["b"]) > 400:
            be += "…"
        lines.append(
            f"| {bid} | {desc.replace('|', '\\|')} | {d['col']} | {ae} | {be} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 四、说明",
        "",
        "- 配对键为 **(Id, PkgDesc)**；同一键在 A/B 出现次数不一致时，**不会**进入第三节。",
        "- 若需按行号对齐对比，需另写脚本。",
        "",
    ]

    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
