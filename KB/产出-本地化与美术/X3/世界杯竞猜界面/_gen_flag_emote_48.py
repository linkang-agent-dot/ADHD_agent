# -*- coding: utf-8 -*-
"""世界杯48队应援表情：母版(Q版爱莉希雅举空白旗) + 真实国旗透视贴到旗面 → 48张。
旗面四角坐标 QUAD 在母版生成后用 _inspect_flag_quad.py 量出来填进来。
保留母版旗布褶皱阴影(multiply) + 缩256。"""
import os, glob
from PIL import Image
import numpy as np

BASE = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面"
MASTER = os.path.join(BASE, "应援表情_Q版", "WC_CheerMaster_FlagTop_1_hires.png")  # 旗顶版候选1
FLAGS = os.path.join(BASE, "flags_48")
OUT = os.path.join(BASE, "应援表情48_举旗")
os.makedirs(OUT, exist_ok=True)

# 旗面四角(母版hires 1242x2128) 顺序: TL,TR,BR,BL —— 2026-06-15实测旗区bbox矩形(106-1136, 107-1057)
QUAD = [(106,107),(1136,107),(1136,1057),(106,1057)]

def warp_flag(flag, quad, canvas_size):
    """把矩形国旗透视映射到 quad 四角，返回 canvas_size 的 RGBA 图层。"""
    fw, fh = flag.size
    src = np.float32([[0,0],[fw,0],[fw,fh],[0,fh]])
    dst = np.float32(quad)
    # 解透视矩阵(8参数) —— 用 PIL 的 QUAD transform 需要逆映射系数
    import numpy.linalg as la
    A=[]; B=[]
    for (sx,sy),(dx,dy) in zip(src,dst):
        A.append([sx,sy,1,0,0,0,-dx*sx,-dx*sy]); B.append(dx)
        A.append([0,0,0,sx,sy,1,-dy*sx,-dy*sy]); B.append(dy)
    h=la.solve(np.array(A),np.array(B)); h=np.append(h,1).reshape(3,3)
    hinv=la.inv(h)
    coeffs=(hinv/hinv[2,2]).flatten()[:8]
    layer=flag.convert("RGBA").transform(canvas_size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    return layer

def build(code):
    master = Image.open(MASTER).convert("RGBA")
    W,H = master.size
    arr = np.array(master)
    # 旗面mask: quad内 + 近浅灰(#d8d8d8±) + 不透明
    from PIL import ImageDraw
    qmask = Image.new("L",(W,H),0); ImageDraw.Draw(qmask).polygon([tuple(p) for p in QUAD], fill=255)
    qm = np.array(qmask)>128
    R,G,B,A = arr[...,0].astype(int),arr[...,1].astype(int),arr[...,2].astype(int),arr[...,3]
    mx=np.maximum(np.maximum(R,G),B); mn=np.minimum(np.minimum(R,G),B)
    sat=mx-mn; mean=(R+G+B)/3.0
    # 旗面=低饱和(<16) + 中等亮度(190~232,排亮白球衣>232) + 非暖色(R-B<10,排白金发/肤色) + 不透明
    grayish = (sat<16)&(mean>=190)&(mean<=232)&((R-B)<10)&(A>150)
    flag_mask = qm & grayish
    # 褶皱阴影: 旗面亮度归一(0.6~1.1)
    luma = (0.299*R+0.587*G+0.114*B)/216.0
    luma = np.clip(luma,0.55,1.12)
    # 透视贴国旗
    flag = Image.open(os.path.join(FLAGS,f"{code}.png"))
    warped = np.array(warp_flag(flag, QUAD, (W,H)))  # RGBA
    out = arr.copy()
    fm = flag_mask & (warped[...,3]>10)
    for c in range(3):
        out[...,c] = np.where(fm, np.clip(warped[...,c]*luma,0,255).astype(np.uint8), out[...,c])
    res = Image.fromarray(out,"RGBA")
    res.save(os.path.join(OUT,f"WC_FlagEmote_{code}_hires.png"))
    # 256: 等比缩放后居中贴透明方画布(不压扁)
    thumb=res.copy(); thumb.thumbnail((256,256), Image.LANCZOS)
    sq=Image.new("RGBA",(256,256),(0,0,0,0))
    sq.paste(thumb,((256-thumb.width)//2,(256-thumb.height)//2),thumb)
    sq.save(os.path.join(OUT,f"WC_FlagEmote_{code}.png"))

if __name__=="__main__":
    assert QUAD, "先用 _inspect_flag_quad.py 量出旗面四角填进 QUAD"
    codes=[os.path.basename(f)[:-4] for f in glob.glob(os.path.join(FLAGS,"*.png"))]
    for i,code in enumerate(sorted(codes)):
        try: build(code); print(f"[{i+1}/{len(codes)}] {code} OK")
        except Exception as e: print(f"{code} ERR {e}")
    print("OUT:",OUT)
