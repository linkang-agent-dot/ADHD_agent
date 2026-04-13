# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('_tmp_hist_v5.json', 'r', encoding='utf-8'))
for f in d['festivals']:
    fd = d['data'][f]
    mods = fd['modules']
    parts = [f'{k}=${v/1000:.0f}K' for k, v in sorted(mods.items(), key=lambda x: -x[1])]
    print(f"{f:12s} total=${fd['total']/1000:.0f}K  {', '.join(parts)}")
