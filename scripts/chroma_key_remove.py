# -*- coding: utf-8 -*-
"""色键(绿幕/洋红幕)扣图：把纯色幕背景的图扣成透明 PNG，含边缘羽化 + 去色溢出 + 可选 fit 画布。

为什么需要它（flood_remove_white_bg 解决不了的场景）：
  当主体自带**与背景同色**的部分时，按颜色/洪水抠图无法分离。典型：玻璃/高光材质物体放在
  白底上，物体表面的纯白高光斑点(255,255,255)与白背景同色且连通 → 洪水填充顺着高光把主体
  吃出洞(2026-06-15 世界杯金奖杯的白色足球顶被吃穿)。
  根治：让 AI 把同一主体**重出到一块远离主体所有颜色的纯色幕**(金/白/绿主体→选洋红 #FF00FF)，
  再用本脚本色键扣幕。洋红 vs 金/白/绿 区分极大，白高光得以完整保留。

判据 m = min(R,B) - G（洋红幕）：洋红底 m≈250；白 m=0；金 m<0；绿草 m<0 → 阈值区分干净。
  绿幕(--key green)判据换成 G - max(R,B)。

用法:
  python chroma_key_remove.py <洋红/绿幕png> --out <透明png> [--key magenta|green]
       [--fit 124x136] [--lo 60] [--hi 140]
  --key   : 幕色，magenta(默认)/green
  --lo/hi : 羽化区间，m<=lo 实心 / m>=hi 透明，中间线性 alpha
  --fit   : 抠完保比例缩放进 WxH 透明画布居中
验收：四角 alpha 应=0；棋盘格合成看主体(尤其白色部分)有没有被抠出洞。
"""
import sys, io, argparse
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def key_alpha(a, key, lo, hi):
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    if key == 'green':
        m = G - np.maximum(R, B)
    else:  # magenta
        m = np.minimum(R, B) - G
    alpha = np.clip((hi - m) / (hi - lo), 0, 1) * 255
    return alpha.astype(np.uint8), (R, G, B)


def despill(R, G, B, alpha, key):
    edge = alpha < 250
    if key == 'green':
        Gc = np.where(edge, np.minimum(G, np.maximum(R, B)), G)  # 杀绿溢出
        return R, Gc, B
    Bc = np.where(edge, np.minimum(B, G), B)                     # 洋红:钳B到G杀紫边
    return R, G, Bc


def fit_canvas(im, W, H):
    am = im.split()[3].point(lambda p: 255 if p >= 20 else 0)
    bb = am.getbbox()
    if bb:
        im = im.crop(bb)
    cw, ch = im.size
    s = min(W / cw, H / ch)
    nw, nh = max(1, round(cw * s)), max(1, round(ch * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cv.paste(im, ((W - nw) // 2, (H - nh) // 2), im)
    return cv, (nw, nh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', required=True)
    ap.add_argument('--key', default='magenta', choices=['magenta', 'green'])
    ap.add_argument('--lo', type=int, default=60)
    ap.add_argument('--hi', type=int, default=140)
    ap.add_argument('--fit', default=None, help='WxH，如 124x136')
    a = ap.parse_args()

    arr = np.array(Image.open(a.src).convert('RGB')).astype(int)
    alpha, (R, G, B) = key_alpha(arr, a.key, a.lo, a.hi)
    R, G, B = despill(R, G, B, alpha, a.key)
    im = Image.fromarray(np.dstack([R, G, B, alpha]).astype(np.uint8), 'RGBA')
    content = im.size
    if a.fit:
        W, H = (int(v) for v in a.fit.lower().split('x'))
        im, content = fit_canvas(im, W, H)
    im.save(a.out)

    al = np.array(im)[:, :, 3]; Hh, Ww = al.shape
    corners = [int(al[3, 3]), int(al[3, Ww - 4]), int(al[Hh - 4, 3]), int(al[Hh - 4, Ww - 4])]
    print(f'色键({a.key})扣图 -> {a.out}  尺寸{im.size} 主体{content} 四角alpha{corners}(应全0)')


if __name__ == '__main__':
    main()
