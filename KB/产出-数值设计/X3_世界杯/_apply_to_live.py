# -*- coding: utf-8 -*-
"""把 _stage_activities/*_add.tsv 追加到 live gdconfig tsv,保LF。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = r'C:\x3\gdconfig'
STAGE = r'C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_activities'
M = [('tsv/ActvOnline__ActvOnline.tsv', 'ActvOnline_add.tsv'),
     ('tsv/ActvPack__ActvPack.tsv', 'ActvPack_add.tsv'),
     ('tsv/Pack__Pack.tsv', 'Pack_add.tsv'),
     ('tsv/TimeCycle__TimeCycle.tsv', 'TimeCycle_add.tsv'),
     ('tsv/Reward__Reward.tsv', 'Reward_add.tsv'),
     ('tsv/i18n/Text__Text.tsv', 'Text_add.tsv')]
for live, add in M:
    lp = os.path.join(BASE, *live.split('/'))
    with open(lp, 'r', encoding='utf-8', newline='') as f:
        cur = f.read()
    add_rows = [l for l in open(os.path.join(STAGE, add), encoding='utf-8').read().split('\n') if l]
    if cur and not cur.endswith('\n'):
        cur += '\n'
    new = cur + '\n'.join(add_rows) + '\n'
    with open(lp, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    print(f'{live}: +{len(add_rows)}行  CRLF={chr(13) in new}')
print('done')
