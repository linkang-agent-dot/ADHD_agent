# -*- coding: utf-8 -*-
"""通用: 把当前所有改过的tsv(vs HEAD)用tsv_to_xlsx手术派生进xlsx(结构保留)。本地导表前跑。"""
import csv, io, os, sys, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPO = r"C:\x3\gdconfig"
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import tsv_to_xlsx as T

def cr(t):
    return [r for r in csv.reader(io.StringIO(t), delimiter='\t')]

def head(p):
    return subprocess.run(['git', 'show', 'HEAD:' + p], cwd=REPO, capture_output=True).stdout.decode('utf-8')

# 改过的tsv
out = subprocess.run(['git', 'status', '--short'], cwd=REPO, capture_output=True).stdout.decode('utf-8')
tsvs = [ln[3:].strip() for ln in out.splitlines() if ln.strip().endswith('.tsv')]
for tsv in tsvs:
    # tsv/{rel}{base}__{sheet}.tsv -> data/{rel}{base}.xlsx sheet {sheet}
    rel = tsv[len('tsv/'):]
    d = os.path.dirname(rel)
    fname = os.path.basename(rel)[:-4]  # 去.tsv
    base, sheet = fname.split('__', 1)
    xlsx = 'data/' + (d + '/' if d else '') + base + '.xlsx'
    b = cr(head(tsv)); n = cr(open(os.path.join(REPO, tsv), encoding='utf-8').read())
    while b and b[-1] == ['']: b.pop()
    while n and n[-1] == ['']: n.pop()
    ch, bk = T.compute_changes(b, n, allow_append=True)
    if bk:
        print('%-50s BLOCK: %s' % (sheet, bk)); continue
    if not ch:
        print('%-50s 无改动' % sheet); continue
    rep = T.patch_xlsx_cells(os.path.join(REPO, xlsx), {sheet: ch})
    blocked = rep['blocked_formula'].get(sheet, [])
    unk = rep['unknown_sheet']
    print('%-50s applied=%d blocked=%d unk=%s' % (sheet, len(rep['applied'].get(sheet, [])), len(blocked), unk))
    if blocked: print('   !!公式格:', blocked[:3])
print('=== sync完成 ===')
