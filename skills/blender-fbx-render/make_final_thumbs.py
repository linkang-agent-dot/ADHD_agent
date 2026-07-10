# -*- coding: utf-8 -*-
"""Build final thumbnails: DK 道具ICON first, folder sprite PNG second, Blender render last."""
import os, re, json, io, base64
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_ROOT = r"E:\P2\client\client"
SKIN_ROOT = os.path.join(LOCAL_ROOT, r"Assets\P2\Res\Map\CityBuildingNew")
RENDERS = os.path.join(HERE, 'renders')
dkmap = json.load(open(os.path.join(HERE, 'dk_icon_map.json'), encoding='utf-8'))
sprites = json.load(open(os.path.join(HERE, 'p2_sprite_pngs.json'), encoding='utf-8'))

EXCLUDE = {'Animation', 'DrillGround', 'MonkeyNest', 'ResourceStation', 'SecurityBox',
           'SecurityBoxMap', 'SurvivorCamp', 'TreasureChest', 'WonderCity',
           'MaincitySkin', 'CityHallLV6'}
data = [d['name'] for d in json.load(open(os.path.join(HERE, 'p2_cityskins.json'), encoding='utf-8'))]
skins = [n for n in data if n not in EXCLUDE]

def pick_folder_sprite(skin):
    items = sprites.get(skin, [])
    s8 = [x for x in items if x['ttype'] == 8]
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
        return (0, int(m.group(1)) if m else 0)
    pool.sort(key=key)
    return os.path.join(SKIN_ROOT, skin, pool[-1]['path'].replace('/', os.sep))

icon_paths = dict(
    (int(k), p.strip()) for k, p in re.findall(
        r'- key: (\d+)\s*\r?\n\s*objPath: (.+)',
        open(os.path.join(HERE, 'bugfix_Path_Icon.asset'), encoding='utf-8', errors='ignore').read()))

def ui_prefab_icon(skin):
    """Fallback: skins whose model isn't DK-registered often have Ui<key>.prefab whose key has an Icon."""
    d = os.path.join(SKIN_ROOT, skin)
    keys = sorted(int(m.group(1)) for f in os.listdir(d)
                  if (m := re.fullmatch(r'Ui(\d+)\.prefab', f)))
    for k in reversed(keys):
        p = icon_paths.get(k)
        if p:
            lp = os.path.join(LOCAL_ROOT, p.replace('/', os.sep))
            if os.path.exists(lp) and os.path.getsize(lp) > 1024:
                return lp, p
    return None, None

thumbs, sources = {}, {}
for skin in skins:
    src = kind = None
    v = dkmap.get(skin)
    if not src and v and v.get('local'):
        src, kind = v['local'], 'icon'
        icon_rel = v['chosen'][1]
    if not src:
        lp, rel = ui_prefab_icon(skin)
        if lp:
            src, kind, icon_rel = lp, 'icon', rel
    if not src:
        p = pick_folder_sprite(skin)
        if p and os.path.exists(p):
            src, kind = p, 'icon'
            icon_rel = os.path.relpath(p, LOCAL_ROOT).replace(os.sep, '/')
    if not src:
        rp = os.path.join(RENDERS, skin + '.png')
        if os.path.exists(rp):
            src, kind, icon_rel = rp, 'render', None
    if not src:
        print('NO-VISUAL', skin)
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
    sources[skin] = {'kind': kind, 'file': os.path.basename(src), 'icon_path': icon_rel}

json.dump(thumbs, open(os.path.join(HERE, 'p2_thumbs.json'), 'w'))
json.dump(sources, open(os.path.join(HERE, 'p2_thumb_sources.json'), 'w'), indent=1)
icon_n = sum(1 for v in sources.values() if v['kind'] == 'icon')
print('thumbs:', len(thumbs), 'icons:', icon_n, 'renders:', len(thumbs) - icon_n,
      'total_kb:', sum(len(v) for v in thumbs.values()) // 1024)
for k, v in sorted(sources.items()):
    print(f"{k:32s} {v['kind']:6s} {v['file']}")
