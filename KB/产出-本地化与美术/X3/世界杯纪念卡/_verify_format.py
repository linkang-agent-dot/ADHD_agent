# -*- coding: utf-8 -*-
"""验收大图(thisver)+256(v5)的格式 vs 历史标准。"""
from PIL import Image
import numpy as np

def info(tag, p, key_by_lum=False):
    im = Image.open(p)
    mode = im.mode
    if mode == "RGBA":
        bb = im.split()[3].getbbox()
        px = im.convert("RGBA").load(); W, H = im.size
        corners = [px[2,2][3], px[W-3,2][3], px[2,H-3][3], px[W-3,H-3][3]]
        w, h = (bb[2]-bb[0], bb[3]-bb[1]) if bb else (0,0)
        print(f"{tag}: {im.size} {mode} | alpha_bbox={bb} 卡{w}x{h} 比{w/h:.3f} | 四角alpha={corners}")
    else:
        a = np.array(im.convert("RGB")); lum = a.max(axis=2)
        ys, xs = np.where(lum > 28)
        bb = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
        w, h = bb[2]-bb[0], bb[3]-bb[1]
        print(f"{tag}: {im.size} {mode}(无alpha) | 亮区bbox={bb} 卡{w}x{h} 比{w/h:.3f}")

print("=== 待验收 ===")
info("大图thisver", r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\候选_轮3\WC_r3_thisver.png")
info("256-v5", r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\_废弃\WC_MemorialCard_v5_alt1缩放透明.png")
print("=== 历史标准 ===")
info("历史大图img76", r"C:\x3-project\client\Assets\Res\UI\Spirits\MemorialCard\img_card_image_76.png")
info("历史256icon76", r"C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_card_image_76.png")
print("\n标准: 大图=384x523铺满(比0.734)四角透明 / 256=256x256卡区189x216(比0.875)四角透明")
