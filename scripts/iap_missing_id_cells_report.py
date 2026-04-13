# -*- coding: utf-8 -*-
"""输出缺失 activity Id 在 iap_config 中对应的列（字母）与 fwcli 名。"""
import re
from pathlib import Path

IAP = Path(r"D:\UGit\x2gdconf\fo\config\iap_config.tsv")
ACT = Path(r"D:\UGit\x2gdconf\fo\config\activity_config.tsv")
MISSING = {"21127226", "21127233", "21127240", "21127241", "21127242", "21127243", "21127244"}


def col_letter(n0: int) -> str:
    n = n0 + 1
    s = ""
    while n:
        n, c = divmod(n - 1, 26)
        s = chr(65 + c) + s
    return s


def main():
    al = ACT.read_text(encoding="utf-8", errors="replace").splitlines()
    ds = next(i + 1 for i, l in enumerate(al) if l.split("\t")[0] == "fwcli_name")
    valid = set()
    for l in al[ds:]:
        p = l.split("\t")
        if len(p) > 1 and p[1].strip().isdigit():
            valid.add(p[1].strip())

    lines = IAP.read_text(encoding="utf-8", errors="replace").splitlines()
    p2 = lines[0].split("\t")
    fw = lines[1].split("\t")
    ds_i = next(i + 1 for i, l in enumerate(lines) if l.split("\t")[0] == "fwcli_name")

    # (missing_id, json_field) -> list of (iap_id, file_line, col_idx)
    hits: dict[tuple[str, str], list[tuple[str, int, int]]] = {}

    rules = [
        (r'"actv_id"\s*:\s*(\d+)', "actv_id", 9),
        (r'"actv_base_id"\s*:\s*(\d+)', "actv_base_id", 9),
        (
            r'"typ"\s*:\s*"recharge_actv"\s*,\s*"id"\s*:\s*(\d+)',
            "recharge_actv.id",
            12,
        ),
    ]

    for li, l in enumerate(lines[ds_i:], start=ds_i + 1):
        parts = l.split("\t")
        iapid = parts[1].strip() if len(parts) > 1 else "?"
        for pat, fld, col_idx in rules:
            for m in re.finditer(pat, l):
                rid = m.group(1)
                if rid in MISSING and rid not in valid:
                    hits.setdefault((rid, fld), []).append((iapid, li, col_idx))

    print("缺失的 activity_config Id → Google Sheet 列（按当前 TSV 列序，首列 A=p2_title）\n")
    print("| 缺失活动Id | 列字母 | p2_title 字段 | fwcli 列名 | JSON 键 | 出现次数 | 示例（iap Id @ 文件行）|")
    print("|------------|--------|---------------|------------|---------|----------|-------------------------|")

    for aid in sorted(MISSING, key=int):
        for fld, cidx in [
            ("actv_id", 9),
            ("actv_base_id", 9),
            ("recharge_actv.id", 12),
        ]:
            key = (aid, fld)
            if key not in hits:
                continue
            lst = hits[key]
            ex = ", ".join(f"{x[0]}@{x[1]}" for x in lst[:3])
            if len(lst) > 3:
                ex += f", …共{len(lst)}处"
            print(
                f"| {aid} | {col_letter(cidx)} | {p2[cidx]} | {fw[cidx]} | {fld} | {len(lst)} | {ex} |"
            )


if __name__ == "__main__":
    main()
