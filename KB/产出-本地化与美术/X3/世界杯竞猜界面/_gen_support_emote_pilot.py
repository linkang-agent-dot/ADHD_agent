# -*- coding: utf-8 -*-
"""世界杯48队支持表情 — 试点(队徽+加油元素)。
套版:队色放射光晕 + 彩带confetti + 闪光 + 队徽(缩80%居中当主体)。256x256透明。"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter
from collections import Counter

BADGE_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\队徽48"
OUT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\支持表情48_试点"
os.makedirs(OUT, exist_ok=True)
S = 256
GOLD = (255, 200, 70)

def flag_colors(im):
    """从盾面提取国旗主色(排金/白)，返回最多3个鲜艳色。"""
    w, h = im.size; px = im.load(); cnt = Counter()
    for y in range(int(h*0.28), int(h*0.62)):
        for x in range(int(w*0.34), int(w*0.66)):
            r, g, b, a = px[x, y]
            if a < 200: continue
            if r > 205 and g > 205 and b > 205: continue          # 白
            if r > 180 and g > 140 and b < 110: continue          # 金
            cnt[(round(r/40)*40, round(g/40)*40, round(b/40)*40)] += 1
    cols = []
    for c, _ in cnt.most_common(8):
        c = tuple(min(255, max(20, v)) for v in c)
        if all(abs(c[i]-d[i]) < 50 for d in cols for i in range(3)) and cols:
            continue
        cols.append(c)
        if len(cols) == 3: break
    return cols or [(220, 30, 30)]

def make(code):
    badge = Image.open(os.path.join(BADGE_DIR, f"WC_Badge_{code}.png")).convert("RGBA")
    badge = badge.resize((S, S))
    cols = flag_colors(badge)
    rng = random.Random(hash(code) & 0xffff)
    cx, cy = S/2, S*0.46

    # --- 1. 放射光晕(sunburst) ---
    rays = Image.new("RGBA", (S, S), (0,0,0,0))
    rd = ImageDraw.Draw(rays)
    n = 24; R = S*0.95
    for i in range(n):
        a0 = (i/n)*2*math.pi; a1 = ((i+0.5)/n)*2*math.pi
        col = cols[i % len(cols)]
        rd.polygon([(cx,cy),
                    (cx+R*math.cos(a0), cy+R*math.sin(a0)),
                    (cx+R*math.cos(a1), cy+R*math.sin(a1))],
                   fill=col+(46,))
    rays = rays.filter(ImageFilter.GaussianBlur(3))
    # 中心柔光
    glow = Image.new("RGBA",(S,S),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([cx-S*0.42,cy-S*0.42,cx+S*0.42,cy+S*0.42], fill=GOLD+(60,))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(glow, rays)

    # --- 2. 彩带 confetti(上半区为主) ---
    conf = Image.new("RGBA",(S,S),(0,0,0,0)); cd=ImageDraw.Draw(conf)
    palette = cols + [GOLD, (255,255,255)]
    for _ in range(46):
        x = rng.uniform(0, S); y = rng.uniform(0, S*0.7)
        w_ = rng.uniform(5, 11); h_ = rng.uniform(9, 18)
        ang = rng.uniform(0, 360)
        piece = Image.new("RGBA",(int(w_*2),int(h_*2)),(0,0,0,0))
        ImageDraw.Draw(piece).rectangle([w_/2,h_/2,w_*1.5,h_*1.5],
            fill=rng.choice(palette)+(235,))
        piece = piece.rotate(ang, expand=True)
        conf.alpha_composite(piece, (int(x-piece.width/2), int(y-piece.height/2)))
    canvas = Image.alpha_composite(canvas, conf)

    # --- 3. 队徽(主体,缩到~80%居中略上) ---
    bs = int(S*0.80)
    bdg = badge.resize((bs, bs))
    canvas.alpha_composite(bdg, (int((S-bs)/2), int(cy-bs/2)))

    # --- 4. 闪光星 ---
    star = Image.new("RGBA",(S,S),(0,0,0,0)); sd=ImageDraw.Draw(star)
    def spark(x,y,r):
        sd.polygon([(x,y-r),(x+r*0.18,y-r*0.18),(x+r,y),(x+r*0.18,y+r*0.18),
                    (x,y+r),(x-r*0.18,y+r*0.18),(x-r,y),(x-r*0.18,y-r*0.18)],
                   fill=(255,255,255,235))
    for _ in range(6):
        spark(rng.uniform(S*0.1,S*0.9), rng.uniform(S*0.08,S*0.85), rng.uniform(5,11))
    canvas = Image.alpha_composite(canvas, star.filter(ImageFilter.GaussianBlur(0.4)))

    canvas.save(os.path.join(OUT, f"WC_Emote_{code}.png"))
    return cols

for code in ["GER","JPN","FRA","ENG"]:
    c = make(code)
    print(code, "colors:", c)
print("OUT:", OUT)
