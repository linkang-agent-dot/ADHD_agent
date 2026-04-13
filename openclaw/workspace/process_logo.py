from PIL import Image, ImageDraw
import os

out_dir = r'C:\ADHD_agent\openclaw\workspace\uploads'

img1 = Image.open(r'C:\Users\linkang\.openclaw\media\inbound\dab95091-e150-45d6-84d6-f9d8fb2da2af.jpg')
img2 = Image.open(r'C:\Users\linkang\.openclaw\media\inbound\77b250f9-eb36-409f-be72-39a2b847f3cf.jpg')

w, h = img1.size  # 1024

def remove_sparkle(img):
    draw = ImageDraw.Draw(img)
    draw.rectangle([w - 85, h - 85, w - 5, h - 5], fill=(0, 0, 0))
    return img

def scale_logo(src, fname, scale_pct):
    img = remove_sparkle(src.copy())
    # Scale logo to scale_pct of original
    new_w = int(w * scale_pct)
    scaled = img.resize((new_w, h), Image.LANCZOS)
    # Paste centered into full-size black canvas
    canvas = Image.new('RGB', (w, h), (0, 0, 0))
    offset_x = (w - new_w) // 2
    canvas.paste(scaled, (offset_x, 0))
    canvas.save(os.path.join(out_dir, fname), 'PNG')
    print('Saved {} (scale={}%)'.format(fname, int(scale_pct * 100)))

# For each image, generate 4 scale versions
for img, suffix in [(img1, 'v1'), (img2, 'v2')]:
    for pct in [1.0, 0.8, 0.6, 0.4]:
        fname = 'jidian_{}pct_{}.png'.format(int(pct*100), suffix)
        scale_logo(img, fname, pct)

print('All done!')
