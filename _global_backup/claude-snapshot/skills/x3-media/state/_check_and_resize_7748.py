import os, sys
from PIL import Image

out_dir = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩'

# List files
files = os.listdir(out_dir)
sys.stdout.write("Files in output_dir:\n")
for f in sorted(files):
    fpath = os.path.join(out_dir, f)
    size = os.path.getsize(fpath)
    sys.stdout.write(f"  {f}: {size} bytes\n")

# Resize nobg_1 to 256x256 -> WC_FaceEmote_AUT.png
src1 = os.path.join(out_dir, 'WC_FaceEmote_AUT_nobg_1.png')
dst1 = os.path.join(out_dir, 'WC_FaceEmote_AUT.png')
if os.path.exists(src1) and not os.path.exists(dst1):
    img = Image.open(src1)
    sys.stdout.write(f"Resizing nobg_1 from {img.size} mode={img.mode}\n")
    img_r = img.resize((256, 256), Image.LANCZOS)
    img_r.save(dst1, 'PNG', optimize=True)
    sys.stdout.write(f"Saved: WC_FaceEmote_AUT.png ({os.path.getsize(dst1)} bytes)\n")
elif os.path.exists(dst1):
    sys.stdout.write(f"WC_FaceEmote_AUT.png already exists: {os.path.getsize(dst1)} bytes\n")
else:
    sys.stdout.write("ERROR: nobg_1 not found\n")

# Resize nobg_2 to 256x256 -> WC_FaceEmote_AUT_v2_256.png
src2 = os.path.join(out_dir, 'WC_FaceEmote_AUT_nobg_2.png')
dst2 = os.path.join(out_dir, 'WC_FaceEmote_AUT_v2_256.png')
if os.path.exists(src2) and not os.path.exists(dst2):
    img2 = Image.open(src2)
    img2_r = img2.resize((256, 256), Image.LANCZOS)
    img2_r.save(dst2, 'PNG', optimize=True)
    sys.stdout.write(f"Saved: WC_FaceEmote_AUT_v2_256.png ({os.path.getsize(dst2)} bytes)\n")
elif os.path.exists(dst2):
    sys.stdout.write(f"WC_FaceEmote_AUT_v2_256.png already exists: {os.path.getsize(dst2)} bytes\n")
else:
    sys.stdout.write("ERROR: nobg_2 not found\n")

sys.stdout.flush()
sys.stdout.write("DONE\n")
