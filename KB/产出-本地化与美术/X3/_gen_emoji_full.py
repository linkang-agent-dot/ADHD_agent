# -*- coding: utf-8 -*-
"""X3 聊天/表情全系统收集 → KB 画廊(表情全系统.html)。
切 custom_emoji1 图集(31自制表情) + 收集 HeroStickers(27英雄贴纸) + 标注另3套。"""
import os, re, shutil, base64
from PIL import Image

CLIENT = r"C:\x3-project\client\Assets"
OUT    = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌"
D_CUSTOM = os.path.join(OUT, "聊天表情_自制EmojiFace")
D_STICK  = os.path.join(OUT, "英雄羁绊贴纸")
for d in (D_CUSTOM, D_STICK):
    os.makedirs(d, exist_ok=True)

# ---- 1. 切 custom_emoji1 图集 ----
asset = os.path.join(CLIENT, "Res/UI/RichText/Emoji/custom_emoji1.asset")
img = Image.open(os.path.join(CLIENT, "Res/UI/RichText/Emoji/custom_emoji1.png")).convert("RGBA")
W, H = img.size
sprites, cur = [], None
for line in open(asset, encoding="utf-8", errors="ignore"):
    m = re.match(r'\s+Name:\s*(\S+)', line)
    if m:
        if cur and all(k in cur for k in ("x", "y", "w", "h")):
            sprites.append(cur)
        cur = {"name": m.group(1)}
        continue
    if cur is None or "{" in line:
        continue
    for key, fld in (("x", "x"), ("y", "y"), ("width", "w"), ("height", "h")):
        mm = re.match(rf'\s+{key}:\s*(\d+)', line)
        if mm and fld not in cur:
            cur[fld] = int(mm.group(1))
if cur and all(k in cur for k in ("x", "y", "w", "h")):
    sprites.append(cur)

custom = []
for s in sprites:
    x, y, w, h = s["x"], s["y"], s["w"], s["h"]
    box = (x, H - y - h, x + w, H - y)   # Unity 左下原点 → PIL 左上
    crop = img.crop(box)
    nm = s["name"].replace("EmojiFace", "") or s["name"]
    fn = f"{nm}.png"
    crop.save(os.path.join(D_CUSTOM, fn))
    custom.append((fn, f"{w}×{h}"))

# ---- 2. 收集 HeroStickers ----
stick = []
sp = os.path.join(CLIENT, "Res/UI/Spirits/HeroStickers")
for fn in sorted(os.listdir(sp), key=lambda n: (len(n), n)):
    if re.match(r'icon_bond_\d+\.png$', fn):
        src = os.path.join(sp, fn)
        shutil.copy2(src, os.path.join(D_STICK, fn))
        w, h = Image.open(src).size
        stick.append((fn, f"{w}×{h}"))

# ---- 2b. 快捷回复表情(9) ----
D_QUICK = os.path.join(OUT, "聊天表情")  # 主画廊已拷过, 直接读
quick = []
if os.path.isdir(D_QUICK):
    for fn in sorted(os.listdir(D_QUICK)):
        if fn.lower().startswith("img_cm_emoji_") and fn.endswith(".png"):
            w, h = Image.open(os.path.join(D_QUICK, fn)).size
            quick.append((fn, f"{w}×{h}"))

# ---- 2c. 大图集缩略预览(emoji_standard / EmojiOne / CuteEmotes) ----
def make_preview(src_rel, out_name, max_w=900):
    src = os.path.join(CLIENT, src_rel)
    if not os.path.exists(src):
        return None, None
    im = Image.open(src).convert("RGBA")
    ow, oh = im.size
    if im.width > max_w:
        im = im.resize((max_w, round(oh * max_w / ow)))
    dst = os.path.join(OUT, out_name)
    im.save(dst)
    return dst, f"{ow}×{oh}"

prev_std, dim_std = make_preview("Res/UI/RichText/Emoji/emoji_standard.png", "_preview_emoji_standard.png")
prev_cute, dim_cute = make_preview("Res/Unit/Role/PopupEmote/Textures/CuteEmotes.png", "_preview_cuteemotes.png")

# ---- 3. HTML ----
def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()

def cards(items, folder, cls=""):
    out = []
    for fn, dim in items:
        p = os.path.join(folder, fn)
        out.append(f'<div class="card {cls}"><div class="thumb"><img src="data:image/png;base64,{b64(p)}"></div>'
                   f'<div class="meta"><b>{fn[:-4]}</b><br><span class="sub">{dim}</span></div></div>')
    return "\n".join(out)

html = f'''<!doctype html><html lang="zh"><meta charset="utf-8">
<title>X3 聊天/表情全系统</title><style>
body{{font-family:"Microsoft YaHei",sans-serif;background:#f4f5f7;margin:0;padding:24px;color:#222}}
h1{{font-size:22px}}h2{{margin-top:34px;border-left:5px solid #4a6cf7;padding-left:10px}}
.d{{color:#666;font-size:13px;margin:6px 0 14px}}
.grid{{display:flex;flex-wrap:wrap;gap:12px}}
.card{{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:120px;overflow:hidden}}
.card.big{{width:160px}}
.thumb{{display:flex;align-items:center;justify-content:center;height:110px;background:repeating-conic-gradient(#e6e8ec 0 25%,#f2f3f6 0 50%) 50%/16px 16px}}
.card.big .thumb{{height:150px}}
.thumb img{{max-width:90%;max-height:90%}}
.meta{{padding:6px 8px;font-size:11px;line-height:1.4}}.meta b{{font-size:12px}}.sub{{color:#999}}
.note{{background:#fff;border-radius:8px;padding:12px 16px;margin:8px 0;font-size:13px;color:#555}}
.tag{{background:#4a6cf7;color:#fff;border-radius:4px;padding:1px 7px;font-size:11px}}
.atlas{{max-width:920px;width:100%;border:1px solid #ddd;border-radius:8px;background:repeating-conic-gradient(#e6e8ec 0 25%,#f2f3f6 0 50%) 50%/16px 16px}}
</style>
<h1>X3 聊天 / 表情 全系统盘点</h1>
<p class="d">实地导出自 <code>C:\\x3-project\\client</code>，2026-06-14。X3 表情共 <b>5 套独立系统</b>，下面按"可做/可卖价值"排序。</p>

<h2>① 英雄羁绊贴纸 HeroStickers · 512×512 · 共 {len(stick)} 个 <span class="tag">收集+点亮Buff</span></h2>
<p class="d">主题立绘式贴纸(双角色+节日道具)，最重的一套。配置 <code>HeroStickers.proto</code>(CHeroStickersCfg)：DKSticker图 + 点亮条件 + 点亮积分/Buff/道具奖励 + 关联英雄组。资源 <code>Res/UI/Spirits/HeroStickers/icon_bond_*.png</code>，另有 6 张 bg + 铜银金钻等级 icon。独立 UI(UIHeroStickers/StickerBoard prefab)。<b>这是英雄羁绊收集系统的可视主体，扩量价值最高。</b></p>
<div class="grid">{cards(stick, D_STICK, "big")}</div>

<h2>② 自制内联表情 custom_emoji1 · 图集1024×512 · 共 {len(custom)} 个 <span class="tag">自制·打字插入</span></h2>
<p class="d">游戏自制的 EmojiFace 系列(经典黄脸)，打字时插在聊天文本里。图集 <code>Res/UI/RichText/Emoji/custom_emoji1.png</code> + <code>.asset</code>(每格rect)，单格约 117×121。<b>这套最适合"做一波新表情"——直接往图集追加格子+.asset登记rect。</b></p>
<div class="grid">{cards(custom, D_CUSTOM)}</div>

<h2>③ 快捷回复表情 ChatEmojyReply · 72×72 · {len(quick)} 个 <span class="tag">内置·不售卖</span></h2>
<p class="d">聊天里点一下发一个大表情气泡(点赞/踩/好的/微笑…)，全员内置不卖、无属性。配置 <code>ChatEmojyReply__ChatEmojyReply.tsv</code>。</p>
<div class="grid">{cards(quick, D_QUICK)}</div>

<h2>④ 标准 EmojiOne 全集 emoji_standard · 图集1024×2048 · 1638 个 <span class="tag">开源·非自制</span></h2>
<p class="d">EmojiOne 开源 unicode emoji 全集(<code>Res/UI/RichText/Emoji/emoji_standard.png</code> / TextMesh Pro <code>EmojiOne.png</code>)，覆盖全部标准 emoji。<b>第三方开源库、不是我们做的，不要动它</b>，自制表情走 ②。下图为图集整体缩略：</p>
{f'<img class="atlas" src="data:image/png;base64,{b64(prev_std)}">' if prev_std else '<p class="d">(预览生成失败)</p>'}

<h2>⑤ 角色头顶 Emote CuteEmotes · 图集{dim_cute or "6656×2560"} <span class="tag">世界内冒泡</span></h2>
<p class="d">角色在世界/城里头顶冒出的 emote 气泡(<code>Res/Unit/Role/PopupEmote/Textures/CuteEmotes.png</code> + Popup/Fadeup 动画 + Emote.prefab)。无 json 切图信息、由 prefab 驱动，和聊天文本表情是两条线。下图为图集整体缩略：</p>
{f'<img class="atlas" src="data:image/png;base64,{b64(prev_cute)}">' if prev_cute else '<p class="d">(预览生成失败)</p>'}
</html>'''

with open(os.path.join(OUT, "表情全系统.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("custom sliced:", len(custom), "| stickers:", len(stick))
print("HTML:", os.path.join(OUT, "表情全系统.html"))
