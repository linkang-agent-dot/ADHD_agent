# -*- coding: utf-8 -*-
"""X3 配置 tsv 安全编辑器（导表已迁 tsv，直接改 tsv 不碰 xlsx）。

用法:
  # 改单元格(可多行同改)，改前断言旧值，命中数必须等于id数
  python tsv_edit.py set  --file tsv/Pack__ChainPack.tsv --id 647 --col 2 --old 1 --new 0
  python tsv_edit.py set  --file tsv/Pack__Pack.tsv --id 210917,210918,210919 --col 12 --old 1 --new 0

  # 从管道列表(a|b|c)里移除若干 ID，可一次处理多列
  python tsv_edit.py remove --file tsv/ActvOnline__ActvOnline.tsv --id 100595 --cols 49,50 --ids 210917,210918,210919

  # 只看不写
  python tsv_edit.py set ... --dry-run
  # 打印某行全字段(带索引)，定位列号用
  python tsv_edit.py show --file tsv/Pack__Pack.tsv --id 210917 [--max 32]

约束:
  - 默认 repo = C:\\x3\\gdconfig，--file 相对该目录解析
  - 保 LF（Windows 下 newline='' 写，不被翻成 CRLF）
  - **绝不修改 xlsx**：tsv 是导表唯一数据源，改 xlsx 反而会被重生成覆盖
  - 任何断言失败立即退出、不写盘
"""
from __future__ import annotations
import argparse, sys, os
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEFAULT_REPO = Path(r"C:\x3\gdconfig")


def resolve(repo: Path, file: str) -> Path:
    p = Path(file)
    if not p.is_absolute():
        p = repo / file
    if not p.exists():
        sys.exit(f"[错误] 文件不存在: {p}")
    return p


def load(path: Path) -> list[str]:
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().split("\n")


def save(path: Path, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))


def cmd_show(args, repo):
    path = resolve(repo, args.file)
    ids = set(args.id.split(",")) if args.id else None
    for ln in load(path):
        f = ln.split("\t")
        if f and (ids is None or f[0] in ids):
            print(" ".join(f"[{i}]{v!r}" for i, v in enumerate(f[: args.max])))


def cmd_set(args, repo):
    path = resolve(repo, args.file)
    ids = args.id.split(",")
    lines = load(path)
    changed, hit_ids = [], set()
    for i, ln in enumerate(lines):
        f = ln.split("\t")
        if f and f[0] in ids:
            if args.col >= len(f):
                sys.exit(f"[错误] 行{f[0]} 只有{len(f)}字段，无 col {args.col}")
            cur = f[args.col]
            if cur != args.old:
                sys.exit(f"[断言失败] 行{f[0]} field[{args.col}] 期望旧值{args.old!r} 实际{cur!r}（未写盘）")
            hit_ids.add(f[0])
            changed.append((f[0], args.col, cur, args.new))
            f[args.col] = args.new
            lines[i] = "\t".join(f)
    missing = set(ids) - hit_ids
    if missing:
        sys.exit(f"[断言失败] 这些ID没找到: {sorted(missing)}（未写盘）")
    for rid, col, old, new in changed:
        print(f"  行{rid} field[{col}] {old} -> {new}")
    if args.dry_run:
        print(f"[dry-run] 命中{len(changed)}处，未写盘")
        return
    save(path, lines)
    print(f"[OK] {path.name} 改了{len(changed)}处")


def cmd_remove(args, repo):
    path = resolve(repo, args.file)
    cols = [int(c) for c in args.cols.split(",")]
    rm = set(args.ids.split(","))
    rid = args.id
    lines = load(path)
    hit = 0
    summary = []
    for i, ln in enumerate(lines):
        f = ln.split("\t")
        if f and f[0] == rid:
            for col in cols:
                if col >= len(f):
                    sys.exit(f"[错误] 行{rid} 无 col {col}")
                parts = f[col].split("|")
                kept = [p for p in parts if p not in rm]
                removed = len(parts) - len(kept)
                if removed != len(rm):
                    sys.exit(f"[断言失败] 行{rid} field[{col}] 实删{removed} 期望{len(rm)}（部分ID不在列表里，未写盘）")
                f[col] = "|".join(kept)
                summary.append((col, removed))
            lines[i] = "\t".join(f)
            hit += 1
    if hit != 1:
        sys.exit(f"[断言失败] 行{rid} 命中{hit} 期望1（未写盘）")
    for col, removed in summary:
        print(f"  行{rid} field[{col}] 移除{removed}个ID")
    if args.dry_run:
        print("[dry-run] 未写盘")
        return
    save(path, lines)
    print(f"[OK] {path.name} 行{rid} 已移除")


def cmd_add(args, repo):
    path = resolve(repo, args.file)
    cols = [int(c) for c in args.cols.split(",")]
    ins = args.ids.split(",")
    rid, after = args.id, args.after
    lines = load(path)
    hit = 0
    summary = []
    for i, ln in enumerate(lines):
        f = ln.split("\t")
        if f and f[0] == rid:
            for col in cols:
                if col >= len(f):
                    sys.exit(f"[错误] 行{rid} 无 col {col}")
                parts = f[col].split("|")
                for x in ins:
                    if x in parts:
                        sys.exit(f"[断言失败] 行{rid} field[{col}] 已含 {x}，勿重复加（未写盘）")
                if after not in parts:
                    sys.exit(f"[断言失败] 行{rid} field[{col}] 找不到锚点 {after}（未写盘）")
                pos = parts.index(after) + 1
                parts[pos:pos] = ins
                f[col] = "|".join(parts)
                summary.append((col, after))
            lines[i] = "\t".join(f)
            hit += 1
    if hit != 1:
        sys.exit(f"[断言失败] 行{rid} 命中{hit} 期望1（未写盘）")
    for col, after in summary:
        print(f"  行{rid} field[{col}] 在 {after} 后插入 {ins}")
    if args.dry_run:
        print("[dry-run] 未写盘")
        return
    save(path, lines)
    print(f"[OK] {path.name} 行{rid} 已插入")


def main():
    ap = argparse.ArgumentParser(description="X3 tsv 安全编辑器")
    ap.add_argument("--repo", default=str(DEFAULT_REPO))
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("show", help="打印行全字段带索引")
    s.add_argument("--file", required=True); s.add_argument("--id", default=None)
    s.add_argument("--max", type=int, default=32)

    s = sub.add_parser("set", help="改单元格(断言旧值)")
    s.add_argument("--file", required=True); s.add_argument("--id", required=True)
    s.add_argument("--col", type=int, required=True)
    s.add_argument("--old", required=True); s.add_argument("--new", required=True)
    s.add_argument("--dry-run", action="store_true")

    s = sub.add_parser("remove", help="从管道列表移除ID")
    s.add_argument("--file", required=True); s.add_argument("--id", required=True)
    s.add_argument("--cols", required=True); s.add_argument("--ids", required=True)
    s.add_argument("--dry-run", action="store_true")

    s = sub.add_parser("add", help="往管道列表锚点ID后插入ID（remove 的逆操作）")
    s.add_argument("--file", required=True); s.add_argument("--id", required=True)
    s.add_argument("--cols", required=True); s.add_argument("--ids", required=True)
    s.add_argument("--after", required=True, help="插在这个锚点ID之后")
    s.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()
    repo = Path(args.repo)
    {"show": cmd_show, "set": cmd_set, "remove": cmd_remove, "add": cmd_add}[args.cmd](args, repo)


if __name__ == "__main__":
    main()
