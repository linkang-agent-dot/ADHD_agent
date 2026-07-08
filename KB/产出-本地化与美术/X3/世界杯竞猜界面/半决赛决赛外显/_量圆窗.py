# -*- coding: utf-8 -*-
"""量框中心透明圆窗: 中心(cx,cy)%、bbox宽高%、等效半径%(sqrt(area/pi))。对比第一批48框 vs 新荣耀之路框。"""
import sys, io, glob, math
from collections import deque
from PIL import Image
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def measure(fp):
    im = Image.open(fp).convert("RGBA"); W,H = im.size
    S = 512
    px = im.split()[3].resize((S,S), Image.NEAREST).load()
    cx,cy = S//2,S//2
    if px[cx,cy] >= 40:
        found=None
        for r in range(1,S//2):
            for dx in range(-r,r+1):
                for dy in (-r,r):
                    x,y=cx+dx,cy+dy
                    if 0<=x<S and 0<=y<S and px[x,y]<40: found=(x,y);break
                if found:break
            if found:break
        if found: cx,cy=found
    seen=[[False]*S for _ in range(S)]; q=deque([(cx,cy)]); seen[cy][cx]=True
    minx=maxx=cx; miny=maxy=cy; area=0; sx=sy=0
    while q:
        x,y=q.popleft(); area+=1; sx+=x; sy+=y
        minx,maxx=min(minx,x),max(maxx,x); miny,maxy=min(miny,y),max(maxy,y)
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<S and 0<=ny<S and not seen[ny][nx] and px[nx,ny]<40:
                seen[ny][nx]=True; q.append((nx,ny))
    ccx,ccy = sx/area, sy/area
    bw,bh = (maxx-minx+1)/S*100, (maxy-miny+1)/S*100
    rad = math.sqrt(area/math.pi)/S*100  # 等效半径 %(占图边长)
    return dict(cx=ccx/S*100, cy=ccy/S*100, bw=bw, bh=bh, r=rad, size=f"{W}x{H}")

import os
print("=== 第一批 48 队框(头像框_48_FINAL) 抽样 ===")
base1 = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL"
for f in sorted(glob.glob(base1+r"\Img_Player_AvatarFrame_WC_*.png"))[:8]:
    try:
        m=measure(f); print(f"  {os.path.basename(f)[-7:]:8} 中心({m['cx']:.1f}%,{m['cy']:.1f}%) 窗{m['bw']:.1f}x{m['bh']:.1f}% 半径{m['r']:.1f}% [{m['size']}]")
    except Exception as e: print(f"  {os.path.basename(f)}: ERR {e}")

print("=== 新荣耀之路框(国家特色版) ===")
base2 = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\半决赛决赛外显\荣耀之路头像框_国家特色版"
for name in ["WC_SF_Frame_MAR_vA_建筑破形","WC_SF_Frame_FRA_v1_铁艺","WC_SF_Frame_NOR_v2_木教堂","WC_SF_Frame_ENG_v1_纹章","WC_SF_Frame_ESP_v1_摩尔拱","WC_SF_Frame_BEL_v1_霍塔","WC_SF_Frame_ESP_v2_巴洛克"]:
    f=base2+"\\"+name+".png"
    if os.path.exists(f):
        m=measure(f); print(f"  {name[13:]:14} 中心({m['cx']:.1f}%,{m['cy']:.1f}%) 窗{m['bw']:.1f}x{m['bh']:.1f}% 半径{m['r']:.1f}%")
