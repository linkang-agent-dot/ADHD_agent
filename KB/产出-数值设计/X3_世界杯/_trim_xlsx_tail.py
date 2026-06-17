# -*- coding: utf-8 -*-
"""删 Text/Reward.xlsx 尾部多余空行,使行数==tsv(v2行数少,--from-tsv留了空尾行)。"""
import io,sys,openpyxl
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE=r'C:\x3\gdconfig'
JOBS=[('data/i18n/Text.xlsx','Text',r'C:\x3\gdconfig\tsv\i18n\Text__Text.tsv'),
      ('data/Reward.xlsx','Reward',r'C:\x3\gdconfig\tsv\Reward__Reward.tsv')]
import os
for xrel,sheet,tsv in JOBS:
    target=sum(1 for ln in open(tsv,encoding='utf-8') if ln.strip('\n')!='' or True)  # 行数=文件行数
    target=sum(1 for _ in open(tsv,encoding='utf-8',newline=''))
    # 更准:tsv行数(非空行)
    with open(tsv,encoding='utf-8',newline='') as f: target=len([l for l in f.read().split('\n') if l!=''])
    xp=os.path.join(BASE,*xrel.split('/'))
    wb=openpyxl.load_workbook(xp); ws=wb[sheet] if sheet in wb.sheetnames else wb.active
    before=ws.max_row
    if ws.max_row>target:
        ws.delete_rows(target+1, ws.max_row-target)
    wb.save(xp);wb.close()
    print(f"{xrel}: tsv行={target} xlsx {before}->{target} (删{before-target})")
print("done")
