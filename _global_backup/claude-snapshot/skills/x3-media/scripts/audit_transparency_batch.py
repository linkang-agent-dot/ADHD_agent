#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量透明体检 —— 一个节日/模块的美术收尾时跑一次，揪出"当年落库时没过闸门"的假透明图。

背景（2026-07-28 马戏节实证）：用户在游戏里肉眼看到一张活动图标是白底方块，回查发现同批 44 张
里有 2 张假透明——拜访礼包图（边框仅 44.9% 透明 + 37% 假棋盘格）、扭蛋机活动图标（整张全不透明）。
两张都是早期出图、`verify_transparency` 闸门规则加入之前落的库。**只信落库那一刻的闸门不够，
模块收尾要整体扫一遍。**

判据：**四边边框透明率 < 80% 即判假透明**（正常件普遍 93~100%）。RGB 模式的图自动跳过（背景类
本就不透明）。

用法：
    python audit_transparency_batch.py <根目录> [关键词] [--border-min 80]

例：
    python audit_transparency_batch.py "C:/x3-project/client/Assets/Res/UI/Spirits" circus
    python audit_transparency_batch.py "C:/x3-project/client/Assets/Res/UI/Spirits" deepsea --border-min 85

对判坏的图：调 grfal remove_background 重抠（输入直接用客户端现役文件），
再过 scripts/verify_transparency.py 闸门，通过才替换落库。
退出码：0=全部通过 / 1=存在假透明（可用于流水线卡口）
"""
import sys
import io
import os
import glob
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from PIL import Image
except ImportError:
    print("需要 Pillow：pip install pillow")
    sys.exit(2)


def border_transparent_pct(alpha, w, h):
    """四边一圈像素里 alpha==0 的占比"""
    vals = []
    for x in range(w):
        vals.append(alpha.getpixel((x, 0)))
        vals.append(alpha.getpixel((x, h - 1)))
    for y in range(h):
        vals.append(alpha.getpixel((0, y)))
        vals.append(alpha.getpixel((w - 1, y)))
    return sum(1 for v in vals if v == 0) / len(vals) * 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="扫描根目录")
    ap.add_argument("keyword", nargs="?", default="", help="文件名关键词（留空=扫全部 png）")
    ap.add_argument("--border-min", type=float, default=80.0, help="边框透明率下限，低于即判假透明")
    args = ap.parse_args()

    pattern = "**/*%s*.png" % args.keyword if args.keyword else "**/*.png"
    files = sorted(set(glob.glob(os.path.join(args.root, pattern), recursive=True)))
    if not files:
        print("没匹配到文件：%s" % pattern)
        return 0

    print("扫描 %d 张：\n" % len(files))
    bad, skipped, ok = [], 0, 0
    for p in files:
        try:
            im = Image.open(p)
        except Exception:
            print("  [读取失败] %s" % p)
            continue
        if im.mode != "RGBA":
            skipped += 1
            continue
        w, h = im.size
        alpha = im.split()[3]
        data = alpha.tobytes()
        transp = sum(1 for v in data if v == 0) / len(data) * 100
        bt = border_transparent_pct(alpha, w, h)
        if bt < args.border_min:
            bad.append((p, transp, bt))
            print("  🔴假透明 透明%5.1f%% 边框透明%5.1f%% | %dx%d %s" % (transp, bt, w, h, os.path.basename(p)))
        else:
            ok += 1
            print("  ✅ 透明%5.1f%% 边框透明%5.1f%% | %dx%d %s" % (transp, bt, w, h, os.path.basename(p)))

    print("\n合计：通过 %d / 假透明 %d / 跳过(非RGBA) %d" % (ok, len(bad), skipped))
    if bad:
        print("\n===== 需要重抠的 =====")
        for p, t, b in bad:
            print("  🔴 %s  (边框仅 %.1f%% 透明)" % (p, b))
        print("\n修法：grfal remove_background 重抠 → verify_transparency 过闸 → 同名覆盖落库")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
