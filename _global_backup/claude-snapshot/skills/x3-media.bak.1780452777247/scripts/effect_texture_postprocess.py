"""Effect texture post-process: luminance -> Alpha, RGB forced to pure white.

Converts an AI-generated "black background + white silhouette" image into a
Unity-style effect texture where:
  - Shape lives entirely in the Alpha channel (A = luminance)
  - RGB is clamped to (255, 255, 255) for every pixel
  - Canvas is a 2^N square (default 256), content centered

Usage
-----
    py effect_texture_postprocess.py <input.png> [--output out.png] [--size 256]
    py effect_texture_postprocess.py --dir <folder>  # batch

See references/type-effect-texture.md for the full spec.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def _luminance(arr: np.ndarray) -> np.ndarray:
    """Grayscale source for the alpha mask.

    If the input is RGBA and the alpha channel already carries shape info
    (i.e. it is not uniformly opaque), use alpha directly — this handles
    existing Unity effect textures that have RGB clamped to white. Otherwise
    fall back to Rec. 601 luma over RGB.
    """
    if arr.ndim == 2:
        return arr
    if arr.shape[2] == 4:
        a = arr[:, :, 3]
        if a.min() < 250:
            return a
    rgb = arr[:, :, :3].astype(np.float32)
    y = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    return np.clip(y, 0, 255).astype(np.uint8)


def _auto_invert_needed(gray: np.ndarray) -> bool:
    """True if the image is white-background / dark-subject, i.e. we need to
    invert so the subject becomes bright."""
    h, w = gray.shape
    b = max(2, min(h, w) // 32)
    corners = np.concatenate([
        gray[:b, :b].ravel(), gray[:b, -b:].ravel(),
        gray[-b:, :b].ravel(), gray[-b:, -b:].ravel(),
    ])
    return corners.mean() > 180


def _square_center(gray: np.ndarray, size: int) -> np.ndarray:
    h, w = gray.shape
    side = min(h, w)
    y0 = (h - side) // 2
    x0 = (w - side) // 2
    crop = gray[y0:y0 + side, x0:x0 + side]
    return np.array(Image.fromarray(crop).resize((size, size), Image.LANCZOS))


def _stretch_contrast(gray: np.ndarray, low_pct: float = 2.0, high_pct: float = 98.0) -> np.ndarray:
    lo = float(np.percentile(gray, low_pct))
    hi = float(np.percentile(gray, high_pct))
    if hi - lo < 8:
        return gray
    out = (gray.astype(np.float32) - lo) * (255.0 / (hi - lo))
    return np.clip(out, 0, 255).astype(np.uint8)


def _center_with_padding(alpha: np.ndarray, padding_ratio: float) -> np.ndarray:
    """Trim to content bbox then re-center on transparent canvas with padding."""
    if padding_ratio <= 0:
        return alpha
    mask = alpha > 10
    if not mask.any():
        return alpha
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    bbox = alpha[y0:y1, x0:x1]
    side = alpha.shape[0]
    inner = int(side * (1.0 - 2.0 * padding_ratio))
    inner = max(16, min(side, inner))
    bh, bw = bbox.shape
    scale = min(inner / bh, inner / bw)
    new_h = max(1, int(round(bh * scale)))
    new_w = max(1, int(round(bw * scale)))
    resized = np.array(Image.fromarray(bbox).resize((new_w, new_h), Image.LANCZOS))
    canvas = np.zeros_like(alpha)
    oy = (side - new_h) // 2
    ox = (side - new_w) // 2
    canvas[oy:oy + new_h, ox:ox + new_w] = resized
    return canvas


def postprocess(path: str, out_path: str, size: int, invert: str, threshold: int,
                smooth: int, desaturate: bool, padding: float) -> dict:
    im = Image.open(path)
    if desaturate:
        im = im.convert("L").convert("RGB")
    arr = np.array(im.convert("RGBA"))
    gray = _luminance(arr)

    # Alpha transport: subject must end up bright
    do_invert = (invert == "on") or (invert == "auto" and _auto_invert_needed(gray))
    if do_invert:
        gray = 255 - gray

    # Square + resize
    gray = _square_center(gray, size)

    # Contrast + optional hard threshold
    gray = _stretch_contrast(gray)
    if threshold > 0:
        gray = np.where(gray >= threshold, 255, 0).astype(np.uint8)

    # Optional edge smoothing
    if smooth > 0:
        im_l = Image.fromarray(gray, mode="L").filter(ImageFilter.MedianFilter(size=2 * smooth + 1))
        gray = np.array(im_l)

    alpha = _center_with_padding(gray, padding)

    # Compose RGBA with RGB forced to pure white
    out = np.empty((size, size, 4), dtype=np.uint8)
    out[:, :, 0:3] = 255
    out[:, :, 3] = alpha
    Image.fromarray(out, mode="RGBA").save(out_path, format="PNG", optimize=True)

    visible = int((alpha > 10).sum())
    ratio = visible / alpha.size
    return {
        "out": out_path,
        "size": size,
        "visible_ratio": round(ratio, 4),
        "inverted": do_invert,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Unity effect-texture post-process: RGB=255, Alpha=luminance, 2^N square.")
    ap.add_argument("input", nargs="?", help="Single image to process")
    ap.add_argument("--dir", help="Batch-process every .png in this directory (in place, unless --output-dir given)")
    ap.add_argument("--output", help="Output path (defaults to input with _fx suffix)")
    ap.add_argument("--output-dir", help="Batch mode: write outputs here instead of in place")
    ap.add_argument("--size", type=int, default=256, choices=[64, 128, 256, 512, 1024], help="Square edge length (2^N). Default 256.")
    ap.add_argument("--invert", choices=["auto", "on", "off"], default="auto", help="Invert luminance (auto detects white-bg). Default auto.")
    ap.add_argument("--threshold", type=int, default=0, help="Hard binarize at this luma (0 = off, keep edge softness).")
    ap.add_argument("--smooth", type=int, default=0, help="Median-filter radius in pixels (0 = off).")
    ap.add_argument("--desaturate", action="store_true", help="Drop any color cast before luma extraction.")
    ap.add_argument("--padding", type=float, default=0.0, help="Re-center content with this margin ratio (e.g. 0.12). 0 = keep original composition.")
    args = ap.parse_args()

    targets: list[tuple[str, str]] = []
    if args.dir:
        src_dir = Path(args.dir)
        if not src_dir.is_dir():
            print(f"[ERR] not a dir: {src_dir}", file=sys.stderr)
            return 2
        dst_dir = Path(args.output_dir) if args.output_dir else src_dir
        dst_dir.mkdir(parents=True, exist_ok=True)
        for p in sorted(src_dir.glob("*.png")):
            targets.append((str(p), str(dst_dir / p.name)))
    elif args.input:
        inp = Path(args.input)
        if args.output:
            out = Path(args.output)
        else:
            out = inp.with_name(inp.stem + "_fx.png")
        targets.append((str(inp), str(out)))
    else:
        ap.print_help()
        return 2

    for src, dst in targets:
        try:
            info = postprocess(src, dst, args.size, args.invert, args.threshold,
                               args.smooth, args.desaturate, args.padding)
            print(f"[OK]  {src} -> {dst}  size={info['size']}  alpha={info['visible_ratio']:.1%}  inverted={info['inverted']}")
        except Exception as e:  # noqa: BLE001
            print(f"[ERR] {src}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
