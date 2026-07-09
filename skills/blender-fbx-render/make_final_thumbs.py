# -*- coding: utf-8 -*-
"""Build final thumbnails: artist sprite PNG preferred, Blender render fallback."""
import os, re, json, io, base64
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew"
RENDERS = os.path.join(HERE, 'renders')
sprites = json.load(open(os.path.join(HERE, 'p2_sprite_pngs.json'), encoding='utf-8'))

def pick_sprite(skin, items):
    s8 = [x for x in items if x['ttype'] == 8]
    # drop effect overlays / item icons when alternatives exist
    core = [x for x in s8 if not re.search(r'effect|itemstrong', x['path'], re.I)]
    pool = core or s8
    if not pool:
        return None
    def key(x):
        base = os.path.basename(x['path'])
        m = re.search(r'[Ll][Vv]\s*(\d+(?:\.\d+)?)', base)
        if m:
            return (1, float(m.group(1)))
        m = re.search(r'(\d{6,})', base)
        if m:
            return (0, int(m.group(1)))
        m = re.search(r'(\d+)', base)
        return (0, int(m.group(1)) if m else 0)
    pool.sort(key=key)
    return pool[-1]['path']

thumbs, sources = {}, {}
for skin, items in sprites.items():
    sp = pick_sprite(skin, items)
    src = None
    if sp:
        src, kind = os.path.join(ROOT, skin, sp.replace('/', os.sep)), 'icon'
    else:
        rp = os.path.join(RENDERS, skin + '.png')
        if os.path.exists(rp):
            src, kind = rp, 'render'
    if not src:
        continue
    img = Image.open(src).convert('RGBA')
    if kind == 'render':
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
    img.thumbnail((220, 220), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    thumbs[skin] = base64.b64encode(buf.getvalue()).decode()
    sources[skin] = {'kind': kind, 'file': os.path.basename(src)}

json.dump(thumbs, open(os.path.join(HERE, 'p2_thumbs.json'), 'w'))
json.dump(sources, open(os.path.join(HERE, 'p2_thumb_sources.json'), 'w'), indent=1)
icon_n = sum(1 for v in sources.values() if v['kind'] == 'icon')
print('thumbs:', len(thumbs), 'icons:', icon_n, 'renders:', len(thumbs) - icon_n,
      'total_kb:', sum(len(v) for v in thumbs.values()) // 1024)
for k, v in sources.items():
    print(f"{k:32s} {v['kind']:6s} {v['file']}")
