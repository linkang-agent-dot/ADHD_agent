# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
p = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_v4直出_alt1.png"
im = Image.open(p).convert("RGB")
a = np.array(im); W, H = im.size; lum = a.max(axis=2)
ys, xs = np.where(lum > 28)
l, t, r, b = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
print(f"alt1 {W}x{H} 卡bbox({l},{t},{r},{b}) 比{(r-l)/(b-t):.3f}")
for yy in [t+5, (t+b)//2, b-5]:
    row = lum[yy]; nz = np.where(row > 28)[0]
    if len(nz): print(f"  y={yy}: 左{nz[0]} 右{nz[-1]} 宽{nz[-1]-nz[0]}")
