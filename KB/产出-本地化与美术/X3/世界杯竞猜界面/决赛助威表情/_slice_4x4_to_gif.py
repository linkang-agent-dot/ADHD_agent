# -*- coding: utf-8 -*-
"""决赛助威动态表情 S3切帧: 4×4 sprite sheet -> 16帧 -> 透明循环GIF + .bytes。
用法: python _slice_4x4_to_gif.py <4x4图.png> [输出名前缀]
"""
import sys, os, shutil
from PIL import Image

def slice_to_gif(src, out_prefix=None, duration=90, cell=256):
    sheet = Image.open(src).convert("RGBA")
    W, H = sheet.size; cw, ch = W//4, H//4
    frames = []
    for r in range(4):
        for c in range(4):
            f = sheet.crop((c*cw, r*ch, (c+1)*cw, (r+1)*ch))
            f.thumbnail((cell, cell))
            frames.append(f)
    out_p = []
    for f in frames:
        a = f.split()[3]; mask = a.point(lambda p: 255 if p >= 128 else 0)
        p = f.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
        p.paste(255, mask.point(lambda v: 255-v).convert("1"))
        out_p.append(p)
    base = out_prefix or (os.path.splitext(src)[0])
    gif = base + ".gif"
    out_p[0].save(gif, save_all=True, append_images=out_p[1:], duration=duration,
                  loop=0, transparency=255, disposal=2, optimize=True)
    shutil.copyfile(gif, base + ".bytes")   # 游戏用 .bytes = gif同内容
    print(f"{src} -> {gif} ({os.path.getsize(gif)//1024}KB) + .bytes")
    return gif

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python _slice_4x4_to_gif.py <4x4图.png> [输出前缀]"); sys.exit(1)
    slice_to_gif(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
