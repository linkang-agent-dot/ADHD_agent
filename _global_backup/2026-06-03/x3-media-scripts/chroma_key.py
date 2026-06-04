#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chroma_key.py — 去绿幕(chroma key) → 透明 PNG (纯 PIL/numpy，无 API)

精细拆图第④步：gpt 把目标层以外重画成纯绿(#00FF00)，这里把绿色判成透明，
并做 anti-spill(边缘溢绿压制)，输出单层透明 PNG。

用法：
  python chroma_key.py --in inpaint.png --out layer.png
  python chroma_key.py --in i.png --out o.png --hue 120 --tol 40 --sat 0.35
"""
from __future__ import annotations
import argparse, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import numpy as np
from PIL import Image


def chroma_key(in_path, out_path, hue=120.0, tol=40.0, sat=0.35):
    im = Image.open(in_path).convert("RGB")
    rgb = np.array(im, dtype=np.float32)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hsv = np.array(im.convert("HSV"), dtype=np.float32)
    Hh = hsv[..., 0] / 255.0 * 360.0      # 0-360
    Ss = hsv[..., 1] / 255.0              # 0-1
    dh = np.abs(((Hh - hue + 180.0) % 360.0) - 180.0)   # 到目标 hue 的环形距离
    green = (dh <= tol) & (Ss > sat)
    alpha = np.where(green, 0, 255).astype(np.uint8)
    # anti-spill：非全绿但 G 偏高(溢绿)→ 把 G 压到 max(R,B)
    spill = (~green) & (G > np.maximum(R, B))
    G2 = np.where(spill, np.maximum(R, B), G)
    # 全透明像素 RGB 清 0，防 jpg 鬼影
    R2 = np.where(green, 0, R); B2 = np.where(green, 0, B); G2 = np.where(green, 0, G2)
    out = np.dstack([R2, G2, B2, alpha]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(out_path)
    return float(green.mean() * 100.0)


def main():
    ap = argparse.ArgumentParser(description="chroma key 去绿 → 透明")
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hue", type=float, default=120.0)
    ap.add_argument("--tol", type=float, default=40.0)
    ap.add_argument("--sat", type=float, default=0.35)
    a = ap.parse_args()
    removed = chroma_key(a.inp, a.out, a.hue, a.tol, a.sat)
    tag = "好" if 5 <= removed <= 95 else ("绿太少?GPT没听话" if removed < 5 else "绿太多?bbox太小切掉目标")
    print(f"[chroma_key] done · removed={removed:.1f}% ({tag}) · {a.out}")


if __name__ == "__main__":
    main()
