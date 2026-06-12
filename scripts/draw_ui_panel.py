# -*- coding: utf-8 -*-
"""程序绘制规则矩形 UI 件：队伍板×2 + 名牌条（横平竖直/对称/九宫格安全），颜色取自效果图"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image, ImageDraw, ImageFilter

KB = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\切图"
CL = r"C:\x3-project\client\Assets\Res\UI\Spirits\ActvWorldCup"

GOLD_DARK = (138, 100, 20)
GOLD_MAIN = (212, 164, 55)
GOLD_HI   = (247, 224, 138)

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
    """金边圆角板：外金框(带上亮下暗倒角) + 内细亮线 + 渐变底"""
    W, H = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    # 外框：暗金底
    img.paste(vgrad(size, GOLD_HI, GOLD_DARK), (0, 0), rounded(size, r))
    # 框主体（略缩进，做出外圈倒角亮边）
    s2 = (W - 8, H - 8)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(vgrad(s2, GOLD_MAIN, GOLD_DARK), (4, 4), rounded(s2, r - 4))
    img = Image.alpha_composite(img, layer)
    # 内亮金细线
    s3 = (W - frame * 2 + 8, H - frame * 2 + 8)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(Image.new("RGB", s3, GOLD_HI), (frame - 4, frame - 4), rounded(s3, max(r - frame + 4, 6)))
    img = Image.alpha_composite(img, layer)
    # 渐变底
    s4 = (W - frame * 2, H - frame * 2)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(vgrad(s4, fill_top, fill_bottom), (frame, frame), rounded(s4, max(r - frame, 5)))
    img = Image.alpha_composite(img, layer)
    # 顶部柔和高光
    hl = Image.new("L", size, 0)
    ImageDraw.Draw(hl).rounded_rectangle([frame, frame, W - frame, frame + (H - frame * 2) // 3], radius=max(r - frame, 5), fill=46)
    hl = hl.filter(ImageFilter.GaussianBlur(18))
    white = Image.new("RGBA", size, (255, 255, 255, 0))
    white.putalpha(hl)
    img = Image.alpha_composite(img, white)
    # 裁回圆角（高光别溢出）
    final = Image.new("RGBA", size, (0, 0, 0, 0))
    final.paste(img, (0, 0), rounded(size, r))
    return final

def nameplate(size=(920, 150), r=42):
    """墨绿名牌条：双金边 + 两端菱形扣，严格左右对称"""
    W, H = size
    img = panel(size, r, (32, 92, 46), (12, 56, 26), frame=14)
    d = ImageDraw.Draw(img)
    # 两端菱形扣（对称）
    for cx in (26, W - 26):
        for rad, col in ((24, GOLD_DARK), (19, GOLD_MAIN), (11, GOLD_HI)):
            d.polygon([(cx, H // 2 - rad), (cx + rad, H // 2), (cx, H // 2 + rad), (cx - rad, H // 2)], fill=col)
    return img

OUT = [
    ("WC_Guess_TeamPanel_Brazil.png",    panel((1000, 840), 56, (244, 222, 85),  (186, 188, 48))),   # 亮金黄→泛绿
    ("WC_Guess_TeamPanel_Argentina.png", panel((1000, 840), 56, (226, 240, 250), (146, 196, 233))),  # 浅白蓝→天蓝
    ("WC_Guess_NamePlate.png",           nameplate()),
]
import shutil
for name, im in OUT:
    kb = KB + "\\" + name.replace("WC_Guess_", "程序绘制_")
    im.save(kb)
    im.save(CL + "\\" + name)   # 原地覆盖客户端，meta/guid 不动
    print(name, im.size)
print("DONE 已覆盖客户端三件")
