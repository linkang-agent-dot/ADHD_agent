# -*- coding: utf-8 -*-
"""队徽主体占比标准化: trim真实主体bbox -> 等比缩放到长边=画布*ratio -> 居中贴透明画布。
用法: python _normalize_badge.py <png路径> [ratio默认0.82] [画布默认256]
对齐标杆BRA/FRA(~82%)。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
import numpy as np

def normalize(path, ratio=0.82, canvas=256):
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    alpha = a[:, :, 3]
    ys, xs = np.where(alpha > 40)  # 真实主体(阈值避抗锯齿噪点)
    if len(xs) == 0:
        print('空图', path); return
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    crop = im.crop((x0, y0, x1 + 1, y1 + 1))
    cw, ch = crop.size
    target = int(canvas * ratio)
    scale = target / max(cw, ch)
    nw, nh = max(1, int(cw * scale)), max(1, int(ch * scale))
    crop = crop.resize((nw, nh), Image.LANCZOS)
    out = Image.new('RGBA', (canvas, canvas), (0, 0, 0, 0))
    out.paste(crop, ((canvas - nw) // 2, (canvas - nh) // 2), crop)
    out.save(path)
    a2 = np.array(out)[:, :, 3]
    ys2, xs2 = np.where(a2 > 40)
    w = (xs2.max() - xs2.min() + 1) / canvas * 100
    h = (ys2.max() - ys2.min() + 1) / canvas * 100
    print(f'{path.split(chr(92))[-1]}: 标准化后占画面 宽{w:.0f}% 高{h:.0f}%')

if __name__ == '__main__':
    path = sys.argv[1]
    ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.82
    normalize(path, ratio)
