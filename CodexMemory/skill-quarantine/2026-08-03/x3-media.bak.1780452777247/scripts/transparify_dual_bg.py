#!/usr/bin/env python3
"""
transparify_dual_bg.py — 双背景差分法精细抠图

社区主流玩法（Transparify pattern）：让 GPT 在白底和黑底分别画一次同一元素，
从两张图的像素差反推真实 alpha 通道。能完美保留毛发 / 光晕 / 半透明边缘，
避免直接用 transparent 参数时的"主体白色被穿洞"和"伪造透明翻车"问题。

数学推导：
  设前景 RGB 为 F，alpha 为 a，白底 W=(255,255,255)，黑底 B=(0,0,0)
  img_white = a*F + (1-a)*W
  img_black = a*F + (1-a)*B = a*F
  → img_white - img_black = (1-a)*W = (1-a)*255
  → a_per_channel = 1 - (img_white - img_black) / 255
  → a_final = min over RGB channels （保守取 min，避免边缘半透明算大）
  → F = img_black / a   （recover foreground from black image，防 0 div）

用法：
  python transparify_dual_bg.py --white path/to/white.png --black path/to/black.png --out path/to/alpha.png
  python transparify_dual_bg.py --white W.png --black B.png --out OUT.png --trim   # 自动裁透明 padding
  python transparify_dual_bg.py --white W.png --black B.png --out OUT.png --resize 512  # 缩放到 512×512

依赖：Pillow + numpy。装：pip install Pillow numpy
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def transparify(white_path: Path, black_path: Path) -> Image.Image:
    """两张图必须**同尺寸 + 同位置 + 同元素**，仅背景不同。"""
    w = Image.open(white_path).convert("RGB")
    b = Image.open(black_path).convert("RGB")
    if w.size != b.size:
        raise ValueError(
            f"白底 {w.size} 和黑底 {b.size} 尺寸不一致；GPT 生成可能位置漂移，需要先用 ImageMagick / autoalign 对齐"
        )

    W = np.array(w, dtype=np.float32)  # H × W × 3
    B = np.array(b, dtype=np.float32)

    # alpha per channel = 1 - (W - B) / 255
    diff = W - B  # 理想情况下应都 ≥ 0；GPT 生成有时反相，clip 一下
    diff = np.clip(diff, 0.0, 255.0)
    alpha_chan = 1.0 - diff / 255.0  # H × W × 3
    alpha_chan = np.clip(alpha_chan, 0.0, 1.0)

    # 三通道取 min（保守，保边缘清晰；取 mean 边缘更软）
    alpha = alpha_chan.min(axis=2)  # H × W

    # 从黑底图反推 foreground：img_black = a*F → F = img_black / a
    eps = 1e-3
    a3 = np.maximum(alpha[..., None], eps)
    F = B / a3
    F = np.clip(F, 0.0, 255.0)

    # 对完全透明的像素，强制 F = 0 防止 jpg 压缩时鬼影
    F[alpha < 0.01] = 0

    a8 = (alpha * 255.0).round().astype(np.uint8)
    F8 = F.astype(np.uint8)
    out = np.dstack([F8, a8])  # H × W × 4
    return Image.fromarray(out, mode="RGBA")


def trim_transparent(img: Image.Image, padding: int = 4) -> Image.Image:
    """裁掉四周完全透明的 padding。"""
    arr = np.array(img)
    alpha = arr[..., 3]
    if not alpha.any():
        return img
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    y0, y1 = int(np.argmax(rows)), int(len(rows) - np.argmax(rows[::-1]))
    x0, x1 = int(np.argmax(cols)), int(len(cols) - np.argmax(cols[::-1]))
    y0 = max(0, y0 - padding)
    x0 = max(0, x0 - padding)
    y1 = min(arr.shape[0], y1 + padding)
    x1 = min(arr.shape[1], x1 + padding)
    return img.crop((x0, y0, x1, y1))


def main():
    p = argparse.ArgumentParser(description="Dual-background alpha matting (Transparify pattern)")
    p.add_argument("--white", required=True, help="白底图路径（GPT 用 pure white background 画的那张）")
    p.add_argument("--black", required=True, help="黑底图路径（同 prompt 用 pure black background 画的那张）")
    p.add_argument("--out", required=True, help="输出 RGBA PNG 路径")
    p.add_argument("--trim", action="store_true", help="裁掉四周完全透明的 padding")
    p.add_argument("--padding", type=int, default=4, help="trim 时保留的边距像素，默认 4")
    p.add_argument("--resize", type=int, default=0, help="非 0 则等比缩放到指定边长（Lanczos）")
    args = p.parse_args()

    white = Path(args.white)
    black = Path(args.black)
    out = Path(args.out)
    if not white.exists():
        print(f"[ERROR] white not found: {white}", file=sys.stderr)
        sys.exit(2)
    if not black.exists():
        print(f"[ERROR] black not found: {black}", file=sys.stderr)
        sys.exit(2)

    print(f"[transparify] white={white.name} black={black.name}")
    rgba = transparify(white, black)

    if args.trim:
        rgba = trim_transparent(rgba, padding=args.padding)
        print(f"[transparify] trimmed to {rgba.size}")

    if args.resize > 0:
        target = args.resize
        rgba.thumbnail((target, target), Image.Resampling.LANCZOS)
        print(f"[transparify] resized to {rgba.size}")

    out.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out, "PNG", optimize=True)
    arr = np.array(rgba)
    opaque = (arr[..., 3] > 250).sum()
    transparent = (arr[..., 3] < 5).sum()
    total = arr.shape[0] * arr.shape[1]
    print(
        f"[transparify] saved {out} · size={rgba.size} · "
        f"opaque={opaque / total * 100:.1f}% transparent={transparent / total * 100:.1f}%"
    )


if __name__ == "__main__":
    main()
