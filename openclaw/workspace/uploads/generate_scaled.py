"""
Generate scaled logo variants for 极点传媒 brand logo.
Scale the FULL original image (icon + text) proportionally to 100%/80%/60%/40%,
then center in a 1024x1024 black canvas.
"""
from PIL import Image
import os

OUT_DIR = r'C:\ADHD_agent\openclaw\workspace\uploads'
os.makedirs(OUT_DIR, exist_ok=True)

SOURCES = [
    (r'C:\Users\linkang\.openclaw\media\inbound\dab95091-e150-45d6-84d6-f9d8fb2da2af.jpg', 'v1'),
    (r'C:\Users\linkang\.openclaw\media\inbound\77b250f9-eb36-409f-be72-39a2b847f3cf.jpg', 'v2'),
]

BASE_SIZE = 1024


def remove_sparkle(img):
    """Fill the bottom-right sparkle with pure black."""
    draw = Image.new('RGB', (BASE_SIZE, BASE_SIZE), (0, 0, 0))
    draw.paste(img, (0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(draw)
    d.rectangle([BASE_SIZE - 85, BASE_SIZE - 85, BASE_SIZE - 5, BASE_SIZE - 5], fill=(0, 0, 0))
    return draw


def make_scaled_variants(src_path, suffix, scale_pcts=(1.0, 0.8, 0.6, 0.4)):
    img = remove_sparkle(Image.open(src_path))
    canvas = Image.new('RGB', (BASE_SIZE, BASE_SIZE), (0, 0, 0))

    for pct in scale_pcts:
        new_size = int(BASE_SIZE * pct)
        scaled = img.resize((new_size, new_size), Image.LANCZOS)
        offset = (BASE_SIZE - new_size) // 2
        canvas.paste(scaled, (offset, offset))
        fname = f'jidian_{int(pct*100)}pct_{suffix}.png'
        canvas.save(os.path.join(OUT_DIR, fname), 'PNG')
        print(f'Saved {fname} ({new_size}x{new_size} centered in {BASE_SIZE}x{BASE_SIZE})')
        # Reset canvas for next iteration
        canvas = Image.new('RGB', (BASE_SIZE, BASE_SIZE), (0, 0, 0))


for src_path, suffix in SOURCES:
    make_scaled_variants(src_path, suffix)

print('All done!')
