# -*- coding: utf-8 -*-
"""梯形透视法做256:量历史76卡4角(圆角梯形)+量alt1卡4角 -> alt1透视warp进历史梯形 -> 梯形遮罩透明。"""
from PIL import Image, ImageDraw
import numpy as np

HIST = r"C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_card_image_76.png"
SRC = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_v4直出_alt1.png"
OUT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_256_梯形.png"

def four_corners(mask):
    ys, xs = np.where(mask)
    s = xs + ys; d = xs - ys
    tl = (int(xs[np.argmin(s)]), int(ys[np.argmin(s)]))
    br = (int(xs[np.argmax(s)]), int(ys[np.argmax(s)]))
    tr = (int(xs[np.argmax(d)]), int(ys[np.argmax(d)]))
    bl = (int(xs[np.argmin(d)]), int(ys[np.argmin(d)]))
    return tl, tr, br, bl

h = Image.open(HIST).convert("RGBA")
H_tl, H_tr, H_br, H_bl = four_corners(np.array(h.split()[3]) > 10)
print("hist76 corners TL%s TR%s BR%s BL%s" % (H_tl, H_tr, H_br, H_bl))

s = Image.open(SRC).convert("RGBA")
S_tl, S_tr, S_br, S_bl = four_corners(np.array(s.convert("RGB")).max(2) > 28)
print("alt1 corners TL%s TR%s BR%s BL%s" % (S_tl, S_tr, S_br, S_bl))

def find_coeffs(dst, src):
    M = []
    for (dx, dy), (sx, sy) in zip(dst, src):
        M.append([dx, dy, 1, 0, 0, 0, -sx*dx, -sx*dy])
        M.append([0, 0, 0, dx, dy, 1, -sy*dx, -sy*dy])
    A = np.array(M, dtype=float); B = np.array([c for p in src for c in p], dtype=float)
    return list(np.linalg.solve(A, B))

coeffs = find_coeffs([H_tl, H_tr, H_br, H_bl], [S_tl, S_tr, S_br, S_bl])
warped = s.transform((256, 256), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
mask = Image.new("L", (256, 256), 0)
ImageDraw.Draw(mask).polygon([H_tl, H_tr, H_br, H_bl], fill=255)
warped.putalpha(mask)
warped.save(OUT)
print("OUT", OUT, "bbox", warped.split()[3].getbbox())
