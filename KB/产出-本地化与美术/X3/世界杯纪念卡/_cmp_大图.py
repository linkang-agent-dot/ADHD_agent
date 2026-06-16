# -*- coding: utf-8 -*-
"""大图对比:当前384 vs 历史76/1/20。看构图/人物占比/正放/满幅。"""
from PIL import Image, ImageDraw
items = [
 ("当前384", r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_img_big_79.png"),
 ("历史76", r"C:\x3-project\client\Assets\Res\UI\Spirits\MemorialCard\img_card_image_76.png"),
 ("历史1", r"C:\x3-project\client\Assets\Res\UI\Spirits\MemorialCard\img_card_image_1.png"),
 ("历史20", r"C:\x3-project\client\Assets\Res\UI\Spirits\MemorialCard\img_card_image_20.png"),
]
cw, ch = 240, 326; pad = 10; lab = 20
W = len(items)*(cw+pad)+pad; H = ch+lab+pad*2
sheet = Image.new("RGB", (W, H), (235, 235, 235)); d = ImageDraw.Draw(sheet)
for i, (n, p) in enumerate(items):
    im = Image.open(p).convert("RGBA")
    bb = im.split()[3].getbbox(); w, h = bb[2]-bb[0], bb[3]-bb[1]
    im = im.resize((cw, ch))
    bg = Image.new("RGBA", (cw, ch), (255, 255, 255, 255))
    for yy in range(0, ch, 18):
        for xx in range(0, cw, 18):
            if (xx//18+yy//18) % 2: bg.paste((205, 205, 205, 255), (xx, yy, xx+18, yy+18))
    bg.alpha_composite(im)
    x = pad+i*(cw+pad); y = pad+lab
    sheet.paste(bg.convert("RGB"), (x, y))
    d.text((x+2, 2), "%s %dx%d %.2f" % (n, w, h, w/h), fill=(0, 0, 0))
sheet.save(r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\_大图对比.png")
print("saved _大图对比.png")
