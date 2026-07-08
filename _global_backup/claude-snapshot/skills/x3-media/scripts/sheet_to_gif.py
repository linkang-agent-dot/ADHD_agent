#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sheet_to_gif.py — 把 4x4(或任意网格) sprite sheet 切帧并合成透明底循环 GIF。

dynamic_march_emoji 的可选交付形态（2026-07-08 柴犬案实证参数）：
    py sheet_to_gif.py --src sheet.png --out out.gif
    py sheet_to_gif.py --src sheet.png --out out.gif --cols 4 --rows 4 --duration 110 --alpha-threshold 128

要点：
- GIF 只有 1-bit 透明：alpha < threshold 的像素置为全透明，其余不透明（毛边会硬化，正常）。
- disposal=2（每帧清空重绘），否则透明区域会残留上一帧拖影。
- loop=0 = 无限循环。
"""
import argparse
from PIL import Image


def sheet_to_gif(src, out, cols=4, rows=4, duration=110, alpha_threshold=128):
    sheet = Image.open(src).convert("RGBA")
    cw, ch = sheet.width // cols, sheet.height // rows
    frames = []
    for r in range(rows):
        for c in range(cols):
            frame = sheet.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
            alpha = frame.getchannel("A").point(lambda a: 255 if a >= alpha_threshold else 0)
            frame.putalpha(alpha)
            p = frame.convert("RGB").quantize(colors=255, method=Image.MEDIANCUT)
            p.paste(255, mask=alpha.point(lambda a: 255 if a == 0 else 0))
            p.info["transparency"] = 255
            frames.append(p)
    frames[0].save(
        out, save_all=True, append_images=frames[1:],
        duration=duration, loop=0, disposal=2, transparency=255, optimize=False,
    )
    print(f"OK {out}: {len(frames)} frames @{duration}ms, {cw}x{ch}/frame, loop forever")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="sprite sheet PNG (透明底)")
    ap.add_argument("--out", required=True, help="输出 GIF 路径")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--duration", type=int, default=110, help="每帧毫秒")
    ap.add_argument("--alpha-threshold", type=int, default=128)
    a = ap.parse_args()
    sheet_to_gif(a.src, a.out, a.cols, a.rows, a.duration, a.alpha_threshold)
