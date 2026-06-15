# -*- coding: utf-8 -*-
"""从四边洪水填充抠掉纯色背景(默认白)，再可选 fit 进指定画布居中。

为什么用洪水填充而不是颜色键(color-key)：
  实体物件(奖杯/箱子/图标)常自带白色高光、白色子元素(如足球)。颜色键会把这些内部白
  一起打穿成洞。洪水填充只移除**与边缘相连**的背景白，被物件包住的内部白不与边缘连通
  → 完整保留。已在世界杯活动图标(v1/v2)验证：0 白边、内部白色足球高光不丢。

典型场景：x3-media 的 activity_icon/skill_icon 等 worker **没做透明化**、直接吐了白底图时，
  本地一步抠干净 + 收口到游戏尺寸(如 ActvIcon 124×136)，比重派 worker 跟它较劲可靠。

用法:
  python flood_remove_white_bg.py <输入png> --out <输出png> [--fit 124x136]
       [--bg 255,255,255] [--thr 235] [--ptp 16]
  --fit WxH  : 抠完按真主体保比例缩放 fit 进 WxH 透明画布居中(不变形)
  --bg       : 背景基准色(默认白 255,255,255)
  --thr      : 三通道下限阈值(>=thr 视为背景色，默认 235)
  --ptp      : 三通道极差上限(<=ptp 视为接近中性色，默认 16；防误吃彩色)
"""
import sys, io, argparse
from collections import deque
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def flood_remove(im, thr, ptp):
    arr = np.array(im.convert('RGBA'))
    H, W, _ = arr.shape
    rgb = arr[:, :, :3].astype(int)
    bgmask = (rgb[:, :, 0] >= thr) & (rgb[:, :, 1] >= thr) & (rgb[:, :, 2] >= thr) & (np.ptp(rgb, axis=2) <= ptp)
    vis = np.zeros((H, W), bool)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if bgmask[y, x] and not vis[y, x]:
                vis[y, x] = True; q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if bgmask[y, x] and not vis[y, x]:
                vis[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not vis[ny, nx] and bgmask[ny, nx]:
                vis[ny, nx] = True; q.append((ny, nx))
    arr[:, :, 3] = np.where(vis, 0, arr[:, :, 3])
    return Image.fromarray(arr, 'RGBA'), int(vis.sum())


def fit_canvas(im, W, H):
    a = im.split()[3].point(lambda p: 255 if p >= 10 else 0)
    bb = a.getbbox()
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
    ap.add_argument('--fit', default=None, help='WxH，如 124x136')
    ap.add_argument('--thr', type=int, default=235)
    ap.add_argument('--ptp', type=int, default=16)
    a = ap.parse_args()

    im = Image.open(a.src)
    im, removed = flood_remove(im, a.thr, a.ptp)
    content = im.size
    if a.fit:
        W, H = (int(v) for v in a.fit.lower().split('x'))
        im, content = fit_canvas(im, W, H)
    im.save(a.out)

    arr = np.array(im); al = arr[:, :, 3]; rgb = arr[:, :, :3].astype(int)
    Hh, Ww, _ = arr.shape
    corners = [al[2, 2], al[2, Ww - 3], al[Hh - 3, 2], al[Hh - 3, Ww - 3]]
    edge = (al > 10) & (al < 200); we = int((edge & (rgb.min(2) >= 225)).sum())
    print(f'抠掉背景 {removed} 像素 -> {a.out}')
    print(f'尺寸 {im.size} 主体 {content} 四角alpha {corners}(应全0) 偏白边缘 {we}(应≈0)')


if __name__ == '__main__':
    main()
