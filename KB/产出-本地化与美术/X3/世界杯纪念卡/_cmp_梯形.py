# -*- coding: utf-8 -*-
"""对比:梯形warp新版 / 历史76 / 历史1 / 旧斜放版FINAL。棋盘格底。"""
from PIL import Image, ImageDraw
items = [
 ("梯形warp新", r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_256_梯形.png"),
 ("历史76", r"C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_card_image_76.png"),
 ("历史1", r"C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_card_image_1.png"),
 ("旧斜放FINAL", r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_FINAL.png"),
]
cell = 300; pad = 10; lab = 20
W = len(items)*(cell+pad)+pad; H = cell+lab+pad*2
sheet = Image.new("RGB", (W, H), (235, 235, 235)); d = ImageDraw.Draw(sheet)
for i, (n, p) in enumerate(items):
    im = Image.open(p).convert("RGBA")
    bb = im.split()[3].getbbox(); w, hh = bb[2]-bb[0], bb[3]-bb[1]
    im = im.resize((cell, cell))
    bg = Image.new("RGBA", (cell, cell), (255, 255, 255, 255))
    for yy in range(0, cell, 20):
        for xx in range(0, cell, 20):
            if (xx//20+yy//20) % 2: bg.paste((205, 205, 205, 255), (xx, yy, xx+20, yy+20))
    bg.alpha_composite(im)
    x = pad+i*(cell+pad); y = pad+lab
    sheet.paste(bg.convert("RGB"), (x, y))
    d.text((x+2, 2), "%s %dx%d %.2f" % (n, w, hh, w/hh), fill=(0, 0, 0))
sheet.save(r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\_梯形对比.png")
print("saved _梯形对比.png")
