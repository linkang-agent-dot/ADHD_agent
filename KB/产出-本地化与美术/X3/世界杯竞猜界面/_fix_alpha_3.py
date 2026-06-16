# -*- coding: utf-8 -*-
"""针对世界杯头像框灰底图: 洪水填充抠掉与边缘连通的浅灰背景(含中心镂空区) -> 透明, 输出2048 RGBA。
背景浅灰渐变(~205-252)且中性色; 框主体是彩色/金/深色, 洪水只抠连通背景区, 不碰主体内部白。"""
import io, sys, glob, os, re
import numpy as np
from PIL import Image
from collections import deque

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL'

def is_bg(px):
    r, g, b = int(px[0]), int(px[1]), int(px[2])
    # 浅灰中性: 三通道都偏亮 + 极差小(中性)
    return r >= 195 and g >= 195 and b >= 195 and (max(r,g,b)-min(r,g,b)) <= 22

def flood(code):
    f = os.path.join(D, f'Img_Player_AvatarFrame_WC_{code}.png')
    # 从备份的原图重抠(避免在已改过的图上叠加)
    raw = os.path.join(D, '_opaque_raw_备份', f'Img_Player_AvatarFrame_WC_{code}.png')
    src = raw if os.path.exists(raw) else f
    im = Image.open(src).convert('RGBA')
    arr = np.array(im)
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(int)
    bgmask = ((rgb[:,:,0]>=195)&(rgb[:,:,1]>=195)&(rgb[:,:,2]>=195)&
              (np.ptp(rgb,axis=2)<=22))
    visited = np.zeros((h,w), bool)
    dq = deque()
    # 种子: 四边 + 中心点(镂空头像区)
    seeds = []
    for x in range(w):
        seeds.append((0,x)); seeds.append((h-1,x))
    for y in range(h):
        seeds.append((y,0)); seeds.append((y,w-1))
    seeds.append((h//2, w//2))  # 中心镂空区种子
    for (y,x) in seeds:
        if bgmask[y,x] and not visited[y,x]:
            visited[y,x]=True; dq.append((y,x))
    while dq:
        y,x = dq.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<h and 0<=nx<w and not visited[ny,nx] and bgmask[ny,nx]:
                visited[ny,nx]=True; dq.append((ny,nx))
    arr[visited, 3] = 0
    out = Image.fromarray(arr, 'RGBA')
    out.save(f)
    a = out.split()[3]
    corners=[a.getpixel(p) for p in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
    print(f'{code}: alpha范围{a.getextrema()} 四角{corners} 中心{a.getpixel((w//2,h//2))} 抠掉{int(visited.sum())}px')

for c in ['TUR','QAT','CPV']:
    flood(c)
