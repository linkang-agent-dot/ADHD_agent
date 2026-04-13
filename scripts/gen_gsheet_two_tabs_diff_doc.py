# -*- coding: utf-8 -*-
"""
对比同一 Spreadsheet 下两个页签（按 gid 或页签名），生成 UTF-8 Markdown。
默认：按 (Id列, PkgDesc列) 对齐，Id 列名取 fwcli_name 行中的 Id；若无则退化为整表逐行 diff。
"""
import argparse
import json
import os
import subprocess
import time
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GWS_STDIN = os.path.join(SCRIPT_DIR, "gws_stdin.js")


def gws_call(args_list, json_body=None):
    stdin_payload = json.dumps(
        {"args": args_list, "json": json_body}, ensure_ascii=False
    )
    for attempt in range(4):
        r = subprocess.run(
            ["node", GWS_STDIN],
            input=stdin_payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if r.returncode == 0:
            return json.loads(r.stdout)
        err = r.stderr or r.stdout
        if attempt < 3:
            time.sleep(2 + attempt * 2)
    raise RuntimeError(err)


def sheet_titles_by_id(spreadsheet_id):
    params = json.dumps(
        {
            "spreadsheetId": spreadsheet_id,
            "fields": "sheets.properties(sheetId,title)",
        },
        separators=(",", ":"),
    )
    data = gws_call(
        ["sheets", "spreadsheets", "get", "--params", params],
    )
    out = {}
    for s in data.get("sheets") or []:
        p = s.get("properties") or {}
        sid = p.get("sheetId")
        title = p.get("title")
        if sid is not None and title:
            out[int(sid)] = title
    return out


def values_get(spreadsheet_id, range_a1):
    params = json.dumps(
        {"spreadsheetId": spreadsheet_id, "range": range_a1},
        separators=(",", ":"),
    )
    return gws_call(
        ["sheets", "spreadsheets", "values", "get", "--params", params],
    )


def norm_row(r):
    return [("" if c is None else str(c).strip()) for c in r]


def find_fwcli_name_row(rows):
    for i, row in enumerate(rows[:50]):
        nr = norm_row(row)
        if nr and nr[0] == "fwcli_name":
            return i, nr
    return None, None


def find_id_col(fwcli_row):
    for j, name in enumerate(fwcli_row):
        if name.strip().lower() == "id":
            return j
    return 1 if len(fwcli_row) > 1 else 0


def max_cols(rows):
    return max((len(r) for r in rows), default=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spreadsheet-id", required=True)
    parser.add_argument("--gid-a", type=int, required=True, help="页签 A（作为对比基准之一）")
    parser.add_argument("--gid-b", type=int, required=True)
    parser.add_argument(
        "--label-a",
        default="页签A",
        help="文档中对 gid-a 的称呼",
    )
    parser.add_argument(
        "--label-b",
        default="页签B",
        help="文档中对 gid-b 的称呼",
    )
    parser.add_argument(
        "--prefer-b",
        action="store_true",
        help="文档第二节写「B 为准，A 改成 B」；默认 A 为准",
    )
    parser.add_argument(
        "--range",
        default="A1:AZ8000",
        help="读取范围",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="输出 .md 路径",
    )
    parser.add_argument(
        "--second-key-0based",
        type=int,
        default=None,
        help="对齐第二键列的 0-based 列号（如 activity_calendar 用 3=ActvComment）；不设则默认第 3 列",
    )
    args = parser.parse_args()
    os.environ["GOOGLE_WORKSPACE_PROJECT_ID"] = "calm-repeater-489707-n1"

    sid = args.spreadsheet_id
    by_gid = sheet_titles_by_id(sid)
    title_a = by_gid.get(args.gid_a)
    title_b = by_gid.get(args.gid_b)
    if not title_a or not title_b:
        raise SystemExit(
            f"找不到 gid：{args.gid_a} -> {title_a!r}, {args.gid_b} -> {title_b!r}"
        )

    rng = args.range
    va = values_get(sid, f"{title_a}!{rng}")
    vb = values_get(sid, f"{title_b}!{rng}")
    rows_a = va.get("values") or []
    rows_b = vb.get("values") or []

    idx_fw_a, fw_a = find_fwcli_name_row(rows_a)
    idx_fw_b, fw_b = find_fwcli_name_row(rows_b)
    data_start_a = (idx_fw_a + 1) if idx_fw_a is not None else 1
    data_start_b = (idx_fw_b + 1) if idx_fw_b is not None else 1

    col_names_a = fw_a if fw_a else norm_row(rows_a[0]) if rows_a else []
    col_names_b = fw_b if fw_b else norm_row(rows_b[0]) if rows_b else []

    id_col_a = find_id_col(col_names_a) if fw_a else 1
    id_col_b = find_id_col(col_names_b) if fw_b else 1
    if args.second_key_0based is not None:
        desc_col_a = desc_col_b = args.second_key_0based
    else:
        desc_col_a = 2 if len(col_names_a) > 2 else 1
        desc_col_b = 2 if len(col_names_b) > 2 else 1

    mc = max(max_cols(rows_a), max_cols(rows_b), len(col_names_a), len(col_names_b))

    def data_rows(rows, start, id_c, desc_c):
        out = []
        for i in range(start, len(rows)):
            nr = norm_row(rows[i])
            while len(nr) < mc:
                nr.append("")
            bid = nr[id_c] if id_c < len(nr) else ""
            desc = nr[desc_c] if desc_c < len(nr) else ""
            out.append((nr, (bid, desc)))
        return out

    da = data_rows(rows_a, data_start_a, id_col_a, desc_col_a)
    db = data_rows(rows_b, data_start_b, id_col_b, desc_col_b)

    by_key_a = defaultdict(list)
    for nr, k in da:
        by_key_a[k].append(nr)
    by_key_b = defaultdict(list)
    for nr, k in db:
        by_key_b[k].append(nr)

    all_keys = sorted(set(by_key_a) | set(by_key_b), key=lambda x: (x[0], x[1]))

    only_a = [k for k in all_keys if k in by_key_a and k not in by_key_b]
    only_b = [k for k in all_keys if k in by_key_b and k not in by_key_a]

    cell_diffs = []
    for k in all_keys:
        la = by_key_a.get(k, [])
        lb = by_key_b.get(k, [])
        if not la or not lb or len(la) != len(lb):
            continue
        for ra, rb in zip(la, lb):
            ref_names = col_names_a if len(col_names_a) >= len(col_names_b) else col_names_b
            for ci in range(max(len(ra), len(rb))):
                a = ra[ci] if ci < len(ra) else ""
                b = rb[ci] if ci < len(rb) else ""
                if a != b:
                    cname = ref_names[ci] if ci < len(ref_names) else f"col{ci}"
                    cell_diffs.append(
                        {"key": k, "col_name": cname, "a": a, "b": b}
                    )

    src_label = args.label_b if args.prefer_b else args.label_a
    tgt_label = args.label_a if args.prefer_b else args.label_b
    src_title = title_b if args.prefer_b else title_a
    tgt_title = title_a if args.prefer_b else title_b
    only_src = only_b if args.prefer_b else only_a
    only_tgt = only_a if args.prefer_b else only_b

    lines = []
    lines.append(f"# 页签对比说明（{src_label} 为准 → 同步到 {tgt_label}）")
    lines.append("")
    lines.append(f"**表格**：https://docs.google.com/spreadsheets/d/{sid}/edit")
    lines.append("")
    lines.append("| 页签名 | gid | 角色 |")
    lines.append("|--------|-----|------|")
    lines.append(f"| `{title_a}` | {args.gid_a} | {args.label_a} |")
    lines.append(f"| `{title_b}` | {args.gid_b} | {args.label_b} |")
    lines.append("")
    lines.append(
        f"- **为准（源）**：`{src_title}`（{src_label}）"
    )
    lines.append(
        f"- **待对齐（目标）**：`{tgt_title}`（{tgt_label}）"
    )
    lines.append(f"- {args.label_a} 数据行数：**{len(da)}**；{args.label_b} 数据行数：**{len(db)}**")
    lines.append(f"- 仅 {src_label} 有、需整行复制到 {tgt_label}：**{len(only_src)}** 行")
    lines.append(f"- 仅 {tgt_label} 有、{src_label} 无：**{len(only_tgt)}** 行")
    lines.append(f"- 两边同 Key 但单元格不同：**{len(cell_diffs)}** 处")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        f"## 一、仅 {src_label} 有（整行从 `{src_title}` 复制到 `{tgt_title}`）"
    )
    lines.append("")
    lines.append(
        f"在 **{src_label}** 页签按 `Id` 搜索，选中整行复制到 **{tgt_label}**；勿覆盖 meta 行。"
    )
    lines.append("")
    lines.append("| # | Id | 描述列（PkgDesc/第二列） |")
    lines.append("|---|-----|--------------------------|")
    for i, (bid, desc) in enumerate(only_src, 1):
        d = desc.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i} | {bid} | {d} |")
    if not only_src:
        lines.append("| — | — | 无 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## 二、仅 {tgt_label} 有（{src_label} 无，是否删除由你决定）")
    lines.append("")
    lines.append("| # | Id | 描述列 |")
    lines.append("|---|-----|--------|")
    for i, (bid, desc) in enumerate(only_tgt, 1):
        d = desc.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i} | {bid} | {d} |")
    if not only_tgt:
        lines.append("| — | — | 无 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        f"## 三、同 Key 不同单元格（{tgt_label} 应改成与 {src_label} 一致）"
    )
    lines.append("")
    lines.append(
        f"| Id | 描述 | 列 | {tgt_label}（当前） | {src_label}（为准） |"
    )
    lines.append("|----|------|-----|-------------------|-------------------|")
    for d in cell_diffs:
        bid, desc = d["key"]
        desc_esc = desc.replace("|", "\\|")
        col = d["col_name"].replace("|", "\\|")
        # 当 prefer_b：src=B tgt=A，cell diff 里 a 来自 sheet A 第一参数... 
        # 我们存的 a 总是 title_a 的值，b 总是 title_b 的值
        val_a = d["a"].replace("|", "\\|")
        val_b = d["b"].replace("|", "\\|")
        if len(val_a) > 400:
            val_a = val_a[:400] + "…"
        if len(val_b) > 400:
            val_b = val_b[:400] + "…"
        if args.prefer_b:
            tgt_val, src_val = val_a, val_b
        else:
            tgt_val, src_val = val_b, val_a
        lines.append(
            f"| {bid} | {desc_esc} | {col} | {tgt_val} | {src_val} |"
        )
    if not cell_diffs:
        lines.append("| — | — | — | — | 无 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 四、说明")
    lines.append("")
    lines.append(
        f"- 对齐 Key：`fwcli_name` 行中 **Id** 列 + 第 **{desc_col_a + 1}** 列（A=1）作为描述；若表结构特殊请人工核对。"
    )
    lines.append(f"- 读取范围：`{rng}`；列过多可改脚本 `--range`。")
    lines.append("")

    out_path = os.path.abspath(args.output)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
