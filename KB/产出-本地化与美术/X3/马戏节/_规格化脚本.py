# -*- coding: utf-8 -*-
"""马戏节美术规格化脚本：按 x3-media task json 的 ref[0] 槽位参考尺寸批量归一。
透明图=trim bbox+等比 contain 居中；实底图=cover 缩放+居中裁切。产出到 规格化/ 目录，原图保留。
换节日复用：改 OUTROOT 与 user_prompt 过滤词。铁律来源=reference_x3_art_resource_spec（尺寸与复用源同槽位对齐）。"""
# ⚠️⚠️ 已知缺陷（2026-07-28 马戏节大富翁地块实证）：
#   本脚本 `min(tw/w,th/h)` + 居中 = **trim 后把内容撑满画布**，只对齐了「画布尺寸」，
#   没对齐「内容占位」。复用源若自带留白（深海地块内容只占画布 28-39%），
#   本脚本产出的新资产会填到 39-55% —— 同为 184x224「规格正确」，摆到同一套坐标上却挤成一坨。
#   → 凡内容需与复用源同密度的场景（地块/棋格/并排图标），改用内容包络版：
#     KB\产出-本地化与美术\X3\马戏节\地块与图标\_地块规格化_内容包络版.py
#   本脚本仅适用于「内容本来就该填满槽位」的资产（单件 icon/banner 等）。

import json, glob, os
from PIL import Image

OUTROOT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\马戏节\规格化"
TASKS = r"C:\Users\linkang\.claude\skills\x3-media\state\tasks"
os.makedirs(OUTROOT, exist_ok=True)


def normalize(src, tw, th, dst):
    im = Image.open(src).convert("RGBA")
    if im.getchannel("A").getextrema()[0] < 250:   # 透明资产
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        r = min(tw / im.width, th / im.height)
        nw, nh = max(1, int(im.width * r)), max(1, int(im.height * r))
        im = im.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        canvas.paste(im, ((tw - nw) // 2, (th - nh) // 2), im)
        canvas.save(dst)
    else:                                           # 实底大图
        r = max(tw / im.width, th / im.height)
        nw, nh = int(im.width * r), int(im.height * r)
        im = im.resize((nw, nh), Image.LANCZOS)
        l, t = (nw - tw) // 2, (nh - th) // 2
        im.crop((l, t, l + tw, t + th)).convert("RGB").save(dst)


n = 0
for p in glob.glob(os.path.join(TASKS, "202607*.json")):
    t = json.load(open(p, encoding="utf-8"))
    if t.get("status") != "success" or "马戏" not in t.get("user_prompt", ""):
        continue
    fn = t["params"].get("output_filename", "")
    if "gacha" in fn:   # 扭蛋机线资产不动
        continue
    outp = os.path.join(t["params"]["output_dir"], fn)
    refs = t["params"].get("reference_images") or []
    if not (fn and os.path.exists(outp) and refs and os.path.exists(refs[0])):
        continue
    rw, rh = Image.open(refs[0]).size
    if Image.open(outp).size == (rw, rh):
        continue
    normalize(outp, rw, rh, os.path.join(OUTROOT, fn))
    n += 1
print("规格化:", n)
