#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X3 活动配置速查：按 ID 或关键词查 ActvOnline，并自动跟一层外键（TimeCycle/ChainPack 等）。

替代每次现场 grep tsv 的手工排查（「查一下XX活动 actvonline 是啥」类需求一条命令出结果）。

用法:
    python actv_lookup.py 102993                # 按活动ID查
    python actv_lookup.py 酒馆                   # 按关键词查（备注/活动名/任意单元格）
    python actv_lookup.py 102993 --no-follow    # 只看本行，不跟外键
    python actv_lookup.py 102993 --table Pack   # 查其他表（默认 ActvOnline）
    python actv_lookup.py 102993 --repo C:\\x3\\gdconfig-worktree  # worktree 下查

tsv 行结构约定: R0=cs标记 R1=类型 R2=外键目标表 R3=注释(可多行) R4=中文名 R5=字段名 R6起=数据。
脚本按「首个 col0 为纯数字的行」自动定位数据起始行，不硬编码行号。
输出不带 emoji（Windows 控制台 GBK 下会崩，见 memory workflow_x3_merge_conflict_audit §⑩）。
"""
import argparse
import csv
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DEFAULT_REPO = r'C:\x3\gdconfig'
_table_cache = {}


def load_table(repo, table):
    """返回 (rows, fk_row, cn_row, name_row, data_start)；找不到返回 None。"""
    key = (repo, table)
    if key in _table_cache:
        return _table_cache[key]
    # 优先同名 sheet，其次该表任意 sheet，最后按「别的文件里的同名子页签」找（如 ActvGroup 在 ActvOnline__ActvGroup.tsv）
    candidates = (glob.glob(os.path.join(repo, 'tsv', '**', f'{table}__{table}.tsv'), recursive=True)
                  or glob.glob(os.path.join(repo, 'tsv', '**', f'{table}__*.tsv'), recursive=True)
                  or glob.glob(os.path.join(repo, 'tsv', '**', f'*__{table}.tsv'), recursive=True))
    if not candidates:
        _table_cache[key] = None
        return None
    path = candidates[0]
    with open(path, encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    data_start = None
    for i, r in enumerate(rows):
        if r and r[0].strip().isdigit():
            data_start = i
            break
    if data_start is None or data_start < 2:
        _table_cache[key] = None
        return None
    result = {
        'path': path,
        'rows': rows,
        'fk': rows[2] if len(rows) > 2 else [],
        'cn': rows[data_start - 2],
        'name': rows[data_start - 1],
        'data': rows[data_start:],
    }
    _table_cache[key] = result
    return result


def cell_ids(v):
    """从单元格里拆出引用ID列表（支持 | , 分隔），非数字忽略。"""
    return [x for x in re.split(r'[|,;]', v.strip()) if x.isdigit()]


def field_label(t, i):
    name = t['name'][i].strip() if i < len(t['name']) else ''
    cn = t['cn'][i].strip() if i < len(t['cn']) else ''
    label = name or f'col{i}'
    if cn and cn != name:
        label += f'({cn})'
    return label


def print_row(t, row, indent='', max_fields=None):
    shown = 0
    for i, v in enumerate(row):
        v = v.strip()
        if not v:
            continue
        print(f'{indent}[{i:>2}] {field_label(t, i)} = {v[:120]}')
        shown += 1
        if max_fields and shown >= max_fields:
            print(f'{indent}     ... (其余非空字段略，--no-follow 后直接查该表看全)')
            break


def find_rows(t, query):
    hits = []
    if query.isdigit():
        for r in t['data']:
            if r and r[0].strip() == query:
                hits.append(r)
        if not hits:  # 业务键在 col1 的表（如 Reward）
            for r in t['data']:
                if len(r) > 1 and r[1].strip() == query:
                    hits.append(r)
    else:
        q = query.lower()
        for r in t['data']:
            if any(q in c.lower() for c in r[:4] if c):
                hits.append(r)
        if not hits:
            for r in t['data']:
                if any(q in c.lower() for c in r if c):
                    hits.append(r)
    return hits


def main():
    ap = argparse.ArgumentParser(description='X3 活动配置速查（tsv 缓存直查 + 一层外键跟随）')
    ap.add_argument('query', help='活动ID 或 关键词')
    ap.add_argument('--table', default='ActvOnline', help='起点表名（默认 ActvOnline）')
    ap.add_argument('--repo', default=DEFAULT_REPO, help='gdconfig 仓路径（worktree 时传对应目录）')
    ap.add_argument('--no-follow', action='store_true', help='不跟外键')
    ap.add_argument('--max-hits', type=int, default=8)
    args = ap.parse_args()

    t = load_table(args.repo, args.table)
    if t is None:
        print(f'[!] 找不到表 {args.table}（{args.repo}\\tsv 下无 {args.table}__*.tsv）')
        return 1
    print(f'== {args.table} ({os.path.relpath(t["path"], args.repo)}) 查 "{args.query}" ==')

    hits = find_rows(t, args.query)
    if not hits:
        print('无命中。关键词可试更短的子串；ID 可试 --table 换表。')
        return 1
    if len(hits) > args.max_hits:
        print(f'命中 {len(hits)} 行，只显示前 {args.max_hits} 行（补充关键词缩小范围）:')
        for r in hits[:args.max_hits]:
            head = ' | '.join(c for c in r[:4] if c.strip())
            print(f'  {head[:110]}')
        return 0

    for r in hits:
        print(f'\n---- 行 col0={r[0]} ----')
        print_row(t, r)
        if args.no_follow:
            continue
        # 跟一层外键：R2 声明了目标表的列，且单元格有值
        for i, target in enumerate(t['fk']):
            target = target.strip()
            if not target or i >= len(r) or not r[i].strip():
                continue
            ids = cell_ids(r[i])
            if not ids:
                continue
            ft = load_table(args.repo, target)
            if ft is None:
                print(f'  -> {field_label(t, i)} 引用 {target}: 表文件未找到')
                continue
            for rid in ids[:6]:
                # Reward 业务键=col1(RewardID)，col0 是会被重排的 seq，必须先按 col1 匹配
                if target == 'Reward':
                    sub = [x for x in ft['data'] if len(x) > 1 and x[1].strip() == rid] \
                          or [x for x in ft['data'] if x and x[0].strip() == rid]
                else:
                    sub = [x for x in ft['data'] if x and x[0].strip() == rid] \
                          or [x for x in ft['data'] if len(x) > 1 and x[1].strip() == rid]
                if sub:
                    tag = f'，共{len(sub)}行' if len(sub) > 1 else ''
                    print(f'  -> {target} #{rid}  (来自 {field_label(t, i)}{tag})')
                    for s in sub[:5]:
                        print_row(ft, s, indent='       ', max_fields=8)
                        if len(sub) > 1:
                            print('       --')
                    if len(sub) > 5:
                        print(f'       ... 其余 {len(sub)-5} 行略')
                else:
                    print(f'  -> {target} #{rid}: 未找到该行（引用悬空，导表会报 depend_keys）')
            if len(ids) > 6:
                print(f'  -> {target}: 还有 {len(ids)-6} 个引用ID未展开')
    return 0


if __name__ == '__main__':
    sys.exit(main())
