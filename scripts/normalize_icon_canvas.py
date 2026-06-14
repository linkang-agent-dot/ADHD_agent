# -*- coding: utf-8 -*-
"""批量图标/徽章画布规范化：以模板占比为基准，全员统一缩放居中→可1:1套版替换。

解决两个常见坑：
  1. getbbox 被 alpha 噪点(边角抗锯齿淡像素 alpha 1~3)骗成满画布 → 先阈值化再取真实主体
  2. 批量 AI 资产占比参差(82%~100%顶满)，换图替换会大小漂移 → 统一缩到模板占比居中

用法:
  python normalize_icon_canvas.py <目录> [--glob "WC_Badge_*.png"] [--occ 0.84] [--thr 30] [--canvas 256]
模板占比 occ 取参考件(如巴西徽)的 主体max边/画布 比值。备份到 <目录>/_raw_备份/。
"""
import sys, io, os, glob, argparse, shutil
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def real_bbox(im, thr):
    a = im.split()[3].point(lambda p: 255 if p >= thr else 0)
    return a.getbbox()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--glob", default="*.png")
    ap.add_argument("--occ", type=float, default=0.84, help="目标主体占画布比(模板基准)")
    ap.add_argument("--thr", type=int, default=30, help="alpha 阈值,去噪点")
    ap.add_argument("--canvas", type=int, default=256)
    ap.add_argument("--no-backup", action="store_true")
    a = ap.parse_args()

    files = glob.glob(os.path.join(a.dir, a.glob))
    files = [f for f in files if "_raw_备份" not in f]
    if not a.no_backup:
        bdir = os.path.join(a.dir, "_raw_备份")
        os.makedirs(bdir, exist_ok=True)
        for f in files:
            shutil.copy(f, bdir)

    target = round(a.canvas * a.occ)
    n = 0
    for f in files:
        im = Image.open(f).convert("RGBA")
        b = real_bbox(im, a.thr)
        if not b:
            continue
        content = im.crop(b)
        cw, ch = content.size
        s = target / max(cw, ch)
        nw, nh = max(1, round(cw * s)), max(1, round(ch * s))
        content = content.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGBA", (a.canvas, a.canvas), (0, 0, 0, 0))
        canvas.paste(content, ((a.canvas - nw) // 2, (a.canvas - nh) // 2), content)
        canvas.save(f)
        n += 1
    # 复检
    bad = []
    for f in files:
        im = Image.open(f).convert("RGBA")
        b = real_bbox(im, a.thr)
        occ = max((b[2]-b[0])/a.canvas, (b[3]-b[1])/a.canvas)
        if abs(occ - a.occ) > 0.02:
            bad.append(f"{os.path.basename(f)}={occ:.0%}")
    print(f"规范化 {n} 张 -> 占比{a.occ:.0%}居中. 复检异常: {bad if bad else '无'}")

if __name__ == "__main__":
    main()
