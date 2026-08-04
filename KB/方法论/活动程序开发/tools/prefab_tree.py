# -*- coding: utf-8 -*-
"""
解析 Unity prefab YAML 的节点层级，打印某个子树的完整路径列表。

为什么需要：写 Auto_ 绑定时**路径必须对真 prefab 逐条断言**，靠"照 X2 层级猜"是限时抢购
第一版界面大面积不工作的根因。而 prefab 是几十万行 YAML，`grep m_Name` 只能证明"这个名字
存在于文件某处"，证不了"它在这条父子链上"。

限制：**嵌套 PrefabInstance 的内部节点不在本文件里**（如 ItemMid 的子节点），本工具看不到；
     那种情况只能运行时 dump（go.transform 遍历）。X2 原生节点都是普通 GameObject，可解析。

用法：python prefab_tree.py <prefab路径> [子树根节点名] [最大深度]
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def parse(path):
    """返回 (go: fileID->name, tr: fileID->(children, gameObject), go2tr: goID->trID)"""
    text = open(path, encoding='utf-8', errors='replace').read()
    blocks = text.split('--- !u!')

    go = {}        # GameObject fileID -> name
    tr_children = {}   # Transform fileID -> [child transform fileIDs]
    tr_go = {}     # Transform fileID -> GameObject fileID
    go_tr = {}     # GameObject fileID -> Transform fileID

    for b in blocks[1:]:
        head = b.split('\n', 1)[0]
        m = re.match(r'(\d+)\s+&(\d+)', head)
        if not m:
            continue
        cls, fid = m.group(1), m.group(2)

        if cls == '1':   # GameObject
            nm = re.search(r'^  m_Name: (.*)$', b, re.M)
            if nm:
                go[fid] = nm.group(1).strip()
        elif cls in ('4', '224'):   # Transform / RectTransform
            gm = re.search(r'^  m_GameObject: \{fileID: (\d+)\}', b, re.M)
            if gm:
                tr_go[fid] = gm.group(1)
                go_tr[gm.group(1)] = fid
            ch = re.search(r'^  m_Children:\n((?:  - \{fileID: \d+\}\n)*)', b, re.M)
            kids = re.findall(r'\{fileID: (\d+)\}', ch.group(1)) if ch else []
            tr_children[fid] = kids

    return go, tr_children, tr_go, go_tr


def walk(trid, go, tr_children, tr_go, prefix, depth, maxdepth, out):
    gid = tr_go.get(trid)
    name = go.get(gid, '?')
    path = name if not prefix else prefix + '/' + name
    out.append((depth, path))
    if depth >= maxdepth:
        return
    for kid in tr_children.get(trid, []):
        walk(kid, go, tr_children, tr_go, path, depth + 1, maxdepth, out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    root_name = sys.argv[2] if len(sys.argv) > 2 else None
    maxdepth = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    go, tr_children, tr_go, go_tr = parse(path)
    print('解析: GameObject %d 个 / Transform %d 个' % (len(go), len(tr_children)))

    if not root_name:
        # 找根：没有被任何人当 child 的 transform
        allkids = {k for v in tr_children.values() for k in v}
        roots = [t for t in tr_children if t not in allkids]
        print('根节点 %d 个: %s' % (len(roots), [go.get(tr_go.get(r), '?') for r in roots[:5]]))
        for r in roots:
            out = []
            walk(r, go, tr_children, tr_go, '', 0, maxdepth, out)
            for d, p in out:
                print('  ' + '  ' * d + p)
        return 0

    # 按名字找目标节点（可能多个同名）
    targets = [gid for gid, nm in go.items() if nm == root_name]
    if not targets:
        print('找不到名为 %s 的节点' % root_name)
        return 1
    print('名为 %s 的节点 %d 个' % (root_name, len(targets)))
    for gid in targets[:4]:
        trid = go_tr.get(gid)
        if not trid:
            continue
        out = []
        walk(trid, go, tr_children, tr_go, '', 0, maxdepth, out)
        print('--- 实例 (goID=%s) ---' % gid)
        for d, p in out:
            print('  ' + '  ' * d + p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
