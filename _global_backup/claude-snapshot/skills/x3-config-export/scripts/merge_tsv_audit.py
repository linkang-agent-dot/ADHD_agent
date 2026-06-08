# -*- coding: utf-8 -*-
"""X3 merge 后 tsv 回归确认点：找「目标分支新增/改、却被合并冲掉」的行。

背景：X3 配置仓 merge 时 xlsx 二进制只能整取一边、tsv 文本三方合并。被「二选一
解成对方版本」的表（尤其冲突清单里的表），目标分支独有的新增行会被静默冲掉，
push 能过、列检查能过，直到导表 depend_keys 才报错。本工具在 merge 后立刻揪出来。

用法:
    python merge_tsv_audit.py [merge_commit]   # 默认 HEAD

判定:
    merge_commit 必须是 merge commit。^1=目标分支(被合入的目的地,如 dev_festival),
    ^2=被合入的源(如 dev), base=两者 merge-base。
    对「目标分支相对 base 改过的每个 tsv」做整行集合差:
        lost = (目标分支行 - base行) - 合并后行
    lost>0 = 目标分支新增/改的这些行在合并后整行消失 → 需人工确认是否该恢复。

注意: 整行级对比是可信信号; 不要用某一列(尤其行序号列)判断主键存在性——
      Reward 表第1列是会被双方重用的 seq, 业务主键在第2列(RewardID), 用 col1 必漏。
"""
import subprocess, sys
REPO = r'C:\x3\gdconfig'

def git(args):
    return subprocess.run(['git', *args], cwd=REPO, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL).stdout.decode('utf-8', 'replace')

def show_lines(ref, path):
    return set(l for l in git(['show', f'{ref}:{path}']).splitlines() if l.strip() and '\t' in l)

def main():
    merge = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    p1 = git(['rev-parse', f'{merge}^1']).strip()
    p2 = git(['rev-parse', f'{merge}^2']).strip()
    if not p2:
        print(f'[!] {merge} 不是 merge commit（无第二父）'); return 1
    base = git(['merge-base', p1, p2]).strip()
    print(f'merge={git(["rev-parse","--short",merge]).strip()}  目标分支^1={p1[:7]}  被合入^2={p2[:7]}  base={base[:7]}\n')

    changed = git(['diff', '--name-only', f'{base}..{p1}', '--', 'tsv']).split()
    print(f'目标分支相对 base 改过 {len(changed)} 个 tsv\n')
    flagged = []
    for f in changed:
        rb, rf, rn = show_lines(base, f), show_lines(p1, f), show_lines(merge, f)
        lost = (rf - rb) - rn
        mark = '  <== 疑似被冲掉' if lost else ''
        print(f'  {f}: 节日新增/改 {len(rf-rb)} 行, 合并后消失 {len(lost)} 行{mark}')
        if lost:
            flagged.append((f, lost))
    for f, lost in flagged:
        print(f'\n=== {f} 消失的行(col1/col2 + 摘要) ===')
        for l in sorted(lost)[:40]:
            c = l.split('\t')
            print(f'  col1={c[0]:<8} col2={(c[1] if len(c)>1 else ""):<8} | {l[:80]}')
    print('\n========== 汇总 ==========')
    print('  无丢失' if not flagged else '  需确认: ' + ', '.join(f'{f}({len(l)}行)' for f, l in flagged))
    return 0

if __name__ == '__main__':
    sys.exit(main())
