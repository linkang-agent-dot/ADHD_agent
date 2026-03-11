#!/usr/bin/env python3
"""Sprite Reskin Tool - Center-crop AI-generated images and apply alpha masks from reference sprites.

No stretching or resizing. AI images are center-cropped to match reference dimensions,
then the reference alpha mask is applied directly.

Usage:
    python sprite_reskin.py --analyze <reference.png>
    python sprite_reskin.py --analyze-dir <folder>
    python sprite_reskin.py --ref <ref.png> --input <ai.png> --output <out.png>
    python sprite_reskin.py --ref-dir <refs> --input-dir <gens> --output-dir <outs>
    python sprite_reskin.py --compose-poster --input <masked.png> --output <out.png>
    python sprite_reskin.py --compose-poster --input-dir <dir> --output-dir <dir>
"""

import argparse
import math
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
except ImportError:
    print("ERROR: Pillow and numpy are required. Install with: pip install Pillow numpy")
    sys.exit(1)


# GenerateImage API supported aspect ratios (width:height)
SUPPORTED_RATIOS = [
    (1, 1), (3, 2), (2, 3), (4, 3), (3, 4),
    (16, 9), (9, 16), (7, 4), (4, 7),
]


def _best_gen_ratio(w, h):
    """Find the closest supported aspect ratio for GenerateImage that covers the target size."""
    target = w / h
    best = None
    best_diff = float("inf")
    for rw, rh in SUPPORTED_RATIOS:
        ratio = rw / rh
        diff = abs(ratio - target)
        if diff < best_diff:
            best_diff = diff
            best = (rw, rh)
    return f"{best[0]}:{best[1]}"


def _opaque_bbox(alpha_array):
    """Return bounding box (left, top, right, bottom) of the opaque region (alpha > 0)."""
    rows = np.any(alpha_array > 0, axis=1)
    cols = np.any(alpha_array > 0, axis=0)
    if not rows.any():
        return 0, 0, alpha_array.shape[1], alpha_array.shape[0]
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return int(cmin), int(rmin), int(cmax) + 1, int(rmax) + 1


def _orientation(w, h):
    """Return orientation string: portrait, landscape, or square."""
    if h > w:
        return "portrait"
    elif w > h:
        return "landscape"
    return "square"


def analyze_image(path):
    """Print image metadata, alpha stats, opaque region, and recommended GenerateImage params."""
    img = Image.open(path).convert("RGBA")
    alpha = np.array(img.getchannel("A"))
    total = alpha.size
    transparent = int((alpha == 0).sum())
    semi = int(((alpha > 0) & (alpha < 255)).sum())
    opaque = int((alpha == 255).sum())

    gen_ratio = _best_gen_ratio(img.width, img.height)
    orient = _orientation(img.width, img.height)
    bbox = _opaque_bbox(alpha)
    vis_w, vis_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    orient_prompt = {
        "portrait": "tall portrait orientation, vertical composition",
        "landscape": "wide landscape orientation, horizontal composition",
        "square": "square composition",
    }[orient]

    print(f"  File: {os.path.basename(path)}")
    print(f"  Size: {img.width}x{img.height}  (aspect {img.width/img.height:.3f}, {orient})")
    print(f"  Alpha: transparent={transparent} ({transparent/total*100:.1f}%), "
          f"semi={semi} ({semi/total*100:.1f}%), "
          f"opaque={opaque} ({opaque/total*100:.1f}%)")
    print(f"  Opaque region: {vis_w}x{vis_h} at ({bbox[0]},{bbox[1]})")
    print(f"  >>> GenerateImage prompt MUST include: \"{orient_prompt}\"")
    print(f"  >>> GenerateImage prompt MUST include: \"{img.width}x{img.height} pixels\"")
    print(f"  >>> Recommended aspect_ratio for prompt: \"{gen_ratio}\"")
    return img.width, img.height, gen_ratio, orient


def apply_mask(ref_path, input_path, output_path):
    """Cover-crop input to reference dimensions, apply reference alpha mask.

    Cover-crop: scale the input so its shorter edge matches the target,
    then center-crop to exact target dimensions. This guarantees no
    stretching and minimal content loss regardless of aspect ratio mismatch.
    """
    ref = Image.open(ref_path).convert("RGBA")
    raw = Image.open(input_path).convert("RGBA")

    tw, th = ref.size
    iw, ih = raw.size

    ref_ratio = tw / th
    input_ratio = iw / ih
    ratio_diff = abs(ref_ratio - input_ratio) / ref_ratio

    if ratio_diff > 0.1:
        print(f"  WARN: Aspect ratio mismatch — ref {tw}x{th} ({ref_ratio:.2f}) "
              f"vs input {iw}x{ih} ({input_ratio:.2f}), diff {ratio_diff*100:.0f}%. "
              f"Cover-crop will trim edges.")

    scale = max(tw / iw, th / ih)
    if scale > 1.0:
        new_w = math.ceil(iw * scale)
        new_h = math.ceil(ih * scale)
        raw = raw.resize((new_w, new_h), Image.LANCZOS)
        iw, ih = new_w, new_h
        print(f"  NOTE: Upscaled to {iw}x{ih} to cover {tw}x{th}")
    elif scale < 1.0 and (iw > tw * 2 or ih > th * 2):
        new_w = max(tw, math.ceil(iw * max(scale, 0.5)))
        new_h = max(th, math.ceil(ih * max(scale, 0.5)))
        raw = raw.resize((new_w, new_h), Image.LANCZOS)
        iw, ih = new_w, new_h

    left = (iw - tw) // 2
    top = (ih - th) // 2
    cropped = raw.crop((left, top, left + tw, top + th))

    ref_alpha = ref.getchannel("A")
    r, g, b, _ = cropped.split()
    result = Image.merge("RGBA", (r, g, b, ref_alpha))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result.save(output_path)
    print(f"  OK: {os.path.basename(output_path)} ({tw}x{th}, cover-crop from {iw}x{ih})")
    return True


def compose_poster(input_path, output_path,
                    border=2, corner_outer=8, corner_inner=6,
                    border_color=(0, 0, 0, 255),
                    stroke_color=(255, 240, 230, 140), stroke_width=2,
                    stroke_blur=0.8):
    """Compose a catalog poster card: rounded-corner border + inner stroke glow + content.

    Replicates the Figma component structure:
      Frame (WxH) > image_outer (WxH, black roundrect) > image_inner ((W-4)x(H-4) at (2,2))

    Args:
        input_path:   masked sprite (output of apply_mask), determines final size
        output_path:  destination PNG
        border:       border width in px (default 2)
        corner_outer: outer roundrect corner radius
        corner_inner: inner roundrect corner radius
        border_color: RGBA tuple for the border fill
        stroke_color: RGBA tuple for the inner glow stroke
        stroke_width: inner stroke line width
        stroke_blur:  Gaussian blur radius for the stroke softness
    """
    src = Image.open(input_path).convert("RGBA")
    outer_w, outer_h = src.size
    inner_w = outer_w - border * 2
    inner_h = outer_h - border * 2

    inner_content = src.crop((border, border, border + inner_w, border + inner_h))

    inner_mask = Image.new("L", (inner_w, inner_h), 0)
    ImageDraw.Draw(inner_mask).rounded_rectangle(
        [(0, 0), (inner_w - 1, inner_h - 1)], radius=corner_inner, fill=255
    )
    ir, ig, ib, ia = inner_content.split()
    ia_arr = np.minimum(np.array(ia), np.array(inner_mask))
    inner_content = Image.merge("RGBA", (ir, ig, ib, Image.fromarray(ia_arr)))

    stroke_img = Image.new("RGBA", (inner_w, inner_h), (0, 0, 0, 0))
    ImageDraw.Draw(stroke_img).rounded_rectangle(
        [(0, 0), (inner_w - 1, inner_h - 1)],
        radius=corner_inner, outline=stroke_color, width=stroke_width,
    )
    if stroke_blur > 0:
        stroke_img = stroke_img.filter(ImageFilter.GaussianBlur(radius=stroke_blur))

    inner_final = Image.alpha_composite(inner_content, stroke_img)

    canvas = Image.new("RGBA", (outer_w, outer_h), (0, 0, 0, 0))
    outer_mask = Image.new("L", (outer_w, outer_h), 0)
    ImageDraw.Draw(outer_mask).rounded_rectangle(
        [(0, 0), (outer_w - 1, outer_h - 1)], radius=corner_outer, fill=255
    )
    border_fill = Image.new("RGBA", (outer_w, outer_h), border_color)
    canvas.paste(border_fill, mask=outer_mask)
    canvas.paste(inner_final, (border, border), inner_final)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.save(output_path)
    print(f"  OK: {os.path.basename(output_path)} ({outer_w}x{outer_h}, "
          f"poster: border={border}px, corners={corner_outer}/{corner_inner})")
    return True


def batch_compose_poster(input_dir, output_dir, suffix="_poster", **kwargs):
    """Batch compose poster cards for all PNGs in input_dir."""
    pngs = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".png")])
    if not pngs:
        print(f"ERROR: No PNG files found in {input_dir}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    results = []
    for f in pngs:
        stem = os.path.splitext(f)[0]
        in_path = os.path.join(input_dir, f)
        out_path = os.path.join(output_dir, f"{stem}{suffix}.png")
        try:
            compose_poster(in_path, out_path, **kwargs)
            results.append({"input": f, "output": os.path.basename(out_path), "status": "ok"})
        except Exception as e:
            print(f"  ERROR: {f} -> {e}")
            results.append({"input": f, "status": "error", "error": str(e)})

    ok = sum(1 for r in results if r["status"] == "ok")
    err = sum(1 for r in results if r["status"] == "error")
    print(f"\nBatch poster complete: {ok} ok, {err} errors (total {len(pngs)})")
    return results


def batch_apply(ref_dir, input_dir, output_dir, suffix="_reskin"):
    """Batch process: for each PNG in ref_dir, find matching file in input_dir and apply mask.

    Matching rules (in order):
    1. Exact filename match: ref/Foo.png <-> input/Foo.png
    2. Suffix match: ref/Foo.png <-> input/Foo_reskin.png or input/Foo_Red.png
    3. If input_dir has exactly one file, use it for all references (1-to-many)
    """
    ref_files = sorted([f for f in os.listdir(ref_dir) if f.lower().endswith(".png")])
    input_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".png")])

    if not ref_files:
        print(f"ERROR: No PNG files found in reference dir: {ref_dir}")
        return []
    if not input_files:
        print(f"ERROR: No PNG files found in input dir: {input_dir}")
        return []

    os.makedirs(output_dir, exist_ok=True)

    input_map = {os.path.splitext(f)[0].lower(): f for f in input_files}
    single_input = input_files[0] if len(input_files) == 1 else None

    results = []
    for ref_name in ref_files:
        ref_stem = os.path.splitext(ref_name)[0]
        ref_path = os.path.join(ref_dir, ref_name)

        matched_input = None
        if ref_stem.lower() in input_map:
            matched_input = input_map[ref_stem.lower()]
        else:
            for input_stem, input_name in input_map.items():
                if input_stem.startswith(ref_stem.lower()):
                    matched_input = input_name
                    break

        if not matched_input and single_input:
            matched_input = single_input

        if not matched_input:
            print(f"  SKIP: No matching input for {ref_name}")
            results.append({"ref": ref_name, "status": "skipped"})
            continue

        input_path = os.path.join(input_dir, matched_input)
        out_name = f"{ref_stem}{suffix}.png"
        output_path = os.path.join(output_dir, out_name)

        try:
            apply_mask(ref_path, input_path, output_path)
            results.append({"ref": ref_name, "input": matched_input, "output": out_name, "status": "ok"})
        except Exception as e:
            print(f"  ERROR: {ref_name} -> {e}")
            results.append({"ref": ref_name, "status": "error", "error": str(e)})

    ok = sum(1 for r in results if r["status"] == "ok")
    skip = sum(1 for r in results if r["status"] == "skipped")
    err = sum(1 for r in results if r["status"] == "error")
    print(f"\nBatch complete: {ok} ok, {skip} skipped, {err} errors (total {len(ref_files)} refs)")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Resize and apply alpha masks from reference sprites to AI-generated images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--analyze", metavar="FILE", help="Analyze a single reference PNG")
    parser.add_argument("--analyze-dir", metavar="DIR", help="Analyze all PNGs in a folder")

    parser.add_argument("--ref", metavar="FILE", help="Single mode: reference PNG with alpha mask")
    parser.add_argument("--input", metavar="FILE", help="Single/poster mode: input PNG")
    parser.add_argument("--output", metavar="FILE", help="Single/poster mode: output path")

    parser.add_argument("--ref-dir", metavar="DIR", help="Batch mode: folder of reference PNGs")
    parser.add_argument("--input-dir", metavar="DIR", help="Batch/poster mode: folder of input PNGs")
    parser.add_argument("--output-dir", metavar="DIR", help="Batch/poster mode: output folder")
    parser.add_argument("--suffix", default="_reskin", help="Batch mode: output filename suffix (default: _reskin)")

    parser.add_argument("--compose-poster", action="store_true",
                        help="Compose catalog poster card: add rounded border + inner stroke glow")
    parser.add_argument("--border", type=int, default=2, help="Poster border width in px (default: 2)")
    parser.add_argument("--corner-outer", type=int, default=8, help="Poster outer corner radius (default: 8)")
    parser.add_argument("--corner-inner", type=int, default=6, help="Poster inner corner radius (default: 6)")

    args = parser.parse_args()

    if args.analyze:
        print("Analyzing image:")
        analyze_image(args.analyze)
    elif args.analyze_dir:
        pngs = sorted([f for f in os.listdir(args.analyze_dir) if f.lower().endswith(".png")])
        print(f"Analyzing {len(pngs)} PNG files in {args.analyze_dir}:\n")
        for f in pngs:
            analyze_image(os.path.join(args.analyze_dir, f))
            print()
    elif args.compose_poster:
        poster_kwargs = dict(
            border=args.border,
            corner_outer=args.corner_outer,
            corner_inner=args.corner_inner,
        )
        if args.input_dir and args.output_dir:
            print("Composing poster cards (batch):")
            batch_compose_poster(args.input_dir, args.output_dir,
                                 suffix=args.suffix, **poster_kwargs)
        elif args.input and args.output:
            print("Composing poster card:")
            compose_poster(args.input, args.output, **poster_kwargs)
        else:
            parser.error("--compose-poster requires (--input + --output) or (--input-dir + --output-dir)")
    elif args.ref_dir:
        if not args.input_dir or not args.output_dir:
            parser.error("Batch mode requires --ref-dir, --input-dir, and --output-dir")
        batch_apply(args.ref_dir, args.input_dir, args.output_dir, args.suffix)
    elif args.ref:
        if not args.input or not args.output:
            parser.error("Single mode requires --ref, --input, and --output")
        print("Applying mask:")
        apply_mask(args.ref, args.input, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
