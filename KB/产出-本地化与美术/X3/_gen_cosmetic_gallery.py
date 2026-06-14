# -*- coding: utf-8 -*-
"""收集 X3 聊天表情/头像框/铭牌(头衔) 现有图 → KB 画廊。读 tsv 配置补中文名/获取方式。"""
import os, shutil, csv, base64
from PIL import Image

CLIENT = r"C:\x3-project\client\Assets"
TSV    = r"C:\x3\gdconfig\tsv"
OUT    = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌"
SUB    = {"frame": "头像框", "emoji": "聊天表情", "title": "铭牌"}
for s in SUB.values():
    os.makedirs(os.path.join(OUT, s), exist_ok=True)

def dk2png(dk):  # DK_xxx -> xxx.png 文件名
    return dk[3:] + ".png" if dk.startswith("DK_") else dk + ".png"

def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return [r.split("\t") for r in f.read().splitlines()]

# ---------- 头像框 ----------
frame_cfg = {}  # png文件名(小写) -> (cfgID, name, obtain)
for r in read_tsv(os.path.join(TSV, "Personalize__PersonalizeAvatarFrameCfg.tsv")):
    if r and r[0].isdigit() and len(r) >= 6:
        png = dk2png(r[4]).lower()
        frame_cfg[png] = (r[0], r[9] if len(r) > 9 else "", r[5])

# 礼包售卖标记：ItemObtain/Item 里出现「购买礼包」的头像框 DK
pack_sold = set()
try:
    with open(os.path.join(TSV, "ItemObtain__#废弃.tsv"), encoding="utf-8") as f:
        for line in f:
            if "头像框" in line and ("购买" in line or "礼包" in line):
                for tok in line.split("\t"):
                    if tok.startswith("DK_Img_Player_AvatarFrame") or "AvatarFrame" in tok:
                        pack_sold.add(dk2png(tok).lower())
except Exception:
    pass

# ---------- 聊天表情 ----------
emoji_cfg = {}  # png -> (id, name)
for r in read_tsv(os.path.join(TSV, "ChatEmojyReply__ChatEmojyReply.tsv")):
    if r and r[0].isdigit() and len(r) >= 3:
        emoji_cfg[dk2png(r[2]).lower()] = (r[0], r[1])

# ---------- 铭牌/头衔 ----------
title_rows = []  # (id, name, dk_icon_png, obtain, quality)
for r in read_tsv(os.path.join(TSV, "PlayerTitle__PlayerTitle.tsv")):
    if r and r[0].isdigit() and len(r) >= 8:
        title_rows.append((r[0], r[1], dk2png(r[2]).lower(), r[5], r[7]))

# ---------- 找文件、拷贝、收集元信息 ----------
def find_png(name_lower, roots):
    for root in roots:
        for dp, _, fns in os.walk(os.path.join(CLIENT, root)):
            for fn in fns:
                if fn.lower() == name_lower and not fn.endswith(".meta"):
                    return os.path.join(dp, fn)
    return None

items = {"frame": [], "emoji": [], "title": []}

# 头像框：遍历磁盘所有 AvatarFrame png
for root in ["Res/UI/Spirits/Personalise/AvatarFrame", "Res/UI/Spirits/ActvGvG"]:
    p = os.path.join(CLIENT, root)
    if not os.path.isdir(p):
        continue
    for fn in sorted(os.listdir(p)):
        if fn.lower().startswith("img_player_avatarframe") and fn.endswith(".png"):
            src = os.path.join(p, fn)
            shutil.copy2(src, os.path.join(OUT, SUB["frame"], fn))
            cid, name, obtain = frame_cfg.get(fn.lower(), ("", "(配置未引用/历史)", ""))
            try:
                w, h = Image.open(src).size
            except Exception:
                w = h = "?"
            items["frame"].append(dict(file=fn, cid=cid, name=name, obtain=obtain,
                                        dim=f"{w}×{h}", pack=fn.lower() in pack_sold))

# 聊天表情
p = os.path.join(CLIENT, "Res/UI/Spirits/Chat")
for fn in sorted(os.listdir(p)):
    if fn.lower().startswith("img_cm_emoji_") and fn.endswith(".png"):
        src = os.path.join(p, fn)
        shutil.copy2(src, os.path.join(OUT, SUB["emoji"], fn))
        eid, name = emoji_cfg.get(fn.lower(), ("", ""))
        try:
            w, h = Image.open(src).size
        except Exception:
            w = h = "?"
        items["emoji"].append(dict(file=fn, cid=eid, name=name, dim=f"{w}×{h}"))

# 铭牌横板（按 PlayerTitle 表引用找）
for cid, name, png, obtain, quality in title_rows:
    src = find_png(png, ["Res/UI/Spirits"])
    if not src:
        continue
    dst_fn = f"{cid}_{name}_{os.path.basename(src)}"
    shutil.copy2(src, os.path.join(OUT, SUB["title"], dst_fn))
    try:
        w, h = Image.open(src).size
    except Exception:
        w = h = "?"
    qmap = {"0": "默认", "1": "蓝", "2": "紫", "3": "橙"}
    items["title"].append(dict(file=dst_fn, cid=cid, name=name, obtain=obtain,
                               dim=f"{w}×{h}", quality=qmap.get(quality, quality)))

# ---------- 生成 HTML ----------
def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def card_frame(it, sub):
    p = os.path.join(OUT, sub, it["file"])
    tag = '<span class="pack">礼包售卖</span>' if it.get("pack") else ""
    return f'''<div class="card"><div class="thumb dark"><img src="data:image/png;base64,{b64(p)}"></div>
<div class="meta"><b>{it['name']}</b> {tag}<br><span class="sub">cfg {it['cid']} · {it['dim']}</span>
<br><span class="ob">{it.get('obtain','')}</span><br><code>{it['file']}</code></div></div>'''

def card_emoji(it, sub):
    p = os.path.join(OUT, sub, it["file"])
    return f'''<div class="card"><div class="thumb"><img src="data:image/png;base64,{b64(p)}"></div>
<div class="meta"><b>{it['name']}</b><br><span class="sub">ID {it['cid']} · {it['dim']}</span><br><code>{it['file']}</code></div></div>'''

def card_title(it, sub):
    p = os.path.join(OUT, sub, it["file"])
    return f'''<div class="card wide"><div class="thumb dark"><img src="data:image/png;base64,{b64(p)}"></div>
<div class="meta"><b>{it['name']}</b> <span class="q">{it['quality']}</span><br><span class="sub">cfg {it['cid']} · {it['dim']}</span>
<br><span class="ob">{it.get('obtain','')}</span></div></div>'''

html = ['''<!doctype html><html lang="zh"><meta charset="utf-8">
<title>X3 外显图库 · 聊天表情/头像框/铭牌</title><style>
body{font-family:"Microsoft YaHei",sans-serif;background:#f4f5f7;margin:0;padding:24px;color:#222}
h1{font-size:22px}h2{margin-top:36px;border-left:5px solid #4a6cf7;padding-left:10px}
.sec-desc{color:#666;font-size:13px;margin:6px 0 14px}
.grid{display:flex;flex-wrap:wrap;gap:14px}
.card{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:190px;overflow:hidden}
.card.wide{width:400px}
.thumb{display:flex;align-items:center;justify-content:center;height:170px;background:#eef0f4}
.card.wide .thumb{height:120px}
.thumb.dark{background:repeating-conic-gradient(#cfd3da 0 25%,#e7e9ee 0 50%) 50%/20px 20px}
.thumb img{max-width:92%;max-height:92%}
.meta{padding:8px 10px;font-size:12px;line-height:1.5}
.meta b{font-size:14px}.sub{color:#888}.ob{color:#3a7;font-size:11px}
.q{background:#ff8c00;color:#fff;border-radius:4px;padding:0 6px;font-size:11px}
.pack{background:#e84393;color:#fff;border-radius:4px;padding:0 6px;font-size:11px}
code{font-size:10px;color:#aaa;word-break:break-all}
</style><h1>X3 外显图库 · 聊天表情 / 头像框 / 铭牌(头衔)</h1>
<p class="sec-desc">实地导出自 <code>C:\\x3-project\\client</code>，中文名/获取方式取自 <code>gdconfig\\tsv</code> 配置表。生成日期 2026-06-14。</p>''']

html.append(f'<h2>① 头像框 (Avatar Frame) · 256×256 · 共 {len(items["frame"])} 个</h2>')
html.append('<p class="sec-desc">PersonalizeAvatarFrameCfg 定义 + Item_80xxx 包成道具发放（永久/限时多档）。粉标=礼包售卖，绿字=获取活动。带站位Buff+虚战力。</p><div class="grid">')
html += [card_frame(it, SUB["frame"]) for it in items["frame"]]
html.append('</div>')

html.append(f'<h2>② 铭牌 / 头衔 (Player Title) · 752×192 · 共 {len(items["title"])} 个</h2>')
html.append('<p class="sec-desc">PlayerTitle 表，活动直接挂发(ActvKvk.PlayerTitleID)。橙标=品质。带站位Buff+重复获取钻石补偿。</p><div class="grid">')
html += [card_title(it, SUB["title"]) for it in items["title"]]
html.append('</div>')

html.append(f'<h2>③ 聊天表情 (Chat Emoji) · 72×72 · 共 {len(items["emoji"])} 个</h2>')
html.append('<p class="sec-desc">ChatEmojyReply 表，全员内置快捷回复表情，不售卖、无属性。</p><div class="grid">')
html += [card_emoji(it, SUB["emoji"]) for it in items["emoji"]]
html.append('</div></html>')

with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write("\n".join(html))

print("OK")
print("frame:", len(items["frame"]), "title:", len(items["title"]), "emoji:", len(items["emoji"]))
print("pack_sold frames:", sorted(pack_sold))
print("HTML:", os.path.join(OUT, "index.html"))
