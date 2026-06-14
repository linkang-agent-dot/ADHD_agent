# -*- coding: utf-8 -*-
"""测量头像框几何：256画布里透空内径/环厚/外径。在 头像框/ 目录下跑。
用法: PYTHONIOENCODING=utf-8 python _measure_frame_geometry.py"""
import glob, statistics as st
from PIL import Image

A = 40  # alpha 阈值, >A 视为不透明
rows = []
for fn in sorted(glob.glob("头像框/*.png")) or sorted(glob.glob("*.png")):
    im = Image.open(fn).convert("RGBA"); W, H = im.size; px = im.load()
    cx, cy = W // 2, H // 2
    def scan(dirx):
        inner = outer = None
        for d in range(1, cx):
            x = cx + dirx * d
            if 0 <= x < W:
                a = px[x, cy][3]
                if a > A and inner is None: inner = d
                if a > A: outer = d
        return inner, outer
    li, lo = scan(-1); ri, ro = scan(1)
    inner = (li + ri) / 2 if li and ri else (li or ri)
    outer = (lo + ro) / 2 if lo and ro else (lo or ro)
    if inner and outer:
        rows.append((fn, W, round(inner * 2), round(outer * 2), round(outer - inner)))

print(f"{'file':46s}{'canvas':>7}{'inner_d':>9}{'outer_d':>9}{'ring_thk':>9}")
for r in rows:
    print(f"{r[0]:46s}{r[1]:>7}{r[2]:>9}{r[3]:>9}{r[4]:>9}")
def col(i): return [r[i] for r in rows]
print("\n=== STATS (px) ===")
for name, i in [("inner_d", 2), ("outer_d", 3), ("ring_thk(单边)", 4)]:
    v = col(i)
    print(f"{name:16s} median {int(st.median(v)):>4}  mean {int(st.mean(v)):>4}  range {min(v)}~{max(v)}")
print("N =", len(rows))
