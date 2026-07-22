# -*- coding: utf-8 -*-
r"""
prefab_dependency_bundler.py
把一个/多个 Unity prefab 的依赖(贴图/材质/动画/shader/子prefab)解析出来,
按 guid 反查源文件,分类拷贝进一个自包含 bundle 目录 + 写 _manifest.txt。
复现 X2 Unity Editor "导出 prefab 依赖" 工具(D:\newX2\Copy\UIactvfesstrong 那种格式),
用于 X2->X3 UI 换皮时把源资产拷出来验收/搬运。

用法:
  python prefab_dependency_bundler.py \
    --prefab <p1.prefab> [<p2.prefab> ...] \
    --index-root <Assets/x2/Res/UI> [--index-root <Assets/P2/Res/UI> ...] \
    --out <输出bundle目录>

分类规则(按扩展名): png->Images  tga/psd->Textures  mat->Materials
  anim/controller->Animations  shader->Shaders  prefab->Prefabs  其它->Other
manifest 末尾列 UNRESOLVED guids(=共享图集/跨项目缺口,需人工确认)。
"""
import os, re, sys, shutil, argparse

GUID_RE = re.compile(rb'guid: ([0-9a-f]{32})')
META_GUID_RE = re.compile(r'guid:\s*([0-9a-f]{32})')

CAT = {
    '.png': 'Images', '.jpg': 'Images', '.jpeg': 'Images',
    '.tga': 'Textures', '.psd': 'Textures', '.exr': 'Textures',
    '.mat': 'Materials',
    '.anim': 'Animations', '.controller': 'Animations',
    '.shader': 'Shaders', '.shadergraph': 'Shaders',
    '.prefab': 'Prefabs',
    '.asset': 'Assets',  # spine skeletonData / scriptableobject 等
}

# 代码/工程类:解析到就算命中,但不拷贝(X3 侧重写),manifest 里只列名
SKIP_COPY_EXT = {'.cs', '.js', '.dll', '.asmdef', '.asmref'}

def collect_guids(prefab_paths):
    guids = set()
    for p in prefab_paths:
        with open(p, 'rb') as f:
            for m in GUID_RE.finditer(f.read()):
                guids.add(m.group(1).decode())
    return guids

def build_index(roots):
    """walk .meta under roots -> {guid: asset_abspath(去掉.meta)}"""
    idx = {}
    for root in roots:
        for dp, _, files in os.walk(root):
            for fn in files:
                if not fn.endswith('.meta'):
                    continue
                mp = os.path.join(dp, fn)
                try:
                    with open(mp, 'r', encoding='utf-8', errors='ignore') as f:
                        head = f.read(400)
                except Exception:
                    continue
                m = META_GUID_RE.search(head)
                if m:
                    idx.setdefault(m.group(1), mp[:-5])  # strip .meta
    return idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefab', nargs='+', required=True)
    ap.add_argument('--index-root', dest='roots', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--repo-root', default='', help='用于 manifest 里显示相对路径')
    args = ap.parse_args()

    guids = collect_guids(args.prefab)
    print(f'[1] {len(args.prefab)} prefab -> {len(guids)} unique guids')

    print(f'[2] building guid index over {len(args.roots)} roots ...')
    idx = build_index(args.roots)
    print(f'    indexed {len(idx)} assets')

    os.makedirs(args.out, exist_ok=True)
    resolved, unresolved, skipped = [], [], []
    for g in sorted(guids):
        src = idx.get(g)
        if not src or not os.path.exists(src):
            unresolved.append(g)
            continue
        ext = os.path.splitext(src)[1].lower()
        rel0 = os.path.relpath(src, args.repo_root) if args.repo_root else src
        if ext in SKIP_COPY_EXT:
            skipped.append(rel0)
            continue
        cat = CAT.get(ext, 'Other')
        dst_dir = os.path.join(args.out, cat)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.basename(src))
        shutil.copy2(src, dst)
        if os.path.exists(src + '.meta'):
            shutil.copy2(src + '.meta', dst + '.meta')
        rel = os.path.relpath(src, args.repo_root) if args.repo_root else src
        resolved.append((cat, rel))

    # 拷 prefab 本体进 Prefabs/
    pfdir = os.path.join(args.out, 'Prefabs')
    os.makedirs(pfdir, exist_ok=True)
    for p in args.prefab:
        shutil.copy2(p, os.path.join(pfdir, os.path.basename(p)))
        if os.path.exists(p + '.meta'):
            shutil.copy2(p + '.meta', os.path.join(pfdir, os.path.basename(p) + '.meta'))

    # manifest
    lines = []
    lines.append('Source prefabs:')
    for p in args.prefab:
        rel = os.path.relpath(p, args.repo_root) if args.repo_root else p
        lines.append('  ' + rel)
    lines.append('=' * 60)
    from collections import defaultdict
    bycat = defaultdict(list)
    for cat, rel in resolved:
        bycat[cat].append(rel)
    for cat in sorted(bycat):
        lines.append(f'\n[{cat} {len(bycat[cat])}]')
        lines.extend('  ' + r for r in sorted(bycat[cat]))
    if skipped:
        lines.append(f'\n[Scripts(命中但不拷,X3重写) {len(skipped)}]')
        lines.extend('  ' + r for r in sorted(skipped))
    lines.append('\n' + '=' * 60)
    lines.append(f'[UNRESOLVED guids {len(unresolved)}] (共享图集/跨项目缺口,需人工确认或美术重出)')
    lines.extend('  ' + g for g in unresolved)
    with open(os.path.join(args.out, '_manifest.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'[3] resolved {len(resolved)} / scripts(skip) {len(skipped)} / unresolved {len(unresolved)}')
    print(f'    bundle -> {args.out}')

if __name__ == '__main__':
    main()
