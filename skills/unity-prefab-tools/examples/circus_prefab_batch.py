# -*- coding: utf-8 -*-
# 马戏扭蛋机 prefab 三批改动一次打包：占位图×3 + 关英雄层×6 + BtnBlue/GiftEntry 子树接回
import io
import re
import subprocess

CUR_P = r'C:\x3-project\client\Assets\Res\UI\Prefab\Activity\UIActvCircusGacha.prefab'
META = r'C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_global_circus_gachacoin.png.meta'
COIN = re.search(r'guid: ([0-9a-f]{32})', io.open(META, encoding='utf-8').read()).group(1)
HEAD = subprocess.run(['git', '-C', r'C:\x3-project', 'show',
                       'HEAD:client/Assets/Res/UI/Prefab/Activity/UIActvCircusGacha.prefab'],
                      capture_output=True).stdout.decode('utf-8', errors='replace')

ANCH = ['NormalItemRecycle/Viewport/ItemTemplate/ItemMid/Scale',
        'SpecialItemRecycle/Viewport/ItemTemplate/ItemMid/Scale',
        'ContReward/ItemParent/Item/ItemMid/Scale']
BTN_RT, BTN_FA, BTN_IDX = 949679887724544909, 7858383133599527571, 1
GIF_RT, GIF_FA, GIF_IDX = 7285065598146952034, 1719464536841538464, 4
ICON_RT = 8612069594649112394


def parse(text):
    parts = re.split(r'(^--- !u!\d+ &\d+\n)', text, flags=re.M)
    docs = []
    for i in range(1, len(parts), 2):
        m = re.match(r'--- !u!(\d+) &(\d+)\n', parts[i])
        docs.append([int(m.group(1)), int(m.group(2)), parts[i], parts[i + 1]])
    return parts[0], docs


def build_tree(docs):
    gos, rt = {}, {}
    for d in docs:
        if d[0] == 1:
            gos[d[1]] = re.search(r'm_Name: (.*)', d[3]).group(1).strip()
        elif d[0] == 224:
            g = int(re.search(r'm_GameObject: \{fileID: (\d+)\}', d[3]).group(1))
            fa = int(re.search(r'm_Father: \{fileID: (\d+)\}', d[3]).group(1))
            ch = ([int(x) for x in re.findall(r'  - \{fileID: (\d+)\}',
                  d[3].split('m_Children:')[1].split('m_Father')[0])]
                  if 'm_Children:' in d[3] else [])
            rt[d[1]] = dict(go=g, fa=fa, ch=ch)
    return gos, rt


cur = io.open(CUR_P, encoding='utf-8', newline='').read()
ch_, cdocs = parse(cur)
gos, rt = build_tree(cdocs)
go2rt = {v['go']: k for k, v in rt.items()}


def path(g):
    out, t = [], go2rt.get(g)
    while t in rt:
        out.append(gos.get(rt[t]['go'], '?'))
        t = rt[t]['fa']
    return '/'.join(reversed(out))


# ---- 批1+2: 占位图 & 关英雄层 ----
icon_fids, hide_fids = set(), set()
for g, name in gos.items():
    p = path(g)
    if any(a in p for a in ANCH):
        if p.endswith('Scale/Icon'):
            icon_fids.add(g)
        if p.endswith('Scale/HeroIconMask') or p.endswith('Scale/heroFrameList'):
            hide_fids.add(g)
sw = hid = 0
for d in cdocs:
    if d[0] == 114 and 'm_Sprite:' in d[3]:
        mg = re.search(r'm_GameObject: \{fileID: (\d+)\}', d[3])
        if mg and int(mg.group(1)) in icon_fids:
            d[3], n = re.subn(r'(m_Sprite: \{fileID: \d+, guid: )[0-9a-f]{32}', r'\g<1>' + COIN, d[3])
            sw += n
    elif d[0] == 1 and d[1] in hide_fids and 'm_IsActive: 1' in d[3]:
        d[3] = d[3].replace('m_IsActive: 1', 'm_IsActive: 0')
        hid += 1
off_total = sum(1 for d in cdocs if d[0] == 1 and d[1] in hide_fids and 'm_IsActive: 0' in d[3])
assert sw == 3, ('占位图替换数不对', sw)
assert off_total == 6, ('英雄层最终关闭总数不对', off_total, '本次新关', hid)

# ---- 批3: 子树接回 ----
hh, hdocs = parse(HEAD)
hmap = {d[1]: d for d in hdocs}
hgos, hrt = build_tree(hdocs)
subtree = []
for root in (BTN_RT, GIF_RT):
    tset, q = [root], [root]
    while q:
        t = q.pop()
        for c in hrt[t]['ch']:
            if c in hrt:
                tset.append(c)
                q.append(c)
    goset = {hrt[t]['go'] for t in tset}
    for d in hdocs:
        mg = re.search(r'm_GameObject: \{fileID: (\d+)\}', d[3]) if d[0] != 1 else None
        if (d[0] == 1 and d[1] in goset) or (mg and int(mg.group(1)) in goset):
            subtree.append(d)
cur_map = {d[1]: d for d in cdocs}
overwritten = 0
for d in subtree:
    if d[1] in cur_map:  # 孤儿(如 BtnBlue/icon 五件套): 整块回写 HEAD 版
        cur_map[d[1]][3] = hmap[d[1]][3]
        overwritten += 1
for fa_fid, root_fid, idx, drop in [(BTN_FA, BTN_RT, BTN_IDX, ICON_RT), (GIF_FA, GIF_RT, GIF_IDX, None)]:
    ok = False
    for d in cdocs:
        if d[0] == 224 and d[1] == fa_fid:
            pre, seg = d[3].split('m_Children:')
            childpart, rest = seg.split('m_Father', 1)
            kids = re.findall(r'  - \{fileID: \d+\}\n', childpart)
            if drop:
                kids = [k for k in kids if str(drop) not in k]
            kids.insert(min(idx, len(kids)), '  - {fileID: %d}\n' % root_fid)
            d[3] = pre + 'm_Children:\n' + ''.join(kids) + '  m_Father' + rest
            ok = True
    assert ok, ('父transform缺失', fa_fid)
new_docs = [d for d in subtree if d[1] not in cur_map]
out = ch_ + ''.join(d[2] + d[3] for d in cdocs) + ''.join(d[2] + d[3] for d in new_docs)
io.open(CUR_P, 'w', encoding='utf-8', newline='').write(out)
print('写入完成: 占位图×%d 英雄层×%d 追加对象×%d 孤儿回写×%d' % (sw, hid, len(new_docs), overwritten))

# ---- 验证 ----
from collections import Counter
final = io.open(CUR_P, encoding='utf-8').read()
n_docs = len(re.findall(r'^--- !u!', final, re.M))
hc = Counter(re.findall(r'^  m_Name: (.+)$', HEAD, re.M))
fc = Counter(re.findall(r'^  m_Name: (.+)$', final, re.M))
missing = {n: hc[n] - fc.get(n, 0) for n in hc if hc[n] - fc.get(n, 0) > 0}
print('验证: 对象数=%d(HEAD=%d) coin=%d处 缺失节点=%s' % (
    n_docs, len(re.findall(r'^--- !u!', HEAD, re.M)), final.count(COIN), missing or '无'))
