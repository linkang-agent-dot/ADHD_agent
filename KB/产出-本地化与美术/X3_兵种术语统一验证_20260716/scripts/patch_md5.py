# -*- coding: utf-8 -*-
import os

SRC = r'C:\X3\gdconfig-dev-l1\temp_dev\ProtoGen\AllTableDataMd5.txt'
DST = r'C:\x3-project\client\Assets\Res\Config\ProtoGen\AllTableDataMd5.txt'

new_md5 = {}
for l in open(SRC, encoding='utf-8').read().splitlines():
    if ' : ' in l:
        k, v = l.split(' : ')
        k = k.strip().replace('\\', '/')
        if k.startswith('i18n/'):
            new_md5[k] = v.strip()

lines = open(DST, encoding='utf-8').read().splitlines(keepends=True)
out, patched = [], 0
for l in lines:
    key = l.split(' : ')[0].strip().replace('\\', '/') if ' : ' in l else None
    if key in new_md5:
        raw_key = l.split(' : ')[0]
        nl = raw_key + ' : ' + new_md5[key] + ('\n' if l.endswith('\n') else '')
        if nl != l:
            patched += 1
        out.append(nl)
    else:
        out.append(l)

tmp = DST + '.tmp'
with open(tmp, 'w', encoding='utf-8', newline='') as f:
    f.writelines(out)
os.replace(tmp, DST)
print('i18n lines in src:', len(new_md5), '| changed in dst:', patched)
