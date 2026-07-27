# -*- coding: utf-8 -*-
"""⚠️已废弃(2026-07-27 用户裁决): GIF 一律=先出视频再切帧,静态图假动效路线打回。
正路见 x3-media/references/video-model-routing.md §3.5。本脚本仅留档勿再用。"""
import os, math, sys, glob, shutil
from PIL import Image

SRC = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_FINAL"
OUT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_GIF"
os.makedirs(OUT, exist_ok=True)
FRAMES = 16          # 帧数
STRETCH = 0.035      # 纵向拉伸幅度(脚为锚,身体抻高=弹跳感)
SHEAR = 0.05         # 上半身切变摆动(脚不动,头/花球摆)
DUR = 65             # 每帧毫秒(~1s一循环)

def make_gif(code, src_png):
    base = Image.open(src_png).convert("RGBA")
    W, H = base.size
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        ph = math.sin(2*math.pi*t)              # -1..1
        # 1) 脚为锚的纵向 squash-stretch: 抻高时头上去脚不动→人在弹跳
        sy = 1 + ph*STRETCH
        nh = max(1,int(round(H*sy)))
        stretched = base.resize((W,nh), Image.LANCZOS)
        layer = Image.new("RGBA",(W,H),(0,0,0,0))
        layer.alpha_composite(stretched,(0,H-nh))   # 底对齐=脚踩地
        # 2) 上半身切变摆动(底部x不变,越往上偏移越大),与拉伸反相→更自然
        sh = math.sin(2*math.pi*t + math.pi/2) * SHEAR
        # 仿射: x' = x + sh*(H-y); c 偏移使底边不动
        layer = layer.transform((W,H), Image.AFFINE, (1, sh, -sh*H, 0,1,0), Image.BICUBIC)
        frames.append(layer)
    # 透明GIF: alpha阈值二值化(GIF只支持1bit透明)
    out_frames = []
    for f in frames:
        a = f.split()[3]
        mask = a.point(lambda p: 255 if p>=128 else 0)
        p = f.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
        # 透明铁律修复(2026-07-27): 透明调色板项设白,防解码器 bg 填充黑边渗色
        pal = p.getpalette(); pal[255*3:255*3+3] = [255,255,255]; p.putpalette(pal)
        # 把透明区设为调色板索引255
        p.paste(255, mask.point(lambda v:255-v).convert("1"))
        out_frames.append(p)
    gif_path = os.path.join(OUT, f"{code}.gif")
    out_frames[0].save(gif_path, save_all=True, append_images=out_frames[1:],
                       duration=DUR, loop=0, transparency=255, background=255, disposal=2, optimize=False)  # background==transparency 铁律(UniGifDecoder), optimize=False 防调色板重排破坏索引对齐
    # .bytes = gif字节副本(游戏运行时加载)
    shutil.cop2 = shutil.copyfile
    shutil.copyfile(gif_path, os.path.join(OUT, f"{code}.bytes"))
    return gif_path, os.path.getsize(gif_path)

if __name__ == "__main__":
    codes = sys.argv[1:] or None
    files = []
    for f in sorted(glob.glob(os.path.join(SRC,"WC_FaceEmote_*.png"))):
        c = os.path.basename(f)[13:16]
        if codes and c not in codes: continue
        files.append((c,f))
    for c,f in files:
        gp,sz = make_gif(c,f); print(f"{c}: {sz//1024}KB -> {gp}")
    print("OUT:", OUT)
