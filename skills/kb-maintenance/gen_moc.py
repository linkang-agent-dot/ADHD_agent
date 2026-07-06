# -*- coding: utf-8 -*-
"""KB 目录索引(MOC)生成器：给每个大目录生成 _索引_<目录>.md，双链挂上目录内全部笔记。
重跑即全量重建（幂等）。新增笔记后跑一次: python C:\\ADHD_agent\\skills\\kb-maintenance\\gen_moc.py
"""
import os, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

KB = r'C:\ADHD_agent\KB'
MIN_NOTES = 4          # 少于这个数的目录不建索引（首页直链）
EXCLUDE_DIRS = {'.obsidian', '__pycache__', '_工作line备份', 'Token周报'}
TODAY = datetime.date.today().isoformat()

tops = [d for d in os.listdir(KB) if os.path.isdir(os.path.join(KB, d)) and d not in EXCLUDE_DIRS]
report = []

for top in sorted(tops):
    top_path = os.path.join(KB, top)
    moc_name = f'_索引_{top}.md'
    # 收集目录内全部 md（排除自身与旧索引）
    groups = collections.defaultdict(list)  # 一级子目录 -> [(relpath_no_ext, basename, subdir_hint)]
    for root, dirs, files in os.walk(top_path):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for fn in sorted(files):
            if not fn.endswith('.md') or fn.startswith('_索引_'):
                continue
            rel = os.path.relpath(os.path.join(root, fn), top_path).replace('\\', '/')
            parts = rel.split('/')
            group = parts[0] if len(parts) > 1 else '（根目录）'
            hint = '/'.join(parts[1:-1])  # 组内更深层的子路径提示
            groups[group].append((f'{top}/{rel[:-3]}', fn[:-3], hint))
    total = sum(len(v) for v in groups.values())
    if total < MIN_NOTES:
        report.append(f'skip  {top}（{total} 篇，首页直链）')
        continue
    lines = [
        '---',
        'tags: [kind/moc, proj/通用]',
        f'updated: {TODAY}',
        'note: 自动生成的目录索引，别手改；重生成 python C:\\ADHD_agent\\skills\\kb-maintenance\\gen_moc.py',
        '---',
        '',
        f'# 索引：{top}',
        '',
        f'> 共 {total} 篇 ｜ 返回 [[_首页]]',
        '',
    ]
    root_grp = groups.pop('（根目录）', None)
    if root_grp:
        for link, name, hint in root_grp:
            lines.append(f'- [[{link}|{name}]]')
        lines.append('')
    for group in sorted(groups):
        lines.append(f'## {group}')
        for link, name, hint in groups[group]:
            prefix = f'`{hint}` ' if hint else ''
            lines.append(f'- {prefix}[[{link}|{name}]]')
        lines.append('')
    with open(os.path.join(top_path, moc_name), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    report.append(f'write {moc_name}（{total} 篇）')

print('\n'.join(report))
