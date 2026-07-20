# -*- coding: utf-8 -*-
"""X3 资产进工程 + 录 DK 一条龙（2026-07-14 手册推广案固化）。
用法: python x3_dk_ingest.py <src.png> <目标文件名.png> <DK_key> [--max-w N] [--max-h N] [--anchor-key DK_xxx]
步骤: trim bbox → thumbnail 到规格 → FASTOCTREE 256色量化 → 存 ActivityImg → meta(复制 nourish_3 模板换新GUID)
     → Path_Activity.asset 两段注册(keys 列表 + objPath 映射, 插在 anchor-key 之后, 默认 bg_24)。
幂等: DK 已存在则跳过注册; meta 已存在不覆盖。
"""
import os, re, sys, uuid
from PIL import Image

DST_DIR = r'C:\x3-project\client\Assets\Res\UI\Spirits\ActivityImg'
PA = r'C:\x3-project\client\Assets\Res\Config\DisplayKey\Path_Activity.asset'
META_TPL = os.path.join(DST_DIR, 'img_Activity_bg_nourish_3.png.meta')

def ingest(src, name, dk_key, max_w=None, max_h=None, anchor_key='DK_img_Activity_bg_24'):
    im = Image.open(src).convert('RGBA')
    bbox = im.getbbox()
    if bbox: im = im.crop(bbox)
    if max_w or max_h:
        im.thumbnail((max_w or 4096, max_h or 4096), Image.LANCZOS)
    q = im.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
    out = os.path.join(DST_DIR, name)
    q.save(out, optimize=True)
    print(name, im.size, f'{os.path.getsize(out)//1024}KB')
    mp = out + '.meta'
    if not os.path.exists(mp):
        tpl = open(META_TPL, encoding='utf-8').read()
        open(mp, 'w', encoding='utf-8', newline='\n').write(
            re.sub(r'guid: [a-f0-9]{32}', 'guid: ' + uuid.uuid4().hex, tpl, count=1))
        print('meta OK')
    raw = open(PA, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw[:3000] else '\n'
    if dk_key in raw:
        print('DK 已存在, 跳过'); return
    a1 = f'    - {anchor_key}{nl}'
    assert a1 in raw, f'anchor keys 段未找到: {anchor_key}'
    raw = raw.replace(a1, a1 + f'    - {dk_key}{nl}', 1)
    m = re.search(rf'    - key: {anchor_key}{nl}      objPath: [^\r\n]+{nl}', raw)
    assert m, f'anchor objPath 段未找到: {anchor_key}'
    raw = raw.replace(m.group(0), m.group(0) + f'    - key: {dk_key}{nl}      objPath: Assets/Res/UI/Spirits/ActivityImg/{name}{nl}', 1)
    open(PA + '.tmp', 'w', encoding='utf-8', newline='').write(raw)
    os.replace(PA + '.tmp', PA)
    print('DK OK:', dk_key)

if __name__ == '__main__':
    a = sys.argv[1:]
    kw = {}
    if '--max-w' in a: kw['max_w'] = int(a[a.index('--max-w')+1])
    if '--max-h' in a: kw['max_h'] = int(a[a.index('--max-h')+1])
    if '--anchor-key' in a: kw['anchor_key'] = a[a.index('--anchor-key')+1]
    ingest(a[0], a[1], a[2], **kw)
