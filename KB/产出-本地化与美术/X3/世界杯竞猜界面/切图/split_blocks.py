# -*- coding: utf-8 -*-
"""Morphix拆分③切块: 透明雪碧图按alpha连通域(投影递归分割)裁切原子块。"""
from PIL import Image
import numpy as np, io, sys, os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

SRC='固定组件雪碧图_透明_1.png'
im=Image.open(SRC).convert('RGBA')
a=np.array(im.getchannel('A'))
mask=a>10

def segments(proj,gap=12):
    """一维投影→连续段(允许gap内的间断合并)"""
    idx=np.where(proj)[0]
    if len(idx)==0: return []
    segs=[]; s=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i-prev>gap: segs.append((s,prev)); s=i
        prev=i
    segs.append((s,prev))
    return segs

blocks=[]
for (r0,r1) in segments(mask.any(axis=1),gap=18):
    band=mask[r0:r1+1]
    for (c0,c1) in segments(band.any(axis=0),gap=18):
        sub=band[:,c0:c1+1]
        rs=np.where(sub.any(axis=1))[0]
        if len(rs)==0: continue
        rr0,rr1=r0+rs[0],r0+rs[-1]
        h,w=rr1-rr0+1,c1-c0+1
        if h<24 or w<24: continue  # 噪点
        blocks.append((rr0,c0,rr1,c1))

print('blocks:',len(blocks))
pad=4
for i,(r0,c0,r1,c1) in enumerate(blocks,1):
    box=(max(0,c0-pad),max(0,r0-pad),min(im.width,c1+pad+1),min(im.height,r1+pad+1))
    crop=im.crop(box)
    crop.save(f'raw_{i:02d}_{box[2]-box[0]}x{box[3]-box[1]}.png')
    print(f'raw_{i:02d}: pos=({c0},{r0}) size={c1-c0+1}x{r1-r0+1}')
