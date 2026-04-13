# -*- coding: utf-8 -*-
"""将本地 iap_config.tsv 的 J(TimeInfo)、M(IapStatus) 列同步到 Google Sheet（与 fwcli 导出行号对齐）。"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

# 与 scripts/gen_iap_qa_master_diff_doc.py 一致（2011 iap 双页签）
DEFAULT_SPREADSHEET = "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY"
DEFAULT_TABS = "iap_config_x2qa,iap_config_x2master"
DEFAULT_TSV = Path(r"D:\UGit\x2gdconf\fo\config\iap_config.tsv")

IDX_TIME = 9
IDX_IAP = 12
DATA_START_1BASED = 8  # 与 x2 TSV 前 7 行元数据一致

NPM_DIR = os.path.join(os.environ.get("APPDATA", ""), "npm")
RUN_GWS_JS = os.path.join(NPM_DIR, "node_modules", "@googleworkspace", "cli", "run-gws.js")
# Windows CreateProcess 对整条命令行有上限；--json 会整段进 argv，需控制单批体积
MAX_JSON_CHARS = 7000


def run_gws_node(args: list[str], json_body: dict | None) -> tuple[int, str, str]:
    cmd = ["node", RUN_GWS_JS] + args
    if json_body is not None:
        cmd.extend(["--json", json.dumps(json_body, ensure_ascii=False)])
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    return r.returncode, r.stdout or "", r.stderr or ""


def load_jm_columns(tsv_path: Path) -> tuple[list[list[str]], list[list[str]], int, int]:
    lines = tsv_path.read_text(encoding="utf-8").splitlines()
    col_j: list[list[str]] = []
    col_m: list[list[str]] = []
    data_rows = 0
    for i, line in enumerate(lines, start=1):
        if i < DATA_START_1BASED:
            continue
        parts = line.split("\t")
        if len(parts) <= IDX_IAP:
            continue
        if not parts[1].strip().isdigit():
            continue
        col_j.append([parts[IDX_TIME]])
        col_m.append([parts[IDX_IAP]])
        data_rows += 1
    last_row = DATA_START_1BASED - 1 + data_rows
    return col_j, col_m, data_rows, last_row


def _make_body(
    esc: str, r0: int, r1: int, jvals: list[list[str]], mvals: list[list[str]]
) -> dict:
    return {
        "valueInputOption": "RAW",
        "data": [
            {
                "range": f"'{esc}'!J{r0}:J{r1}",
                "majorDimension": "ROWS",
                "values": jvals,
            },
            {
                "range": f"'{esc}'!M{r0}:M{r1}",
                "majorDimension": "ROWS",
                "values": mvals,
            },
        ],
    }


def batch_update_tab(
    spreadsheet_id: str,
    tab: str,
    col_j: list[list[str]],
    col_m: list[list[str]],
    chunk_rows: int,
    dry_run: bool,
) -> None:
    n = len(col_j)
    if n != len(col_m):
        raise SystemExit("internal: J/M row count mismatch")
    esc = tab.replace("'", "''")
    params = json.dumps({"spreadsheetId": spreadsheet_id}, separators=(",", ":"))
    start = 0
    while start < n:
        # 自适应批大小，避免 Windows 命令行超长 (WinError 206)
        max_try = min(chunk_rows, n - start)
        chunk = max_try
        while chunk >= 1:
            end = start + chunk
            r0 = DATA_START_1BASED + start
            r1 = DATA_START_1BASED + end - 1
            body = _make_body(esc, r0, r1, col_j[start:end], col_m[start:end])
            if len(json.dumps(body, ensure_ascii=False)) <= MAX_JSON_CHARS:
                break
            if chunk == 1:
                raise SystemExit(
                    "单行 J/M JSON 仍超过 MAX_JSON_CHARS，请调大限制或改用 API 直传"
                )
            chunk = max(1, chunk // 2)
        end = start + chunk
        r0 = DATA_START_1BASED + start
        r1 = DATA_START_1BASED + end - 1
        body = _make_body(esc, r0, r1, col_j[start:end], col_m[start:end])
        if dry_run:
            print(
                f"[dry-run] {tab} rows {r0}-{r1} ({end - start} rows) "
                f"json_len={len(json.dumps(body, ensure_ascii=False))}"
            )
            start = end
            continue
        for attempt in range(12):
            code, out, err = run_gws_node(
                ["sheets", "spreadsheets", "values", "batchUpdate", "--params", params],
                body,
            )
            if code == 0:
                break
            err_l = (err or "") + (out or "")
            if "429" in err_l or "Quota exceeded" in err_l:
                wait = min(90, 20 + attempt * 15)
                print(f"  [429] wait {wait}s then retry ({attempt + 1}/12) rows {r0}-{r1}")
                time.sleep(wait)
                continue
            raise SystemExit(f"gws batchUpdate failed tab={tab} rows {r0}-{r1}:\n{err}\n{out}")
        else:
            raise SystemExit(f"gws batchUpdate failed after retries tab={tab} rows {r0}-{r1}")
        time.sleep(0.35)
        try:
            meta = json.loads(out)
            total = meta.get("totalUpdatedCells", "?")
            print(f"  OK {tab} J/M rows {r0}-{r1} -> totalUpdatedCells={total}")
        except json.JSONDecodeError:
            print(f"  OK {tab} rows {r0}-{r1} (stdout not json)")
        start = end


def main() -> None:
    os.environ.setdefault("GOOGLE_WORKSPACE_PROJECT_ID", "calm-repeater-489707-n1")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    ap.add_argument("--spreadsheet", default=DEFAULT_SPREADSHEET)
    ap.add_argument("--tabs", default=DEFAULT_TABS, help="comma-separated sheet names")
    ap.add_argument(
        "--chunk-rows",
        type=int,
        default=120,
        help="单批最大行数（过大会触发命令行超长，脚本会自动减半重试）",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not Path(RUN_GWS_JS).is_file():
        raise SystemExit(f"找不到 gws: {RUN_GWS_JS}")

    col_j, col_m, nrows, last_row = load_jm_columns(args.tsv)
    print(f"TSV: {args.tsv}")
    print(f"数据行: {nrows} (sheet 行 {DATA_START_1BASED}-{last_row}), J+M -> spreadsheet {args.spreadsheet}")

    for tab in [t.strip() for t in args.tabs.split(",") if t.strip()]:
        print(f"-- tab: {tab}")
        batch_update_tab(
            args.spreadsheet,
            tab,
            col_j,
            col_m,
            args.chunk_rows,
            args.dry_run,
        )


if __name__ == "__main__":
    main()
