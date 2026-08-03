# -*- coding: utf-8 -*-
"""tsv 批量删行（字节级安全版）—— 下线功能 / 清活动配置时用。

跟 tsv_edit.py delrow 的区别：
- **多行 cell 安全**：用 csv.reader 的 line_num 算出每条「逻辑行」占用的物理行区间，
  整段剔除；tsv_edit.py delrow 按物理行首字段匹配，遇到跨行 cell 只会删掉第一行。
- **不重写无关字节**：只对原始字节按行号剔除，绝不用 csv.writer 回写
  （writer 会把 tsv 里的裸引号重新转义，污染无关行——Text__Text.tsv 土耳其语实测）。
- 支持按 col0 的 ID 删、按 key 前缀删、按任意列的值删；全部先断言命中数。

用法：
  # 按 ID（col0）删，断言恰好命中 8 行
  python tsv_delrows.py --repo C:\\x3\\gdconfig-wt-x --file tsv/Pack__Pack.tsv \\
      --ids 211101-211108 --expect 8 --dry-run

  # 按某列的值删（如 Reward 表按 col1 的 RewardID 组）
  python tsv_delrows.py --file tsv/Reward__Reward.tsv --col 1 \\
      --ids 8202101-8202104,211101-211108 --expect 30

  # 按 key 前缀删 i18n 行
  python tsv_delrows.py --file tsv/i18n/Text__Text.tsv \\
      --prefix TXT_ActvFlashSale_,Text_ErrCodeActivityFlashSale --expect 15

  # 删全部数据行（保留前 N 行表头）——注意导表禁止空表(X3NEW-20)，
  # 整表下线请直接 git rm 该 tsv
  python tsv_delrows.py --file tsv/Foo__Foo.tsv --all-data --header 6 --expect 12

约定：命中数 != --expect 直接退出不写盘；--dry-run 只打印。
"""
from __future__ import annotations
import argparse
import csv
import sys
from pathlib import Path

DEFAULT_REPO = Path(r"C:\x3\gdconfig")


def parse_ids(spec: str) -> set[str]:
    """支持 '1,2,5-8' 形式；范围仅对纯数字生效。"""
    out: set[str] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part and all(s.strip().isdigit() for s in part.split("-", 1)):
            a, b = (int(s) for s in part.split("-", 1))
            out.update(str(i) for i in range(a, b + 1))
        else:
            out.add(part)
    return out


def spans(path: Path):
    """yield (row, first_physical_line, last_physical_line)，行号 1-indexed。"""
    with open(path, encoding="utf-8", newline="") as f:
        rdr = csv.reader(f, delimiter="\t")
        prev = 0
        for row in rdr:
            end = rdr.line_num
            yield row, prev + 1, end
            prev = end


def main() -> int:
    ap = argparse.ArgumentParser(description="tsv 批量删行（多行 cell 安全 + 字节级不污染）")
    ap.add_argument("--repo", default=str(DEFAULT_REPO), help="仓库/worktree 根目录")
    ap.add_argument("--file", required=True, help="相对 repo 的 tsv 路径")
    ap.add_argument("--ids", help="要删的值，逗号分隔，支持数字范围 a-b")
    ap.add_argument("--col", type=int, default=0, help="--ids 匹配哪一列（默认 0）")
    ap.add_argument("--prefix", help="按首列 key 前缀删，逗号分隔多个前缀")
    ap.add_argument("--all-data", action="store_true", help="删所有数据行（配 --header）")
    ap.add_argument("--header", type=int, default=6, help="表头逻辑行数，默认 6")
    ap.add_argument("--expect", type=int, required=True, help="预期命中逻辑行数（断言）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if sum(bool(x) for x in (args.ids, args.prefix, args.all_data)) != 1:
        return int(bool(sys.stderr.write("[错误] --ids / --prefix / --all-data 三选一\n"))) or 2

    path = Path(args.file)
    if not path.is_absolute():
        path = Path(args.repo) / args.file
    if not path.exists():
        sys.exit(f"[错误] 文件不存在: {path}")

    ids = parse_ids(args.ids) if args.ids else set()
    prefixes = tuple(p.strip() for p in args.prefix.split(",")) if args.prefix else ()

    kill: set[int] = set()
    hits: list[str] = []
    for idx, (row, a, b) in enumerate(spans(path)):
        if not row:
            continue
        if args.all_data:
            match = idx >= args.header
        elif prefixes:
            match = row[0].startswith(prefixes)
        else:
            match = len(row) > args.col and row[args.col] in ids
        if match:
            hits.append(row[0])
            kill.update(range(a, b + 1))

    if len(hits) != args.expect:
        sys.exit(f"[断言失败] 命中 {len(hits)} 逻辑行 != 预期 {args.expect}（未写盘）\n  命中首列: {hits[:20]}")

    for h in hits[:40]:
        print(f"  - {h}")
    if len(hits) > 40:
        print(f"  ... 共 {len(hits)} 行")
    print(f"[{'dry-run' if args.dry_run else 'OK'}] {path.name}: 删 {len(hits)} 逻辑行 / {len(kill)} 物理行")

    if not args.dry_run:
        raw = path.read_bytes()
        if b"\r" in raw:
            sys.exit("[错误] 文件含 \\r，本脚本只支持 LF 的 tsv（未写盘）")
        lines = raw.split(b"\n")
        path.write_bytes(b"\n".join(l for n, l in enumerate(lines, 1) if n not in kill))
        print("已写盘（LF 保持，其余字节零改动）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
