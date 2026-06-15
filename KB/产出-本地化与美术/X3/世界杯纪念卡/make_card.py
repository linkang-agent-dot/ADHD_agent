# -*- coding: utf-8 -*-
"""纪念卡卡面合成器：场景画(无框) + 历史卡框模板 → 256×256 RGBA 卡面(对齐 icon_card_image_*)。
用法: python make_card.py <场景画.png> <输出.png> [模板卡.png]
原理: 取模板卡(默认#76)→把"内框区"抠成透明洞,只留金框环+透明边=框overlay;
      场景画居中cover裁到内框区贴底,再叠框overlay(金框压在画上,透明角来自模板)。
内框区(INNER)按 256 画布标定;换模板或框厚不同时调 INNER / CORNER_R,跑一次看效果微调。
"""
import sys
from PIL import Image, ImageDraw, ImageChops

TEMPLATE_DEFAULT = r"C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_card_image_76.png"
# #76 卡区 bbox=(34,20,223,236);金框厚约12px → 内框(art可见区)估值,跑一次按效果微调
INNER = (46, 32, 212, 225)          # (left, top, right, bottom) in 256 canvas
CORNER_R = 8                         # 内框圆角,匹配框内圆角

def make_card(art_path, out_path, template=TEMPLATE_DEFAULT, inner=INNER, corner_r=CORNER_R):
    tpl = Image.open(template).convert("RGBA")
    W, H = tpl.size                                  # 256x256
    l, t, r, b = inner
    iw, ih = r - l, b - t

    # 1) 框overlay = 模板抠掉内框区(rounded hole) → 只剩金框环+透明边
    hole = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hole).rounded_rectangle((l, t, r - 1, b - 1), radius=corner_r, fill=255)
    frame = tpl.copy()
    frame.putalpha(ImageChops.subtract(tpl.split()[3], hole))   # alpha - hole(洞处→0)

    # 2) 场景画 cover 裁到内框宽高比(不变形),缩放填满内框
    art = Image.open(art_path).convert("RGBA")
    ar_t, ar_a = iw / ih, art.width / art.height
    if ar_a > ar_t:                                  # 画太宽→裁左右
        nw = int(art.height * ar_t)
        art = art.crop(((art.width - nw) // 2, 0, (art.width - nw) // 2 + nw, art.height))
    else:                                            # 画太高→裁上下(略偏上保头部)
        nh = int(art.width / ar_t)
        top = int((art.height - nh) * 0.30)
        art = art.crop((0, top, art.width, top + nh))
    art = art.resize((iw, ih), Image.LANCZOS)
    amask = Image.new("L", (iw, ih), 0)
    ImageDraw.Draw(amask).rounded_rectangle((0, 0, iw - 1, ih - 1), radius=corner_r, fill=255)

    # 3) 合成: 透明底 → 贴场景画 → 叠金框环
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(art, (l, t), amask)
    canvas.alpha_composite(frame)
    canvas.save(out_path)
    print("saved:", out_path, canvas.size, "inner=", inner)

if __name__ == "__main__":
    a, o = sys.argv[1], sys.argv[2]
    tpl = sys.argv[3] if len(sys.argv) > 3 else TEMPLATE_DEFAULT
    make_card(a, o, tpl)
