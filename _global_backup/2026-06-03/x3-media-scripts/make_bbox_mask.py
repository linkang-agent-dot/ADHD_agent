#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_bbox_mask.py — 画精细拆图用的「反向 mask」(纯 PIL，无 API)

语义(gpt-image-2 mask edit)：mask 是 RGBA PNG，跟源图同尺寸——
  alpha == 0  的像素 → 服务端 100% 保留原图（= 我们要拆的目标层）
  alpha  > 0  的像素 → gpt 按 prompt 重画（= 后面填成纯绿，再去绿）
所以「保留目标层」要把它的 bbox 内 alpha 设 0，bbox 外设 255，边缘 feather 过渡。

用法：
  python make_bbox_mask.py --src 源图.png --bbox 40,980,1000,80 --out mask.png
  多 bbox 并集(同一层跨多区域，如左右对称装饰)：重复 --bbox
  python make_bbox_mask.py --src s.png --bbox 60,300,320,600 --bbox 700,300,320,600 --out m.png --feather 4
"""
from __future__ import annotations
import argparse, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def make_mask(src_path, bboxes, out_path, feather=4):
    im = Image.open(src_path)
    W, H = im.size
    alpha = Image.new("L", (W, H), 255)          # 默认全部可编辑
    d = ImageDraw.Draw(alpha)
    for (x, y, w, h) in bboxes:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=0)   # bbox 内=保留
    if feather > 0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather))   # 边缘 feather
    rgb0 = Image.new("L", (W, H), 0)
    mask = Image.merge("RGBA", (rgb0, rgb0, rgb0, alpha))
    mask.save(out_path)
    a = np.array(alpha)
    preserved = int((a < 128).sum())
    editable = int((a >= 128).sum())
    return W, H, preserved, editable


def main():
    ap = argparse.ArgumentParser(description="画反向 bbox mask")
    ap.add_argument("--src", required=True)
    ap.add_argument("--bbox", action="append", required=True,
                    help="x,y,w,h（可重复，多个=并集）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--feather", type=int, default=4)
    a = ap.parse_args()
    bboxes = []
    for s in a.bbox:
        parts = [int(round(float(v))) for v in s.replace("，", ",").split(",")]
        if len(parts) != 4:
            ap.error(f"--bbox 要 x,y,w,h 四个数：{s}")
        bboxes.append(tuple(parts))
    W, H, pre, edt = make_mask(a.src, bboxes, a.out, a.feather)
    print(f"[bbox_mask] done · {W}x{H} · preserved={pre} editable={edt} · {a.out}")


if __name__ == "__main__":
    main()
