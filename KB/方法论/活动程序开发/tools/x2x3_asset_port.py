#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
X2/P2 → X3 UI 资产搬运：依赖差集计算 + 保 guid 落地

背景：X2/P2/X3 同源，大量公共资产在 X3 里已存在且 guid 相同（原地解析、零拷贝）。
      整包倒进 X3 会造出一堆重复副本，后续 X3 公共件改版你这套不跟着走。
      本工具算出「X3 已有 vs 必须拷」，只搬必须的，并保住 .meta（guid 靠它）。

前置：先用 x2client 的 Editor 工具导出资产包
      Tools ▸ X2 ▸ Prefab Asset Export  → <输出目录>\<prefab名>\{Images,Textures,Materials,Animations,Shaders,Prefabs}
      ⚠️ 输出目录每次填本次专属目录（默认目录会把历史包掺进来，重名加 _1 后缀而非覆盖）

用法（三步，索引可复用）：
  # 1. 建 X3 guid 索引（扫 3~4 万个 .meta，约 10 分钟，建议后台跑；X3 没大改动可复用缓存）
  python x2x3_asset_port.py index --x3 C:\x3-project\client

  # 2. 算差集 + 出落地计划（预演，不写盘）
  python x2x3_asset_port.py plan --pkg D:\newX2\FlashSale D:\newX2\FlashSalePop --actv UIActvFlashSale

  # 3. 确认无误后执行（⚠️ X3 的 Unity 必须关闭）
  python x2x3_asset_port.py plan --pkg ... --actv UIActvFlashSale --go

  # 4. 落地后、开 Unity 前先算「哪些脚本会 missing」（省得靠 Console 慢慢刷）
  python x2x3_asset_port.py scripts --x3 C:\x3-project\client --x2 D:\UGit\x2client\client \
         --prefab FlashSale.prefab FlashSaleItem.prefab FlashSalePop.prefab FlashSaleRewardGet.prefab
  # 输出：唯一脚本 guid 数 / 组件实例数 / X3 共享的 / X3 缺的（＝要补的 X3 等价件清单）
  # ⚠️ 反查脚本名必须连 Packages/ 一起扫，只扫 Assets 会有解不出的（限时抢购 19 个全解不出）

落点约定（2026-07-31 拿 108 个已有件实证，别照 X2 路径平移——只有 68% 能平移）：
  Images     → Assets/Res/UI/Sprite/<活动名>/Images
  Animations → Assets/Res/UI/Animation/<活动名>      ← 子目录，避开同名不同 guid 碰撞（先例 HeroClub）
  Materials  → Assets/Res/UI/Materials/<活动名>       ← 先例 UIActvLaborGacha
  Textures   → Assets/Res/UI/Materials/<活动名>/Textures
  Shaders    → Assets/Res/Shader/Effect
  Prefabs    → Assets/Res/UI/Prefab/Activity          ← 代码常硬编码此路径，不能改名换目录
  两条 X3 真实约定：① Effect/Material 在 X3 叫 Materials(复数) ② 换皮带进来的公共件塞进本活动自己的目录

安全设计：
  - 只新增不覆盖：目标已存在一律 SKIP 并报告（同名不同 guid 会覆盖掉 X3 原件，必须人工裁决）
  - 同名多份（导出包里的 _1 副本）先比 MD5，一致才自动取非 _1 的；不一致挂起等人工
  - 落地全是 untracked，回退 = git clean -fd 那几个目录
"""
import os, re, io, sys, json, shutil, hashlib, argparse, collections

CATS = ['Prefabs', 'Images', 'Animations', 'Materials', 'Textures', 'Shaders']
GUID_RE = re.compile(r'^guid:\s*([0-9a-f]{32})', re.M)


def target_map(actv):
    return {
        'Images':     os.path.join('Assets', 'Res', 'UI', 'Sprite', actv, 'Images'),
        'Animations': os.path.join('Assets', 'Res', 'UI', 'Animation', actv),
        'Materials':  os.path.join('Assets', 'Res', 'UI', 'Materials', actv),
        'Textures':   os.path.join('Assets', 'Res', 'UI', 'Materials', actv, 'Textures'),
        'Shaders':    os.path.join('Assets', 'Res', 'Shader', 'Effect'),
        'Prefabs':    os.path.join('Assets', 'Res', 'UI', 'Prefab', 'Activity'),
    }


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_guid(meta_path):
    try:
        with io.open(meta_path, 'r', encoding='utf-8', errors='ignore') as fh:
            m = GUID_RE.search(fh.read(300))
        return m.group(1) if m else None
    except Exception:
        return None


def cmd_index(args):
    """扫 X3 全部 .meta 建 guid -> 路径 索引"""
    root = os.path.join(args.x3, 'Assets')
    idx, cnt = {}, 0
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith('.meta'):
                continue
            cnt += 1
            g = read_guid(os.path.join(dirpath, f))
            if g:
                rel = os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, '/')[:-5]
                idx.setdefault(g, []).append('Assets/' + rel)
    json.dump(idx, io.open(args.out, 'w', encoding='utf-8'))
    print('scanned .meta: %d   unique guid: %d' % (cnt, len(idx)))
    print('index -> %s' % args.out)


def collect_pkgs(pkgs):
    """从导出包收集 guid -> {分类, 文件名, 磁盘路径候选}"""
    need = {}
    for pk in pkgs:
        for dirpath, _, files in os.walk(pk):
            cat = os.path.basename(dirpath)
            if cat not in CATS:
                continue
            for f in files:
                if f.endswith('.meta'):
                    continue
                mp = os.path.join(dirpath, f + '.meta')
                if not os.path.exists(mp):
                    continue
                g = read_guid(mp)
                if not g:
                    continue
                e = need.setdefault(g, {'cat': cat, 'name': f, 'disk': []})
                e['disk'].append(os.path.join(dirpath, f))
    return need


def cmd_plan(args):
    if not os.path.exists(args.index):
        sys.exit('索引不存在，先跑: %s index --x3 <X3工程client目录>' % os.path.basename(__file__))
    idx = json.load(open(args.index))
    need = collect_pkgs(args.pkg)
    TG = target_map(args.actv)

    have = {g: v for g, v in need.items() if g in idx}
    miss = {g: v for g, v in need.items() if g not in idx}

    plan, warn = [], []
    for g, v in sorted(miss.items(), key=lambda kv: (kv[1]['cat'], kv[1]['name'])):
        disk = v['disk']
        if len({md5(p) for p in disk}) > 1:
            warn.append('同名多份内容不同(人工定): %s -> %s' % (v['name'], disk))
            continue
        # 取不带 _N 后缀的那份
        pick = sorted(disk, key=lambda p: (bool(re.search(r'_\d+(\.[^.]+)?$', os.path.basename(p))), len(p)))[0]
        dst = os.path.join(args.x3, TG[v['cat']], v['name'])
        plan.append((v['cat'], v['name'], pick, dst, len(disk), g))

    L = []
    def P(x=''):
        L.append(x)

    P('=== X2→X3 资产落地计划（%s）===' % ('DRY RUN 预演' if not args.go else '真实执行'))
    P('导出包 : %s' % ', '.join(args.pkg))
    P('X3工程 : %s   活动名: %s' % (args.x3, args.actv))
    P('⚠️ 执行前 X3 的 Unity 必须关闭（Unity 开着拷会吃到导入中间态；拖进 Project 窗口会重生成 guid）')
    P()
    P('依赖唯一 guid %d  →  X3 已有 %d（零拷贝）  /  必须拷 %d' % (len(need), len(have), len(miss)))
    P()
    by = collections.defaultdict(list)
    for row in plan:
        by[row[0]].append(row)
    collide = []
    for cat in CATS:
        if cat not in by:
            continue
        P('[%s %d]  ->  %s' % (cat, len(by[cat]), TG[cat]))
        for cat_, nm, src, dst, k, g in by[cat]:
            flags = ''
            if os.path.exists(dst):
                og = read_guid(dst + '.meta')
                if og == g:
                    flags += '  (已存在·同 guid，跳过)'
                else:
                    flags += '  ⚠️同名不同 guid！会覆盖 X3 原件 → 已跳过，需换目录'
                    collide.append((nm, dst, g, og))
            if k > 1:
                flags += '  (源%d份·MD5同·取非_1)' % k
            P('   %-54s%s' % (nm, flags))
        P()
    P('合计 %d 件（+ .meta = %d 文件）' % (len(plan), len(plan) * 2))

    if collide:
        P()
        P('=== 🔴 同名不同 guid 碰撞 %d 条（必须人工处理）===' % len(collide))
        for nm, dst, g, og in collide:
            P('  %s' % nm)
            P('     要拷的 guid: %s' % g)
            P('     X3 原件 guid: %s  @ %s' % (og, dst))
        P('  处理办法：把这批放进活动专属子目录（先例 Res/UI/Animation/HeroClub、Res/UI/Animation/UIActvFlashSale）')
    if warn:
        P()
        P('=== 需人工处理 %d 条 ===' % len(warn))
        for w in warn:
            P('  ' + w)

    if args.go:
        P()
        P('=== 执行结果 ===')
        ok = skip = 0
        for cat, nm, src, dst, k, g in plan:
            if os.path.exists(dst):
                skip += 1
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            if os.path.exists(src + '.meta'):
                shutil.copy2(src + '.meta', dst + '.meta')
            ok += 1
        P('  拷入 %d，跳过 %d' % (ok, skip))
        P('  ⚠️ 校验用 git status（copy2 保留源 mtime，用 find -newermt 会数出 0）')
        P('  回退: cd <X3仓> && git clean -fd 上面那几个目录')

    txt = '\n'.join(L)
    if args.log:
        io.open(args.log, 'w', encoding='utf-8').write(txt)
        print('log -> %s' % args.log)
    try:
        print(txt)
    except UnicodeEncodeError:
        print('(控制台 GBK 编码不了，看 --log 输出的文件)')


SCRIPT_RE = re.compile(r'm_Script:\s*\{fileID:\s*(-?\d+),\s*guid:\s*([0-9a-f]{32})')


def cs_index(root, with_packages=True):
    """guid -> 脚本相对路径。
    ⚠️ 三处都要扫，少一处就会误报 missing（2026-07-31 实证，两次踩到）：
       Assets/                → 项目自己的脚本
       Packages/              → 内嵌/本地包（UGUI 常在这，LayoutElement/ContentSizeFitter/Shadow…）
       Library/PackageCache/  → 注册表包的实际落地处（Spine 的 SkeletonGraphic、UIEffect 的 Bevel/UIParticleSystem）
    只扫 Assets 会误报 19 个缺失；漏 PackageCache 会误报 4 个。真实答案是 1 个。
    """
    idx = {}
    gp = re.compile(r'^guid:\s*([0-9a-f]{32})', re.M)
    roots = [os.path.join(root, 'Assets')]
    if with_packages:
        roots.append(os.path.join(root, 'Packages'))
        roots.append(os.path.join(root, 'Library', 'PackageCache'))
    for r in roots:
        if not os.path.isdir(r):
            continue
        for dp, _, files in os.walk(r):
            for f in files:
                if not f.endswith('.cs.meta'):
                    continue
                try:
                    with io.open(os.path.join(dp, f), 'r', encoding='utf-8', errors='ignore') as fh:
                        m = gp.search(fh.read(300))
                except Exception:
                    continue
                if m:
                    idx[m.group(1)] = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')[:-5]
    return idx


def cmd_scripts(args):
    """落地 prefab 的脚本引用体检：哪些 X3 认得、哪些会 missing"""
    land = os.path.join(args.x3, 'Assets', 'Res', 'UI', 'Prefab', 'Activity')
    cnt = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    for pf in args.prefab:
        p = pf if os.path.isabs(pf) else os.path.join(land, pf)
        if not os.path.exists(p):
            print('缺 prefab: %s' % p)
            continue
        with io.open(p, 'r', encoding='utf-8', errors='ignore') as fh:
            for fid, g in SCRIPT_RE.findall(fh.read()):
                cnt[g] += 1
                per[os.path.basename(p)][g] += 1

    x3i = cs_index(args.x3)
    x2i = cs_index(args.x2) if args.x2 else {}

    L = []
    def P(x=''):
        L.append(x)
    ok = [g for g in cnt if g in x3i]
    bad = [g for g in cnt if g not in x3i]
    P('=== 脚本引用体检 ===')
    P('唯一脚本 guid %d（组件实例 %d）' % (len(cnt), sum(cnt.values())))
    P('  X3 有   : %d  → 开 Unity 正常认领' % len(ok))
    P('  X3 没有 : %d  → 会报 missing script，共 %d 个实例（＝Console 预期条数）'
      % (len(bad), sum(cnt[g] for g in bad)))
    P()
    P('=== 🔴 要补 X3 等价件的 ===')
    for g, n in cnt.most_common():
        if g in x3i:
            continue
        who = ' / '.join('%s×%d' % (pf.replace('.prefab', ''), per[pf][g]) for pf in per if per[pf][g])
        P('  %5d 实例  %-46s  %s' % (n, os.path.basename(x2i.get(g, '')) or ('guid ' + g), who))
        if g in x2i:
            P('              X2 源: %s' % x2i[g])
    P()
    P('=== ✅ X3 共享同 guid 的（框架层通常全共享）===')
    for g, n in cnt.most_common():
        if g in x3i:
            P('  %5d 实例  %-46s  %s' % (n, os.path.basename(x3i[g]), x3i[g]))
    txt = '\n'.join(L)
    if args.log:
        io.open(args.log, 'w', encoding='utf-8').write(txt)
        print('log -> %s' % args.log)
    try:
        print(txt)
    except UnicodeEncodeError:
        print('(控制台 GBK 编码不了，看 --log)')


def main():
    ap = argparse.ArgumentParser(description='X2/P2 → X3 UI 资产搬运：差集 + 保 guid 落地')
    sub = ap.add_subparsers(dest='cmd', required=True)

    a = sub.add_parser('index', help='建 X3 guid 索引（慢，可复用）')
    a.add_argument('--x3', required=True, help='X3 工程 client 目录')
    a.add_argument('--out', default='x3_guid_index.json')
    a.set_defaults(func=cmd_index)

    b = sub.add_parser('plan', help='算差集 + 落地（默认预演，--go 才写盘）')
    b.add_argument('--pkg', nargs='+', required=True, help='一个或多个导出包目录')
    b.add_argument('--x3', default=r'C:\x3-project\client')
    b.add_argument('--actv', required=True, help='X3 活动名，如 UIActvFlashSale')
    b.add_argument('--index', default='x3_guid_index.json')
    b.add_argument('--log', default='port_plan.txt')
    b.add_argument('--go', action='store_true', help='真实执行（X3 的 Unity 须关闭）')
    b.set_defaults(func=cmd_plan)

    c = sub.add_parser('scripts', help='落地后体检：哪些脚本 X3 认得 / 哪些会 missing')
    c.add_argument('--x3', default=r'C:\x3-project\client')
    c.add_argument('--x2', default=r'D:\UGit\x2client\client', help='用来反查缺失脚本的原名')
    c.add_argument('--prefab', nargs='+', required=True, help='落地后的 prefab 文件名或绝对路径')
    c.add_argument('--log', default='script_check.txt')
    c.set_defaults(func=cmd_scripts)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
