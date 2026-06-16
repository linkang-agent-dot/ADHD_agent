# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
import numpy as np

DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡"
SRC_FRONT = DIR + r"\候选_轮3\WC_r3_front_v1.png"
# TARGET rotated bbox from hist 256_76: x(35,222) y(20,235) -> w188 h216 (avg of samples ~188x216)
TGT_W, TGT_H = 188, 215
TGT_CX, TGT_CY = (35+222)/2.0, (20+235)/2.0  # 128.5, 127.5
ANG = 9.0  # clockwise tilt

def rounded_mask(w,h,rad):
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],radius=rad,fill=255); return m

import math
ca, sa = math.cos(math.radians(ANG)), math.sin(math.radians(ANG))
# rotated bbox of upright CWxCH: W = CW*ca + CH*sa ; H = CW*sa + CH*ca
# solve for CW,CH given target W,H
# two eqs: TGT_W = CW*ca+CH*sa ; TGT_H = CW*sa+CH*ca
A=np.array([[ca,sa],[sa,ca]])
sol=np.linalg.solve(A, np.array([TGT_W,TGT_H]))
CW,CH=int(round(sol[0])),int(round(sol[1]))
print("upright card size ->",CW,CH,"aspect",round(CW/CH,3))

src=Image.open(SRC_FRONT).convert("RGB")
sw,sh=src.size
scale=max(CW/sw,CH/sh)
rs=src.resize((int(round(sw*scale)),int(round(sh*scale))),Image.LANCZOS)
nw,nh=rs.size
card=rs.crop(((nw-CW)//2,(nh-CH)//2,(nw-CW)//2+CW,(nh-CH)//2+CH)).convert("RGBA")
card.putalpha(rounded_mask(CW,CH,12))
rot=card.rotate(-ANG,resample=Image.BICUBIC,expand=True)
canvas=Image.new("RGBA",(256,256),(0,0,0,0))
rw,rh=rot.size
# place so center of rotated content at TGT_CX,TGT_CY
px=int(round(TGT_CX - rw/2.0)); py=int(round(TGT_CY - rh/2.0))
canvas.alpha_composite(rot,(px,py))
out=DIR+r"\WC_MemorialCard_Aerisia_FINAL.png"
canvas.save(out)
a=np.array(canvas)[:,:,3]; ys,xs=np.where(a>10)
print("256 bbox",(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),
      "corners",int(a[0,0]),int(a[0,-1]),int(a[-1,0]),int(a[-1,-1]))
print("HIST target bbox (35,20,222,235)")
