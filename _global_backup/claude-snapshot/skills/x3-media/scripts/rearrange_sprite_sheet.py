from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def default_indices(src_cols: int, src_rows: int, dst_cols: int, dst_rows: int) -> list[int]:
    total_src = src_cols * src_rows
    total_dst = dst_cols * dst_rows

    if src_cols == 5 and src_rows == 2 and dst_cols == 3 and dst_rows == 3:
        return [0, 1, 2, 3, 5, 6, 7, 8, 9]
    if src_cols == 5 and src_rows == 2 and dst_cols == 4 and dst_rows == 4:
        return [0, 1, 1, 2, 3, 4, 5, 5, 6, 7, 7, 8, 8, 9, 9, 8]

    out = list(range(min(total_src, total_dst)))
    while len(out) < total_dst:
        out.append(out[-1] if out else 0)
    return out


def rearrange_sheet(
    src_path: str,
    out_path: str,
    *,
    src_cols: int,
    src_rows: int,
    dst_cols: int,
    dst_rows: int,
    out_size: int = 1024,
    selected_indices: list[int] | None = None,
    white_threshold: int = 245,
    crop_pad: int = 12,
    fit_ratio: float = 0.82,
) -> None:
    if selected_indices is None:
        selected_indices = default_indices(src_cols, src_rows, dst_cols, dst_rows)

    img = Image.open(src_path).convert("RGBA")
    w, h = img.size
    src_cell_w = w / src_cols
    src_cell_h = h / src_rows

    canvas = Image.new("RGBA", (out_size, out_size), (255, 255, 255, 255))
    dst_cell_w = out_size / dst_cols
    dst_cell_h = out_size / dst_rows

    for dst_i, src_i in enumerate(selected_indices[: dst_cols * dst_rows]):
        src_r = src_i // src_cols
        src_c = src_i % src_cols
        left = int(round(src_c * src_cell_w))
        top = int(round(src_r * src_cell_h))
        right = int(round((src_c + 1) * src_cell_w))
        bottom = int(round((src_r + 1) * src_cell_h))

        cell = img.crop((left, top, right, bottom))
        rgb = cell.convert("RGB")
        bbox = rgb.point(lambda p: 0 if p > white_threshold else 255).getbbox()
        if bbox:
            l = max(0, bbox[0] - crop_pad)
            t = max(0, bbox[1] - crop_pad)
            r = min(cell.size[0], bbox[2] + crop_pad)
            b = min(cell.size[1], bbox[3] + crop_pad)
            cell = cell.crop((l, t, r, b))

        fit_w = int(dst_cell_w * fit_ratio)
        fit_h = int(dst_cell_h * fit_ratio)
        ratio = min(fit_w / cell.size[0], fit_h / cell.size[1])
        new_size = (
            max(1, int(cell.size[0] * ratio)),
            max(1, int(cell.size[1] * ratio)),
        )
        cell = cell.resize(new_size, Image.Resampling.LANCZOS)

        dst_r = dst_i // dst_cols
        dst_c = dst_i % dst_cols
        cell_x0 = int(round(dst_c * dst_cell_w))
        cell_y0 = int(round(dst_r * dst_cell_h))
        x = cell_x0 + int((dst_cell_w - cell.size[0]) / 2)
        y = cell_y0 + int((dst_cell_h - cell.size[1]) / 2)
        canvas.alpha_composite(cell, (x, y))

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="把不规则逐帧图重排成严格网格（3x3/4x4 等）")
    ap.add_argument("--src", required=True, help="输入图路径")
    ap.add_argument("--out", required=True, help="输出图路径")
    ap.add_argument("--src-cols", type=int, required=True)
    ap.add_argument("--src-rows", type=int, required=True)
    ap.add_argument("--dst-cols", type=int, required=True)
    ap.add_argument("--dst-rows", type=int, required=True)
    ap.add_argument("--out-size", type=int, default=1024)
    ap.add_argument(
        "--indices",
        default="",
        help="源帧索引，逗号分隔；不传则按内置默认或顺序补齐",
    )
    args = ap.parse_args()

    indices = None
    if args.indices.strip():
        indices = [int(x.strip()) for x in args.indices.split(",") if x.strip()]

    rearrange_sheet(
        args.src,
        args.out,
        src_cols=args.src_cols,
        src_rows=args.src_rows,
        dst_cols=args.dst_cols,
        dst_rows=args.dst_rows,
        out_size=args.out_size,
        selected_indices=indices,
    )
    print(args.out)


if __name__ == "__main__":
    main()
