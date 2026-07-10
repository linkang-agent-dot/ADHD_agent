# -*- coding: utf-8 -*-
"""Map every city skin folder -> DK keys -> icon paths, using bugfix-branch Path assets."""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_ROOT = r"E:\P2\client\client"

def parse_path_asset(fn):
    txt = open(os.path.join(HERE, fn), encoding='utf-8', errors='ignore').read()
    return dict((int(k), p.strip()) for k, p in re.findall(r'- key: (\d+)\s*\r?\n\s*objPath: (.+)', txt))

import shutil
for f in ['Path_Prefab', 'Path_Icon']:
    shutil.copy(os.path.join(LOCAL_ROOT, 'Assets', 'P2', 'Res', 'DisplayKey', f + '.asset'), os.path.join(HERE, 'bugfix_' + f + '.asset'))
prefab = parse_path_asset('bugfix_Path_Prefab.asset')
icon = parse_path_asset('bugfix_Path_Icon.asset')

# group prefab keys by CityBuildingNew skin folder
skin_keys = {}
for k, p in prefab.items():
    m = re.search(r'Map/CityBuildingNew/([^/]+)/', p)
    if m:
        skin_keys.setdefault(m.group(1), []).append(k)

EXCLUDE = {'Animation', 'DrillGround', 'MonkeyNest', 'ResourceStation', 'SecurityBox',
           'SecurityBoxMap', 'SurvivorCamp', 'TreasureChest', 'WonderCity',
           'MaincitySkin', 'CityHallLV6'}

result, need_dl = {}, []
for skin in sorted(skin_keys):
    if skin in EXCLUDE:
        continue
    keys = sorted(skin_keys[skin])
    icons = [(k, icon[k]) for k in keys if k in icon]
    chosen = icons[-1] if icons else None  # highest key = usually highest level
    local = None
    if chosen:
        lp = os.path.join(LOCAL_ROOT, chosen[1].replace('/', os.sep))
        if os.path.exists(lp) and os.path.getsize(lp) > 1024:
            local = lp
        else:
            need_dl.append({'skin': skin, 'key': chosen[0], 'repo_path': 'client/' + chosen[1]})
    result[skin] = {'keys': keys, 'icons': icons, 'chosen': chosen, 'local': local}

json.dump(result, open(os.path.join(HERE, 'dk_icon_map.json'), 'w'), indent=1)
json.dump(need_dl, open(os.path.join(HERE, 'icon_download_list.json'), 'w'), indent=1)
print('skins with DK prefab keys:', len(result))
no_icon = [s for s, v in result.items() if not v['chosen']]
print('no icon entry:', len(no_icon), no_icon)
print('need download:', len(need_dl))
for d in need_dl:
    print('  DL', d['skin'], d['repo_path'])
have = [s for s, v in result.items() if v['local']]
print('local ok:', len(have))
