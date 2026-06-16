# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
p = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\_src_img11.png"
im = Image.open(p).convert("RGB")
a = np.array(im); W, H = im.size
lum = a.max(axis=2)
ys, xs = np.where(lum > 28)
l, t, r, b = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
print(f"img11 {W}x{H}")
print(f"卡bbox: ({l},{t},{r},{b}) 卡{r-l}x{b-t} 比{(r-l)/(b-t):.3f}")
print(f"边距: 左{l} 右{W-r} 上{t} 下{H-b}")
# 检查是否倾斜:看顶边第一非黑行的左右起点 vs 卡中部
for yy in [t+5, (t+b)//2, b-5]:
    row = lum[yy]; nz = np.where(row > 28)[0]
    if len(nz): print(f"  y={yy}: 左{nz[0]} 右{nz[-1]}")
