"""
极点传媒logo - v4
文字保持原始尺寸不变，只有左侧图标（星星+圆环）按比例缩小
"""
from PIL import Image
import numpy as np
import os

OUT_DIR = r'C:\ADHD_agent\openclaw\workspace\uploads'
os.makedirs(OUT_DIR, exist_ok=True)

SOURCES = [
    (r'C:\Users\linkang\.openclaw\media\inbound\dab95091-e150-45d6-84d6-f9d8fb2da2af.jpg', 'v1'),
    (r'C:\Users\linkang\.openclaw\media\inbound\77b250f9-eb36-409f-be72-39a2b847f3cf.jpg', 'v2'),
]

ICON_RIGHT = 455
TEXT_LEFT = 460
W, H = 1024, 1024
BG = (0, 0, 0)
THRESH = 100  # 亮度>100为前景


def remove_sparkle(img):
    canvas = Image.new('RGB', img.size, BG)
    canvas.paste(img, (0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(canvas)
    d.rectangle([img.width - 85, img.height - 85, img.width - 5, img.height - 5], fill=BG)
    return canvas


def extract_foreground(big_img, x1, x2, thresh):
    crop = big_img.crop((x1, 0, x2, H))
    arr = np.array(crop, dtype=np.float32)
    brightness = arr.sum(axis=2)
    result = np.zeros((H, x2 - x1, 3), dtype=np.uint8)
    mask = brightness > thresh
    result[mask] = arr[mask].astype(np.uint8)
    return Image.fromarray(result, 'RGB')


def make_variants(src_path, suffix):
    img = remove_sparkle(Image.open(src_path))
    text_w = W - TEXT_LEFT  # 文字区域原始宽度

    # 文字前景（保持原始尺寸）
    text_fore = extract_foreground(img, TEXT_LEFT, W, THRESH)

    for pct in [1.0, 0.8, 0.6, 0.4]:
        # 图标缩小，文字不变
        icon_scaled_w = int(ICON_RIGHT * pct)
        icon_scaled_h = int(H * pct)

        icon_crop = extract_foreground(img, 0, ICON_RIGHT, THRESH)
        icon_scaled = icon_crop.resize((icon_scaled_w, icon_scaled_h), Image.LANCZOS)

        # 文字保持原始尺寸
        text_w_current = text_w  # 文字不变
        text_h_current = H

        # 组合总宽度
        total_w = icon_scaled_w + text_w_current

        # 如果超出1024，等比整体缩放
        if total_w > W:
            scale = W / total_w
            new_h = int(H * scale)
            icon_scaled = icon_crop.resize((int(ICON_RIGHT * scale), new_h), Image.LANCZOS)
            text_scaled = text_fore.resize((int(text_w * scale), new_h), Image.LANCZOS)
            total_w = icon_scaled.width + text_scaled.width
        else:
            text_scaled = text_fore

        # 纯黑画布
        canvas = Image.new('RGB', (W, H), BG)
        y_off = (H - icon_scaled.height) // 2
        x_off = (W - total_w) // 2
        canvas.paste(icon_scaled, (x_off, y_off))
        canvas.paste(text_scaled, (x_off + icon_scaled.width, y_off))

        fname = 'jidian_{:02.0f}pct_{}.png'.format(pct * 100, suffix)
        canvas.save(os.path.join(OUT_DIR, fname), 'PNG')
        print('Saved: {} (icon:{}x{}, text:{}x{}, total:{})'.format(
            fname, icon_scaled.width, icon_scaled.height,
            text_scaled.width, text_scaled.height, total_w))


for src_path, suffix in SOURCES:
    print('Processing', suffix)
    make_variants(src_path, suffix)

print('All done!')
