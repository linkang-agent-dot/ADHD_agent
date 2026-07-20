# -*- coding: utf-8 -*-
"""活动顶部 banner 规格化后处理（对标 ActvOnline c22 场景图，如 img_Activity_bg_24）。
用法: python banner_postprocess.py <src.png> <dst.png> [--w 540] [--h 500] [--fade 0.28]
中心裁剪到目标比例 → LANCZOS 缩放 → 底部 fade 比例区间 alpha 线性渐隐（衔接下方面板）。
2026-07-14 手册推广案（海妖/船只 banner）建立。
"""
import sys, os
from PIL import Image

def bannerize(src, dst, tw=540, th=500, fade=0.28):
    im = Image.open(src).convert('RGBA')
    ratio = tw / th
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / ratio); im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    im = im.resize((tw, th), Image.LANCZOS)
    px = im.load()
    fade_start = int(th * (1 - fade))
    for y in range(fade_start, th):
        f = 1.0 - (y - fade_start) / (th - fade_start)
        for x in range(tw):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * f))
    im.save(dst)
    return dst

if __name__ == '__main__':
    args = sys.argv[1:]
    src, dst = args[0], args[1]
    kw = {}
    if '--w' in args: kw['tw'] = int(args[args.index('--w') + 1])
    if '--h' in args: kw['th'] = int(args[args.index('--h') + 1])
    if '--fade' in args: kw['fade'] = float(args[args.index('--fade') + 1])
    out = bannerize(src, dst, **kw)
    print('OK', out, os.path.getsize(out))
