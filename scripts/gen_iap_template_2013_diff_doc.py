# -*- coding: utf-8 -*-
"""生成 iap_template_x2（qa） vs iap_template_x2master 差异说明 Markdown（2013_x2_iap_template）。"""
import json
import os
import subprocess
import time
from collections import defaultdict

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "iap_template_x2master_sync_from_qa.md")
os.environ["GOOGLE_WORKSPACE_PROJECT_ID"] = "calm-repeater-489707-n1"
SPREADSHEET_ID = "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E"
# 表宽 45 列（至 AS），行数按页签上限多留余量
RANGE_ = "A1:AS7000"
SHEET_QA = "iap_template_x2（qa）"
SHEET_MASTER = "iap_template_x2master"
GID_QA = 1938706798
GID_MASTER = 1378862323
HEADER_ROWS = 7


def gws_values_get(range_a1, retries=3):
    params = json.dumps(
        {"spreadsheetId": SPREADSHEET_ID, "range": range_a1},
        separators=(",", ":"),
    )
    args = ["sheets", "spreadsheets", "values", "get", "--params", params]
    stdin_payload = json.dumps({"args": args, "json": None}, ensure_ascii=False)
    root = os.path.dirname(__file__)
    js = os.path.join(root, "gws_stdin.js")
    last_err = None
    for attempt in range(retries):
        r = subprocess.run(
            ["node", js],
            input=stdin_payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        if r.returncode == 0:
            return json.loads(r.stdout)
        last_err = r.stderr or r.stdout
        time.sleep(2 + attempt * 2)
    raise RuntimeError(last_err)


def norm_row(r):
    return [("" if c is None else str(c).strip()) for c in r]


def col_id_pkgdesc(fwcli_row):
    names = norm_row(fwcli_row)
    id_i = names.index("Id") if "Id" in names else 1
    pkg_i = names.index("PkgDesc") if "PkgDesc" in names else 8
    return id_i, pkg_i


def main():
    qa_range = f"'{SHEET_QA}'!{RANGE_}"
    master_range = f"{SHEET_MASTER}!{RANGE_}"
    qa = gws_values_get(qa_range)
    master = gws_values_get(master_range)
    qa_vals = qa.get("values") or []
    m_vals = master.get("values") or []

    fwcli = qa_vals[1] if len(qa_vals) > 1 else []
    id_i, pkg_i = col_id_pkgdesc(fwcli)
    col_names = norm_row(fwcli)
    max_cols = max(len(col_names), 45)

    def prep_data(rows):
        out = []
        for i, row in enumerate(rows):
            if i < HEADER_ROWS:
                continue
            nr = norm_row(row)
            while len(nr) < max_cols:
                nr.append("")
            out.append(nr)
        return out

    qa_d = prep_data(qa_vals)
    m_d = prep_data(m_vals)

    def key_row(r):
        bid = r[id_i] if len(r) > id_i else ""
        desc = r[pkg_i] if len(r) > pkg_i else ""
        return (bid, desc)

    qa_by = defaultdict(list)
    for idx, r in enumerate(qa_d):
        qa_by[key_row(r)].append((idx, r))
    m_by = defaultdict(list)
    for idx, r in enumerate(m_d):
        m_by[key_row(r)].append((idx, r))

    all_keys = sorted(set(qa_by) | set(m_by), key=lambda k: (k[0], k[1]))
    only_qa = [k for k in all_keys if k not in m_by]
    cell_diffs = []

    for k in all_keys:
        ql = qa_by.get(k, [])
        ml = m_by.get(k, [])
        if not ql or not ml or len(ql) != len(ml):
            continue
        for (_, qr), (_, mr) in zip(ql, ml):
            for ci, (a, b) in enumerate(zip(qr, mr)):
                if a != b:
                    cname = col_names[ci] if ci < len(col_names) else f"col{ci}"
                    cell_diffs.append({"key": k, "col_name": cname, "qa": a, "master": b})

    lines = []
    lines.append("# iap_template：以 QA 为准同步到 master 说明")
    lines.append("")
    lines.append("**文档表**：`2013_x2_iap_template`  \n")
    lines.append(f"**链接**：https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    lines.append("")
    lines.append("| 页签 | gid | 说明 |")
    lines.append("|------|-----|------|")
    lines.append(f"| `{SHEET_QA}` | {GID_QA} | **为准（源）** |")
    lines.append(f"| `{SHEET_MASTER}` | {GID_MASTER} | **待对齐（目标）** |")
    lines.append("")
    lines.append(f"- QA 数据行数：**{len(qa_d)}**；master 数据行数：**{len(m_d)}**")
    lines.append(f"- 仅 QA 有、需整行复制到 master：**{len(only_qa)}** 行")
    lines.append(f"- 两边都有但单元格不同：**{len(cell_diffs)}** 处")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## 一、仅 QA 有（整行从 `{SHEET_QA}` 复制到 `{SHEET_MASTER}`）")
    lines.append("")
    lines.append(
        "在 QA 页签中按 `Id` 搜索，选中**整行**（含所有列），复制后粘贴到 master 表数据区；勿覆盖前 7 行 meta。"
    )
    lines.append("")
    lines.append("| # | Id | PkgDesc（QA） |")
    lines.append("|---|-----|---------------|")
    for i, (bid, desc) in enumerate(only_qa, 1):
        desc_esc = desc.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i} | {bid} | {desc_esc} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 二、两边都有：把 master 改成与 QA 一致")
    lines.append("")
    lines.append("| Id | PkgDesc | 列（fwcli） | master 当前（应改掉） | QA（为准，覆盖到 master） |")
    lines.append("|----|---------|-------------|----------------------|---------------------------|")
    for d in cell_diffs:
        bid, desc = d["key"]
        desc_esc = desc.replace("|", "\\|")
        qa_esc = d["qa"].replace("|", "\\|")[:500]
        m_esc = d["master"].replace("|", "\\|")[:500]
        if len(d["qa"]) > 500:
            qa_esc += "…"
        if len(d["master"]) > 500:
            m_esc += "…"
        lines.append(
            f"| {bid} | {desc_esc} | {d['col_name']} | {m_esc} | {qa_esc} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 三、操作检查清单")
    lines.append("")
    lines.append("1. 完成「一」中所有行的整行复制。")
    lines.append("2. 对「二」中每一行，在 master 打开对应 `Id`，将所列列改为 QA 单元格内容（或直接复制 QA 该格）。")
    lines.append("3. 保存后如需落 git，再按你们 `fwcli`/导表流程导出 TSV。")
    lines.append("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
