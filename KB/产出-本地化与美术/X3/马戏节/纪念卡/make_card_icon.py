# -*- coding: utf-8 -*-
r"""从纪念卡卡面生成配套的道具图标（256x256 透明）。

为什么能程序化生成：现役 icon_card_image_83/84 就是卡面本身做了个约 3.9° 的旋转
（实测四角 TL(60,21) TR(208,31) BR(194,234) BL(46,224) 是**平行四边形**——上下等宽、
左右等高，所以是仿射不是透视），再加投影。换皮时只要把新卡面按同一组四角贴回去，
边框/投影/发光全部原样保留，比重新 AI 出图更保真、零随机偏差。

用法: python make_card_icon.py <新卡面.png> <现役图标.png> <输出.png>
"""
import sys
import numpy as np
from PIL import Image

# 实测自现役 icon_card_image_83/84（两者几何完全一致，同一套模板）
QUAD = {'TL': (60, 21), 'TR': (208, 31), 'BL': (46, 224)}
CANVAS = (256, 256)
CARD_RATIO = 384 / 523          # 卡面标准宽高比


def solve_affine(dst_tl, dst_tr, dst_bl, w, h):
    """求 dst->src 的仿射系数（PIL Image.AFFINE 要的就是逆映射）。"""
    A = np.array([[dst_tl[0], dst_tl[1], 1],
                  [dst_tr[0], dst_tr[1], 1],
                  [dst_bl[0], dst_bl[1], 1]], float)
    abc = np.linalg.solve(A, np.array([0, w, 0], float))   # src_x
    de_f = np.linalg.solve(A, np.array([0, 0, h], float))  # src_y
    return (*abc, *de_f)


def center_crop_to_ratio(im, ratio):
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio)
        return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = round(w / ratio)
    return im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def main(card_path, ref_icon_path, out_path):
    card = center_crop_to_ratio(Image.open(card_path).convert('RGBA'), CARD_RATIO)
    w, h = card.size
    coeffs = solve_affine(QUAD['TL'], QUAD['TR'], QUAD['BL'], w, h)

    # 变换到画布；BICUBIC 保边框细节
    warped = card.transform(CANVAS, Image.AFFINE, coeffs, resample=Image.BICUBIC)

    # 变换后画布外区域会被边缘像素拉伸填充 → 用几何算出的四边形自己做遮罩，别信 warp 的 alpha
    from PIL import ImageDraw
    TL, TR, BL = QUAD['TL'], QUAD['TR'], QUAD['BL']
    BR = (TR[0] + BL[0] - TL[0], TR[1] + BL[1] - TL[1])
    mask = Image.new('L', CANVAS, 0)
    ImageDraw.Draw(mask).polygon([TL, TR, BR, BL], fill=255)

    out = Image.open(ref_icon_path).convert('RGBA')   # 打底：保留投影/发光
    out.paste(warped, (0, 0), mask)
    out.save(out_path, 'PNG', optimize=True)

    a = np.array(out)[:, :, 3]
    ys, xs = np.nonzero(a > 16)
    print(f'  {out_path}')
    print(f'    画布{out.size} bbox=({xs.min()},{ys.min()})-({xs.max()},{ys.max()}) '
          f'不透明占比{(a > 16).mean() * 100:.1f}%')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main(*sys.argv[1:4])
