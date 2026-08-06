# -*- coding: utf-8 -*-
"""交互原型（单文件 HTML）→ 素材包 + 「原型键 → 工程真身路径」映射清单。

用途：把 demo 内嵌的 base64 图素导出成文件夹，并生成给程序拼 prefab 用的映射表。

设计要点（都是踩过的坑，别删）：
1. 声明字典可能被**多个 Object.assign 追加**（本工具 union 全部块）。
   2026-08-05 挖孔案：只抓第一个 const 字面量 → 少 43 条 → 误判"原型没声明" → 白跑一轮 phash 反查、出 11 组错值。
2. **量级校验**：解析到的键数 vs 文中实际出现的键数。不一致 = 还有没抓到的声明块，
   直接 FAIL 退出，不许"少给一半数据还打印个正常数字"。
3. 存在性校验用 `git ls-tree`，**不要用 os.path.exists** —— 稀疏 worktree 下会把全部判成缺失。

用法：
    python prototype_assets_export.py <demo.html> <输出目录> [--repo <仓根>] [--ref <git ref>]
        [--srcvar X3_SKIN_SRC] [--skinpre x3_,x3t_] [--assetroot client/Assets/Res/UI/]
"""
import argparse
import base64
import io
import json
import os
import re
import subprocess
import sys


def parse_src_dict(doc, varname):
    """union 所有声明块：const X = {...} 以及后续 Object.assign(X, {...})。"""
    pat = r'(?:const\s+%s\s*=\s*|Object\.assign\(\s*%s\s*,\s*)(\{.*?\})\s*\)?\s*;' % (varname, varname)
    blocks = list(re.finditer(pat, doc, re.S))
    out = {}
    for m in blocks:
        try:
            out.update(json.loads(re.sub(r',\s*\}', '}', m.group(1))))
        except ValueError as e:
            print('[WARN] 第 %d 个声明块解析失败: %s' % (blocks.index(m) + 1, e))
    return out, len(blocks)


def sanity_check(doc, src, prefixes):
    """量级校验：文中出现的键 ⊆ 字典的键。差集非空 = 还有声明块没抓到。"""
    seen = set()
    for p in prefixes:
        seen |= set(re.findall(r'\b(%s[a-z_0-9]+)' % re.escape(p), doc))
    # 以 `_` 结尾的不是真键，是 JS 拼接模板前缀（如 'x3t_q_'+quality）——单独报出来，
    # 它是「素材靠代码动态拼名」的信号：这类键不会出现在字典里，也不能靠静态扫描盘全。
    dyn = sorted(k for k in seen if k.endswith('_') or k in prefixes)
    seen = set(k for k in seen if k not in dyn)
    undeclared = sorted(seen - set(src))
    return seen, undeclared, dyn


def git_tracked(repo, ref, subdir):
    try:
        out = subprocess.check_output(
            ['git', '-C', repo, 'ls-tree', '-r', '--name-only', ref, '--', subdir],
            stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, OSError) as e:
        print('[WARN] git ls-tree 失败，跳过存在性校验: %s' % e)
        return None
    return set(l.strip() for l in out.decode('utf-8', 'replace').splitlines() if l.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('demo')
    ap.add_argument('out')
    ap.add_argument('--repo', default=None, help='工程仓根，给了才做存在性校验')
    ap.add_argument('--ref', default='HEAD')
    ap.add_argument('--srcvar', default='X3_SKIN_SRC')
    ap.add_argument('--skinpre', default='x3_,x3t_', help='算「工程官方件」的键前缀，逗号分隔')
    ap.add_argument('--assetroot', default='client/Assets/Res/UI/', help='字典里路径的仓内前缀')
    a = ap.parse_args()
    prefixes = [p for p in a.skinpre.split(',') if p]

    doc = io.open(a.demo, encoding='utf-8', errors='replace').read()
    src, nblocks = parse_src_dict(doc, a.srcvar)
    seen, undeclared, dyn = sanity_check(doc, src, prefixes)
    print('[INFO] %s: %d 个声明块 / %d 条映射；文中出现 %d 个键' % (a.srcvar, nblocks, len(src), len(seen)))
    if dyn:
        print('[INFO] 动态拼接前缀 %d 个（代码按状态拼名，静态扫描盘不全，交接时要点明）: %s'
              % (len(dyn), ', '.join(dyn)))
    if undeclared:
        print('[FAIL] %d 个键在文中出现但字典里没有 —— 极可能还有声明块没抓到，先查清楚再用：' % len(undeclared))
        print('       ' + ', '.join(undeclared[:30]) + (' …' if len(undeclared) > 30 else ''))
        return 1

    # 存在性校验（git 索引，不用 os.path.exists）
    tracked, missing = None, []
    if a.repo:
        sub = a.assetroot.rstrip('/')
        # 字典里的路径可能自带 assetroot 的尾段（如 "Spirits/xx.png" 对 root ".../UI/"）
        tracked = git_tracked(a.repo, a.ref, sub)
        if tracked is not None:
            missing = [k for k, v in src.items() if (a.assetroot + v) not in tracked]
            print('[INFO] 在仓命中 %d/%d' % (len(src) - len(missing), len(src)))
            if missing:
                print('[WARN] 缺失: ' + ', '.join(sorted(missing)))

    # 导出内嵌素材
    m = re.search(r'const ASSETS\s*=\s*(\{.*?\n\s*\});', doc, re.S)
    rows_skin, rows_own = [], []
    if not m:
        print('[WARN] 未找到 ASSETS 块，只出映射表不导素材')
    else:
        pairs = re.findall(r'"([^"]+)"\s*:\s*"data:image/([a-z]+);base64,([A-Za-z0-9+/=]+)"', m.group(1))
        for sub in ('_工程官方件', '_玩法专属件'):
            d = os.path.join(a.out, sub)
            if not os.path.isdir(d):
                os.makedirs(d)
        for name, fmt, b64 in pairs:
            raw = base64.b64decode(b64)
            key = name.rsplit('.', 1)[0]
            is_skin = any(key.startswith(p) for p in prefixes)
            sub = '_工程官方件' if is_skin else '_玩法专属件'
            with open(os.path.join(a.out, sub, name), 'wb') as f:
                f.write(raw)
            (rows_skin if is_skin else rows_own).append((name, fmt, len(raw), src.get(key, '')))
        rows_skin.sort()
        rows_own.sort()
        print('[INFO] 导出素材 官方件 %d / 玩法件 %d' % (len(rows_skin), len(rows_own)))

    used = set(re.findall(r'--A-(' + '|'.join(re.escape(p) for p in prefixes) + r'[a-z_0-9]+)\)', doc))
    L = ['# 原型素材 → 工程真身 映射表', '',
         '> 真源 = 原型内 `%s`（%d 个声明块合并，共 %d 条）。本表由 `prototype_assets_export.py` 生成，**别手改**。' % (a.srcvar, nblocks, len(src)),
         '> 存在性用 `git ls-tree` 核（稀疏 worktree 下 `os.path.exists` 会全判缺失）。', '',
         '| 原型键 | 工程路径（`%s` 下） | 在仓 | 原型在用 |' % a.assetroot, '|---|---|---|---|']
    for k, v in sorted(src.items()):
        ex = '—' if tracked is None else ('Y' if k not in missing else '**缺**')
        L.append('| `%s` | `%s` | %s | %s |' % (k, v, ex, 'Y' if k in used else '-'))
    if rows_own:
        L += ['', '## 玩法专属件（原型内嵌，需回源仓取原图）', '', '| 文件 | 格式 | KB |', '|---|---|---|']
        L += ['| `%s` | %s | %.1f |' % (n, f, s / 1024.0) for n, f, s, _ in rows_own]
    L += ['', '⚠️ 内嵌 `.webp` 都是原型压过的，**正式进包一律回源仓取原图**，别从原型抽。']
    if not os.path.isdir(a.out):
        os.makedirs(a.out)
    tmp = os.path.join(a.out, '_映射清单.md.tmp')
    io.open(tmp, 'w', encoding='utf-8').write('\n'.join(L))
    os.replace(tmp, os.path.join(a.out, '_映射清单.md'))
    print('[OK] %s' % os.path.join(a.out, '_映射清单.md'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
