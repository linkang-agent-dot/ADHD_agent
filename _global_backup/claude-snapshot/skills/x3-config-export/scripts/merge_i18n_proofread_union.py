#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""i18n「校对情况」列在互合时被 driver cell 合并清空 -> 双向并集补回。

背景：tsv/i18n/Text__Text.tsv 的 row3 里有若干「XX语校对情况」列（实测 col23-26 =
法/德/西/印尼），每列是**该语种独立**的人工校对标。两侧分别校对不同语种时，
driver 做 cell 级 3 路合并会各取一边、把另一边的标清成空（§⑨ 静默清列的 i18n 变体）。
正解是**并集**（谁校对了哪个语种就保留谁的标），不是二选一。

用法（在未提交的 merge 态下跑，即 MERGE_HEAD 存在时）：
    python merge_i18n_proofread_union.py [repo_path]

安全性：只在「某行相对某个 parent 的全部差异都落在校对列上」时才补标——
内容有差异的行一律跳过（内容改了，旧校对标可能已过期，不能盲目盖）。
"""
import os
import subprocess
import sys

TSV = "tsv/i18n/Text__Text.tsv"
NL = "\n"
TAB = "\t"
MARK = "已校对"
HEADER_ROW = 2  # 0-based: row3 是列含义行
PROOF_KEY = "校对情况"


def blob(repo, ref):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, TSV)],
                       cwd=repo, capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace").replace("\r\n", NL)


def by_unique_key(text):
    """col0 -> 整行；重复 col0 的键直接剔除（不可靠，不参与补标）。"""
    d, dup = {}, set()
    for row in text.split(NL):
        if not row.strip():
            continue
        k = row.split(TAB)[0]
        if k in d:
            dup.add(k)
        d[k] = row
    for k in dup:
        d.pop(k, None)
    return d


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    path = os.path.join(repo, TSV.replace("/", os.sep))
    if not os.path.exists(path):
        print("[skip] %s 不存在" % TSV)
        return 0

    raw = open(path, encoding="utf-8").read().replace("\r\n", NL)
    lines = raw.split(NL)
    if len(lines) <= HEADER_ROW:
        print("[skip] 文件过短")
        return 0

    header = lines[HEADER_ROW].split(TAB)
    proof_cols = [i for i, h in enumerate(header) if PROOF_KEY in h]
    if not proof_cols:
        print("[skip] 未找到「%s」列" % PROOF_KEY)
        return 0
    print("校对列 idx = %s" % proof_cols)

    parents = {}
    for ref in ("HEAD", "MERGE_HEAD"):
        t = blob(repo, ref)
        if t is None:
            print("[warn] 取不到 %s，跳过该侧（是否不在 merge 态？）" % ref)
            continue
        parents[ref] = by_unique_key(t)
    if not parents:
        print("[skip] 两侧 parent 都取不到")
        return 0

    out, seen = [], {}
    n_row = n_cell = 0
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        key = line.split(TAB)[0]
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:          # 重复 col0，不动
            out.append(line)
            continue

        cells = line.split(TAB)
        touched = False
        for pmap in parents.values():
            if key not in pmap:
                continue
            pc = pmap[key].split(TAB)
            width = max(len(pc), len(cells))
            pc += [""] * (width - len(pc))
            cells += [""] * (width - len(cells))
            diff = [i for i in range(width) if pc[i] != cells[i]]
            # 只有当全部差异都落在校对列上才认为「仅校对标差异」，否则内容变了、跳过
            if not diff or any(i not in proof_cols for i in diff):
                continue
            for i in diff:
                if pc[i] == MARK and cells[i] == "":
                    cells[i] = MARK
                    n_cell += 1
                    touched = True
        if touched:
            n_row += 1
        out.append(TAB.join(cells))

    if n_cell:
        open(path, "w", encoding="utf-8", newline="").write(NL.join(out))
    print("并集补标：行=%d 单元格=%d" % (n_row, n_cell))
    return 0


if __name__ == "__main__":
    sys.exit(main())
