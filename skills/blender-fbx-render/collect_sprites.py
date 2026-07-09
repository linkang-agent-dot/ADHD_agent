# -*- coding: utf-8 -*-
import os, re, json
ROOT = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew"
EXCLUDE = {'Animation','DrillGround','MonkeyNest','ResourceStation','SecurityBox','SecurityBoxMap',
           'SurvivorCamp','TreasureChest','WonderCity','MaincitySkin','CityHallLV6'}
HERE = os.path.dirname(os.path.abspath(__file__))
result = {}
for skin in sorted(os.listdir(ROOT)):
    sd = os.path.join(ROOT, skin)
    if not os.path.isdir(sd) or skin in EXCLUDE:
        continue
    sprites = []
    for dp, _, fns in os.walk(sd):
        for f in fns:
            if not f.lower().endswith('.png'):
                continue
            p = os.path.join(dp, f)
            if os.path.getsize(p) < 1024:
                continue
            meta = p + '.meta'
            ttype = None
            if os.path.exists(meta):
                mtxt = open(meta, encoding='utf-8', errors='ignore').read()
                m = re.search(r'textureType:\s*(\d+)', mtxt)
                ttype = int(m.group(1)) if m else None
            sprites.append({'path': os.path.relpath(p, sd).replace(os.sep, '/'),
                            'size': os.path.getsize(p), 'ttype': ttype})
    result[skin] = sprites
json.dump(result, open(os.path.join(HERE, 'p2_sprite_pngs.json'), 'w'), indent=1)
for k, v in result.items():
    s8 = [x for x in v if x['ttype'] == 8]
    names = ', '.join(x['path'].split('/')[-1] for x in s8[:6])
    print(f"{k:32s} sprite8={len(s8):2d} otherpng={len(v)-len(s8):2d} | {names}")
