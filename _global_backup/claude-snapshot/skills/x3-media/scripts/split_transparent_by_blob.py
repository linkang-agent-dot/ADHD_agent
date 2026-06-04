#!/usr/bin/env python3
"""
split_transparent_by_blob.py — 把一张透明背景 PNG 自动拆成 N 张独立元素 PNG

使用场景：
  双底差分（ui_extract_fine）拿到的整张透明 PNG，里面有多个孤立元素（每个带软阴影/光晕），
  想拆成独立 PNG。常规连通域分析会因为软阴影 alpha 渐变把同一元素切散，本脚本用
  膨胀（dilate）把元素 + 阴影连接起来识别为同一 blob，再按 bbox 裁原图。

核心算法：
  1. 读 RGBA PNG
  2. 用低 alpha 阈值（默认 5）二值化得到 fg mask
  3. 形态学膨胀（默认半径 6px）把元素 + 其投影阴影/光晕边缘连到一起
  4. 4 连通找 blobs
  5. 过滤太小的 blob（默认 min_area=2000 像素）
  6. 对每个 blob bbox + padding，从**原图**切（不是膨胀图！保留真实软 alpha）

输出：
  - element_1.png, element_2.png, ..., element_N.png（按面积倒序）
  - JSON 进度行（stdin 流式协议）：
      {"stage":"read","width":W,"height":H,"alpha_min":..,"alpha_max":..}
      {"stage":"mask","fg_pixels":...,"fg_pct":...}
      {"stage":"dilate","radius":6,"connected_pixels":...}
      {"stage":"blobs","count":N,"after_filter":M,"filtered_out":[...]}
      {"stage":"crop","index":1,"file":"...","bbox":[x,y,w,h],"area":...}
      {"stage":"done","outdir":"...","results":[...]}

用法：
  python split_transparent_by_blob.py <input.png> <out_dir>
  python split_transparent_by_blob.py <input.png> <out_dir> \
      --min-area 1500 --padding 6 --dilate 8 --alpha-threshold 5

依赖：Pillow + numpy（不需要 OpenCV，所有操作 numpy 自己做）
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def emit(stage: str, **kwargs) -> None:
    """流式 JSON 行输出（主进程解析）"""
    print(json.dumps({"stage": stage, **kwargs}, ensure_ascii=False), flush=True)


def dilate_mask(mask: np.ndarray, radius: int) -> np.ndarray:
    """
    形态学膨胀，纯 numpy 实现（避免 OpenCV/scipy 依赖）。
    用方形 kernel + 多次 1px 膨胀替代。对小半径（< 20）足够快。
    """
    out = mask.copy()
    for _ in range(radius):
        # 4 邻域膨胀：上/下/左/右移位后 OR
        u = np.zeros_like(out)
        u[:-1, :] = out[1:, :]
        d = np.zeros_like(out)
        d[1:, :] = out[:-1, :]
        l_ = np.zeros_like(out)
        l_[:, :-1] = out[:, 1:]
        r = np.zeros_like(out)
        r[:, 1:] = out[:, :-1]
        out = out | u | d | l_ | r
    return out


def label_4connected(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """
    4 连通组件标记（纯 numpy + 栈式 BFS，类似 flood fill）。
    返回 (labels, num_blobs)，labels[i,j] = 0 表背景，> 0 表 blob id。
    """
    H, W = mask.shape
    labels = np.zeros((H, W), dtype=np.int32)
    cur = 0
    # 用 list 当栈（Python 栈快过 deque 在小规模）
    for y0 in range(H):
        for x0 in range(W):
            if not mask[y0, x0] or labels[y0, x0] != 0:
                continue
            cur += 1
            stack = [(y0, x0)]
            while stack:
                y, x = stack.pop()
                if y < 0 or y >= H or x < 0 or x >= W:
                    continue
                if not mask[y, x] or labels[y, x] != 0:
                    continue
                labels[y, x] = cur
                stack.append((y - 1, x))
                stack.append((y + 1, x))
                stack.append((y, x - 1))
                stack.append((y, x + 1))
    return labels, cur


def split(
    input_path: Path,
    out_dir: Path,
    min_area: int = 2000,
    padding: int = 8,
    dilate_radius: int = 6,
    alpha_threshold: int = 5,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    H, W = arr.shape[:2]
    alpha = arr[..., 3]
    emit(
        "read",
        path=str(input_path),
        width=W,
        height=H,
        alpha_min=int(alpha.min()),
        alpha_max=int(alpha.max()),
    )

    # 1. 低阈值前景 mask
    fg = alpha > alpha_threshold
    fg_pixels = int(fg.sum())
    fg_pct = fg_pixels / (W * H) * 100
    emit("mask", fg_pixels=fg_pixels, fg_pct=round(fg_pct, 2))
    if fg_pixels == 0:
        emit("done", outdir=str(out_dir), results=[])
        return

    # 2. 膨胀连接软阴影边缘
    dilated = dilate_mask(fg, dilate_radius)
    emit("dilate", radius=dilate_radius, connected_pixels=int(dilated.sum()))

    # 3. 连通域标记
    labels, num = label_4connected(dilated)

    # 4. 收集每个 blob 的统计（基于膨胀图算 bbox；面积用原 fg 算，避免膨胀虚胖）
    raw_blobs = []
    for bid in range(1, num + 1):
        ys, xs = np.where(labels == bid)
        if len(xs) == 0:
            continue
        y0, y1 = int(ys.min()), int(ys.max())
        x0, x1 = int(xs.min()), int(xs.max())
        # 真实面积（不膨胀，落到该 blob 区域内的原 fg 像素）
        sub_fg = fg[y0 : y1 + 1, x0 : x1 + 1]
        sub_lab = labels[y0 : y1 + 1, x0 : x1 + 1] == bid
        true_area = int((sub_fg & sub_lab).sum())
        raw_blobs.append({"id": bid, "bbox_in": [x0, y0, x1 - x0 + 1, y1 - y0 + 1], "area": true_area})

    # 5. 过滤太小的（按真实面积）
    kept = [b for b in raw_blobs if b["area"] >= min_area]
    dropped = [b for b in raw_blobs if b["area"] < min_area]
    # 按面积倒序，最大的元素为 element_1
    kept.sort(key=lambda b: b["area"], reverse=True)
    emit(
        "blobs",
        count=len(raw_blobs),
        after_filter=len(kept),
        filtered_out=[{"area": b["area"]} for b in dropped[:10]],
    )

    # 6. 裁切每个 blob（用**原图** RGBA，不用膨胀图！这样软阴影保真）
    results = []
    for i, blob in enumerate(kept, start=1):
        x, y, w, h = blob["bbox_in"]
        # 加 padding，但 clamp 到图像边界
        x0 = max(0, x - padding)
        y0 = max(0, y - padding)
        x1 = min(W, x + w + padding)
        y1 = min(H, y + h + padding)
        # 用 mask 把 bbox 内其他 blob 的像素抹掉（避免重叠时邻居元素被切进来）
        crop = arr[y0:y1, x0:x1].copy()
        lab_crop = labels[y0:y1, x0:x1]
        # 仅保留属于当前 blob 的像素 alpha；其余 alpha 置 0
        belongs = lab_crop == blob["id"]
        crop[..., 3] = np.where(belongs, crop[..., 3], 0)
        out_path = out_dir / f"element_{i}.png"
        Image.fromarray(crop, mode="RGBA").save(out_path, optimize=True)
        rec = {
            "index": i,
            "file": str(out_path),
            "bbox": [x0, y0, x1 - x0, y1 - y0],
            "area": blob["area"],
        }
        results.append(rec)
        emit("crop", **rec)

    emit("done", outdir=str(out_dir), results=results)


def main():
    p = argparse.ArgumentParser(
        description="Split a transparent PNG into individual element PNGs by blob detection"
    )
    p.add_argument("input", help="输入 RGBA PNG 路径")
    p.add_argument("out_dir", help="输出目录（element_*.png 落到这里）")
    p.add_argument(
        "--min-area", type=int, default=2000, help="过滤小于此面积的 blob（默认 2000 像素）"
    )
    p.add_argument(
        "--padding", type=int, default=8, help="裁切时每边加的 padding 像素（默认 8）"
    )
    p.add_argument(
        "--dilate",
        type=int,
        default=6,
        help="膨胀半径（用于把元素 + 软阴影边缘连到同一 blob，默认 6）",
    )
    p.add_argument(
        "--alpha-threshold",
        type=int,
        default=5,
        help="前景判定 alpha 阈值（>此值算前景，默认 5；越小越保软阴影）",
    )
    args = p.parse_args()

    inp = Path(args.input)
    out = Path(args.out_dir)
    if not inp.exists():
        emit("error", msg=f"input not found: {inp}")
        sys.exit(2)
    try:
        split(
            inp,
            out,
            min_area=args.min_area,
            padding=args.padding,
            dilate_radius=args.dilate,
            alpha_threshold=args.alpha_threshold,
        )
    except Exception as e:
        emit("error", msg=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
