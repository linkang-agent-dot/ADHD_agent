# -*- coding: utf-8 -*-
"""孤儿检查：统计既无出链、也没被任何笔记链到的 md。"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
KB = r'C:\ADHD_agent\KB'
EXCL = ('.obsidian', '__pycache__', '_自动流水')

notes = {}  # 绝对路径 -> (rel, basename_no_ext, outlinks)
for root, dirs, fns in os.walk(KB):
    dirs[:] = [d for d in dirs if d not in EXCL]
    for fn in fns:
        if fn.endswith('.md'):
            p = os.path.join(root, fn)
            txt = open(p, encoding='utf-8', errors='replace').read()
            links = re.findall(r'\[\[([^\]|#]+)', txt)
            rel = os.path.relpath(p, KB).replace('\\', '/')
            notes[p] = (rel, fn[:-3], [l.strip() for l in links])

by_base, by_rel = {}, {}
for p, (rel, base, _) in notes.items():
    by_base.setdefault(base, []).append(p)
    by_rel[rel[:-3]] = p

linked = set()
for p, (rel, base, links) in notes.items():
    for l in links:
        l = l.replace('\\', '/')
        if l in by_rel:
            linked.add(by_rel[l])
        elif l in by_base:
            for t in by_base[l]:
                linked.add(t)

orphans = [rel for p, (rel, base, links) in notes.items() if not links and p not in linked]
print(f'总笔记: {len(notes)}')
print(f'孤儿(无出链且无入链): {len(orphans)}')
for o in sorted(orphans):
    print('  ' + o)
