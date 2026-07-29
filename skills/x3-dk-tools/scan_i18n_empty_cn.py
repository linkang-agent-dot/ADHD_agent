# -*- coding: utf-8 -*-
"""扫「i18n 里中文本身就空、但配置表源列有值」的 key —— 上一版扫描器的盲区。"""
import csv, sys, os, re, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r"C:/X3/gdconfig-amina-video"
os.chdir(ROOT)

def load(p):
    with open(p, encoding='utf-8', errors='replace', newline='') as f:
        return list(csv.reader(f, delimiter='\t'))

# 马戏节 ID 集
ao = load('tsv/ActvOnline__ActvOnline.tsv')
CID = set()
for r in ao[6:]:
    if len(r) > 38 and r[38].strip() in ('143', '144'):
        CID.add(r[0])
        if len(r) > 4 and r[4].strip():
            CID.add(r[4].strip())
for p in glob.glob('tsv/*.tsv'):
    try:
        rows = load(p)
    except Exception:
        continue
    if len(rows) < 7:
        continue
    for r in rows[6:]:
        if r and r[0].strip() and ('马戏' in ' '.join(r[:4]) or '巡游' in ' '.join(r[:4])):
            CID.add(r[0].strip())

def is_circus(keystr):
    for k in keystr.split('|'):
        m = re.search(r'_(\d{3,})$', k)
        if m and m.group(1) in CID:
            return True
    return False

# i18n 里 cn 为空的 key
tx = load('tsv/i18n/Text__Text.tsv')
empty_cn = {}
for r in tx:
    if not r or not (r[0].startswith('TXT_') or r[0].startswith('Text_')):
        continue
    if len(r) <= 3 or r[3].strip():
        continue
    for k in r[0].split('|'):
        empty_cn[k] = r

# 反查配置表源列（TXT_ 标记列）有没有值
found = []
for p in sorted(glob.glob('tsv/*.tsv')):
    base = os.path.basename(p)
    if base.startswith('Text'):
        continue
    try:
        rows = load(p)
    except Exception:
        continue
    if len(rows) < 7:
        continue
    h4 = rows[4]
    tbl = base.replace('.tsv', '').split('__')[-1]
    txt_cols = [(i, h4[i]) for i in range(len(h4)) if h4[i].startswith('TXT_')]
    if not txt_cols:
        continue
    fields = rows[5]
    for r in rows[6:]:
        if not r or not r[0].strip():
            continue
        for i, label in txt_cols:
            if i >= len(r) or not r[i].strip():
                continue
            fld = fields[i] if i < len(fields) else ''
            key = 'TXT_%s_%s_%s' % (tbl, fld, r[0])
            if key in empty_cn:
                found.append((key, r[i][:36], base, is_circus(key)))

cir = [x for x in found if x[3]]
oth = [x for x in found if not x[3]]
print('配置表源列有值、但 i18n 里 cn 为空的 key: %d 个' % len(found))
print('  ★马戏节: %d   其它: %d' % (len(cir), len(oth)))
print()
if cir:
    print('=== ★马戏节（需修） ===')
    for k, v, b, _ in cir:
        print('   %-46s = %s   (%s)' % (k, v, b))
print()
if oth:
    print('=== 其它（非本次范围，仅列出） ===')
    for k, v, b, _ in oth[:15]:
        print('   %-46s = %s   (%s)' % (k, v, b))
    if len(oth) > 15:
        print('   … 还有 %d 个' % (len(oth) - 15))
