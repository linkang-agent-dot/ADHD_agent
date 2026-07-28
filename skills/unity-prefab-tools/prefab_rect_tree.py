# -*- coding: utf-8 -*-
r"""Unity prefab YAML 结构速查：不开 Unity 打印节点的 RectTransform 链/子节点锚定参数。

用法:
  python prefab_rect_tree.py <prefab路径> --node Top          # 打印所有名为 Top 的节点参数 + 其直接子节点
  python prefab_rect_tree.py <prefab路径> --chain <节点名>     # 打印该节点到根的父链(锚点/位置/尺寸)
  python prefab_rect_tree.py <prefab路径> --key <languageKey>  # 按 TFWText languageKey 定位节点并打印父链
  python prefab_rect_tree.py <prefab路径> --img <节点名>        # 子节点的 Image 属性(type/fill/sprite guid)+真实渲染顺序

典型用途：
1. 诊断「prefab 编辑器里位置怪、运行时又对」——看目标节点是否拉伸锚定(负 sizeDelta)，
   见 KB\方法论\活动程序开发\X3客户端GUI知识.md「拉伸锚定节点在 prefab 编辑模式下错位是正常的」。
2. `--img` 诊断进度条/填充类控件：**Image 的 m_Type 决定 fillAmount 有没有用**——只有 Filled(3) 才吃
   fillAmount，Sliced(1)/Simple(0) 写了不报错但毫无效果，这类条要改锚点比例填充。
   见同文档「分档积分轨道的段内进度填充」。--node/--img 的子节点均按 m_Children 真实顺序（后者盖前者）。
"""
import argparse
import io
import re


IMG_TYPES = {'0': 'Simple', '1': 'Sliced', '2': 'Tiled', '3': 'Filled'}


def parse(path):
    text = io.open(path, encoding='utf-8').read()
    blocks = re.split(r'^--- !u!(\d+) &(\d+)\n', text, flags=re.M)
    docs = [(int(blocks[i]), int(blocks[i + 1]), blocks[i + 2]) for i in range(1, len(blocks), 3)]
    gos, rts, keyowners, imgs = {}, {}, [], {}
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
            seg = body.split('m_Children:')
            kids = [int(x) for x in re.findall(r'\{fileID: (\d+)\}', seg[1].split('m_Father:')[0])] if len(seg) > 1 else []
            rts[fid] = dict(go=g, fa=fa, kids=kids, **vals)
        elif cls == 114:
            mg = re.search(r'm_GameObject: \{fileID: (\d+)\}', body)
            mk = re.search(r'languageKey: (.+)', body)
            if mg and mk:
                mc = re.search(r'm_Color: \{r: ([\d.]+), g: ([\d.]+), b: ([\d.]+), a: ([\d.]+)\}', body)
                hexc = ('#%02X%02X%02X a=%.2f' % tuple(
                    [round(float(mc.group(i)) * 255) for i in (1, 2, 3)] + [float(mc.group(4))])) if mc else '?'
                keyowners.append((mk.group(1).strip(), int(mg.group(1)), hexc))
            # Image/TFWImage：判 sprite 字段存在
            if mg and re.search(r'm_Sprite: ', body):
                def _g(pat, default='-'):
                    m = re.search(pat, body)
                    return m.group(1) if m else default
                sp = re.search(r'm_Sprite: \{fileID: (-?\d+)(?:, guid: ([0-9a-f]+))?', body)
                imgs[int(mg.group(1))] = dict(
                    type=IMG_TYPES.get(_g(r'm_Type: (\d+)'), _g(r'm_Type: (\d+)')),
                    fillMethod=_g(r'm_FillMethod: (\d+)'),
                    fillOrigin=_g(r'm_FillOrigin: (\d+)'),
                    fillAmount=_g(r'm_FillAmount: ([\d.]+)'),
                    enabled=_g(r'm_Enabled: (\d)'),
                    guid=(sp.group(2) if sp and sp.group(2) else 'NONE(白块)'),
                )
    return gos, rts, keyowners, imgs


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
    ap.add_argument('--img', help='按节点名打印其子树第一层的 Image 属性(type/fill/sprite)+真实兄弟顺序')
    a = ap.parse_args()
    gos, rts, keyowners, imgs = parse(a.prefab)
    go2rt = {d['go']: fid for fid, d in rts.items()}
    if a.node:
        for fid, d in rts.items():
            if gos.get(d['go'], ('?',))[0] == a.node:
                print('==', fmt(gos, d))
                # 按 m_Children 真实顺序（后者盖前者），而非字典遍历序
                for fid2 in d['kids']:
                    if fid2 in rts:
                        print('  ', fmt(gos, rts[fid2]))
    if a.img:
        for fid, d in rts.items():
            if gos.get(d['go'], ('?',))[0] != a.img:
                continue
            print('== %s children (render order, later covers earlier):' % a.img)
            for i, fid2 in enumerate(d['kids']):
                if fid2 not in rts:
                    continue
                d2 = rts[fid2]
                nm = gos.get(d2['go'], ('?', '?'))[0]
                im = imgs.get(d2['go'])
                line = '  [%d] %-16s aMin=%-14s aMax=%-14s size=%-16s piv=%s' % (
                    i, nm, d2['m_AnchorMin'], d2['m_AnchorMax'], d2['m_SizeDelta'], d2['m_Pivot'])
                print(line)
                if im:
                    print('       Image type=%-7s fillMethod=%s fillOrigin=%s fillAmount=%s enabled=%s sprite=%s'
                          % (im['type'], im['fillMethod'], im['fillOrigin'], im['fillAmount'], im['enabled'], im['guid']))
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
