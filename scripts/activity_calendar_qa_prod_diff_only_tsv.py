# -*- coding: utf-8 -*-
"""
Build *_Nrows_only.tsv: QA 相对 线上 multiset 多出来的数据行（贴到 activity_calendar_x2（线上）数据区、不覆盖 meta）。

对比：QA gid=681415886 vs 线上 gid=1459407900（2111_x2_ActivityCalendar）。

输入：_export_activity_calendar_tabs_tsv.py 生成的 activity_calendar_x2_QA_only.tsv、
      activity_calendar_x2_online_only.tsv

输出：activity_calendar_x2qa_{N}rows_only.tsv
"""
import csv
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
QA_ONLY = BASE / "activity_calendar_x2_QA_only.tsv"
ONLINE_ONLY = BASE / "activity_calendar_x2_online_only.tsv"
OUT_PREFIX = "activity_calendar_x2qa"


def _load_rows(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f, delimiter="\t"))


def _write_tsv(path: Path, rows: list[list[str]]) -> None:
    maxc = max((len(r) for r in rows), default=0)

    def pad(r: list[str]) -> list[str]:
        return list(r) + [""] * (maxc - len(r))

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        for r in rows:
            w.writerow(pad(r))


def main() -> None:
    qa = _load_rows(QA_ONLY)
    online = _load_rows(ONLINE_ONLY)
    cq = Counter(map(tuple, qa))
    co = Counter(map(tuple, online))
    diff = cq - co
    # 稳定顺序：按整行 tuple 排序
    out_rows: list[list[str]] = []
    for t in sorted(diff.keys(), key=lambda x: x):
        out_rows.extend([list(t)] * diff[t])
    n = len(out_rows)
    out_path = BASE / f"{OUT_PREFIX}_{n}rows_only.tsv"
    _write_tsv(out_path, out_rows)
    print("QA rows", len(qa), "线上 rows", len(online))
    print("multiset QA - 线上:", n, "rows ->", out_path)
    online_extra = sum((co - cq).values())
    if online_extra:
        print("note: 线上 - QA has", online_extra, "rows (仅线上多出的行，未写入此文件)")


if __name__ == "__main__":
    main()
