# -*- coding: utf-8 -*-
r"""荣耀之路头像框 — 塞真实头像预览「游戏内观感」(通用·任意国家框复用)。
自动探框中心透明洞(BFS flood fill)→ 裁英雄头肩 → 头像垫底缩放居中 → 框盖上 → 出透明版+深色UI底版两张。
游戏里头像渲染在框【底下】,框叠上层,故合成顺序=头像层→框。

用法:
  python _头像预览合成.py <框png路径> [英雄立绘png路径]
  例: python _头像预览合成.py "荣耀之路头像框_国家特色版\WC_SF_Frame_FRA.png"
产出(同框目录): _预览_<框名>_含头像.png(透明) + _预览_<框名>_含头像_游戏内感.png(深蓝灰底)
默认英雄=足球宝贝爱莉希雅FINAL(本次世界杯主角)。换头像传第二个参数即可。
"""
import sys, io, pathlib
from collections import deque
from PIL import Image, ImageDraw
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

if len(sys.argv) < 2:
    sys.exit("用法: python _头像预览合成.py <框png路径> [英雄立绘png]")
FRAME = sys.argv[1]
HERO = sys.argv[2] if len(sys.argv) > 2 else r"C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\足球宝贝爱莉希雅_FINAL_白金高质量_v1.png"
fp = pathlib.Path(FRAME)
OUT_TRANS = str(fp.with_name(f"_预览_{fp.stem}_含头像.png"))
OUT_UI    = str(fp.with_name(f"_预览_{fp.stem}_含头像_游戏内感.png"))

frame = Image.open(FRAME).convert("RGBA")
W, H = frame.size
a = frame.split()[3]

# --- 中心透明洞: 从中心 BFS 出【真实窗口形状】(不是圆·框啥形头像填啥形) ---
S = 768
px = a.resize((S, S), Image.NEAREST).load()
seen = [[False]*S for _ in range(S)]
cx, cy = S//2, S//2
if px[cx, cy] >= 40:  # 中心不透明→螺旋找最近透明点
    found = None
    for r in range(1, S//2):
        for dx in range(-r, r+1):
            for dy in (-r, r):
                x, y = cx+dx, cy+dy
                if 0 <= x < S and 0 <= y < S and px[x, y] < 40:
                    found = (x, y); break
            if found: break
        if found: break
    if found: cx, cy = found
q = deque([(cx, cy)]); seen[cy][cx] = True
minx = maxx = cx; miny = maxy = cy
holemask_s = Image.new("L", (S, S), 0); hm = holemask_s.load()
while q:
    x, y = q.popleft(); hm[x, y] = 255
    minx, maxx = min(minx, x), max(maxx, x); miny, maxy = min(miny, y), max(maxy, y)
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < S and 0 <= ny < S and not seen[ny][nx] and px[nx, ny] < 40:
            seen[ny][nx] = True; q.append((nx, ny))
sc = W / S
hx0, hy0, hx1, hy1 = minx*sc, miny*sc, maxx*sc, maxy*sc
hw, hh = hx1-hx0, hy1-hy0
hole_cx, hole_cy = (hx0+hx1)/2, (hy0+hy1)/2
# 真实窗口蒙版(升到全分辨率)——头像只在此形状内显示,和框严丝合缝
HOLE = holemask_s.resize((W, H), Image.BILINEAR)
print(f"中心洞 bbox: ({hx0:.0f},{hy0:.0f})-({hx1:.0f},{hy1:.0f}) {hw:.0f}x{hh:.0f} (用真实窗口形状蒙版)")

# --- 裁英雄头肩 + 按【脸锚点】对位(默认英雄=足球宝贝爱莉希雅FINAL 1536x2048) ---
hero = Image.open(HERO).convert("RGBA")
HW, HH = hero.size
# 默认英雄的裁剪框+脸中心(占裁框比例)。换别的英雄需重标这两个常量。
CROP_BOX = (470, 60, 1010, 600)          # 头+肩方形裁剪
FACE_FRAC = (0.43, 0.28)                  # 脸中心在裁框内的相对位置(x,y)
crop = hero.crop(CROP_BOX).convert("RGBA")
cw, ch = crop.size
# 缩放: 盖满整个窗口(cover·消除方形白边)——按宽高较大比例放大
scale = max(hw / cw, hh / ch) * 1.02
crop2 = crop.resize((int(cw*scale), int(ch*scale)), Image.LANCZOS)
# 脸落到窗口中上部(hole 中心略上 12%),按脸锚点反算粘贴位
fx = FACE_FRAC[0] * crop2.width
fy = FACE_FRAC[1] * crop2.height
paste_x = int(hole_cx - fx)
paste_y = int((hole_cy - hh*0.12) - fy)

def build(bg):
    canvas = Image.new("RGBA", (W, H), bg)
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    layer.paste(crop2, (paste_x, paste_y), crop2)
    # 用框自身真实窗口形状(HOLE)当蒙版——头像严丝合缝填进窗,不露缝不出界
    layer.putalpha(Image.composite(layer.split()[3], Image.new("L",(W,H),0), HOLE))
    return Image.alpha_composite(Image.alpha_composite(canvas, layer), frame)

build((0,0,0,0)).save(OUT_TRANS)
build((34,40,54,255)).save(OUT_UI)
print("已存:", OUT_TRANS)
print("已存:", OUT_UI)
