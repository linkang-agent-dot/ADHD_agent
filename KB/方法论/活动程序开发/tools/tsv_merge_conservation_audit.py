# -*- coding: utf-8 -*-
"""
tsv 合并后「列级非空值计数守恒」审计 —— X3 配置仓每次 merge 后的必做项。

为什么需要独立脚本：`scripts/pre_push_check.py` 只查**列结构**（列头在不在、列数对不对），
查不出「列头在、值被清空」。2026-07-15 事故就是这么漏的：ActvOnline 列结构冲突被处理成
"补空列"，BaseActvID 12 行 + ForbidRestartOpen 4 行的值全清，pre_push_check 绿灯通过。
官方 skill（`gdconfig/scripts/x3_skill_merge.md` 五.1.5 节）要求做这个审计但只给了代码注释，
没给可跑脚本 —— 本文件补上。

判据：**merged 每列非空 cell 数 ≥ max(父1, 父2) 同名列非空数**。小于就是丢值，必须回填。

🔴 两个实战踩到的坑（2026-08-04 限时抢购回流）：
  1. **表头可能有同名列**！X3 Text 表 `已校对` 就有**两个**（idx 25 / 26，col23-26 是各语种校对情况）。
     用 `names.index(col)` 只拿到第一个 ⇒ 回填后仍差值。本脚本按「同名列合计」统计，回填同理必须遍历全部同名列。
  2. **丢值不一定是删行造成的**。本案首轮报 `已校对` -38，被删的 48 行该列却全空；
     真因是 35 行多 key 行（`TXT_A|TXT_B|...`）上游标了校对、driver 取了我方空值。
     ⇒ 报出丢值后要**定位到具体行**再回填，别猜。本脚本 --detail 直接列出这些行。

用法（在 merge 冲突已解决、尚未 commit 的状态下跑）：
    python tsv_merge_conservation_audit.py                       # 审计本次 merge 涉及的全部 tsv
    python tsv_merge_conservation_audit.py --files tsv/a.tsv ...  # 只审指定文件
    python tsv_merge_conservation_audit.py --detail 已校对        # 列出该列具体丢在哪些行
    python tsv_merge_conservation_audit.py --repo C:/x3/gdconfig  # 指定仓（默认 C:/x3/gdconfig）

前提：处于 merge 状态（HEAD = LOCAL 父，MERGE_HEAD = REMOTE 父）。
"""
import argparse
import csv
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HDR = 5   # row0-4 元数据，row5 = 字段名，数据从 row6 起


def sh(repo, *args):
    return subprocess.run(args, cwd=repo, capture_output=True).stdout.decode('utf-8', 'replace')


def rows_of(repo, path, rev=None):
    """rev=None 读工作区；否则读 git 版本"""
    if rev is None:
        full = os.path.join(repo, path)
        if not os.path.exists(full):
            return None
        data = open(full, encoding='utf-8', errors='replace').read()
    else:
        data = sh(repo, 'git', 'show', '%s:%s' % (rev, path))
        if not data:
            return None
    return list(csv.reader(io.StringIO(data), delimiter='\t'))


def counts(rows):
    """按字段名统计非空 cell 数。⚠️ 同名列合计（X3 Text 表 已校对 有两列）"""
    if not rows or len(rows) <= HDR:
        return {}, []
    names = rows[HDR]
    c = {}
    for r in rows[HDR + 1:]:
        for i, v in enumerate(r):
            if i < len(names) and names[i] and v.strip():
                c[names[i]] = c.get(names[i], 0) + 1
    return c, names


def changed_tsvs(repo):
    out = sh(repo, 'git', 'diff', '--cached', '--name-only')
    out += sh(repo, 'git', 'diff', '--name-only')
    return sorted({f for f in out.split('\n') if f.endswith('.tsv')})


def detail(repo, path, col):
    """列出「父有值、merged 空、行还在」的具体行（含全部同名列）"""
    mine, up, mg = (rows_of(repo, path, 'HEAD'), rows_of(repo, path, 'MERGE_HEAD'), rows_of(repo, path))
    if not (mine and up and mg):
        print('  取不到三方版本'); return
    idx = [i for i, n in enumerate(mg[HDR]) if n == col]
    if not idx:
        print('  该表没有名为 %s 的列' % col); return
    print('  名为「%s」的列: %s' % (col, idx))

    def m(rows):
        d = {}
        for r in rows[HDR + 1:]:
            if r and r[0].strip():
                d[r[0]] = {i: (r[i].strip() if len(r) > i else '') for i in idx}
        return d

    A, B, M = m(mine), m(up), m(mg)
    hits = []
    for k in set(A) | set(B):
        if k not in M:
            continue
        for i in idx:
            want = A.get(k, {}).get(i, '') or B.get(k, {}).get(i, '')
            if want and not M[k].get(i, ''):
                hits.append((k, i, want))
    print('  「父有值 / merged 空 / 行还在」: %d 处' % len(hits))
    for k, i, w in hits[:15]:
        print('    col%-3d [%s]  %s' % (i, w, k[:64]))
    gone = [k for k in set(A) | set(B) if k not in M
            and any((A.get(k, {}).get(i) or B.get(k, {}).get(i)) for i in idx)]
    print('  「父有值但整行不在 merged」: %d 处（这类是真丢行，优先查）' % len(gone))
    for k in gone[:8]:
        print('    %s' % k[:70])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=r'C:/x3/gdconfig')
    ap.add_argument('--files', nargs='*')
    ap.add_argument('--detail', help='对某列列出丢值的具体行')
    a = ap.parse_args()

    if not os.path.exists(os.path.join(a.repo, '.git', 'MERGE_HEAD')):
        print('⚠️ 当前不在 merge 状态（无 .git/MERGE_HEAD）——本审计需要 HEAD/MERGE_HEAD 两个父版本')
        return 2

    files = a.files or changed_tsvs(a.repo)
    print('审计 %d 个 tsv\n' % len(files))
    bad = []
    for f in files:
        mine, up, mg = (rows_of(a.repo, f, 'HEAD'), rows_of(a.repo, f, 'MERGE_HEAD'), rows_of(a.repo, f))
        if mg is None:
            continue
        ca, _ = counts(mine or [])
        cb, _ = counts(up or [])
        cm, _ = counts(mg)
        losses = [(n, cm.get(n, 0), max(ca.get(n, 0), cb.get(n, 0)))
                  for n in set(ca) | set(cb) if cm.get(n, 0) < max(ca.get(n, 0), cb.get(n, 0))]
        if losses:
            bad.append(f)
            print('  [X] %s' % f)
            for n, m_, mx in sorted(losses, key=lambda x: x[1] - x[2]):
                print('       %-24s merged=%-7d max(parent)=%-7d 差 %d' % (n, m_, mx, m_ - mx))
        else:
            print('  [OK] %s' % f)

    print('\n结论: %s' % ('全部守恒 ✅' if not bad else '%d 个表丢值，必须回填后再 commit 🔴' % len(bad)))
    if a.detail and bad:
        for f in bad:
            print('\n--- %s 的「%s」丢值明细 ---' % (f, a.detail))
            detail(a.repo, f, a.detail)
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
