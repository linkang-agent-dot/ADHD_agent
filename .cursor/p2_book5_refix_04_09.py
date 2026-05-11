#!/usr/bin/env python3
"""仅重出册5「拓荒大富翁」卡 04、09：在原有 layout + 活动棋盘 ref 上，再叠 01/02/03 成卡作棋盘风格参考，使黄框回字格与同套其它图一致。输出到 Temp 下集卡册目录。"""
import importlib.util
import json
import os
import io
import sys
import time
import urllib.request
import urllib.error
from PIL import Image, ImageOps

sys.stdout.reconfigure(line_buffering=True)

GRFAL = r"C:/ADHD_agent/.cursor/skills/grfal-api/scripts/call_grfal.py"
URL = "http://172.20.90.45:6018"
W, H = 240, 320
TMP = r"C:/Users/linkang/AppData/Local/Temp"
OUT = os.path.join(TMP, "p2_cards", "集卡册资源", "05_拓荒大富翁")
TOKEN_PATH = "C:/Users/linkang/.config/grfal-api/token_store.json"

ROGER = f"{TMP}/p2_roger_correct.jpg"
SCOTT = f"{TMP}/p2_scott.jpg"

REF_BOARD = r"C:\Users\linkang\.cursor\projects\c-ADHD-agent\assets\c__Users_linkang_AppData_Roaming_Cursor_User_workspaceStorage_7d4f74cb3f9ca92bae996d3f4ee49ba0_images_25535563506_219298700945_25672648951_219298656794_______-0ebdae96-856e-4fc4-8524-5e3c9be0f2cb.png"
LAYOUT_DIR = r"C:\Users\linkang\Pictures\集卡册\05_拓荒大富翁(1)"


def layout_path2(idx: int) -> str:
    return os.path.join(LAYOUT_DIR, f"151105{326 + idx:03d}.png")


def good_board_paths():
    names = ["01_解锁雷达.png", "02_收获丰盛.png", "03_神秘卡片.png"]
    ps = [os.path.join(OUT, n) for n in names]
    return [p for p in ps if os.path.exists(p)]


BASE = (
    "game collectible card illustration, vertical 3:4, no border, "
    "no English text, no Chinese text, no title plaque, no card number, no app UI chrome, no left sidebar, no top bar, no complete buttons, "
    "3D P2 game art, "
    "CRITICAL: keep the same camera framing character size pose and action as the LAYOUT reference image for this card. "
    "Do NOT change the overall card composition. "
    "The ground under the character must be the same EVENT BOARD as in the GOOD BOARD reference images: "
    "those are other approved cards in this same series, copy their flat rectangular yellow-bordered tile loop, "
    "hollow center progress hub, mine desert cactus water tower, warm sunset, same mat texture and loop shape as 01-03 NOT a different table or classic Monopoly green ring, "
    "also use the static board shape reference (last file) for icon language. "
    "no dice, no readable numbers on UI, gem pips ok, "
    "character 70-80% frame height centered full body"
)

SCENES = {
    4: (
        "04 打开奖赏",
        "P2 Roger the brown monkey crouching opening a large treasure chest on the path, brilliant light from chest, open mouth joy, "
        "chest and character placement match layout ref, feet on event yellow tiles",
    ),
    9: (
        "09 夺得宝石",
        "IDENTITY: figure A must be the same P2 Roger as reference image 1 repeated (small lean brown monkey, tan muzzle, big ears, NOT a gorilla). "
        "figure B must be the same P2 Scott as reference image 2 repeated (large dark gray gorilla, heavy build, distinct from Roger). "
        "Copy their faces fur color body proportions and costume details EXACTLY from those two refs, no generic monkey, no merging species. "
        "P2 Roger and P2 Scott both on the event board, triumphant high five, large treasure of coins and gems at their feet, "
        "victory grins, both full body in frame following layout ref positions, subtle confetti ok",
    ),
}

os.makedirs(OUT, exist_ok=True)
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
    """结果图 URL 优先带 Bearer，失败再裸 GET。"""
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


def save(path, b):
    img = Image.open(io.BytesIO(b)).convert("RGB")
    if abs(img.size[0] / img.size[1] - W / H) < 0.01:
        img = img.resize((W, H), Image.LANCZOS)
    else:
        img = ImageOps.fit(img, (W, H), Image.LANCZOS, centering=(0.5, 0.4))
    img.save(path, "PNG")


def run_one(idx: int) -> bool:
    name, scene = SCENES[idx]
    good = good_board_paths()
    if not good:
        print("missing good board refs 01-03 in", OUT)
        return False
    lay = layout_path2(idx)
    if not os.path.exists(lay):
        print("missing layout", lay)
        return False
    if not os.path.exists(REF_BOARD):
        print("missing REF_BOARD", REF_BOARD)
        return False
    ptxt = f"{BASE} {scene}, Pioneer 拓荒大富翁 {name}"
    params = {"prompt": ptxt, "model": "gemini", "aspect_ratio": "3:4", "num_images": 1}
    if idx == 4:
        file_args = [f"reference_images={ROGER}", f"reference_images={lay}"]
    else:
        # 9：先双次 Roger/Scott 加重身份，再 layout 与棋盘，避免被 good-board 图带偏物种
        file_args = [
            f"reference_images={ROGER}",
            f"reference_images={ROGER}",
            f"reference_images={SCOTT}",
            f"reference_images={SCOTT}",
            f"reference_images={lay}",
        ]
    for p in good:
        file_args.append(f"reference_images={p}")
    file_args.append(f"reference_images={REF_BOARD}")

    try:
        d = submit_async_with_auth("generate_image", params, file_args)
    except urllib.error.HTTPError as e:
        print("submit HTTP", e.code, e.read()[:500].decode("utf-8", "replace"))
        return False
    except Exception as e:
        print("submit fail", e)
        return False

    tid = d.get("task_id") or d.get("id")
    if not d.get("success") or not tid:
        print("submit fail", json.dumps(d, ensure_ascii=False)[:500])
        return False
    print("  task", tid, "wait 3min")
    time.sleep(180)
    part = name.split(" ", 1)[1] if " " in name else name
    dest = os.path.join(OUT, f"{idx:02d}_{part}.png")
    t0 = time.time()
    while time.time() - t0 < 600:
        try:
            rurl = f"{URL}/api/async/result/{tid}?delete=false"
            req = urllib.request.Request(rurl, headers=_headers_get())
            with urllib.request.urlopen(req, timeout=60) as x:
                b = x.read()
            d = json.loads(b.decode("utf-8"))
        except Exception:
            time.sleep(20)
            continue
        if d.get("success") and d.get("result"):
            u = d["result"][0]
            u = u if u.startswith("http") else f"{URL}{u}"
            save(dest, fetch_image_bytes(u))
            print("  OK", dest, os.path.getsize(dest) // 1024, "KB")
            return True
        if d.get("status") in ("failed", "error"):
            print("  gen fail", d)
            return False
        time.sleep(20)
    print("  timeout")
    return False


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--only",
        type=int,
        nargs="*",
        metavar="N",
        help="只重跑指定卡号，如 --only 9 ；默认 4 和 9",
    )
    args = ap.parse_args()
    indices = tuple(args.only) if args.only else (4, 9)

    for p in (ROGER, SCOTT):
        if not os.path.isfile(p):
            print("missing character ref:", p)
            return 1

    g = good_board_paths()
    print("good board refs:", len(g), "TOKEN", "set" if TOKEN else "EMPTY", "indices:", indices)
    if not TOKEN:
        print("提示: C:\\Users\\linkang\\.config\\grfal-api\\token_store.json 无 access_token 时，async/submit 可能 401。请用 GRFal 页登录后刷新 token 或运行 x2-media/scripts/get_grfal_cookie.py")
    ok = 0
    for idx in indices:
        if idx not in SCENES:
            print("unknown card", idx)
            continue
        print(f"\n--- {idx:02d} ---")
        if run_one(idx):
            ok += 1
    want = len([i for i in indices if i in SCENES])
    print(f"\n=== {ok}/{want} done ===")
    return 0 if ok == want and want else 1


if __name__ == "__main__":
    raise SystemExit(main())
