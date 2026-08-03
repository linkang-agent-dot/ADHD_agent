#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
X3 i18n 速查：按 key 前缀 + ID 批量捞多语言文本（默认 cn/en）。

典型用途：出「给社区同学看的 What's New 文本」时，把各活动的正式中英名和
描述从配置现捞出来，避免手写与游戏内不一致。

用法：
  # 活动名 + 描述（默认前缀 ActvOnline_ActvName / ActvOnline_ActvDesc）
  python i18n_lookup.py 101026 101027 102803

  # 指定 key 前缀（不含 TXT_ 与尾部 ID）
  python i18n_lookup.py --prefix Pack_Name 130051 130052
  python i18n_lookup.py --prefix HeroSkin_Name --prefix Item_Name 102001

  # 指定语言列 / 指定分支 / 直接指定 tsv
  # ⚠️ ids 必须放在 --lang 之前（--lang 是 nargs=+，写在它后面的 ID 会被它吞掉报错）
  python i18n_lookup.py 101026 --lang cn en jp
  python i18n_lookup.py 101026 --branch dev_festival
  python i18n_lookup.py 101026 --tsv D:/somewhere/Text__Text.tsv

  # 输出 markdown 到文件（Windows 控制台是 GBK，中文直接 print 会乱码/报错，
  #   要看中文结果一律 -o 写文件再读）
  python i18n_lookup.py -o out.md 101026 101027

数据源：gdconfig 的 tsv/i18n/Text__Text.tsv（导表已迁 tsv 缓存，xlsx 早已不在 data/ 下）。
默认不切分支、不碰工作区：用 `git show <branch>:tsv/i18n/Text__Text.tsv` 导到临时文件读。

⚠️ Text__Text.tsv 两个坑（本脚本已处理，手写解析必踩）：
  1. key 有两种排布——有的在 col0、有的在 col2（col2 为空时 key 在 col0）。
     只扫 col2 会漏掉一大半行（换皮活动名基本都在 col0）。
  2. 多个 key 共享同一条文本时，key 列用 `|` 合并成一格，必须 split('|') 再比对。
  语言列固定：col3=cn col4=en col5=sp col6=fr col7=id col8=de col9=kr col10=zh(繁)
              col11=ru col12=ua col13=jp col14=it col15=pl col16=po col17=tr col18=th
"""
import argparse
import os
import subprocess
import sys
import tempfile
import csv

LANG_COL = {
    "cn": 3, "en": 4, "sp": 5, "fr": 6, "id": 7, "de": 8, "kr": 9, "zh": 10,
    "ru": 11, "ua": 12, "jp": 13, "it": 14, "pl": 15, "po": 16, "tr": 17, "th": 18,
}
DEFAULT_PREFIXES = ["ActvOnline_ActvName", "ActvOnline_ActvDesc"]
TSV_REL = "tsv/i18n/Text__Text.tsv"

# 主仓有隔离闸门（别的 worktree 在用时禁止在主仓操作），所以优先挑一个已存在的
# worktree 跑 git show —— 只读、不写工作区，任何 worktree 都能读到同一 object store。
REPO_CANDIDATES = [
    r"C:\X3\wt_circus_float",
    r"C:\x3\gdconfig",
]


def _pick_repo(explicit=None):
    if explicit:
        return explicit
    for p in REPO_CANDIDATES:
        if os.path.isdir(os.path.join(p, ".git")) or os.path.isfile(os.path.join(p, ".git")):
            return p
    # 兜底：扫 C:\x3 下任意 worktree
    base = r"C:\x3"
    if os.path.isdir(base):
        for d in os.listdir(base):
            p = os.path.join(base, d)
            if os.path.exists(os.path.join(p, ".git")):
                return p
    raise SystemExit("[i18n_lookup] 找不到 gdconfig 仓，请用 --repo 指定")


def export_tsv(branch, repo=None):
    """从指定分支导出 Text__Text.tsv 到临时文件，不切分支不碰工作区。"""
    repo = _pick_repo(repo)
    for ref in (f"origin/{branch}", branch):
        try:
            data = subprocess.check_output(
                ["git", "show", f"{ref}:{TSV_REL}"], cwd=repo, stderr=subprocess.DEVNULL
            )
            fd, path = tempfile.mkstemp(suffix="_Text.tsv")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            return path
        except subprocess.CalledProcessError:
            continue
    raise SystemExit(f"[i18n_lookup] 无法从 {repo} 导出 {branch}:{TSV_REL}")


def load(tsv_path):
    """→ {key: [列...]}，已处理「key 在 col0 或 col2」+「| 合并多 key」两个坑。"""
    idx = {}
    with open(tsv_path, encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 5:
                continue
            keys = set()
            for ci in (0, 2):
                if ci < len(row) and row[ci]:
                    keys.update(row[ci].split("|"))
            for k in keys:
                if k.startswith("TXT_") and k not in idx:
                    idx[k] = row
    return idx


def main():
    ap = argparse.ArgumentParser(description="X3 i18n 批量速查（按 key 前缀 + ID）")
    ap.add_argument("ids", nargs="+", help="配置 ID，如 101026 101027")
    ap.add_argument("--prefix", action="append", default=None,
                    help=f"key 前缀，可多次；默认 {DEFAULT_PREFIXES}")
    ap.add_argument("--lang", nargs="+", default=["cn", "en"],
                    help=f"语言列，默认 cn en；可选 {list(LANG_COL)}")
    ap.add_argument("--branch", default="dev_festival", help="分支，默认 dev_festival")
    ap.add_argument("--repo", default=None, help="gdconfig 仓/worktree 路径")
    ap.add_argument("--tsv", default=None, help="直接指定 Text__Text.tsv，跳过 git show")
    ap.add_argument("-o", "--out", default=None,
                    help="输出 markdown 文件（Windows 控制台 GBK，看中文务必用它）")
    a = ap.parse_args()

    prefixes = a.prefix or DEFAULT_PREFIXES
    for lg in a.lang:
        if lg not in LANG_COL:
            raise SystemExit(f"[i18n_lookup] 未知语言 {lg}，可选 {list(LANG_COL)}")

    tsv_path, tmp = (a.tsv, False) if a.tsv else (export_tsv(a.branch, a.repo), True)
    try:
        idx = load(tsv_path)
    finally:
        if tmp:
            try:
                os.remove(tsv_path)
            except OSError:
                pass

    lines, missing = [], []
    for i in a.ids:
        lines.append(f"### {i}")
        for p in prefixes:
            key = f"TXT_{p}_{i}"
            row = idx.get(key)
            if not row:
                lines.append(f"- {p}: (无此 key)")
                missing.append(key)
                continue
            vals = []
            for lg in a.lang:
                c = LANG_COL[lg]
                v = row[c] if c < len(row) else ""
                vals.append(f"{lg}=[{v}]")
                if not v.strip():
                    missing.append(f"{key} ({lg} 为空)")
            lines.append(f"- {p}: " + "  ".join(vals))
        lines.append("")
    if missing:
        lines.append("## ⚠️ 缺失 / 空值（换皮漏改的高发点）")
        lines.extend(f"- {m}" for m in missing)

    text = "\n".join(lines)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[i18n_lookup] wrote {a.out}  ({len(a.ids)} ids, {len(missing)} missing)")
    else:
        # 控制台是 GBK，中文会崩 → 只报统计，提示用 -o
        print(f"[i18n_lookup] {len(a.ids)} ids, {len(missing)} missing. "
              f"中文结果请加 -o out.md 写文件后查看。")


if __name__ == "__main__":
    main()
