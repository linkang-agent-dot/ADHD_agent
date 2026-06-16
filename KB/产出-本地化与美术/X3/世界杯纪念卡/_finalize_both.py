# -*- coding: utf-8 -*-
"""格式归一两张定稿:
  大图 = thisver(正面,1152x2048) -> 裁0.734比 -> 384x523 -> 圆角透明  (对齐 img_card_image)
  256  = alt1源(侧面) -> 裁0.875近方 -> 189x216 填满 -> 圆角透明居中256  (对齐 icon_card_image)
"""
from PIL import Image, ImageDraw
import numpy as np

BIG_SRC = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\候选_轮3\WC_r3_thisver.png"
ICON_SRC = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_v4直出_alt1.png"
OUT_BIG = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_img_big_79.png"
OUT_ICON = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_FINAL.png"

def card_crop(im):
    """扣掉黑底/外边,取卡bbox(亮度)。RGB或RGBA都行。"""
    a = np.array(im.convert("RGB")); lum = a.max(axis=2)
    ys, xs = np.where(lum > 28)
    return im.convert("RGBA").crop((int(xs.min()), int(ys.min()), int(xs.max())+1, int(ys.max())+1))

def crop_to_ratio(card, target, anchor=0.12):
    cw, ch = card.size
    if cw/ch < target:           # 偏窄高 -> 裁高(偏上保头)
        nh = int(cw/target); top = int((ch-nh)*anchor)
        return card.crop((0, top, cw, top+nh))
    else:                        # 偏宽 -> 裁宽居中
        nw = int(ch*target); l = (cw-nw)//2
        return card.crop((l, 0, l+nw, ch))

def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1), radius=r, fill=255)
    return m

# 大图 384x523 (比0.734)
big = crop_to_ratio(card_crop(Image.open(BIG_SRC)), 384/523, anchor=0.05).resize((384,523), Image.LANCZOS)
big.putalpha(rmask(384,523,26))
big.save(OUT_BIG)
print("大图:", big.size, big.split()[3].getbbox())

# 256 卡区189x216(比0.875) 填满,放256画布(左34上20)
icard = crop_to_ratio(card_crop(Image.open(ICON_SRC)), 189/216, anchor=0.10).resize((189,216), Image.LANCZOS)
icard.putalpha(rmask(189,216,14))
canvas = Image.new("RGBA",(256,256),(0,0,0,0))
canvas.alpha_composite(icard,(34,20))
canvas.save(OUT_ICON)
print("256:", canvas.size, canvas.split()[3].getbbox(), "(标准34,20,223,236)")
