#!/usr/bin/env python3
"""技能图标后处理：输出 256×256，整圆完整不裁切，且输出必须通过合规自检才保留。

做法：按内容 bbox 裁图后，用「长边适配」缩放：scale = 256/max(w,h)，使整圆进入画布，
再居中放到 256×256。保存后执行合规检测，不通过则删除输出并报错，不向用户交付不合规图。

用法:
  python skill_icon_postprocess.py <图片路径>
  python skill_icon_postprocess.py <图片路径> -o <输出路径>
  python skill_icon_postprocess.py --dir <目录>
"""
import argparse
import os
import sys
from PIL import Image

ALPHA_THRESHOLD = 1   # 自检贴边/合规判定用
BBOX_ALPHA = 10      # 取 bbox 时仅考虑 alpha>=此值
# 合规：输出图内容面积至少达到此像素数，否则视为空白/无效
MIN_CONTENT_AREA = 2000


def _content_bbox_and_center(alpha_ch) -> tuple[tuple[int, int, int, int], float, float] | None:
    """返回 (x_min, y_min, x_max, y_max), cx, cy。用 alpha>=BBOX_ALPHA 的像素算 bbox。"""
    # PIL getbbox() 只支持单阈值，需手算 alpha>=BBOX_ALPHA 的 bbox
    w, h = alpha_ch.size
    x_min, y_min, x_max, y_max = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            if alpha_ch.getpixel((x, y)) >= BBOX_ALPHA:
                x_min, y_min = min(x_min, x), min(y_min, y)
                x_max, y_max = max(x_max, x + 1), max(y_max, y + 1)
                found = True
    if not found:
        bbox = alpha_ch.getbbox()
        if not bbox:
            return None
        x_min, y_min, x_max, y_max = bbox
    w, h = x_max - x_min, y_max - y_min
    if w <= 0 or h <= 0:
        return None
    cx = (x_min + x_max) / 2.0
    cy = (y_min + y_max) / 2.0
    return (x_min, y_min, x_max, y_max), cx, cy


def check_edges_touch(path: str, verbose: bool = False) -> bool:
    """自检：输出图四边是否都有非透明像素（贴边）。"""
    try:
        img = Image.open(path).convert("RGBA")
    except Exception:
        return False
    if img.width != 256 or img.height != 256:
        return False
    alpha = img.split()[3]
    top_ok = any(alpha.getpixel((x, 0)) >= ALPHA_THRESHOLD for x in range(256))
    bottom_ok = any(alpha.getpixel((x, 255)) >= ALPHA_THRESHOLD for x in range(256))
    left_ok = any(alpha.getpixel((0, y)) >= ALPHA_THRESHOLD for y in range(256))
    right_ok = any(alpha.getpixel((255, y)) >= ALPHA_THRESHOLD for y in range(256))
    if verbose and not (top_ok and bottom_ok and left_ok and right_ok):
        miss = []
        if not top_ok: miss.append("上")
        if not bottom_ok: miss.append("下")
        if not left_ok: miss.append("左")
        if not right_ok: miss.append("右")
        print(f"      [自检] 未贴边: {', '.join(miss)}")
    return top_ok and bottom_ok and left_ok and right_ok


def validate_compliant(path: str, verbose: bool = True) -> tuple[bool, str]:
    """合规检测：仅当通过时才可交付用户。返回 (是否合规, 失败原因，合规时为空)。"""
    try:
        img = Image.open(path).convert("RGBA")
    except Exception as e:
        return False, f"无法打开: {e}"
    if img.width != 256 or img.height != 256:
        return False, f"尺寸非 256×256: {img.width}×{img.height}"
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    if not bbox:
        return False, "无有效内容(全透明)"
    x_min, y_min, x_max, y_max = bbox
    area = (x_max - x_min) * (y_max - y_min)
    if area < MIN_CONTENT_AREA:
        return False, f"内容面积过小({area} < {MIN_CONTENT_AREA})"
    # 至少有一条边有内容，避免完全缩在中间的小点
    top_ok = any(alpha.getpixel((x, 0)) >= ALPHA_THRESHOLD for x in range(256))
    bottom_ok = any(alpha.getpixel((x, 255)) >= ALPHA_THRESHOLD for x in range(256))
    left_ok = any(alpha.getpixel((0, y)) >= ALPHA_THRESHOLD for y in range(256))
    right_ok = any(alpha.getpixel((255, y)) >= ALPHA_THRESHOLD for y in range(256))
    if not (top_ok or bottom_ok or left_ok or right_ok):
        return False, "四边均无内容，图标未贴画布"
    if verbose:
        edges = []
        if top_ok: edges.append("上")
        if bottom_ok: edges.append("下")
        if left_ok: edges.append("左")
        if right_ok: edges.append("右")
        print(f"      [合规] 通过 256×256 内容面积≥{MIN_CONTENT_AREA} 至少一边贴画布 {','.join(edges)}")
    return True, ""


def postprocess_one(path: str, out_path: str | None = None, verify: bool = True) -> bool:
    """输出 256×256：内容长边=256 整圆入画布，居中放置，圆不裁切。"""
    out_path = out_path or path
    try:
        img = Image.open(path).convert("RGBA")
    except Exception as e:
        print(f"  [skip] {path}: {e}", file=sys.stderr)
        return False

    alpha = img.split()[3]
    bc = _content_bbox_and_center(alpha)
    if not bc:
        img_out = img.resize((256, 256), Image.Resampling.LANCZOS)
        img_out.save(out_path)
        if verify:
            ok, reason = validate_compliant(out_path, verbose=True)
            if not ok:
                try:
                    os.remove(out_path)
                except OSError:
                    pass
                print(f"  [不合规] {path} 无有效内容，已删除输出: {reason}", file=sys.stderr)
                return False
        print(f"  [ok] {path} -> 256x256 (无内容图已保存，通过合规)")
        return True

    (x_min, y_min, x_max, y_max), _cx, _cy = bc
    w, h = x_max - x_min, y_max - y_min
    img_crop = img.crop((x_min, y_min, x_max, y_max))
    # 长边适配：scale = 256/max(w,h)，整圆进画布，左右/上下不裁
    scale = 256.0 / max(w, h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    img_scaled = img_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # 居中贴到 256×256 透明画布
    out = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    paste_x = (256 - new_w) // 2
    paste_y = (256 - new_h) // 2
    out.paste(img_scaled, (paste_x, paste_y), img_scaled.split()[3])
    img_out = out
    img_out.save(out_path)

    # 合规检测：不通过则不交付，删除输出并报错
    if verify:
        ok, reason = validate_compliant(out_path, verbose=True)
        if not ok:
            try:
                os.remove(out_path)
            except OSError:
                pass
            print(f"  [不合规] {path} -> 已删除输出，不交付。原因: {reason}", file=sys.stderr)
            return False
        if check_edges_touch(out_path, verbose=True):
            print(f"  [ok] {path} -> 256x256 合规交付 [四边贴合]")
        else:
            print(f"  [ok] {path} -> 256x256 合规交付 [整圆完整]")
    else:
        ok, reason = validate_compliant(out_path, verbose=False)
        if not ok:
            try:
                os.remove(out_path)
            except OSError:
                pass
            print(f"  [不合规] {path} 已删除输出: {reason}", file=sys.stderr)
            return False
        print(f"  [ok] {path} -> 256x256 合规交付")
    return True


def main():
    ap = argparse.ArgumentParser(description="技能图标后处理：256×256 + 内容贴边画布")
    ap.add_argument("paths", nargs="*", help="图片路径")
    ap.add_argument("--dir", "-d", help="处理目录下所有 .png 文件")
    ap.add_argument("--out", "-o", help="输出路径（仅单张时有效）")
    ap.add_argument("--no-verify", action="store_true", help="跳过自检四边贴边")
    args = ap.parse_args()
    do_verify = not getattr(args, "no_verify", False)

    paths = list(args.paths)
    if args.dir:
        d = args.dir
        paths.extend(os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(".png"))

    if not paths:
        ap.print_help()
        sys.exit(1)

    failed = 0
    for p in paths:
        if not os.path.isfile(p):
            print(f"  [skip] {p}: not a file", file=sys.stderr)
            continue
        if not postprocess_one(p, args.out if len(paths) == 1 and args.out else None, verify=do_verify):
            failed += 1
    if failed:
        print(f"Done. {failed} 张未通过合规检测，未交付。", file=sys.stderr)
        sys.exit(1)
    print("Done. 全部合规已交付。")


if __name__ == "__main__":
    main()
