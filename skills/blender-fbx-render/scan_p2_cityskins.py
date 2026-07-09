# -*- coding: utf-8 -*-
"""Scan P2 CityBuildingNew folders, collect resource structure into JSON."""
import os, json, re, sys, io, base64
from datetime import datetime

ROOT = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2_cityskins.json")

def rel_files(base):
    out = []
    for dp, dns, fns in os.walk(base):
        for f in fns:
            if f.endswith('.meta'):
                continue
            p = os.path.join(dp, f)
            out.append(os.path.relpath(p, base).replace('\\', '/'))
    return out

data = []
for name in sorted(os.listdir(ROOT)):
    full = os.path.join(ROOT, name)
    if not os.path.isdir(full):
        continue
    files = rel_files(full)
    prefabs_high = [f.split('/')[-1] for f in files if f.startswith('High/') and f.endswith('.prefab')]
    prefabs_low  = [f.split('/')[-1] for f in files if f.startswith('Low/') and f.endswith('.prefab')]
    prefabs_root = [f for f in files if '/' not in f and f.endswith('.prefab')]
    fbx = [f for f in files if f.lower().endswith('.fbx')]
    textures = [f for f in files if re.search(r'\.(tga|png|psd|jpg|tif)$', f, re.I)]
    mats = [f for f in files if f.endswith('.mat')]
    anims = [f for f in files if f.endswith('.anim') or f.endswith('.controller')]
    # level pattern in high prefabs
    lv_prefabs = [p for p in prefabs_high if re.search(r'[Ll][Vv]\s*\d', p)]
    # date range
    mtimes = []
    for f in files:
        try:
            mtimes.append(os.path.getmtime(os.path.join(full, f)))
        except OSError:
            pass
    # size
    total = 0
    for f in files:
        try:
            total += os.path.getsize(os.path.join(full, f))
        except OSError:
            pass
    # representative diffuse texture (prefer Common/Texture then High/Texture, Diffuse_High)
    diffuse = [f for f in textures if 'diffuse' in f.lower()]
    diffuse.sort(key=lambda f: (0 if f.startswith('Common/') else 1, f))
    rep = diffuse[0] if diffuse else (textures[0] if textures else None)
    data.append({
        'name': name,
        'file_count': len(files),
        'size_mb': round(total / 1048576, 1),
        'prefabs_high': sorted(prefabs_high),
        'prefabs_low': sorted(prefabs_low),
        'prefabs_root': sorted(prefabs_root),
        'lv_count': len(lv_prefabs),
        'fbx_count': len(fbx),
        'tex_count': len(textures),
        'mat_count': len(mats),
        'anim_count': len(anims),
        'has_common': any(f.startswith('Common/') for f in files),
        'has_high': any(f.startswith('High/') for f in files),
        'has_low': any(f.startswith('Low/') for f in files),
        'top_dirs': sorted({f.split('/')[0] for f in files if '/' in f}),
        'rep_texture': rep,
        'mtime_min': datetime.fromtimestamp(min(mtimes)).strftime('%Y-%m') if mtimes else None,
        'mtime_max': datetime.fromtimestamp(max(mtimes)).strftime('%Y-%m') if mtimes else None,
        'textures_common': sorted([f for f in textures if f.startswith('Common/')])[:60],
    })

with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)
print('folders:', len(data))
print('written', OUT)
