# -*- coding: utf-8 -*-
"""X3 merge 严格三方 cell 级审计（--no-commit 合并态或 merge commit 后均可跑）。

比 merge_tsv_audit.py（整行集合差）更进一步，抓三类整行审计漏掉的问题：
  1. remote 单侧改动未被 driver 应用（§⑨/⑯B/⑰ 静默清列·未命名列漏应用）
  2. local 单侧改动被回退
  3. 双方改同一 cell、结果却谁都不是（§⑭ cell 级污染）
另附 Text 拆管道重复 key 审计（对比两 parent 基线，只报新增 dup）。

用法（在 gdconfig 仓根目录）：
  python merge_strict_cell_audit.py            # 未提交合并态: base=merge-base, L=HEAD, R=MERGE_HEAD, W=工作树
  python merge_strict_cell_audit.py <merge_sha> # 已提交: L=sha^1, R=sha^2, W=sha

输出 UTF-8 写到 merge_strict_audit_out.txt（防 GBK 控制台崩）。
有意让号/定向编辑会报出来——人工核对清单即可，不要求零输出；零输出=完全干净。
"""
import csv, io, os, subprocess, sys
from collections import Counter


def sh(*args):
    return subprocess.run(list(args), capture_output=True)


def rows_of(ref, path, worktree=False):
    if worktree:
        if not os.path.exists(path):
            return None
        text = open(path, 'rb').read().decode('utf-8-sig')
    else:
        r = sh('git', 'show', f'{ref}:{path}')
        if r.returncode != 0:
            return None
        text = r.stdout.decode('utf-8-sig', 'replace')
    return list(csv.reader(io.StringIO(text), delimiter='\t'))


def main():
    if len(sys.argv) > 1:
        M = sys.argv[1]
        L, R, W_ref = M + '^1', M + '^2', M
        wt_is_tree = False
    else:
        L, R, W_ref = 'HEAD', 'MERGE_HEAD', None
        wt_is_tree = True
    BASE = sh('git', 'merge-base', L, R).stdout.decode().strip()
    out = io.open('merge_strict_audit_out.txt', 'w', encoding='utf-8')

    def changed(ref):
        r = sh('git', 'diff', '--name-only', BASE, ref, '--', 'tsv/')
        return set(r.stdout.decode().split())

    files = sorted(changed(L) | changed(R))
    viol = []
    for p in files:
        if p == 'tsv/i18n/Text__Text.tsv':
            continue
        rb = rows_of(BASE, p)
        rl = rows_of(L, p)
        rr = rows_of(R, p)
        rw = rows_of(W_ref, p, worktree=wt_is_tree)
        if rw is None:
            continue

        def dmap(rows):
            if not rows or len(rows) < 7:
                return {}, []
            h = rows[5]
            seen = {}
            C = []
            for i, c in enumerate(h):
                name = c if c else f'__u{i}'
                if name in seen:
                    name = f'{name}#{seen[name]}'
                seen[name.split("#")[0]] = seen.get(name.split("#")[0], 0) + 1
                C.append(name)
            m = {}
            for r in rows[6:]:
                if r and r[0] and r[0] not in m:
                    m[r[0]] = {C[i]: (r[i] if i < len(r) else '') for i in range(len(C))}
            return m, C

        mb, _ = dmap(rb)
        ml, _ = dmap(rl)
        mr, _ = dmap(rr)
        mw, _ = dmap(rw)
        is_reward = p.endswith('Reward__Reward.tsv')
        for k in set(ml) | set(mr):
            b, l, r, w = mb.get(k), ml.get(k), mr.get(k), mw.get(k)
            if w is None:
                continue  # 删行走整行审计（merge_tsv_audit.py）
            cols = set()
            for d in (b, l, r, w):
                if d:
                    cols.update(d)
            for cn in cols:
                if is_reward and cn in ('ID', 'DisplayOrder'):
                    continue
                vb = b.get(cn, '') if b else None
                vl = l.get(cn, '') if l else None
                vr = r.get(cn, '') if r else None
                vw = w.get(cn, '')
                if vl is not None and vr is not None and vb is not None:
                    if vl == vb and vr != vb and vw != vr:
                        viol.append((p, k, cn, 'remote单侧改动未应用', vw, vl, vr))
                    elif vr == vb and vl != vb and vw != vl:
                        viol.append((p, k, cn, 'local单侧改动被回退', vw, vl, vr))
                    elif vl != vb and vr != vb and vl != vr and vw not in (vl, vr):
                        viol.append((p, k, cn, '双改cell结果谁都不是(污染)', vw, vl, vr))
                elif vb is None:
                    if vl is not None and vr is None and vw != vl:
                        viol.append((p, k, cn, 'local新行cell被改', vw, vl, vr))
                    elif vr is not None and vl is None and vw != vr:
                        viol.append((p, k, cn, 'remote新行cell被改', vw, vl, vr))
                    elif vl is not None and vr is not None and vw not in (vl, vr):
                        viol.append((p, k, cn, 'add-add cell谁都不是', vw, vl, vr))
    out.write('=== cell 级三方违规（含有意让号编辑，人工核对）: %d ===\n' % len(viol))
    for p, k, cn, why, vw, vl, vr in viol:
        out.write('%s [%s] col[%s] %s: wt=%r L=%r R=%r\n' % (p, k, cn, why, str(vw)[:60], str(vl)[:60], str(vr)[:60]))

    # Text 拆管道新增重复 key 审计
    P = 'tsv/i18n/Text__Text.tsv'

    def keycnt(rows):
        c = Counter()
        if not rows:
            return c
        for r in rows[6:]:
            if r and r[0]:
                for k in r[0].split('|'):
                    if k:
                        c[k] += 1
        return c

    cw = keycnt(rows_of(W_ref, P, worktree=wt_is_tree))
    cl = keycnt(rows_of(L, P))
    cr = keycnt(rows_of(R, P))
    new_dups = sorted(k for k, v in cw.items() if v > 1 and cl.get(k, 0) <= 1 and cr.get(k, 0) <= 1)
    out.write('\n=== Text 新增重复 key（两 parent 都不 dup、合并后 dup）: %d ===\n' % len(new_dups))
    for k in new_dups:
        out.write('  %s x%d\n' % (k, cw[k]))
    # key 丢失
    def keyset(c):
        return set(c)
    lost = sorted(((keyset(cl) | keyset(cr)) - keyset(keycnt(rows_of(BASE, P)))) - keyset(cw))
    out.write('\n=== Text 新增 key 丢失: %d ===\n' % len(lost))
    for k in lost[:50]:
        out.write('  %s\n' % k)
    out.close()
    print('done. violations=%d text_new_dups=%d text_key_lost=%d -> merge_strict_audit_out.txt' % (len(viol), len(new_dups), len(lost)))


if __name__ == '__main__':
    main()
