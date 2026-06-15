"""Download remove_bg result and resize to 256x256"""
import json, sys, os, urllib.request, shutil

GRFAL_URL = "http://172.20.90.45:6018"
# From the remove_background result
IMG_URL = "https://grfal.tap4fun.com/api/output/remove_background/2026-06-15/17814938733564_0_0.png"

OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩"
OUTPUT_NOBG = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_nobg.png")
OUTPUT_NOBG_1024 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_nobg_1024.png")
OUTPUT_256 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR.png")

# Download
token_store_path = os.path.join(os.path.expanduser("~"), ".config", "grfal-api", "token_store.json")
headers = {}
try:
    with open(token_store_path) as f:
        ts = json.load(f)
    access_token = ts.get("access_token", "")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
        print("[dl2] Using bearer token", flush=True)
except Exception as e:
    print(f"[dl2] No token: {e}", flush=True)

os.makedirs(OUTPUT_DIR, exist_ok=True)
req = urllib.request.Request(IMG_URL, headers=headers)
print(f"[dl2] Downloading {IMG_URL}...", flush=True)
with urllib.request.urlopen(req, timeout=120) as resp:
    with open(OUTPUT_NOBG, "wb") as f:
        shutil.copyfileobj(resp, f)
print(f"[dl2] Saved: {OUTPUT_NOBG} ({os.path.getsize(OUTPUT_NOBG)} bytes)", flush=True)

# Check alpha quality
from PIL import Image
import numpy as np

img = Image.open(OUTPUT_NOBG)
print(f"[dl2] Mode: {img.mode}, Size: {img.size}", flush=True)

if img.mode == "RGBA":
    arr = np.array(img)
    alpha = arr[:, :, 3]
    opaque = (alpha == 255).sum()
    transparent = (alpha == 0).sum()
    semi = ((alpha > 0) & (alpha < 255)).sum()
    total = alpha.size
    print(f"[dl2] Alpha stats: opaque={opaque/total*100:.1f}%, transparent={transparent/total*100:.1f}%, semi={semi/total*100:.1f}%", flush=True)
else:
    print(f"[dl2] WARNING: not RGBA mode", flush=True)

# Save 1024 hires version
img_1024 = img.resize((1024, 1024), Image.LANCZOS)
img_1024.save(OUTPUT_NOBG_1024, "PNG")
print(f"[dl2] 1024 saved: {OUTPUT_NOBG_1024}", flush=True)

# Save 256
img_256 = img.resize((256, 256), Image.LANCZOS)
img_256.save(OUTPUT_256, "PNG")
print(f"[dl2] 256 saved: {OUTPUT_256}", flush=True)

print(f"SAVED_NOBG={OUTPUT_NOBG}", flush=True)
print(f"SAVED_NOBG_1024={OUTPUT_NOBG_1024}", flush=True)
print(f"SAVED_256={OUTPUT_256}", flush=True)
print("[dl2] SUCCESS", flush=True)
