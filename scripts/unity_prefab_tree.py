# -*- coding: utf-8 -*-
"""打印 Unity prefab 的节点树（不开 Unity 看真实层级/节点名）。

用法: python unity_prefab_tree.py <prefab路径> [最大深度,默认6]
用途: 远程指导拼 prefab、核对 FindByFullPath 路径、写操作指南前确认模板真实结构。
局限: 嵌套 prefab 实例(class 1001 PrefabInstance,如 UIBtnPurchase 这类蓝色节点)看不到——
      它们在 YAML 里是 PrefabInstance+修改记录,不是内联 GameObject 块。读不到≠节点不存在!
      核对绑定路径时,嵌套 prefab 节点要去 Unity Hierarchy 里另行确认。
"""
import re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = sys.argv[1]
maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 6
text = open(path, encoding='utf-8', errors='replace').read()

blocks = re.split(r'^--- !u!(\d+) &(\d+)\s*$', text, flags=re.M)
go_name, tr_go, tr_children, tr_parent = {}, {}, {}, {}

i = 1
while i < len(blocks):
    cls, fid, body = blocks[i], blocks[i + 1], blocks[i + 2]
    i += 3
    if cls == '1':  # GameObject
        m = re.search(r'm_Name: (.*)', body)
        go_name[fid] = m.group(1).strip() if m else '?'
    elif cls in ('4', '224'):  # Transform / RectTransform
        m = re.search(r'm_GameObject: \{fileID: (\d+)\}', body)
        if m:
            tr_go[fid] = m.group(1)
        if 'm_Children:' in body:
            seg = body.split('m_Children:')[1].split('m_Father')[0]
            tr_children[fid] = re.findall(r'- \{fileID: (\d+)\}', seg)
        pm = re.search(r'm_Father: \{fileID: (\d+)\}', body)
        if pm:
            tr_parent[fid] = pm.group(1)

roots = [t for t in tr_go if tr_parent.get(t, '0') == '0' or tr_parent.get(t) not in tr_go]

def dump(t, depth=0):
    print('  ' * depth + go_name.get(tr_go.get(t), '?'))
    if depth < maxdepth:
        for c in tr_children.get(t, []):
            if c in tr_go:
                dump(c, depth + 1)

for r in roots:
    dump(r)
