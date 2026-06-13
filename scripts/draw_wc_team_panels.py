# -*- coding: utf-8 -*-
"""2026世界杯48队队伍板批量程序绘制：金框圆角板+各队主场队服主色渐变，1000x840 九宫格安全"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\队伍板48"
os.makedirs(OUT_DIR, exist_ok=True)

GOLD_DARK = (138, 100, 20); GOLD_MAIN = (212, 164, 55); GOLD_HI = (247, 224, 138)

def vgrad(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g.resize((w, h))

def rounded(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
    return m

def panel(size, r, fill_top, fill_bottom, frame=22):
    W, H = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    img.paste(vgrad(size, GOLD_HI, GOLD_DARK), (0, 0), rounded(size, r))
    s2 = (W - 8, H - 8)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(vgrad(s2, GOLD_MAIN, GOLD_DARK), (4, 4), rounded(s2, r - 4))
    img = Image.alpha_composite(img, layer)
    s3 = (W - frame * 2 + 8, H - frame * 2 + 8)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(Image.new("RGB", s3, GOLD_HI), (frame - 4, frame - 4), rounded(s3, max(r - frame + 4, 6)))
    img = Image.alpha_composite(img, layer)
    s4 = (W - frame * 2, H - frame * 2)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(vgrad(s4, fill_top, fill_bottom), (frame, frame), rounded(s4, max(r - frame, 5)))
    img = Image.alpha_composite(img, layer)
    hl = Image.new("L", size, 0)
    ImageDraw.Draw(hl).rounded_rectangle([frame, frame, W - frame, frame + (H - frame * 2) // 3], radius=max(r - frame, 5), fill=46)
    hl = hl.filter(ImageFilter.GaussianBlur(18))
    white = Image.new("RGBA", size, (255, 255, 255, 0))
    white.putalpha(hl)
    img = Image.alpha_composite(img, white)
    final = Image.new("RGBA", size, (0, 0, 0, 0))
    final.paste(img, (0, 0), rounded(size, r))
    return final

# 48队：FIFA三字码 -> (中文名, 渐变上端色, 渐变下端色)  主色=主场队服
TEAMS = {
 'MEX': ('墨西哥',   (54,150,104),  (16,84,55)),
 'RSA': ('南非',     (244,214,80),  (66,130,60)),
 'KOR': ('韩国',     (228,80,90),   (160,30,50)),
 'CZE': ('捷克',     (222,80,72),   (140,32,40)),
 'CAN': ('加拿大',   (230,70,64),   (150,26,32)),
 'BIH': ('波黑',     (90,120,200),  (32,56,130)),
 'QAT': ('卡塔尔',   (158,52,80),   (96,22,46)),
 'SUI': ('瑞士',     (226,60,60),   (150,20,26)),
 'BRA': ('巴西',     (244,222,85),  (186,188,48)),
 'MAR': ('摩洛哥',   (200,60,66),   (34,98,60)),
 'HAI': ('海地',     (80,110,200),  (180,50,60)),
 'SCO': ('苏格兰',   (70,100,180),  (20,40,100)),
 'USA': ('美国',     (240,244,250), (60,90,170)),
 'PAR': ('巴拉圭',   (224,80,86),   (60,80,160)),
 'TUR': ('土耳其',   (226,52,58),   (148,18,24)),
 'AUS': ('澳大利亚', (250,210,70),  (40,110,70)),
 'GER': ('德国',     (245,245,245), (120,125,135)),
 'CUW': ('库拉索',   (90,160,220),  (28,70,140)),
 'CIV': ('科特迪瓦', (245,150,60),  (190,90,24)),
 'ECU': ('厄瓜多尔', (250,212,60),  (190,140,30)),
 'NED': ('荷兰',     (250,150,55),  (200,85,20)),
 'JPN': ('日本',     (70,100,190),  (22,38,110)),
 'SWE': ('瑞典',     (250,216,60),  (60,110,180)),
 'TUN': ('突尼斯',   (228,60,60),   (150,22,28)),
 'BEL': ('比利时',   (226,56,56),   (90,30,40)),
 'EGY': ('埃及',     (220,55,60),   (140,20,28)),
 'IRN': ('伊朗',     (245,245,245), (90,150,100)),
 'NZL': ('新西兰',   (248,248,248), (140,148,158)),
 'ESP': ('西班牙',   (228,60,52),   (160,120,30)),
 'CPV': ('佛得角',   (80,130,210),  (26,62,140)),
 'KSA': ('沙特',     (70,160,90),   (20,96,46)),
 'URU': ('乌拉圭',   (130,190,235), (60,120,180)),
 'FRA': ('法国',     (70,90,170),   (20,32,96)),
 'SEN': ('塞内加尔', (245,245,240), (60,140,80)),
 'IRQ': ('伊拉克',   (80,160,100),  (28,96,52)),
 'NOR': ('挪威',     (226,56,60),   (40,60,140)),
 'ARG': ('阿根廷',   (226,240,250), (146,196,233)),
 'ALG': ('阿尔及利亚',(245,248,245),(70,150,100)),
 'AUT': ('奥地利',   (228,60,64),   (245,245,245)),
 'JOR': ('约旦',     (224,58,60),   (140,22,30)),
 'POR': ('葡萄牙',   (170,40,52),   (90,16,30)),
 'COD': ('刚果民主共和国',(80,140,220),(200,60,50)),
 'UZB': ('乌兹别克斯坦',(245,250,250),(80,170,200)),
 'COL': ('哥伦比亚', (250,212,60),  (190,140,28)),
 'ENG': ('英格兰',   (248,248,250), (170,178,190)),
 'CRO': ('克罗地亚', (235,235,240), (200,60,66)),
 'GHA': ('加纳',     (245,245,240), (200,160,50)),
 'PAN': ('巴拿马',   (226,58,62),   (50,70,150)),
}

for code, (cn, top, bot) in TEAMS.items():
    img = panel((1000, 840), 56, top, bot)
    img.save(os.path.join(OUT_DIR, f"WC_TeamPanel_{code}.png"))
print(f"DONE {len(TEAMS)} 张 -> {OUT_DIR}")
