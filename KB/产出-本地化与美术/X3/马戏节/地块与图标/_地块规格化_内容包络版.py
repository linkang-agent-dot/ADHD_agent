# -*- coding: utf-8 -*-
"""
大富翁地块图规格化（内容包络版）—— 修 `_规格化脚本.py` 的 contain+居中 缺陷

🔴 缺陷根因（2026-07-28 马戏节实证）：
    老脚本 `r = min(tw/w, th/h)` + 居中 = **把内容撑满画布**。
    深海原件是美术画的、自带留白（内容只占画布 28-39%）；
    马戏是 AI 出图被 trim 紧裁后再 contain 撑满 → 同是 184×224，内容却占到 39-55%。
    → **"规格化"只对齐了画布尺寸，没对齐内容占位** → 棋格坐标照抄深海，但地块胖了一圈 → 挤成一坨。
    凡过老脚本的透明资产都有同样隐患，不止地块。

本脚本的两条修正：
    ① 目标不是"填满画布"，而是 **内容 bbox ≤ 指定包络**（这里=深海族的 165×170）
    ② **底边对齐**而非垂直居中 —— 地块是站在地面上的物件，
       只缩不对齐会变成一排浮空/陷地的高低差（深海五张底边 198-204，基线取 201）

用法: python _地块规格化_内容包络版.py [--dry-run]
输入 = KB 2048 原件（不是已压到 184px 的客户端图，避免二次重采样）
输出 = 直接覆盖 client 同名文件（画布仍 184×224 → prefab / DK / 代码零改动）
"""
import argparse, os, sys
from PIL import Image

KB     = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\马戏节\地块与图标'
CLIENT = r'C:\x3-project\client\Assets\Res\UI\Spirits\ActvVoyage'
BACKUP = os.path.join(KB, '_缩放对比', '_改前客户端原件')

CANVAS      = (184, 224)
ENVELOPE    = (165, 170)   # 内容 bbox 上限 = 深海族包络（深海实测 w 157-184 / h 127-170）
BASELINE_Y  = 201          # 底边基线 = 深海五张 bbox 底边 198/200/201/202/204 的均值

# 只动超标的三张；start(39.0% 本就正确) / mystery(仅+4pt) 不动
TARGETS = ['lucky', 'diamond', 'treasure']


def stats(im):
    a = im.split()[3]
    bb = a.getbbox()
    w, h = im.size
    px = a.load()
    cnt = sum(1 for y in range(0, h, 2) for x in range(0, w, 2) if px[x, y] > 30)
    total = len(range(0, h, 2)) * len(range(0, w, 2))
    return bb, (bb[2]-bb[0], bb[3]-bb[1]), cnt / total * 100


def rebuild(src_2048):
    """从 2048 原件重建 184×224：内容缩到 ENVELOPE 内，水平居中，底边对齐 BASELINE_Y。"""
    im = Image.open(src_2048).convert('RGBA')
    bb = im.split()[3].getbbox()
    content = im.crop(bb)
    ew, eh = ENVELOPE
    s = min(ew / content.width, eh / content.height)
    nw, nh = max(1, round(content.width * s)), max(1, round(content.height * s))
    content = content.resize((nw, nh), Image.LANCZOS)
    out = Image.new('RGBA', CANVAS, (0, 0, 0, 0))
    out.paste(content, ((CANVAS[0] - nw) // 2, BASELINE_Y - nh), content)
    return out


def main(dry):
    os.makedirs(BACKUP, exist_ok=True)
    print(f'内容包络上限 {ENVELOPE[0]}x{ENVELOPE[1]}  底边基线 y={BASELINE_Y}  画布 {CANVAS[0]}x{CANVAS[1]}\n')
    print(f"{'地块':<10} {'改前 bbox':<12} {'改前占比':<9} {'改后 bbox':<12} {'改后占比':<9} 深海参照")
    for t in TARGETS:
        kb  = os.path.join(KB, f'img_Activity_circus_island_{t}.png')
        cli = os.path.join(CLIENT, f'img_Activity_circus_island_{t}.png')
        ds  = os.path.join(CLIENT, f'img_Activity_deepsea_island_{t}.png')
        for p in (kb, cli, ds):
            if not os.path.exists(p):
                raise SystemExit(f'!! 缺文件 {p}')

        _, before_wh, before_r = stats(Image.open(cli).convert('RGBA'))
        _, ds_wh, ds_r         = stats(Image.open(ds).convert('RGBA'))
        new = rebuild(kb)
        _, after_wh, after_r   = stats(new)

        print(f"{t:<10} {before_wh[0]}x{before_wh[1]:<8} {before_r:>5.1f}%   "
              f"{after_wh[0]}x{after_wh[1]:<8} {after_r:>5.1f}%    {ds_wh[0]}x{ds_wh[1]} {ds_r:.1f}%")

        if not dry:
            Image.open(cli).save(os.path.join(BACKUP, f'{t}_改前.png'))   # 备份可回滚
            new.save(cli)
            new.save(os.path.join(KB, '_缩放对比', f'{t}_FINAL.png'))
    print('\n' + ('[dry-run] 未写盘' if dry else '✅ 已覆盖 client（改前原件备份在 _缩放对比\\_改前客户端原件\\）'))
    print('未改动: start（39.0% 本就正确） / mystery（仅超 4pt）')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    main(a.dry_run)
