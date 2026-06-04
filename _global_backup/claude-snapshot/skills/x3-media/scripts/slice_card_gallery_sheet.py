"""slice_card_gallery_sheet.py — 3x3 white-bg item sheet → 9 transparent PNGs

card_gallery 角色驱动批量生成流水线 P9 第三步：
    Step 1 (card_gallery) → 3x3 grid sheet 白底图
    Step 2 (ui_extract_fine 双底差分) → 透明背景 grid sheet
    Step 3 (本脚本) → 9 张透明独立 item PNG

设计：见 docs/plans/2026-05-29-card-gallery-role-driven-design.md (P9)

切图方法（用户研究过的最优方案，3x3 grid 切单 item 时优于直接等分裁切）：
- 连通域分析 + 按 3x3 cell 取最大 blob
- 非白 mask：亮度<240 或 饱和度>14 当前景
- 形态学闭运算填补内部小空隙
- 4 连通域 BFS 标记 → 过滤面积 < 总面积 0.3% 的噪点（label / 孤立像素）
- 按质心分配到 3x3 cell，每 cell 保留最大 blob（label 文字会被自动剔除）
- 软 alpha：dilate + GaussianBlur(1.2) 羽化边缘

用法：
    python slice_card_gallery_sheet.py <input.png> <output_dir>

输出：
    <output_dir>/slot_1.png ... slot_9.png  (RGBA)
    stdout 末尾输出一个 JSON 总结 + 进度行
"""
import sys
import os
import json
from collections import deque
import numpy as np
from PIL import Image, ImageFilter


def log(stage: str, msg: str, **extra):
    payload = {"stage": stage, "msg": msg}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def main():
    if len(sys.argv) < 3:
        log("error", "用法: slice_card_gallery_sheet.py <input.png> <output_dir>")
        sys.exit(1)
    src = sys.argv[1]
    outdir = sys.argv[2]

    if not os.path.isfile(src):
        log("error", f"源图不存在: {src}")
        sys.exit(2)
    os.makedirs(outdir, exist_ok=True)

    log("load", f"读图 {os.path.basename(src)}")
    im = Image.open(src).convert("RGB")
    arr = np.array(im)
    H, W, _ = arr.shape
    log("size", f"{W}x{H}", w=W, h=H)

    # 1) non-white mask
    R = arr[:, :, 0].astype(int)
    G = arr[:, :, 1].astype(int)
    B = arr[:, :, 2].astype(int)
    lum = (R + G + B) / 3
    sat = arr.max(axis=2).astype(int) - arr.min(axis=2).astype(int)
    mask = (lum < 240) | (sat > 14)

    # 2) morphological close — fill small inside holes
    log("morph", "形态学闭运算（填内部小空隙）")
    mim = Image.fromarray((mask * 255).astype(np.uint8))
    mim = mim.filter(ImageFilter.MaxFilter(5))  # dilate
    mim = mim.filter(ImageFilter.MinFilter(7))  # erode bigger to fill
    mask = np.array(mim) > 128

    # 3) 4-connected components via BFS
    log("cc", "4 连通域标记...")
    labels = np.zeros((H, W), np.int32)
    cur = 0
    blobs = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and labels[y, x] == 0:
                cur += 1
                q = deque([(y, x)])
                labels[y, x] = cur
                minx = maxx = x
                miny = maxy = y
                cnt = 0
                sx = 0
                sy = 0
                while q:
                    cy, cx = q.popleft()
                    cnt += 1
                    sx += cx
                    sy += cy
                    if cx < minx:
                        minx = cx
                    if cx > maxx:
                        maxx = cx
                    if cy < miny:
                        miny = cy
                    if cy > maxy:
                        maxy = cy
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and labels[ny, nx] == 0:
                            labels[ny, nx] = cur
                            q.append((ny, nx))
                blobs.append(
                    {
                        "id": cur,
                        "bbox": (minx, miny, maxx, maxy),
                        "area": cnt,
                        "cx": sx / cnt,
                        "cy": sy / cnt,
                    }
                )
    log("cc_done", f"找到 {len(blobs)} 个 blob", count=len(blobs))

    # 4) drop tiny noise (<0.3% area = label text, specks)
    total = H * W
    blobs = [b for b in blobs if b["area"] >= total * 0.003]
    log("filter", f"过滤后剩 {len(blobs)} 个 blob (剔除 < 0.3% 面积噪点)", count=len(blobs))

    # 5) assign to 3x3 cell by centroid
    cw, ch = W / 3, H / 3
    for b in blobs:
        b["row"] = min(2, int(b["cy"] // ch))
        b["col"] = min(2, int(b["cx"] // cw))

    # 6) per cell keep largest blob
    cells = {}
    for b in blobs:
        k = (b["row"], b["col"])
        if k not in cells or b["area"] > cells[k]["area"]:
            cells[k] = b

    # 7-8) crop + soft alpha + save
    results = []
    saved = 0
    for r in range(3):
        for c in range(3):
            slot = r * 3 + c + 1
            if (r, c) not in cells:
                log("miss", f"slot_{slot}: 该 cell 无 item", slot=slot)
                results.append({"slot": slot, "status": "missing"})
                continue
            b = cells[(r, c)]
            minx, miny, maxx, maxy = b["bbox"]
            pad = 8
            minx = max(0, minx - pad)
            miny = max(0, miny - pad)
            maxx = min(W - 1, maxx + pad)
            maxy = min(H - 1, maxy + pad)
            sub_rgb = arr[miny : maxy + 1, minx : maxx + 1]
            sub_mask = labels[miny : maxy + 1, minx : maxx + 1] == b["id"]
            # soft alpha: dilate + feather
            sm = Image.fromarray((sub_mask * 255).astype(np.uint8))
            sm = sm.filter(ImageFilter.MaxFilter(3))
            sm = sm.filter(ImageFilter.GaussianBlur(1.2))
            alpha = np.array(sm)
            rgba = np.dstack([sub_rgb, alpha]).astype(np.uint8)
            out = os.path.join(outdir, f"slot_{slot}.png")
            Image.fromarray(rgba, "RGBA").save(out)
            results.append({"slot": slot, "status": "ok", "file": out, "area": b["area"]})
            saved += 1
            log("save", f"slot_{slot} 保存 ({b['area']} px)", slot=slot, area=b["area"])

    log("done", f"完成 {saved}/9", saved=saved, src=src, outdir=outdir, results=results)


if __name__ == "__main__":
    main()
