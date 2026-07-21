# -*- coding: utf-8 -*-
r"""Unity prefab YAML 结构速查：不开 Unity 打印节点的 RectTransform 链/子节点锚定参数。

用法:
  python prefab_rect_tree.py <prefab路径> --node Top          # 打印所有名为 Top 的节点参数 + 其直接子节点
  python prefab_rect_tree.py <prefab路径> --chain <节点名>     # 打印该节点到根的父链(锚点/位置/尺寸)
  python prefab_rect_tree.py <prefab路径> --key <languageKey>  # 按 TFWText languageKey 定位节点并打印父链

典型用途：诊断「prefab 编辑器里位置怪、运行时又对」——看目标节点是否拉伸锚定(负 sizeDelta)，
见 KB\方法论\活动程序开发\X3客户端GUI知识.md「拉伸锚定节点在 prefab 编辑模式下错位是正常的」。
"""
import argparse
import io
import re


def parse(path):
    text = io.open(path, encoding='utf-8').read()
    blocks = re.split(r'^--- !u!(\d+) &(\d+)\n', text, flags=re.M)
    docs = [(int(blocks[i]), int(blocks[i + 1]), blocks[i + 2]) for i in range(1, len(blocks), 3)]
    gos, rts, keyowners = {}, {}, []
    for cls, fid, body in docs:
        if cls == 1:
            name = re.search(r'm_Name: (.+)', body)
            act = re.search(r'm_IsActive: (\d)', body)
            gos[fid] = (name.group(1).strip() if name else '?', act.group(1) if act else '?')
        elif cls == 224:
            g = int(re.search(r'm_GameObject: \{fileID: (\d+)\}', body).group(1))
            fa = int(re.search(r'm_Father: \{fileID: (\d+)\}', body).group(1))
            vals = {}
            for k in ('m_AnchorMin', 'm_AnchorMax', 'm_AnchoredPosition', 'm_SizeDelta', 'm_Pivot'):
                m = re.search(k + r': (\{[^}]+\})', body)
                vals[k] = m.group(1) if m else '?'
            rts[fid] = dict(go=g, fa=fa, **vals)
        elif cls == 114:
            mg = re.search(r'm_GameObject: \{fileID: (\d+)\}', body)
            mk = re.search(r'languageKey: (.+)', body)
            if mg and mk:
                mc = re.search(r'm_Color: \{r: ([\d.]+), g: ([\d.]+), b: ([\d.]+), a: ([\d.]+)\}', body)
                hexc = ('#%02X%02X%02X a=%.2f' % tuple(
                    [round(float(mc.group(i)) * 255) for i in (1, 2, 3)] + [float(mc.group(4))])) if mc else '?'
                keyowners.append((mk.group(1).strip(), int(mg.group(1)), hexc))
    return gos, rts, keyowners


def fmt(gos, d):
    n, act = gos.get(d['go'], ('?', '?'))
    return '%-18s act=%s aMin=%-14s aMax=%-14s pos=%-22s size=%-22s piv=%s' % (
        n, act, d['m_AnchorMin'], d['m_AnchorMax'], d['m_AnchoredPosition'], d['m_SizeDelta'], d['m_Pivot'])


def chain_of(gos, rts, go2rt, go_fid):
    out, tfid = [], go2rt.get(go_fid)
    while tfid in rts:
        out.append(fmt(gos, rts[tfid]))
        tfid = rts[tfid]['fa']
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prefab')
    ap.add_argument('--node', help='按节点名打印参数+直接子节点')
    ap.add_argument('--chain', help='按节点名打印到根的父链')
    ap.add_argument('--key', help='按 languageKey 定位并打印父链')
    a = ap.parse_args()
    gos, rts, keyowners = parse(a.prefab)
    go2rt = {d['go']: fid for fid, d in rts.items()}
    if a.node:
        for fid, d in rts.items():
            if gos.get(d['go'], ('?',))[0] == a.node:
                print('==', fmt(gos, d))
                for fid2, d2 in rts.items():
                    if d2['fa'] == fid:
                        print('  ', fmt(gos, d2))
    if a.chain:
        for fid, d in rts.items():
            if gos.get(d['go'], ('?',))[0] == a.chain:
                print('== chain of', a.chain)
                for line in chain_of(gos, rts, go2rt, d['go']):
                    print('  ', line)
    if a.key:
        for k, g, hexc in keyowners:
            if a.key in k:
                print('== languageKey:', k, ' color=', hexc)
                for line in chain_of(gos, rts, go2rt, g):
                    print('  ', line)


if __name__ == '__main__':
    main()
