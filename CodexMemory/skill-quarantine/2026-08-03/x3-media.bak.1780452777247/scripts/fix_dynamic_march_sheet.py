from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter

CELL_SIZE = 256
GRID_COLS = 4
GRID_ROWS = 4


def _build_foreground_mask(cell: Image.Image) -> Image.Image:
    rgb = cell.convert("RGB")
    mask = Image.new("L", cell.size, 0)
    w, h = cell.size
    src = rgb.load()

    bg_candidates = [[False for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            mx = max(r, g, b)
            mn = min(r, g, b)
            sat = mx - mn
            lum = (r + g + b) / 3.0

            # Treat low-saturation checkerboard colors as candidate background,
            # then keep only the candidate area that is connected to cell borders.
            bg_candidates[y][x] = sat < 30 and 24 <= lum <= 250

    bg = [[False for _ in range(w)] for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    for x in range(w):
        if bg_candidates[0][x]:
            bg[0][x] = True
            q.append((x, 0))
        if bg_candidates[h - 1][x] and not bg[h - 1][x]:
            bg[h - 1][x] = True
            q.append((x, h - 1))
    for y in range(h):
        if bg_candidates[y][0] and not bg[y][0]:
            bg[y][0] = True
            q.append((0, y))
        if bg_candidates[y][w - 1] and not bg[y][w - 1]:
            bg[y][w - 1] = True
            q.append((w - 1, y))

    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and bg_candidates[ny][nx] and not bg[ny][nx]:
                bg[ny][nx] = True
                q.append((nx, ny))

    dst = mask.load()
    for y in range(h):
        for x in range(w):
            dst[x, y] = 0 if bg[y][x] else 255

    # Close small holes and keep line art.
    mask = mask.filter(ImageFilter.MaxFilter(3))
    mask = mask.filter(ImageFilter.MaxFilter(3))
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = _keep_largest_component(mask)
    return mask


def _extract_cell_content(cell: Image.Image, crop_pad: int) -> Image.Image:
    mask = _build_foreground_mask(cell)
    bbox = mask.getbbox()
    if not bbox:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    l = max(0, bbox[0] - crop_pad)
    t = max(0, bbox[1] - crop_pad)
    r = min(cell.size[0], bbox[2] + crop_pad)
    b = min(cell.size[1], bbox[3] + crop_pad)

    cropped = cell.crop((l, t, r, b)).convert("RGBA")
    cropped_mask = mask.crop((l, t, r, b))
    cropped.putalpha(cropped_mask)
    _remove_edge_line_artifacts(cropped)
    _clear_hidden_rgb(cropped)
    return cropped


def _extract_consistent_half_body(
    cell: Image.Image,
    *,
    crop_width_ratio: float,
    crop_height_ratio: float,
    anchor_y_ratio: float,
    top_lock: bool,
) -> Image.Image:
    mask = _build_foreground_mask(cell)
    bbox = mask.getbbox()

    crop_w = max(1, int(round(cell.size[0] * crop_width_ratio)))
    crop_h = max(1, int(round(cell.size[1] * crop_height_ratio)))

    if bbox:
        px = mask.load()
        total = 0
        sum_x = 0.0
        sum_y = 0.0
        for y in range(mask.size[1]):
            for x in range(mask.size[0]):
                if px[x, y]:
                    total += 1
                    sum_x += x
                    sum_y += y
        if total:
            center_x = sum_x / total
            center_y = sum_y / total
        else:
            center_x = (bbox[0] + bbox[2]) / 2.0
            center_y = (bbox[1] + bbox[3]) / 2.0
    else:
        center_x = cell.size[0] / 2.0
        center_y = cell.size[1] / 2.0

    left = int(round(center_x - crop_w / 2.0))
    left = max(0, min(cell.size[0] - crop_w, left))
    if top_lock:
        top = 0
    else:
        top = int(round(center_y - crop_h * anchor_y_ratio))
        top = max(0, min(cell.size[1] - crop_h, top))

    cropped = cell.crop((left, top, left + crop_w, top + crop_h)).convert("RGBA")
    cropped_mask = _build_foreground_mask(cropped)
    cropped.putalpha(cropped_mask)
    _remove_edge_line_artifacts(cropped)
    _clear_hidden_rgb(cropped)
    return cropped


def _clear_hidden_rgb(img: Image.Image) -> None:
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                px[x, y] = (0, 0, 0, 0)


def _alpha_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    return img.getchannel("A").getbbox()


def _keep_largest_component(mask: Image.Image) -> Image.Image:
    src = mask.load()
    w, h = mask.size
    seen = [[False for _ in range(w)] for _ in range(h)]
    best_component: list[tuple[int, int]] = []

    for y in range(h):
        for x in range(w):
            if seen[y][x] or src[x, y] == 0:
                continue

            q: deque[tuple[int, int]] = deque([(x, y)])
            seen[y][x] = True
            component: list[tuple[int, int]] = []

            while q:
                cx, cy = q.popleft()
                component.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and src[nx, ny] != 0:
                        seen[ny][nx] = True
                        q.append((nx, ny))

            if len(component) > len(best_component):
                best_component = component

    cleaned = Image.new("L", mask.size, 0)
    dst = cleaned.load()
    for x, y in best_component:
        dst[x, y] = 255
    return cleaned


def _remove_edge_line_artifacts(img: Image.Image, max_thickness: int = 3) -> None:
    alpha = img.getchannel("A")
    src = alpha.load()
    w, h = alpha.size
    seen = [[False for _ in range(w)] for _ in range(h)]
    remove_pixels: list[tuple[int, int]] = []

    for y in range(h):
        for x in range(w):
            if seen[y][x] or src[x, y] == 0:
                continue

            q: deque[tuple[int, int]] = deque([(x, y)])
            seen[y][x] = True
            component: list[tuple[int, int]] = []
            min_x = max_x = x
            min_y = max_y = y
            touches_edge = False

            while q:
                cx, cy = q.popleft()
                component.append((cx, cy))
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)
                if cx == 0 or cy == 0 or cx == w - 1 or cy == h - 1:
                    touches_edge = True

                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and src[nx, ny] != 0:
                        seen[ny][nx] = True
                        q.append((nx, ny))

            comp_w = max_x - min_x + 1
            comp_h = max_y - min_y + 1
            if touches_edge and (comp_w <= max_thickness or comp_h <= max_thickness):
                remove_pixels.extend(component)

    if not remove_pixels:
        return

    px = img.load()
    for x, y in remove_pixels:
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, 0)


def _keep_only_main_subject(img: Image.Image) -> None:
    alpha = img.getchannel("A")
    alpha = _keep_largest_component(alpha)
    img.putalpha(alpha)
    _clear_hidden_rgb(img)


def fix_sheet(
    src_path: str,
    out_path: str,
    *,
    cols: int = GRID_COLS,
    rows: int = GRID_ROWS,
    cell_size: int = CELL_SIZE,
    crop_pad: int = 10,
    fit_ratio: float = 0.78,
    paste_top_padding_ratio: float = 0.04,
    preserve_layout: bool = False,
    consistent_half_body: bool = True,
    crop_width_ratio: float = 0.72,
    crop_height_ratio: float = 0.92,
    anchor_y_ratio: float = 0.56,
    top_lock: bool = False,
) -> None:
    img = Image.open(src_path).convert("RGBA")
    w, h = img.size
    cell_w = w / cols
    cell_h = h / rows
    out_size = cell_size * cols

    canvas = Image.new("RGBA", (out_size, out_size), (0, 0, 0, 0))
    dst_cell = cell_size
    fit_w = int(cell_size * fit_ratio)
    fit_h = int(cell_size * fit_ratio)

    extracted: list[tuple[int, int, Image.Image, tuple[int, int, int, int] | None]] = []
    ref_visible_w = 0
    ref_visible_h = 0

    for row in range(rows):
        for col in range(cols):
            left = int(round(col * cell_w))
            top = int(round(row * cell_h))
            right = int(round((col + 1) * cell_w))
            bottom = int(round((row + 1) * cell_h))

            cell = img.crop((left, top, right, bottom))
            if preserve_layout:
                content = cell.resize((dst_cell, dst_cell), Image.Resampling.LANCZOS).convert("RGBA")
                content_mask = _build_foreground_mask(content)
                content.putalpha(content_mask)
                _remove_edge_line_artifacts(content)
                _clear_hidden_rgb(content)
                extracted.append((row, col, content, _alpha_bbox(content)))
                if ref_visible_w == 0 and _alpha_bbox(content):
                    bbox = _alpha_bbox(content)
                    ref_visible_w = max(1, bbox[2] - bbox[0])
                    ref_visible_h = max(1, bbox[3] - bbox[1])
                continue

            if consistent_half_body:
                content = _extract_consistent_half_body(
                    cell,
                    crop_width_ratio=crop_width_ratio,
                    crop_height_ratio=crop_height_ratio,
                    anchor_y_ratio=anchor_y_ratio,
                    top_lock=top_lock,
                )
            else:
                content = _extract_cell_content(cell, crop_pad)

            bbox = _alpha_bbox(content)
            extracted.append((row, col, content, bbox))

            if ref_visible_w == 0 and bbox:
                ref_visible_w = max(1, bbox[2] - bbox[0])
                ref_visible_h = max(1, bbox[3] - bbox[1])

    if ref_visible_w == 0 or ref_visible_h == 0:
        ref_visible_w = fit_w
        ref_visible_h = fit_h

    ref_ratio = min(fit_w / ref_visible_w, fit_h / ref_visible_h)
    target_visible_w = max(1, int(round(ref_visible_w * ref_ratio)))
    target_visible_h = max(1, int(round(ref_visible_h * ref_ratio)))

    for row, col, content, bbox in extracted:
        if bbox:
            visible_w = max(1, bbox[2] - bbox[0])
            visible_h = max(1, bbox[3] - bbox[1])
            ratio = min(target_visible_w / visible_w, target_visible_h / visible_h)
        else:
            ratio = 1.0

        new_size = (
            max(1, int(round(content.size[0] * ratio))),
            max(1, int(round(content.size[1] * ratio))),
        )
        content = content.resize(new_size, Image.Resampling.LANCZOS)
        _keep_only_main_subject(content)
        bbox = _alpha_bbox(content)

        x0 = int(round(col * dst_cell))
        y0 = int(round(row * dst_cell))
        if bbox:
            visible_w = bbox[2] - bbox[0]
            x = x0 + int((dst_cell - visible_w) / 2) - bbox[0]
            y = y0 + int(dst_cell * paste_top_padding_ratio) - bbox[1]
            y = max(y0, y)
        else:
            x = x0 + int((dst_cell - content.size[0]) / 2)
            y = y0 + int(dst_cell * paste_top_padding_ratio)

        canvas.alpha_composite(content, (x, y))

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fix dynamic march emoji sheet to a fixed 4x4 grid with 256x256 cells.")
    ap.add_argument("--src", required=True, help="Input sprite sheet path")
    ap.add_argument("--out", required=True, help="Output sprite sheet path")
    ap.add_argument("--cols", type=int, default=GRID_COLS)
    ap.add_argument("--rows", type=int, default=GRID_ROWS)
    ap.add_argument("--cell-size", type=int, default=CELL_SIZE)
    ap.add_argument("--free-crop", action="store_true", help="Use adaptive crop instead of consistent half-body window")
    ap.add_argument("--preserve-layout", action="store_true", help="Keep each source cell composition and only clean background")
    ap.add_argument("--fit-ratio", type=float, default=0.78)
    ap.add_argument("--crop-width-ratio", type=float, default=0.72)
    ap.add_argument("--crop-height-ratio", type=float, default=0.92)
    ap.add_argument("--anchor-y-ratio", type=float, default=0.56)
    ap.add_argument("--top-lock", action="store_true", help="Lock crop to the top edge for stricter exposure consistency")
    ap.add_argument("--paste-top-padding-ratio", type=float, default=0.04)
    args = ap.parse_args()

    fix_sheet(
        args.src,
        args.out,
        cols=args.cols,
        rows=args.rows,
        cell_size=args.cell_size,
        fit_ratio=args.fit_ratio,
        paste_top_padding_ratio=args.paste_top_padding_ratio,
        preserve_layout=args.preserve_layout,
        consistent_half_body=not args.free_crop,
        crop_width_ratio=args.crop_width_ratio,
        crop_height_ratio=args.crop_height_ratio,
        anchor_y_ratio=args.anchor_y_ratio,
        top_lock=args.top_lock,
    )
    print(args.out)


if __name__ == "__main__":
    main()
