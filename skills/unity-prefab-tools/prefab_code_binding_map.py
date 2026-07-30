# -*- coding: utf-8 -*-
"""prefab ↔ 代码 绑定反查（换皮/搬运开工第一步用）。

解决的问题：搬一个活动界面时，光看 prefab 名字猜不出「谁加载它、节点名能不能改」。
本脚本按 **GUID** 双向反查，给出可直接照着搬的映射：
  1) prefab → 挂在它身上的 MonoBehaviour 脚本（区分「本模块专属」与「通用组件」）
  2) prefab ← 谁通过 assetPath / GUID 引用它（真正的加载方，通常在 Auto_*.cs 里）
  3) prefab 之间的嵌套关系（拆一个会不会连带另一个）
  4) 相关代码里 GetChild("路径") / GetComponent<T>("路径") 绑定的**节点路径清单**
     —— 这些路径是硬编码的，换皮时节点改名即断，必须原样保留

用法：
  python prefab_code_binding_map.py --assets D:\\UGit\\x2client\\client\\Assets \\
      --prefabs x2/Res/UI/Prefab/Activity/FlashSale.prefab,x2/Res/UI/Prefab/Activity/FlashSaleItem.prefab \\
      --keyword FlashSale
  # --keyword 用于判定「专属脚本」+ 搜相关 .cs（可给多个，逗号分隔）

⚠️ 大仓（x2client / x3-project）全量 walk 需数分钟：用 --code-root 把代码扫描面缩小，
   或先用 find 定位模块目录再跑。别用 ripgrep 全仓 grep（20s 就超时）。
2026-07-30 X2 限时抢购搬运实证：4 个 prefab 各自独立加载、prefab 上零专属脚本、
绑定全靠代码里的节点路径 —— 这个结论只有反查得出来，看 prefab 看不出来。
"""
from __future__ import annotations
import argparse
import os
import re

SKIP_DIRS = ('Library', '.git', 'Temp', 'obj', 'Bin', 'Logs')
RE_SCRIPT_GUID = re.compile(r'm_Script:\s*\{fileID:\s*\d+,\s*guid:\s*([0-9a-f]{32})')
RE_GUID = re.compile(r'guid:\s*([0-9a-f]{32})')
RE_META_GUID = re.compile(r'guid:\s*([0-9a-f]{32})')
RE_NODE = re.compile(r'(?:GetChild|GetComponent<[^>]+>|AddListener\([^,]+,)\s*\(?\s*"([^"]+)"')
RE_ASSETPATH = re.compile(r'assetPath\s*=>\s*"([^"]+)"')


def walk_files(root: str, exts: tuple[str, ...]):
    for dp, dn, fn in os.walk(root):
        if any(x in dp for x in SKIP_DIRS):
            dn[:] = []
            continue
        for f in fn:
            if f.endswith(exts):
                yield os.path.join(dp, f)


def read(p: str) -> str:
    try:
        return open(p, encoding='utf-8', errors='replace').read()
    except OSError:
        return ''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--assets', required=True, help='Unity Assets 目录绝对路径')
    ap.add_argument('--prefabs', required=True, help='相对 Assets 的 prefab 路径，逗号分隔')
    ap.add_argument('--keyword', required=True, help='模块关键词（判定专属脚本 / 搜相关 cs），逗号分隔')
    ap.add_argument('--code-root', default='', help='只扫这个子目录下的 .cs（相对 Assets，留空=全扫）')
    a = ap.parse_args()

    assets = a.assets
    kws = [k.strip() for k in a.keyword.split(',') if k.strip()]
    prefabs = [p.strip().replace('/', os.sep) for p in a.prefabs.split(',') if p.strip()]

    # prefab 自身 GUID + 引用的脚本 GUID
    own_guid, script_guids = {}, {}
    for rel in prefabs:
        full = os.path.join(assets, rel)
        meta = read(full + '.meta')
        m = RE_META_GUID.search(meta)
        own_guid[rel] = m.group(1) if m else '?'
        script_guids[rel] = sorted(set(RE_SCRIPT_GUID.findall(read(full))))
        print(f'{rel}  guid={own_guid[rel]}  引用脚本GUID={len(script_guids[rel])}')
    rev_own = {v: k for k, v in own_guid.items()}

    print('\n=== prefab 互相嵌套 ===')
    for rel in prefabs:
        txt = read(os.path.join(assets, rel))
        hit = {os.path.basename(rev_own[g]) for g in RE_GUID.findall(txt)
               if g in rev_own and rev_own[g] != rel}
        print(f'  {os.path.basename(rel)} → {sorted(hit) if hit else "无（各自独立加载）"}')

    # 扫 .cs.meta 反解脚本 GUID；同时收集相关 .cs
    need = set(g for v in script_guids.values() for g in v)
    g2cs, related = {}, []
    code_root = os.path.join(assets, a.code_root) if a.code_root else assets
    for fp in walk_files(assets, ('.cs.meta',)):
        t = read(fp)[:400]
        m = RE_META_GUID.search(t)
        if m and m.group(1) in need:
            g2cs[m.group(1)] = os.path.relpath(fp[:-5], assets).replace(os.sep, '/')
    for fp in walk_files(code_root, ('.cs',)):
        if any(k.lower() in os.path.basename(fp).lower() for k in kws):
            related.append(fp)

    print(f'\n=== prefab 上挂的脚本（GUID 反解 {len(g2cs)}/{len(need)}，未解=内置/DLL）===')
    for rel in prefabs:
        named = sorted(g2cs[g] for g in script_guids[rel] if g in g2cs)
        own = [s for s in named if any(k in s for k in kws)]
        print(f'  {os.path.basename(rel)}')
        print(f'    ★专属: {own or "无 —— 绑定靠代码节点路径，不靠挂脚本"}')
        print(f'    通用件: {[os.path.basename(s) for s in named if s not in own]}')

    print('\n=== 谁加载这些 prefab（assetPath / GUID 引用）===')
    for fp in sorted(set(related)):
        txt = read(fp)
        aps = RE_ASSETPATH.findall(txt)
        if aps:
            rel = os.path.relpath(fp, assets).replace(os.sep, '/')
            for ap_ in aps:
                print(f'  {rel}\n      assetPath = "{ap_}"')

    print('\n=== 代码硬编码的节点路径（换皮必须原样保留）===')
    for fp in sorted(set(related)):
        nodes = sorted(set(n for n in RE_NODE.findall(read(fp)) if '/' in n or n[:1].isupper()))
        if nodes:
            print(f'\n  -- {os.path.relpath(fp, assets)}')
            for n in nodes:
                print(f'     {n}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
