# -*- coding: utf-8 -*-
"""只扫每张表「第一个可见页签」，列出命中科技节卡包 ID 的条目 ID（A_INT_id）。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".cursor" / "skills" / "google-workspace-cli"))
import gsheet_query as gq  # noqa: E402

TECH_IDS = (111110002, 111110003, 111110004, 111110005, 111110006)
ID_RE = re.compile(r'"id":(11111000[2-6])(?=[,}\]])')


def first_visible_tab_title(meta: dict) -> str:
    for s in meta.get("sheets", []):
        p = s.get("properties", {})
        if not p.get("hidden"):
            return p.get("title", "")
    return ""


def detect_id_col(header_row: list) -> int:
    if not header_row:
        return 0
    if str(header_row[0]).strip() == "p2_title":
        return 1
    try:
        return header_row.index("A_INT_id")
    except ValueError:
        return 1 if len(header_row) > 1 else 0


def scan_one_table(table_key: str, label: str) -> dict:
    sid, _ = gq.resolve_table(table_key)
    if not sid:
        return {"label": label, "error": "cannot resolve"}
    meta = gq.gws_sheet_meta(sid)
    tab = first_visible_tab_title(meta)
    rows = gq.gws_values(sid, f"'{tab}'!A:AZ")
    if not rows:
        return {"label": label, "tab": tab, "error": "empty"}
    header = rows[0]
    id_col = detect_id_col(header)
    # id -> set of entry ids (as str)
    hits: dict[int, set[str]] = {i: set() for i in TECH_IDS}
    for row_i, row in enumerate(rows[1:], start=2):
        line = "\t".join(str(c) for c in row)
        found_ids = {int(m.group(1)) for m in ID_RE.finditer(line)}
        if not found_ids:
            continue
        try:
            eid = str(row[id_col]).strip() if id_col < len(row) else ""
        except IndexError:
            eid = ""
        for iid in found_ids:
            if iid in hits and eid:
                hits[iid].add(eid)
    return {
        "label": label,
        "sid": sid,
        "tab": tab,
        "id_col": id_col,
        "hits": hits,
    }


def main() -> None:
    blocks = [
        scan_one_table("2115_dev", "2115"),
        scan_one_table("2013_dev", "2013"),
    ]
    names = {
        111110002: "科技节·白",
        111110003: "科技节·绿",
        111110004: "科技节·蓝",
        111110005: "科技节·紫",
        111110006: "科技节·橙",
    }
    for b in blocks:
        print(f"\n## {b['label']}\n")
        if b.get("error"):
            print(f"- 错误: {b['error']}\n")
            continue
        print(f"- **第一个可见页签**: `{b['tab']}`")
        print(f"- **条目 ID 列**: col[{b['id_col']}]（表头 `A_INT_id` 或 P2 偏移）\n")
        for iid in TECH_IDS:
            s = b["hits"][iid]
            if not s:
                print(f"- **`{iid}`**（{names[iid]}）: 无命中\n")
                continue
            ids_sorted = sorted(s, key=lambda x: (len(x), x))
            # 数字 ID 尽量按数值排
            try:
                ids_sorted = sorted(s, key=lambda x: int(x))
            except ValueError:
                pass
            preview = ", ".join(ids_sorted[:30])
            more = f" … 共 **{len(s)}** 条" if len(s) > 30 else f"（共 **{len(s)}** 条）"
            print(f"- **`{iid}`**（{names[iid]}）: {preview}{more}\n")


if __name__ == "__main__":
    main()
