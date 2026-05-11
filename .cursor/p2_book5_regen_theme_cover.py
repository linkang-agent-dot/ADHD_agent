#!/usr/bin/env python3
"""册5「拓荒大富翁」卡册主题图（封面/道具立绘 304x328 透明底）— 与活动回字格黄框沙盘、套内成卡风格对齐后重新生成。"""

import importlib.util
import io
import json
import os
import shutil
import sys
import time
import urllib.request
import urllib.error

import numpy as np
from PIL import Image, ImageFilter

sys.stdout.reconfigure(line_buffering=True)

GRFAL = r"C:/ADHD_agent/.cursor/skills/grfal-api/scripts/call_grfal.py"
URL = "http://172.20.90.45:6018"
TMP = r"C:/Users/linkang/AppData/Local/Temp"
OUT_COVERS = os.path.join(TMP, "p2_cards", "covers")
OUT_BOOK = os.path.join(TMP, "p2_cards", "集卡册资源", "05_拓荒大富翁")
TOKEN_PATH = "C:/Users/linkang/.config/grfal-api/token_store.json"

# P2 卡册封面外轮廓/描边风格参考（与其它册一致，若本机有）
REF_OUTLINE = r"C:\Users\linkang\.cursor\projects\c-ADHD-agent\assets\c__Users_linkang_AppData_Roaming_Cursor_User_workspaceStorage_7d4f74cb3f9ca92bae996d3f4ee49ba0_images_151105042-bd89cd6e-ab3d-48b6-9540-3649361ef59a.png"
# 活动内「拓荒大富翁」棋盘 UI（黄框回字格）
REF_BOARD = r"C:\Users\linkang\.cursor\projects\c-ADHD-agent\assets\c__Users_linkang_AppData_Roaming_Cursor_User_workspaceStorage_7d4f74cb3f9ca92bae996d3f4ee49ba0_images_25535563506_219298700945_25672648951_219298656794_______-0ebdae96-856e-4fc4-8524-5e3c9be0f2cb.png"

PROMPT = (
    "game prop item render on a pure solid white background, no characters no penguin no animals no people, "
    "a compact isometric P2 festival Monopoly event board: rectangular loop of bright yellow border tiles, "
    "hollow center desert mine hub with cart tracks, cactus, water tower, warm sunset, "
    "wooden treasure chests with gold and gems, stacks of gold coins, orange card decks, "
    "3D P2 mobile game art, saturated and cheerful, match the YELLOW loop board from references, "
    "NOT classic green-park Monopoly center, NOT a round ring, use the same mat language as the event board ref, "
    "dark thick outline stroke around the entire board prop, generous white margin, book theme icon for album UI, "
    "no dice with readable numbers, no English text, no app UI, "
    "consistent with the approved in-set card art mood from the other reference"
)

# 最终立绘安全区与 p2_covers_gen 册封面一致
W, H = 304, 328

os.makedirs(OUT_COVERS, exist_ok=True)

TOKEN = ""
if os.path.isfile(TOKEN_PATH):
    try:
        with open(TOKEN_PATH, encoding="utf-8") as f:
            tok = json.load(f)
        TOKEN = tok.get("access_token") or tok.get("bearer_token") or ""
    except Exception:
        pass

_grfal = None


def _load_grfal():
    global _grfal
    if _grfal is None:
        spec = importlib.util.spec_from_file_location("grfal_call", GRFAL)
        _grfal = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_grfal)
    return _grfal


def _headers_json():
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def _headers_get():
    if TOKEN:
        return {"Authorization": f"Bearer {TOKEN}"}
    return {}


def auth_get(u):
    r = urllib.request.Request(u, headers=_headers_get())
    with urllib.request.urlopen(r, timeout=120) as x:
        return x.read()


def fetch_image_bytes(u):
    try:
        return auth_get(u)
    except urllib.error.HTTPError:
        with urllib.request.urlopen(u, timeout=120) as x:
            return x.read()


def submit_async_with_auth(tool_name, params_dict, file_arg_strings):
    mod = _load_grfal()
    params = dict(params_dict)
    params = mod.inject_files(params, file_arg_strings)
    body = json.dumps({"tool": tool_name, "params": params}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{URL.rstrip('/')}/api/async/submit",
        data=body,
        method="POST",
        headers=_headers_json(),
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_file_args():
    files = []
    if os.path.isfile(REF_OUTLINE):
        files.append(f"reference_images={REF_OUTLINE}")
    if not os.path.isfile(REF_BOARD):
        raise FileNotFoundError(REF_BOARD)
    files.append(f"reference_images={REF_BOARD}")
    for name in ("01_解锁雷达.png", "02_收获丰盛.png"):
        p = os.path.join(OUT_BOOK, name)
        if os.path.isfile(p):
            files.append(f"reference_images={p}")
    if not files:
        raise SystemExit("no reference files")
    return files


def post_rembg_to_final(raw_path: str, final_path: str) -> bool:
    """抠图 + 外描边 + 落入 304x328 画布，逻辑对齐 p2_covers_gen。"""
    try:
        from rembg import remove
    except ImportError as e:
        print("  rembg not installed:", e)
        return False
    w, h = W, H
    with open(raw_path, "rb") as f:
        raw_bytes = f.read()
    out_bytes = remove(raw_bytes)
    img = Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    bb = img.getbbox()
    if bb:
        img = img.crop(bb)
    alpha = img.split()[3]
    spx = max(2, int(img.width * 0.008))
    expanded = alpha.filter(ImageFilter.MaxFilter(spx * 2 + 1))
    oa = np.array(Image.new("RGBA", img.size, (0, 0, 0, 0)))
    exa = np.array(expanded)
    aa = np.array(alpha)
    sm = (exa > 128) & (aa < 128)
    oa[sm] = (30, 25, 20, 255)
    line = Image.fromarray(oa)
    res = Image.alpha_composite(line, img)
    th = int(h * 0.60)
    r = th / res.height
    if res.width * r > w * 0.75:
        r = (w * 0.75) / res.width
    nw, nh = int(res.width * r), int(res.height * r)
    res = res.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(res, ((w - nw) // 2, int(h * 0.03)), res)
    canvas.save(final_path, "PNG")
    cb = canvas.getbbox()
    if cb:
        cw, ch = cb[2] - cb[0], cb[3] - cb[1]
    pct = 100 * cw * ch // (w * h) if w * h else 0
    print(f"  postprocess: OK {nw}x{nh} area%={pct} fileKB={os.path.getsize(final_path) // 1024}")
    return True


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--only-post":
        raw_path = os.path.join(OUT_COVERS, "cover_05_pioneer_raw.png")
        final_path = os.path.join(OUT_COVERS, "cover_05_final.png")
        if not os.path.isfile(raw_path):
            print("ERROR: missing", raw_path)
            return 1
        if not post_rembg_to_final(raw_path, final_path):
            return 1
        os.makedirs(OUT_BOOK, exist_ok=True)
        shutil.copy2(final_path, os.path.join(OUT_BOOK, "00_卡册主题_拓荒大富翁.png"))
        print("  copy -> 00_卡册主题_拓荒大富翁.png")
        return 0

    if not TOKEN:
        print("ERROR: 无 GRFal token，请配置 token_store.json")
        return 1
    try:
        file_args = build_file_args()
    except FileNotFoundError as e:
        print("ERROR:", e)
        return 1
    print("refs:", len(file_args), "OUT_COVERS", OUT_COVERS)

    params = {
        "prompt": PROMPT,
        "model": "gemini",
        "aspect_ratio": "1:1",
        "num_images": 1,
    }
    try:
        d = submit_async_with_auth("generate_image", params, file_args)
    except Exception as e:
        print("submit", e)
        return 1
    tid = d.get("task_id") or d.get("id")
    if not d.get("success") or not tid:
        print("submit", json.dumps(d, ensure_ascii=False)[:500])
        return 1
    print("  task", tid, "wait 3min")
    time.sleep(180)

    raw_path = os.path.join(OUT_COVERS, "cover_05_pioneer_raw.png")
    final_path = os.path.join(OUT_COVERS, "cover_05_final.png")
    t0 = time.time()
    while time.time() - t0 < 600:
        try:
            req = urllib.request.Request(
                f"{URL}/api/async/result/{tid}?delete=false", headers=_headers_get()
            )
            with urllib.request.urlopen(req, timeout=60) as x:
                b = x.read()
            d = json.loads(b.decode("utf-8"))
        except Exception:
            time.sleep(20)
            continue
        if d.get("success") and d.get("result"):
            u = d["result"][0]
            u = u if u.startswith("http") else f"{URL}{u}"
            with open(raw_path, "wb") as f:
                f.write(fetch_image_bytes(u))
            print("  raw", raw_path, os.path.getsize(raw_path) // 1024, "KB")
            break
        if d.get("status") in ("failed", "error"):
            print("gen fail", d)
            return 1
        time.sleep(20)
    else:
        print("timeout")
        return 1

    if not post_rembg_to_final(raw_path, final_path):
        return 1
    os.makedirs(OUT_BOOK, exist_ok=True)
    book_copy = os.path.join(OUT_BOOK, "00_卡册主题_拓荒大富翁.png")
    try:
        shutil.copy2(final_path, book_copy)
        print("  copy ->", book_copy)
    except Exception as e:
        print("  copy failed:", e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
