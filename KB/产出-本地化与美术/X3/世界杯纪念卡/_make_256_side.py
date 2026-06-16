# -*- coding: utf-8 -*-
"""256道具图标:side_2_1裁成近方0.875填满189x216(对齐历史76/1)+圆角透明,居中放256画布。"""
from PIL import Image, ImageDraw
import numpy as np

SRC = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\候选_轮2\WC_side_2_1.png"
OUT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_256_side.png"

src = Image.open(SRC).convert("RGBA")
a = np.array(src.convert("RGB")); lum = a.max(axis=2)
ys, xs = np.where(lum > 28)
card = src.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
cw, ch = card.size

TW, TH = 189, 216
target = TW / TH
if cw / ch < target:
    nh = int(cw / target)
    top = int((ch - nh) * 0.18)
    card = card.crop((0, top, cw, top + nh))
else:
    nw = int(ch * target)
    card = card.crop(((cw - nw) // 2, 0, (cw - nw) // 2 + nw, ch))
card = card.resize((TW, TH), Image.LANCZOS)

m = Image.new("L", (TW, TH), 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, TW - 1, TH - 1), radius=14, fill=255)
card.putalpha(m)
canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
canvas.alpha_composite(card, (34, 20))
canvas.save(OUT)
print("out", canvas.size, "bbox", canvas.split()[3].getbbox(), "(hist=34,20,223,236)")
