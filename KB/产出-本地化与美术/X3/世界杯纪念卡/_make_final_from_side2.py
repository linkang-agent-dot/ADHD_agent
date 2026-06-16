# -*- coding: utf-8 -*-
"""从 side_2_1(黑底带金框竖卡) 产两格式: 大图384x523铺满圆角透明 + 道具图标256按高216居中圆角透明。
方法: 亮度阈值取卡bbox扣黑底 -> resize -> 圆角矩形alpha遮罩(只透四角不打洞)。"""
from PIL import Image, ImageDraw
import numpy as np

SRC = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\候选_轮2\WC_side_2_1.png"
OUT_BIG = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_img_big_79.png"
OUT_ICON = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_FINAL.png"

def card_bbox(im):
    a = np.array(im.convert("RGB")); lum = a.max(axis=2)
    ys, xs = np.where(lum > 28)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return m

src = Image.open(SRC).convert("RGBA")
card = src.crop(card_bbox(src))
print("card crop:", card.size)

big = card.resize((384, 523), Image.LANCZOS)
big.putalpha(rmask(384, 523, 26))
big.save(OUT_BIG)
print("big:", big.size, big.split()[3].getbbox())

TH = 216
cw, ch = card.size
tw = int(cw * TH / ch)
ic = card.resize((tw, TH), Image.LANCZOS)
ic.putalpha(rmask(tw, TH, 14))
canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
canvas.alpha_composite(ic, ((256 - tw) // 2, 20))
canvas.save(OUT_ICON)
print("icon:", canvas.size, canvas.split()[3].getbbox())
