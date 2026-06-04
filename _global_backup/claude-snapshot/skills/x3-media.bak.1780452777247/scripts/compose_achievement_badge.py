"""
成就徽章合成：同一张中央图 + 5 张不同底板，输出 128×128（与 x3-media type-achievement-badge 流程一致）。

底板清单默认见 references/achievement_badge_manifest.json（仓库内固定 5 张 PNG），
勿再用单张参考图 + 色相偏移冒充 5 底板。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def load_bases_from_manifest(manifest_path: Path) -> tuple[list[dict], float]:
    """
    返回 (底板条目列表, 默认 icon_scale)。
    每条: {"id", "path", "icon_scale": Optional[float]}，icon_scale 缺省则用全局默认。
    """
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    default_scale = float(data.get("default_icon_scale", 0.35))
    out: list[dict] = []
    for b in data["bases"]:
        rel = b["file"]
        p = (root / rel).resolve()
        bid = str(b.get("id", b.get("name", "")))
        entry: dict = {"id": bid, "path": p}
        if "icon_scale" in b and b["icon_scale"] is not None:
            entry["icon_scale"] = float(b["icon_scale"])
        out.append(entry)
    return out, default_scale


# 兼容旧流程：仅 1 张底板时用色相伪造多档（不推荐）
TIER_SHIFTS = (
    (0, 1.0),
    (8, 1.05),
    (-10, 0.92),
    (18, 1.08),
    (-18, 0.88),
)


def _tint_base_rgba(base_rgba: np.ndarray, hue_shift: int, sat_scale: float) -> np.ndarray:
    bgr = cv2.cvtColor(base_rgba[:, :, :3], cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_scale, 0, 255)
    hsv = hsv.astype(np.uint8)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    out = base_rgba.copy()
    out[:, :, :3] = rgb
    return out


def _fit_center_icon(icon: Image.Image, canvas_w: int, canvas_h: int, scale: float) -> Image.Image:
    icon = icon.convert("RGBA")
    max_w = int(canvas_w * scale)
    max_h = int(canvas_h * scale)
    iw, ih = icon.size
    r = min(max_w / iw, max_h / ih, 1.0)
    nw, nh = max(1, int(iw * r)), max(1, int(ih * r))
    return icon.resize((nw, nh), Image.Resampling.LANCZOS)


def _tint_center_gold(
    icon: Image.Image,
    strength: float = 0.98,
    *,
    crystalline: bool = True,
) -> Image.Image:
    """
    中央图标金色化。
    - crystalline=True：对齐参考图（高饱和金黄、左上受光、裂隙琥珀阴影、粗黑外描边+块面内线）。
    - strength=0：不处理。
    """
    if strength <= 0:
        return icon

    arr = np.array(icon.convert("RGBA"))
    h, w = arr.shape[:2]
    a = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)

    if not crystalline:
        return _tint_center_gold_soft(rgb, a, strength)

    _, mask_hard = cv2.threshold(a.astype(np.uint8), 20, 255, cv2.THRESH_BINARY)

    gray = np.dot(rgb, [0.299, 0.587, 0.114])
    gray_u8 = np.clip(gray, 0, 255).astype(np.uint8)
    if np.any(mask_hard > 0):
        clahe = cv2.createCLAHE(clipLimit=4.5, tileGridSize=(8, 8))
        gray_enh = clahe.apply(gray_u8)
        gray_f = gray_enh.astype(np.float32) * 0.9 + gray_u8.astype(np.float32) * 0.1
    else:
        gray_f = gray_u8.astype(np.float32)

    # 左上受光（与参考图高光方向一致）
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nl = (xx / max(w - 1, 1.0) + yy / max(h - 1, 1.0)) * 0.5
    gray_f = np.clip(gray_f * (0.92 + 0.28 * (1.0 - nl)), 0, 255)

    t_raw = np.power(np.clip(gray_f / 255.0, 0, 1), 0.48)
    t = np.clip(0.06 + 0.94 * t_raw, 0, 1)
    t1 = t[..., None]

    # 参考图采样：暗部琥珀金、体块金黄、高光近白黄（RGB 来自 gold 区域统计）
    c0 = np.array([98.0, 73.0, 39.0])
    c1 = np.array([168.0, 134.0, 62.0])
    c2 = np.array([237.0, 191.0, 40.0])
    c3 = np.array([255.0, 250.0, 220.0])
    u = t1
    gold = np.where(
        u < 0.45,
        (1.0 - u / 0.45) ** 2 * c0
        + 2.0 * (u / 0.45) * (1.0 - u / 0.45) * c1
        + (u / 0.45) ** 2 * np.array([200.0, 155.0, 48.0]),
        (1.0 - (u - 0.45) / 0.55) ** 2 * np.array([200.0, 155.0, 48.0])
        + 2.0 * ((u - 0.45) / 0.55) * (1.0 - (u - 0.45) / 0.55) * c2
        + ((u - 0.45) / 0.55) ** 2 * c3,
    )
    gold = np.clip(gold, 0, 255)

    w_blend = np.clip((strength * (a / 255.0))[:, :, None] * 1.02, 0.0, 1.0)
    if strength >= 0.94:
        body_rgb = gold * w_blend + rgb * (1.0 - w_blend)
    else:
        body_rgb = rgb * (1.0 - w_blend) + gold * w_blend

    body_u8 = np.clip(body_rgb, 0, 255).astype(np.uint8)
    bgr = cv2.cvtColor(body_u8, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    mh = mask_hard > 0
    # 锁 H≈21；S/V 压到与参考图统计接近（参考 gold 区 mean S≈151、V≈168）
    hsv[..., 0] = np.where(mh, 21.0, hsv[..., 0])
    hsv[..., 1] = np.where(
        mh,
        np.clip(hsv[..., 1] * 0.72 + 38.0, 95.0, 175.0),
        hsv[..., 1],
    )
    hsv[..., 2] = np.where(
        mh,
        np.clip(hsv[..., 2] * 0.88 + 10.0, 0.0, 255.0),
        hsv[..., 2],
    )
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    body_rgb = cv2.cvtColor(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2RGB).astype(np.float32)

    # 块面内线（略粗、深，贴近参考「分段黑线」）
    blurred = cv2.GaussianBlur(gray_u8, (0, 0), 0.9)
    gx = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    m_in = mag[mask_hard > 0]
    th = float(np.percentile(m_in, 68)) if m_in.size > 0 else 30.0
    p95 = float(np.percentile(m_in, 95)) if m_in.size > 0 else 100.0
    inner_edge = (mag > th * 0.48) & (mask_hard > 0)
    inner_edge = cv2.dilate(inner_edge.astype(np.uint8) * 255, np.ones((2, 2), np.uint8))
    edge_w = (np.minimum(mag / (p95 + 1e-6), 1.0) * (inner_edge > 0).astype(np.float32))
    edge_w = np.clip(edge_w * 0.72, 0, 1)[..., None]
    ink = np.array([12.0, 8.0, 4.0])
    body_rgb = body_rgb * (1.0 - edge_w * 0.68) + ink * edge_w * 0.68

    sw = max(2, min(8, min(h, w) // 38))
    ksz = sw * 2 + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksz, ksz))
    dil = cv2.dilate(mask_hard, kernel)
    outer_ring = cv2.bitwise_and(dil, cv2.bitwise_not(mask_hard))

    out = np.zeros((h, w, 4), dtype=np.float32)
    out[:, :, :3] = body_rgb
    out[:, :, 3] = a
    ring = outer_ring > 0
    out[ring, 0] = 5.0
    out[ring, 1] = 3.0
    out[ring, 2] = 2.0
    out[ring, 3] = 255.0

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def _tint_center_gold_soft(
    rgb: np.ndarray,
    a: np.ndarray,
    strength: float,
) -> Image.Image:
    """旧版：平滑金色渐变，无粗描边。"""
    gray = np.dot(rgb, [0.299, 0.587, 0.114]) / 255.0
    gray = np.clip(gray[..., None], 0, 1)
    c0 = np.array([85.0, 58.0, 22.0])
    c1 = np.array([198.0, 145.0, 38.0])
    c2 = np.array([255.0, 230.0, 140.0])
    t = gray
    gold_rgb = (1.0 - t) ** 2 * c0 + 2.0 * (1.0 - t) * t * c1 + t**2 * c2
    mask = (a > 8.0).astype(np.float32) * (strength * (a / 255.0))
    mask = mask[..., None]
    blended = rgb * (1.0 - mask) + gold_rgb * mask
    out = np.concatenate([blended, a[..., None]], axis=-1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def _paste_center(canvas: Image.Image, layer: Image.Image) -> Image.Image:
    cw, ch = canvas.size
    lw, lh = layer.size
    x = (cw - lw) // 2
    y = (ch - lh) // 2
    out = canvas.copy()
    out.alpha_composite(layer, (x, y))
    return out


def compose_badges(
    center_path: Path,
    bases: list[dict],
    out_dir: Path,
    out_size: int = 128,
    icon_scale: float = 0.35,
    prefix: str = "Achievement_Badge",
    *,
    uniform_scale: float | None = None,
    gold_strength: float = 0.98,
    gold_crystalline: bool = True,
) -> list[Path]:
    icon_src = Image.open(center_path).convert("RGBA")
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    for entry in bases:
        bid = entry["id"]
        base_path = entry["path"]
        if uniform_scale is not None:
            sc = uniform_scale
        else:
            sc = float(entry["icon_scale"]) if entry.get("icon_scale") is not None else icon_scale
        if not base_path.is_file():
            raise FileNotFoundError(f"底板不存在: {base_path}")
        base_img = Image.open(base_path).convert("RGBA")
        h, w = base_img.size[1], base_img.size[0]
        icon = _fit_center_icon(icon_src, w, h, sc)
        icon = _tint_center_gold(
            icon, strength=gold_strength, crystalline=gold_crystalline
        )
        canvas = _paste_center(base_img, icon)
        canvas = canvas.resize((out_size, out_size), Image.Resampling.LANCZOS)
        outp = out_dir / f"{prefix}_{bid}.png"
        canvas.save(outp, optimize=True)
        saved.append(outp)
    return saved


def compose_badges_legacy_tint(
    center_path: Path,
    base_path: Path,
    out_dir: Path,
    out_size: int = 128,
    icon_scale: float = 0.35,
    prefix: str = "Achievement_Badge",
    gold_strength: float = 0.98,
    gold_crystalline: bool = True,
) -> list[Path]:
    """单底板 + 5 档色相（仅兼容旧用法）。"""
    base_arr = np.array(Image.open(base_path).convert("RGBA"))
    h, w = base_arr.shape[:2]
    icon = _fit_center_icon(Image.open(center_path).convert("RGBA"), w, h, icon_scale)
    icon = _tint_center_gold(
        icon, strength=gold_strength, crystalline=gold_crystalline
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for idx, (hue_shift, sat_scale) in enumerate(TIER_SHIFTS, start=1):
        tinted = _tint_base_rgba(base_arr, hue_shift, sat_scale)
        canvas = Image.fromarray(tinted, "RGBA")
        canvas = _paste_center(canvas, icon)
        canvas = canvas.resize((out_size, out_size), Image.Resampling.LANCZOS)
        outp = out_dir / f"{prefix}_{idx:02d}.png"
        canvas.save(outp, optimize=True)
        saved.append(outp)
    return saved


def _default_manifest_path() -> Path:
    """定位 achievement_badge_manifest.json（支持 x3-media/scripts、UX/game-video-workflow 等路径）。"""
    script = Path(__file__).resolve()
    # x3-media/scripts/compose_*.py → ../references/
    p = script.parent.parent / "references" / "achievement_badge_manifest.json"
    if p.is_file():
        return p
    # UX/game-video-workflow/compose_*.py → ./references/
    p = script.parent / "references" / "achievement_badge_manifest.json"
    if p.is_file():
        return p
    for anc in script.parents:
        cand = anc / ".cursor" / "skills" / "x3-media" / "references" / "achievement_badge_manifest.json"
        if cand.is_file():
            return cand
    return script.parent / "references" / "achievement_badge_manifest.json"


def _agent_skill_root() -> Path:
    script = Path(__file__).resolve()
    for anc in script.parents:
        if (anc / ".cursor" / "skills" / "x3-media").is_dir():
            return anc
    return script.parents[2]


def main() -> None:
    root = _agent_skill_root()
    default_manifest = _default_manifest_path()
    default_center = Path(
        r"C:\Users\chaixingyu\.cursor\projects\c-Users-chaixingyu-agent-skill\assets"
        r"\c__Users_chaixingyu_AppData_Roaming_Cursor_User_workspaceStorage_8f59b2860e753065c7107ca5c8202817_images_IconRssCoal-259bf2f8-bc4f-47cb-9769-873d325f87b4.png"
    )
    default_legacy_base = (
        root
        / ".cursor"
        / "skills"
        / "x3-media"
        / "references"
        / "activity-icon-ref"
        / "Medal__15118392.png"
    )

    ap = argparse.ArgumentParser(description="合成成就徽章 128×128 ×5")
    ap.add_argument("--center", type=Path, default=default_center, help="中央内容 PNG")
    ap.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
        help="底板清单 JSON（默认 5 张固定底板）",
    )
    ap.add_argument("--out-dir", type=Path, default=Path.home() / "Downloads", help="输出目录")
    ap.add_argument("--prefix", type=str, default="Achievement_Badge_Coal", help="输出文件名前缀")
    ap.add_argument("--size", type=int, default=128, help="输出边长")
    ap.add_argument(
        "--scale",
        type=float,
        default=None,
        help="若指定：全部底板统一使用该比例（忽略 manifest 各条 icon_scale）；不指定则按 manifest 分底板缩放",
    )
    ap.add_argument(
        "--legacy-tint",
        action="store_true",
        help="使用单张 Medal + 色相偏移（旧流程，不推荐）",
    )
    ap.add_argument("--legacy-base", type=Path, default=default_legacy_base, help="--legacy-tint 时底板路径")
    ap.add_argument(
        "--gold-strength",
        type=float,
        default=0.98,
        help="中央图标金色化强度 0～1，0 为保持原色（默认 0.98，避免原图土色残留）",
    )
    ap.add_argument(
        "--gold-soft",
        action="store_true",
        help="使用旧版平滑金色（无粗黑外描边与内部块面线）",
    )
    args = ap.parse_args()

    if not args.center.is_file():
        raise SystemExit(f"找不到中央图: {args.center}")

    if args.legacy_tint:
        if not args.legacy_base.is_file():
            raise SystemExit(f"找不到 legacy 底板: {args.legacy_base}")
        scale = args.scale if args.scale is not None else 0.35
        paths = compose_badges_legacy_tint(
            args.center,
            args.legacy_base,
            args.out_dir,
            out_size=args.size,
            icon_scale=scale,
            prefix=args.prefix,
            gold_strength=args.gold_strength,
            gold_crystalline=not args.gold_soft,
        )
    else:
        if not args.manifest.is_file():
            raise SystemExit(f"找不到 manifest: {args.manifest}")
        bases, manifest_default = load_bases_from_manifest(args.manifest)
        if len(bases) != 5:
            raise SystemExit(f"manifest 底板数量应为 5，当前 {len(bases)}")
        paths = compose_badges(
            args.center,
            bases,
            args.out_dir,
            out_size=args.size,
            icon_scale=manifest_default,
            prefix=args.prefix,
            uniform_scale=args.scale,
            gold_strength=args.gold_strength,
            gold_crystalline=not args.gold_soft,
        )
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
