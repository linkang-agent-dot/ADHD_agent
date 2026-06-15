"""Download and post-process the completed GRFal image for task 20260615-103650-0ffa"""
import json, sys, os, urllib.request, shutil

GRFAL_URL = "http://172.20.90.45:6018"
RELATIVE_URLS = [
    "/api/output/image_generation/2026-06-15/17814936226372_0_0.png",
    "/api/output/image_generation/2026-06-15/17814935744166_0_0.png",
]
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩"
OUTPUT_HIRES = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_hires.png")
OUTPUT_256 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR.png")

# Full URL
img_url = GRFAL_URL.rstrip("/") + RELATIVE_URLS[0]
print(f"[download] Downloading: {img_url}", flush=True)

# Load bearer token
token_store_path = os.path.join(os.path.expanduser("~"), ".config", "grfal-api", "token_store.json")
headers = {}
try:
    with open(token_store_path) as f:
        ts = json.load(f)
    access_token = ts.get("access_token", "")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
        print("[download] Using bearer token auth", flush=True)
except Exception as e:
    print(f"[download] No token: {e}", flush=True)

os.makedirs(OUTPUT_DIR, exist_ok=True)

req = urllib.request.Request(img_url, headers=headers)
with urllib.request.urlopen(req, timeout=120) as resp:
    with open(OUTPUT_HIRES, "wb") as f:
        shutil.copyfileobj(resp, f)

file_size = os.path.getsize(OUTPUT_HIRES)
print(f"[download] Saved hires: {OUTPUT_HIRES} ({file_size} bytes)", flush=True)

# Resize to 256x256
print(f"[download] Resizing to 256x256...", flush=True)
from PIL import Image
img = Image.open(OUTPUT_HIRES)
print(f"[download] Mode: {img.mode}, Size: {img.size}", flush=True)

# Apply single-pass remove_bg if not already transparent
if img.mode != "RGBA":
    print("[download] Not RGBA - will need remove_bg step", flush=True)

img_256 = img.resize((256, 256), Image.LANCZOS)
img_256.save(OUTPUT_256, "PNG")
print(f"[download] 256px saved: {OUTPUT_256}", flush=True)
print(f"SAVED_HIRES={OUTPUT_HIRES}", flush=True)
print(f"SAVED_256={OUTPUT_256}", flush=True)
print("[download] SUCCESS", flush=True)
