#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_transparency.py — 透明资产验证闸门（icon/贴纸/道具类必须真透明）

背景：gpt 等模型对 "transparent background" 常输出**假透明**——
把灰白棋盘格 / 浅色背景烤进 RGB 像素，只在四角留一点 alpha=0，
naive 检查（mode==RGBA 或 alpha 范围含 0）会误判通过。
本脚本做确定性检测，揪出假透明。

用法：
  python verify_transparency.py <png路径> [--json]
退出码：0=通过，1=不透明/假透明（不通过，需 grfal remove_background 或重出）

检测项（任一 block 即 fail）：
  NO_ALPHA      — 非 RGBA / 无 alpha 通道
  ALL_OPAQUE    — 几乎没有透明像素（alpha 全 255）
  BORDER_OPAQUE — 外边框一圈不是透明（典型=背景没抠/烤了背景方块）
  CHECKERBOARD  — 大片 gpt 假透明棋盘格色（≈233 灰 / ≈254 白 的不透明像素）
warn（不 fail，仅提示）：
  LOW_ALPHA_RATIO — 透明占比偏低（主体可能过满，复核）
"""
import sys, json, io
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

def analyze(path):
    from PIL import Image
    im = Image.open(path)
    res = {"path": path, "size": list(im.size), "mode": im.mode,
           "blocks": [], "warns": [], "stats": {}}
    if im.mode not in ("RGBA", "LA"):
        res["blocks"].append("NO_ALPHA: mode=%s 无 alpha 通道" % im.mode)
        return res
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    n = w * h
    a = im.getchannel("A")
    alist = list(a.getdata())
    transp = sum(1 for v in alist if v <= 15)
    opaque = sum(1 for v in alist if v >= 240)
    tr_ratio = transp / n * 100
    op_ratio = opaque / n * 100
    res["stats"] = {"transp_pct": round(tr_ratio, 1), "opaque_pct": round(op_ratio, 1)}

    # ALL_OPAQUE：透明像素 < 2%
    if tr_ratio < 2:
        res["blocks"].append("ALL_OPAQUE: 透明像素仅 %.1f%%（背景没抠）" % tr_ratio)

    # BORDER_OPAQUE：外边框一圈（厚度=min(w,h)*5%，至少2px）应大部分透明
    bt = max(2, int(min(w, h) * 0.05))
    border_pts, border_transp = 0, 0
    for x in range(w):
        for y in list(range(bt)) + list(range(h - bt, h)):
            border_pts += 1
            if px[x, y][3] <= 30:
                border_transp += 1
    for y in range(bt, h - bt):
        for x in list(range(bt)) + list(range(w - bt, w)):
            border_pts += 1
            if px[x, y][3] <= 30:
                border_transp += 1
    border_transp_pct = border_transp / border_pts * 100 if border_pts else 0
    res["stats"]["border_transp_pct"] = round(border_transp_pct, 1)
    if border_transp_pct < 80:
        res["blocks"].append(
            "BORDER_OPAQUE: 外边框仅 %.0f%% 透明（应≥80%%；典型=背景没抠/烤了背景方块）"
            % border_transp_pct)

    # CHECKERBOARD：不透明像素里 gpt 假透明棋盘格色（≈233 灰 / ≈254 白）占比
    ck = 0
    for i in range(0, n, max(1, n // 20000)):  # 采样约 2 万点
        x, y = i % w, i // w
        r, g, b, al = px[x, y]
        if al >= 200 and abs(r - g) < 8 and abs(g - b) < 8:  # 近灰
            if 225 <= r <= 240 or 248 <= r <= 255:
                ck += 1
    sampled = len(range(0, n, max(1, n // 20000)))
    ck_pct = ck / sampled * 100 if sampled else 0
    res["stats"]["checkerboard_pct"] = round(ck_pct, 1)
    if ck_pct > 12:
        res["blocks"].append(
            "CHECKERBOARD: %.0f%% 像素是 gpt 假透明棋盘格灰白色（背景烤进了 RGB）" % ck_pct)

    # warn：透明占比偏低
    if not res["blocks"] and tr_ratio < 18:
        res["warns"].append("LOW_ALPHA_RATIO: 透明仅 %.0f%%，主体可能过满，复核" % tr_ratio)
    return res

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print("用法: python verify_transparency.py <png> [--json]"); sys.exit(2)
    res = analyze(args[0])
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("文件:", res["path"], res["size"], res["mode"])
        print("统计:", res.get("stats"))
        for w in res["warns"]:
            print("  ⚠️", w)
        if res["blocks"]:
            for b in res["blocks"]:
                print("  ❌", b)
            print("不通过：假透明/不透明，需 grfal remove_background 或重出")
        else:
            print("✅ 透明验证通过")
    sys.exit(1 if res["blocks"] else 0)

if __name__ == "__main__":
    main()
