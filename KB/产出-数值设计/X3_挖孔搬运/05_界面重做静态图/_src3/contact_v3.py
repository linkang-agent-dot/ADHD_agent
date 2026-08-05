# -*- coding: utf-8 -*-
"""把 v3 静态图拷进交付目录 + 出 _全屏对照_v3.png 缩略拼版（v1 / v2 图不动）"""
import os, sys, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'png')
OUT = os.path.abspath(os.path.join(HERE, '..'))

names = sorted(os.listdir(SRC))
for n in names:
    shutil.copyfile(os.path.join(SRC, n), os.path.join(OUT, n))

TW = 340
cols, pad, lab = 5, 22, 44
ims = []
for n in names:
    im = Image.open(os.path.join(SRC, n)).convert('RGB')
    im = im.resize((TW, int(TW * im.height / im.width)), Image.LANCZOS)
    ims.append((n[:-4], im))
TH = ims[0][1].height
rows = (len(ims) + cols - 1) // cols
W = pad + cols * (TW + pad)
H = pad + rows * (TH + lab + pad) + 60
sheet = Image.new('RGB', (W, H), (16, 12, 10))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    fh = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 30)
except Exception:
    f = fh = ImageFont.load_default()
d.text((pad, 16), 'X3 挖孔（异星探索）· 老模块界面 v3「X3 标准弹窗形态」· 1080×1920 · 2026-08-05',
       fill=(238, 211, 118), font=fh)
for i, (n, im) in enumerate(ims):
    cx, cy = i % cols, i // cols
    x = pad + cx * (TW + pad)
    y = 60 + pad + cy * (TH + lab + pad)
    sheet.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + TW, y + TH], outline=(96, 76, 52))
    d.text((x, y + TH + 8), n.replace('_v3弹窗', ''), fill=(232, 220, 196), font=f)
tmp = os.path.join(OUT, '_全屏对照_v3.png.tmp')
sheet.save(tmp, format='PNG')
os.replace(tmp, os.path.join(OUT, '_全屏对照_v3.png'))
sys.stdout.reconfigure(encoding='utf-8')
print('copied %d, sheet %dx%d' % (len(names), W, H))
