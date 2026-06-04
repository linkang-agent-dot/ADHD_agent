#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transparify_asset.py — 透明化资产「整机」(双底差分一条龙)

把零散的三步包成一条命令：生白底图 → 生黑底图(同 prompt) → 差分出透明 PNG。
适用：每个 ICON / DK 类 AI 生图都要透明底——技能图标 / 活动图标 / 资源 / 道具 /
英雄碎片 / 小图标 / 行军表情 / 特效贴图等。

依赖现有零件（同 skill 内自动定位，无需改）：
  · 生图：  ../grfal-api/scripts/call_grfal.py   (generate_image，返回 URL)
  · 差分：  ./transparify_dual_bg.py             (白底+黑底 → alpha)

== 模式 A：全自动（给 prompt，出透明 PNG）==
  python transparify_asset.py --prompt "a glowing blue diamond game icon, 3D cartoon" --out diamond.png
  可选：--model gpt|gemini|...   --trim(裁透明边)   --resize 256   --keep(保留中间白/黑图)

== 模式 B：只差分（你已经有白底+黑底两张）==
  python transparify_asset.py --white W.png --black B.png --out OUT.png [--trim] [--resize 256]

⚠ 双底差分硬要求：白/黑两张必须**同尺寸+同位置+同元素**，仅背景不同。
  所以两次生图 prompt 除背景外**一字不差**（脚本已自动只换背景段），并强调 keep pixel-aligned。
  GPT 仍可能漂移；漂了就重跑（产物明显错位时）。
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, urllib.request, tempfile, os
from pathlib import Path

# 强制 UTF-8 输出：Windows 默认 GBK，打印中文/子进程中文会崩（与终端无关，是真崩）
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

HERE = Path(__file__).resolve().parent
CALL_GRFAL = HERE.parent.parent / "grfal-api" / "scripts" / "call_grfal.py"
TRANSPARIFY = HERE / "transparify_dual_bg.py"

WHITE_BG = "on a pure white solid background (RGB 255,255,255)"
BLACK_BG = "on a pure black solid background (RGB 0,0,0)"
ALIGN = "keep pixel-aligned, identical pose, size and composition, centered, no cropping"
URL_RE = re.compile(r'https?://[^\s"\'<>]+?\.(?:png|jpg|jpeg|webp)', re.I)


def run_gen(prompt: str, model: str, dest: Path, timeout: int):
    """调 call_grfal 生 1 张图，解析 stdout 里的 URL，下载到 dest。"""
    params = json.dumps({"prompt": prompt, "model": model, "num_images": 1}, ensure_ascii=False)
    cmd = [sys.executable, str(CALL_GRFAL), "--tool", "generate_image", "--params", params, "--timeout", str(timeout)]
    print(f"  → 生图: {prompt[:70]}...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    urls = URL_RE.findall(out)
    if not urls:
        raise RuntimeError(f"call_grfal 没返回图片 URL。退出码={r.returncode}\n--- stdout/stderr 末尾 ---\n{out[-800:]}")
    url = urls[0]
    print(f"  → 下载: {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "transparify_asset"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())
    if dest.stat().st_size < 1024:
        raise RuntimeError(f"下载的图过小({dest.stat().st_size}B)，疑似失败：{dest}")


def run_diff(white: Path, black: Path, out: Path, trim: bool, resize: int):
    cmd = [sys.executable, str(TRANSPARIFY), "--white", str(white), "--black", str(black), "--out", str(out)]
    if trim:
        cmd.append("--trim")
    if resize:
        cmd += ["--resize", str(resize)]
    print("  → 双底差分 →", out, flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"transparify_dual_bg 失败：\n{r.stdout}\n{r.stderr}")
    sys.stdout.write(r.stdout)


def main():
    ap = argparse.ArgumentParser(description="透明化资产（双底差分一条龙）")
    ap.add_argument("--prompt", help="模式A：元素描述（不要带背景词，脚本自动加）")
    ap.add_argument("--white", help="模式B：已有白底图")
    ap.add_argument("--black", help="模式B：已有黑底图")
    ap.add_argument("--out", required=True, help="输出透明 PNG 路径")
    ap.add_argument("--model", default="gpt", help="生图模型（默认 gpt）")
    ap.add_argument("--trim", action="store_true", help="裁掉透明边距")
    ap.add_argument("--resize", type=int, default=0, help="缩放到 N×N（如 256）")
    ap.add_argument("--timeout", type=int, default=300, help="单次生图超时秒")
    ap.add_argument("--keep", action="store_true", help="保留中间白/黑图（默认删）")
    a = ap.parse_args()

    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)

    # 模式 B：已有两张，直接差分
    if a.white and a.black:
        run_diff(Path(a.white), Path(a.black), out, a.trim, a.resize)
        print("✅ 完成（差分模式）:", out); return

    # 模式 A：生白底 + 生黑底 + 差分
    if not a.prompt:
        ap.error("要么给 --prompt（全自动），要么给 --white + --black（只差分）")
    base = a.prompt.strip().rstrip(",.")
    tmpdir = Path(tempfile.mkdtemp(prefix="transparify_"))
    w_img, b_img = tmpdir / "_white.png", tmpdir / "_black.png"
    try:
        print("[1/3] 白底版"); run_gen(f"{base}, {WHITE_BG}, {ALIGN}", a.model, w_img, a.timeout)
        print("[2/3] 黑底版"); run_gen(f"{base}, {BLACK_BG}, {ALIGN}", a.model, b_img, a.timeout)
        print("[3/3] 差分");   run_diff(w_img, b_img, out, a.trim, a.resize)
        print("✅ 完成（全自动）:", out)
        if a.keep:
            import shutil
            for p in (w_img, b_img):
                shutil.copy(p, out.parent / p.name.lstrip("_"))
            print("   中间图已留在:", out.parent)
    finally:
        if not a.keep:
            for p in (w_img, b_img):
                p.unlink(missing_ok=True)
            try: tmpdir.rmdir()
            except OSError: pass


if __name__ == "__main__":
    main()
