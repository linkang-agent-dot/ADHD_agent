#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ui_extract_postprocess.py — Resize + 量化压缩 UI 拆解产物

输入：<DLDIR>/<id>_nobg_trimmed.png（已抠图+裁剪）
输出：<DLDIR>/<id>_resized.png（按 element_class 等比缩放）
      <DLDIR>/<id>_final.png（量化压缩，入 Unity 用）

用法：
  python ui_extract_postprocess.py --input-dir <DLDIR> --manifest <DLDIR>/manifest.json

manifest.json 格式：{"slider_full": "slider", "btn_minus": "button", ...}

退出码：0=全部 OK；1=有元素失败/缺失。
"""
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    print("[FATAL] Pillow not installed. pip install Pillow", file=sys.stderr)
    sys.exit(2)

# X3 项目图标规范：所有 icon 类都放进 256×256 透明画布，边缘留 20px padding
ICON_CANVAS_PX = 256
ICON_PADDING_PX = 20
# 视为"图标"的 element_class（命中 → 走 256 画布规范化）
ICON_CLASSES = {"micro_icon", "small_icon", "button", "tab"}
# 非图标 element_class（命中 → 不缩放，trimmed 直接当 final，仅做无损 optipng/pngquant）
NON_ICON_CLASSES = {"slider", "title_frame", "panel"}

# 文件大小预算（仅做 warn 用）
SIZE_LIMIT_KB = {
    "micro_icon":  20,
    "small_icon":  25,
    "button":      30,
    "tab":         35,
    "slider":      50,
    "title_frame": 80,
    "panel":       150,
}
# 量化色数
QUANT_COLORS = {
    "micro_icon":  256,
    "small_icon":  256,
    "button":      256,
    "tab":         256,
    "slider":      256,
    "title_frame": 256,
    "panel":       256,
}

DEFAULT_HISTORY = Path(__file__).resolve().parent.parent / "state" / "history.jsonl"


def normalize_to_icon_canvas(src: Path, dst: Path, canvas: int = ICON_CANVAS_PX,
                              padding: int = ICON_PADDING_PX) -> tuple[int, int]:
    """X3 图标规范：把元素居中放入 canvas×canvas 透明画布，最长边缩放到 (canvas - 2*padding)。"""
    img = Image.open(src).convert("RGBA")
    inner = canvas - 2 * padding
    # 等比缩放使最长边 = inner，最短边按比例
    img.thumbnail((inner, inner), Image.LANCZOS)
    canvas_img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    x = (canvas - img.width) // 2
    y = (canvas - img.height) // 2
    canvas_img.paste(img, (x, y), img)
    canvas_img.save(dst, "PNG")
    return canvas_img.size


def copy_trimmed_as_final(src: Path, dst: Path) -> tuple[int, int]:
    """非图标类：trimmed 不再 resize，直接 copy 当 _resized.png 给量化用。"""
    img = Image.open(src).convert("RGBA")
    img.save(dst, "PNG")
    return img.size


def _try(cmd: list[str]) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def quantize(src: Path, dst: Path, colors: int) -> str:
    """Try pngquant → oxipng → optipng → PIL. Return tool name used."""
    if shutil.which("pngquant"):
        if _try([
            "pngquant", "--quality", "70-95", "--speed", "1", "--strip", "--force",
            "--output", str(dst), str(colors), str(src),
        ]):
            return "pngquant"
    if shutil.which("oxipng"):
        if _try(["oxipng", "-o", "4", "--strip", "safe", "--out", str(dst), str(src)]):
            return "oxipng"
    if shutil.which("optipng"):
        if _try(["optipng", "-o7", "-strip", "all", "-out", str(dst), str(src)]):
            return "optipng"
    # PIL 兜底（无 pngquant 量化，但开 optimize）
    Image.open(src).save(dst, "PNG", optimize=True)
    return "pil_optimize"


def append_history(record: dict, history_path: Path) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_one(element_id: str, element_class: str, input_dir: Path,
                ref_path: Optional[str] = None) -> dict:
    """Returns a result dict with status, sizes, tool used."""
    src = input_dir / f"{element_id}_nobg_trimmed.png"
    resized = input_dir / f"{element_id}_resized.png"
    final = input_dir / f"{element_id}_final.png"

    result: dict = {
        "id": element_id,
        "element_class": element_class,
        "ok": False,
    }

    is_icon = element_class in ICON_CLASSES
    is_non_icon = element_class in NON_ICON_CLASSES
    if not is_icon and not is_non_icon:
        result["error"] = f"unknown element_class: {element_class} (not in ICON_CLASSES nor NON_ICON_CLASSES)"
        return result
    if not src.exists():
        result["error"] = f"missing source: {src}"
        return result

    try:
        if is_icon:
            # X3 图标规范：256×256 透明画布，20px padding
            w, h = normalize_to_icon_canvas(src, resized)
            result["resized_px"] = f"{w}x{h}"
            result["icon_canvas"] = f"{ICON_CANVAS_PX}x{ICON_CANVAS_PX}+pad{ICON_PADDING_PX}"
        else:
            # 非图标（panel / title_frame / slider）：保留 trimmed 原始尺寸
            w, h = copy_trimmed_as_final(src, resized)
            result["resized_px"] = f"{w}x{h} (no_resize)"
    except Exception as e:
        result["error"] = f"normalize failed: {e}"
        return result

    try:
        tool = quantize(resized, final, QUANT_COLORS[element_class])
        result["quant_tool"] = tool
    except Exception as e:
        result["error"] = f"quantize failed: {e}"
        return result

    size_b = final.stat().st_size
    size_kb = size_b / 1024
    target_kb = SIZE_LIMIT_KB[element_class]
    result["final_size_kb"] = round(size_kb, 1)
    result["target_kb"] = target_kb
    result["oversize"] = size_kb > target_kb * 1.5
    result["ok"] = True
    result["final_path"] = str(final)
    if ref_path:
        result["ref"] = ref_path
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="ui_extract resize + quantize postprocess")
    ap.add_argument("--input-dir", required=True, help="Directory containing <id>_nobg_trimmed.png files")
    ap.add_argument("--manifest", required=True, help="JSON file: {id: element_class}")
    ap.add_argument("--ref", default=None, help="Optional reference image path for history record")
    ap.add_argument("--history", default=str(DEFAULT_HISTORY), help="history.jsonl path")
    ap.add_argument("--no-history", action="store_true", help="Skip writing history.jsonl")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"[FATAL] input dir not found: {input_dir}", file=sys.stderr)
        return 2

    with io.open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    if not isinstance(manifest, dict) or not manifest:
        print(f"[FATAL] manifest must be non-empty JSON object: {args.manifest}", file=sys.stderr)
        return 2

    history_path = Path(args.history)
    ts = time.strftime("%Y-%m-%d")

    print(f"[info] processing {len(manifest)} elements from {input_dir}")
    fail_ids: list[str] = []
    over_ids: list[str] = []

    for element_id, element_class in manifest.items():
        r = process_one(element_id, element_class, input_dir, ref_path=args.ref)
        if r["ok"]:
            tag = "OVER" if r["oversize"] else "ok"
            print(
                f"  [{tag:4}] {element_id:24} {element_class:11} "
                f"{r['resized_px']:>9}  {r['final_size_kb']:6.1f}KB  "
                f"(<= {r['target_kb']}KB target via {r['quant_tool']})"
            )
            if r["oversize"]:
                over_ids.append(element_id)
            if not args.no_history:
                append_history({
                    "ts": ts,
                    "type": "ui_extract/postprocess",
                    "model": "pil_local+" + r["quant_tool"],
                    "backend": "local",
                    "id": element_id,
                    "element_class": element_class,
                    "final_size_kb": r["final_size_kb"],
                    "oversize": r["oversize"],
                    "results": [r["final_path"]],
                    **({"refs": [r["ref"]]} if r.get("ref") else {}),
                }, history_path)
        else:
            print(f"  [FAIL] {element_id:24} {r.get('error')}", file=sys.stderr)
            fail_ids.append(element_id)

    print()
    print(f"[done] success={len(manifest) - len(fail_ids)}/{len(manifest)}  "
          f"oversize={len(over_ids)}  failed={len(fail_ids)}")
    if over_ids:
        print(f"[warn] oversize ids (final >150% target): {', '.join(over_ids)}")
    if fail_ids:
        print(f"[fail] failed ids: {', '.join(fail_ids)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
