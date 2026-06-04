#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ui_extract_fine.py — 精细拆图「整机」(脱离 DesignDeck 也能跑)

把原来散在 DesignDeck 主进程(jimp)里的两步补成本地脚本 + 串起整条流程：
  每层： make_bbox_mask(画反向mask) → grfal image_mask_edit(填绿) → 下载 → chroma_key(去绿) → 透明层PNG

== 人工判断节点（看图定层 → 确认 → 再拆）==
  1. 看源图，写 manifest_layers.json：[{"id","desc","bbox":[x,y,w,h]}, ...]
     （bbox 可为 [x,y,w,h] 或 [[..],[..]] 多区域并集）
  2. 预览确认（不烧 API）：
       python ui_extract_fine.py --src 源图.png --manifest m.json --preview
     → 在源图上画出各层框+id，存 _preview.png；你/agent 看一眼，框不对就改 manifest
  3. 确认后开拆：
       python ui_extract_fine.py --src 源图.png --manifest m.json --out-dir 输出目录 [--model gpt]

依赖同 skill 内零件（自动定位）：make_bbox_mask.py / chroma_key.py / ../grfal-api/scripts/call_grfal.py
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, urllib.request
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_bbox_mask import make_mask          # noqa: E402
from chroma_key import chroma_key             # noqa: E402

CALL_GRFAL = HERE.parent.parent / "grfal-api" / "scripts" / "call_grfal.py"
GREEN_PROMPT = ("Fill the masked editable region with a single uniform pure solid chroma key "
                "green color (#00FF00, RGB 0 255 0). Do not add any objects, shadows, gradients, "
                "text or texture. The whole non-preserved area must be one flat bright green.")
URL_RE = re.compile(r'https?://[^\s"\'<>]+?\.(?:png|jpg|jpeg|webp)', re.I)


def norm_bboxes(bbox):
    """[x,y,w,h] → [(x,y,w,h)]；[[..],[..]] → 多个"""
    if bbox and isinstance(bbox[0], (list, tuple)):
        return [tuple(int(round(v)) for v in b) for b in bbox]
    return [tuple(int(round(v)) for v in bbox)]


def preview(src, layers, out):
    im = Image.open(src).convert("RGB"); d = ImageDraw.Draw(im)
    colors = [(255,60,60),(60,160,255),(60,200,120),(240,180,40),(190,90,220),(255,120,200)]
    for i, ly in enumerate(layers):
        c = colors[i % len(colors)]
        for (x, y, w, h) in norm_bboxes(ly["bbox"]):
            d.rectangle([x, y, x+w-1, y+h-1], outline=c, width=4)
            d.text((x+5, y+5), ly.get("id", f"layer_{i+1}"), fill=c)
    im.save(out)
    print(f"[preview] 画了 {len(layers)} 层框 → {out}  （看一眼，框不对就改 manifest，再开拆）")


def call_mask_edit(src, mask, dest, model, timeout):
    params = json.dumps({"multimodal": {"text": GREEN_PROMPT, "files": []},
                         "model_type": model, "num_images": 1}, ensure_ascii=False)
    cmd = [sys.executable, str(CALL_GRFAL), "--tool", "image_mask_edit", "--params", params,
           "--file", f"image_path={src}", "--file", f"mask_path={mask}", "--timeout", str(timeout)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    urls = URL_RE.findall(out)
    if not urls:
        raise RuntimeError(f"image_mask_edit 没返回 URL (退出码={r.returncode})\n{out[-700:]}")
    req = urllib.request.Request(urls[0], headers={"User-Agent": "ui_extract_fine"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def main():
    ap = argparse.ArgumentParser(description="精细拆图整机")
    ap.add_argument("--src", required=True)
    ap.add_argument("--manifest", required=True, help="manifest_layers.json")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--model", default="gpt")
    ap.add_argument("--feather", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--preview", action="store_true", help="只画框预览(不烧API)，给人确认")
    a = ap.parse_args()

    layers = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    outdir = Path(a.out_dir); outdir.mkdir(parents=True, exist_ok=True)

    if a.preview:
        preview(a.src, layers, str(outdir / "_preview.png")); return

    results = []
    for i, ly in enumerate(layers):
        lid = ly.get("id", f"layer_{i+1}")
        bboxes = norm_bboxes(ly["bbox"])
        print(f"\n=== [{i+1}/{len(layers)}] {lid} ===")
        try:
            mask = outdir / f"{lid}_mask.png"
            make_mask(a.src, bboxes, str(mask), a.feather)
            inpaint = outdir / f"{lid}_inpaint.png"
            call_mask_edit(a.src, str(mask), str(inpaint), a.model, a.timeout)
            final = outdir / f"{lid}.png"
            removed = chroma_key(str(inpaint), str(final))
            status = "success" if 5 <= removed <= 95 else "partial"
            results.append({"id": lid, "path": str(final), "bbox": ly["bbox"],
                            "chroma_removed_pct": round(removed, 1), "status": status})
        except Exception as e:
            print(f"  ✗ {lid} 失败：{e}")
            results.append({"id": lid, "status": "failed", "error": str(e)[:200]})

    ok = sum(1 for r in results if r.get("status") == "success")
    overall = "success" if ok == len(layers) else ("partial" if ok else "failed")
    print(f"\nMEDIA_DONE type=ui_extract_fine status={overall}  ({ok}/{len(layers)} 层成功)")
    print(json.dumps({"layers": results, "source_image": a.src, "total_layers": len(layers)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
