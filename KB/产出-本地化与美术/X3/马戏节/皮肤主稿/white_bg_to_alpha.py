# -*- coding: utf-8 -*-
r"""纯白底立绘 → 透明 RGBA（本地确定性抠图，不依赖 GRFal）。

【为什么要有这个】皮肤主稿一律生成在纯白底上（prompt 强制），这种图用本地算法抠比
调远端服务更可控、更快、可复现。GRFal remove_background 卡住时这就是兜底。

【算法】三步，避开两个常见坑：
  ① **从画布四边 flood fill 找背景**，而不是"所有接近白的像素都当背景"——
     后者会把人物身上的高光(金色滚边/珍珠/眼白)一起挖成洞。
  ② 边缘羽化：硬掩膜直接用会有锯齿，对掩膜做小半径高斯得到软 alpha。
  ③ **白色反预乘**(un-multiply)：抗锯齿边缘像素是"前景色×a + 白×(1-a)"的混合，
     直接保留会留一圈白边。按 C_out=(C_in-(1-a)·255)/a 还原真实前景色。

用法: python white_bg_to_alpha.py <输入.png> <输出.png> [--tol 12] [--feather 1.0]
     --tol      判定"接近白"的容差(每通道与255的最大差值)，默认12
     --feather  边缘羽化半径(像素)，默认1.0
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from collections import deque


def flood_bg(near_white, h, w):
    """从四边灌水，只把与画布边缘连通的近白像素判为背景。"""
    bg = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near_white[y, x] and not bg[y, x]:
                bg[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near_white[y, x] and not bg[y, x]:
                bg[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near_white[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; dq.append((ny, nx))
    return bg


def main(src, dst, tol=12, feather=1.0):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    h, w = a.shape[:2]

    near_white = (255 - a).max(axis=2) <= tol
    bg = flood_bg(near_white, h, w)
    print(f'  背景像素占比 {bg.mean()*100:.1f}%  (孤立白点未被误判: {int(near_white.sum()-bg.sum())} 个保留为前景)')

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    if feather > 0:
        alpha = np.asarray(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(feather)))

    af = alpha.astype(np.float32) / 255.0
    rgb = a.astype(np.float32)
    with np.errstate(divide='ignore', invalid='ignore'):
        un = (rgb - (1.0 - af)[..., None] * 255.0) / np.maximum(af, 1e-6)[..., None]
    rgb = np.where(af[..., None] > 0.004, un, rgb)          # 全透明处不还原，免得放大噪声
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    out = np.dstack([rgb, alpha])
    Image.fromarray(out, 'RGBA').save(dst, 'PNG', optimize=True)

    tr = (alpha < 16).mean() * 100
    mid = ((alpha > 16) & (alpha < 240)).mean() * 100
    ys, xs = np.nonzero(alpha > 16)
    print(f'  ✅ {dst}')
    print(f'     透明占比 {tr:.1f}%   软边占比 {mid:.2f}%   内容bbox=({xs.min()},{ys.min()})-({xs.max()},{ys.max()})')
    border = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])
    print(f'     四边最大alpha {border.max()} (应为0或接近0)')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    args = sys.argv[1:]
    tol = int(args[args.index('--tol') + 1]) if '--tol' in args else 12
    fe = float(args[args.index('--feather') + 1]) if '--feather' in args else 1.0
    pos = [x for x in args if not x.startswith('--') and args[args.index(x) - 1] not in ('--tol', '--feather')]
    main(pos[0], pos[1], tol, fe)
