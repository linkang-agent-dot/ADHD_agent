# -*- coding: utf-8 -*-
"""
把 HTML 引用的图片/视频**压缩后 base64 内嵌**，产出一个自包含单文件 HTML。

用途：验收速览页 / 交互原型 / 报告这类要发给别人看的页面——对方本地没有素材目录，
发一个 .html 就能打开，不必部署到内网 demo、也不怕素材目录丢失。

用法：
  python html_inline_assets.py 源.html                      # 产出 源_单文件.html
  python html_inline_assets.py 源.html -o 输出.html
  python html_inline_assets.py 源.html --img-q 85 --crf 26  # 调质量（数越小越清晰越大）
  python html_inline_assets.py 源.html --no-compress        # 原样内嵌不压缩

抓取的引用：`src="..."` 与 `data-video="..."`（相对路径，相对 HTML 所在目录）。
外链 http(s)、已有的 data: URI 一律跳过。

压缩策略（需要 ffmpeg 在 PATH）：
  - png/jpg/jpeg  → WebP（-q:v，默认 82）。UI 截图实测约压到 1/6，肉眼无损。
  - mp4/webm/mov  → H.264 CRF（默认 28）+ 去音轨 + faststart。录屏实测约压到 1/4。
  - gif/webp/svg  → 原样内嵌（不重压）。
转换结果按「源文件 mtime+size」缓存在 `.inline_cache/`，重跑不必再压一遍。

⚠️ 单文件体积上限经验：**别超过 ~15MB**。base64 会再膨胀 33%，且整份 HTML 要一次性
解析进内存，太大在低配机上开页会卡几秒。视频多的话优先降 CRF / 裁掉冗长片段。
"""
import argparse
import base64
import hashlib
import mimetypes
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

IMG_EXT = {".png", ".jpg", ".jpeg"}
VID_EXT = {".mp4", ".webm", ".mov"}
PASS_EXT = {".gif", ".webp", ".svg", ".ico"}
REF_RE = re.compile(r'(?:src|data-video)\s*=\s*"([^"]+)"')


def sh(cmd):
    return subprocess.run(cmd, capture_output=True).returncode == 0


def cache_key(src: Path, tag: str) -> str:
    st = src.stat()
    raw = f"{src.name}|{st.st_size}|{int(st.st_mtime)}|{tag}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def convert(src: Path, cache: Path, img_q: int, crf: int, compress: bool):
    """→ (bytes, mime)"""
    ext = src.suffix.lower()
    if not compress or ext in PASS_EXT:
        return src.read_bytes(), mimetypes.guess_type(src.name)[0] or "application/octet-stream"

    if ext in IMG_EXT:
        out = cache / f"{cache_key(src, f'webp{img_q}')}.webp"
        if not out.exists():
            if not sh(["ffmpeg", "-v", "error", "-i", str(src), "-q:v", str(img_q), str(out), "-y"]):
                return src.read_bytes(), mimetypes.guess_type(src.name)[0]
        return out.read_bytes(), "image/webp"

    if ext in VID_EXT:
        out = cache / f"{cache_key(src, f'h264crf{crf}')}.mp4"
        if not out.exists():
            ok = sh(["ffmpeg", "-v", "error", "-i", str(src), "-c:v", "libx264",
                     "-crf", str(crf), "-preset", "slow", "-an",
                     "-movflags", "+faststart", str(out), "-y"])
            if not ok:
                return src.read_bytes(), "video/mp4"
        return out.read_bytes(), "video/mp4"

    return src.read_bytes(), mimetypes.guess_type(src.name)[0] or "application/octet-stream"


def main():
    ap = argparse.ArgumentParser(description="把 HTML 的图片/视频压缩后内嵌成单文件")
    ap.add_argument("html", help="源 HTML")
    ap.add_argument("-o", "--out", default=None, help="输出，默认 <源>_单文件.html")
    ap.add_argument("--img-q", type=int, default=82, help="WebP 质量 (ffmpeg -q:v)，默认 82")
    ap.add_argument("--crf", type=int, default=28, help="H.264 CRF，默认 28（越小越清晰）")
    ap.add_argument("--no-compress", action="store_true", help="原样内嵌不压缩")
    a = ap.parse_args()

    if not shutil.which("ffmpeg") and not a.no_compress:
        sys.exit("[错误] 找不到 ffmpeg（压缩需要它）；只想内嵌可加 --no-compress")

    src_html = Path(a.html).resolve()
    if not src_html.exists():
        sys.exit(f"[错误] 文件不存在: {src_html}")
    root = src_html.parent
    out_html = Path(a.out).resolve() if a.out else root / f"{src_html.stem}_单文件.html"
    cache = root / ".inline_cache"
    cache.mkdir(exist_ok=True)

    text = src_html.read_text(encoding="utf-8")
    refs, seen = [], set()
    for m in REF_RE.finditer(text):
        u = m.group(1)
        if u.startswith(("http://", "https://", "data:", "#", "//")):
            continue
        if u not in seen:
            seen.add(u)
            refs.append(u)

    if not refs:
        sys.exit("[中止] 没找到任何本地素材引用（只认 src=\"...\" / data-video=\"...\"）")

    total_src = total_out = 0
    missing = []
    for u in refs:
        p = (root / unquote(u)).resolve()
        if not p.exists():
            missing.append(u)
            continue
        data, mime = convert(p, cache, a.img_q, a.crf, not a.no_compress)
        total_src += p.stat().st_size
        total_out += len(data)
        b64 = base64.b64encode(data).decode()
        text = text.replace(f'"{u}"', f'"data:{mime};base64,{b64}"')
        print(f"  {u}  {p.stat().st_size/1024:.0f}KB -> {len(data)/1024:.0f}KB  [{mime}]")

    if missing:
        sys.exit(f"[中止] 以下素材找不到，先修好再打包：\n  " + "\n  ".join(missing))

    tmp = out_html.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8", newline="")
    os.replace(tmp, out_html)

    mb = out_html.stat().st_size / 1024 / 1024
    print(f"\n素材 {len(refs)} 个：{total_src/1024/1024:.1f}MB -> {total_out/1024/1024:.1f}MB")
    print(f"单文件产出：{out_html}  ({mb:.1f}MB)")
    if mb > 15:
        print("⚠️ 超过 15MB，低配机开页会卡；建议调大 --crf 或裁短视频")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
