# -*- coding: utf-8 -*-
"""Scan 2115 / 2013 GSheets for tech festival guaranteed pack item IDs."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".cursor" / "skills" / "google-workspace-cli"))
import gsheet_query as gq  # noqa: E402

TECH_IDS = (111110002, 111110003, 111110004, 111110005, 111110006)
# JSON 里道具 id 常见形态，避免匹配到 1111100020 之类
ID_RE = re.compile(
    r'"id":(11111000[2-6])(?=[,}\]])'
)


def scan_spreadsheet(sid: str, label: str) -> dict:
    per_id: dict[int, list[tuple[str, int, str]]] = {i: [] for i in TECH_IDS}
    meta = gq.gws_sheet_meta(sid)
    sheets = meta.get("sheets", [])
    for s in sheets:
        props = s.get("properties", {})
        if props.get("hidden"):
            continue
        tab = props.get("title", "")
        rows = gq.gws_values(sid, f"'{tab}'!A:AZ")
        for row_i, row in enumerate(rows, start=1):
            line = "\t".join(str(c) for c in row)
            for m in ID_RE.finditer(line):
                iid = int(m.group(1))
                if iid in per_id:
                    # 截一段上下文便于定位
                    snip = line[max(0, m.start() - 40) : m.end() + 40]
                    per_id[iid].append((tab, row_i, snip.replace("\t", " ")))
    return {"label": label, "sid": sid, "per_id": per_id}


def main() -> None:
    targets = [
        ("2115_dev", "2115 (activity_task 等同表)"),
        ("2013_dev", "2013 (iap_template 等同表)"),
    ]
    all_out = []
    for key, label in targets:
        sid, _ = gq.resolve_table(key)
        if not sid:
            print(f"[skip] cannot resolve {key}", file=sys.stderr)
            continue
        print(f"[scan] {label} {sid[:24]}...", file=sys.stderr)
        all_out.append(scan_spreadsheet(sid, label))

    print("# 科技节保底卡包 ID 扫描（2115 / 2013）\n")
    print("| 道具 ID | 说明 | 出现次数 | 位置摘要 |")
    print("|---------|------|----------|----------|")
    names = {
        111110002: "科技节·白",
        111110003: "科技节·绿",
        111110004: "科技节·蓝",
        111110005: "科技节·紫",
        111110006: "科技节·橙",
    }
    for iid in TECH_IDS:
        total = 0
        loc_lines = []
        for block in all_out:
            hits = block["per_id"][iid]
            total += len(hits)
            for tab, row_i, snip in hits[:8]:
                loc_lines.append(f"`{block['label']}` / `{tab}` 行{row_i}")
            if len(hits) > 8:
                loc_lines.append(f"`{block['label']}` … 另有 {len(hits) - 8} 处")
        loc = "<br>".join(loc_lines) if loc_lines else "—"
        print(f"| `{iid}` | {names[iid]} | **{total}** | {loc} |")

    print("\n---\n")
    print("## 批量替换建议（复活节对应）\n")
    print("| 科技节 | 复活节 |")
    print("|--------|--------|")
    print("| 111110002 | 111110305 |")
    print("| 111110003 | 111110306 |")
    print("| 111110004 | 111110307 |")
    print("| 111110005 | 111110308 |")
    print("| 111110006 | 111110309 |")


if __name__ == "__main__":
    main()
