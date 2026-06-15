"""Remove background from hires image, then resize to 256x256"""
import subprocess, json, sys, os, urllib.request, shutil

SCRIPT = r"C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py"
GRFAL_URL = "http://172.20.90.45:6018"
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩"
INPUT_HIRES = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_hires.png")
OUTPUT_NOBG = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_nobg.png")
OUTPUT_256 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR.png")

params = {"format": "png"}
params_str = json.dumps(params)

cmd = [
    sys.executable, SCRIPT,
    "--tool", "remove_background",
    "--params", params_str,
    "--file", f"image_paths={INPUT_HIRES}",
    "--url", GRFAL_URL,
    "--public-url", "none",
    "--timeout", "120",
    "--no-auth-interactive",
    "--sync",
]

print(f"[removebg] Calling remove_background on {INPUT_HIRES}...", flush=True)

result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
print(f"[removebg] exit={result.returncode}", flush=True)
if result.stderr:
    print(f"[removebg] STDERR: {result.stderr[:500]}", flush=True)
if result.stdout:
    print(f"[removebg] STDOUT: {result.stdout[:2000]}", flush=True)

try:
    data = json.loads(result.stdout.strip())
except Exception as e:
    print(f"[removebg] JSON parse error: {e}", flush=True)
    sys.exit(1)

if not data.get("success"):
    print(f"[removebg] failed: {data}", flush=True)
    sys.exit(2)

result_urls = data.get("result", [])
if not result_urls:
    print(f"[removebg] No URLs: {data}", flush=True)
    sys.exit(3)

rel_url = result_urls[0] if isinstance(result_urls, list) else result_urls
img_url = GRFAL_URL.rstrip("/") + rel_url if rel_url.startswith("/") else rel_url
print(f"[removebg] Got URL: {img_url}", flush=True)

# Download no-bg image
token_store_path = os.path.join(os.path.expanduser("~"), ".config", "grfal-api", "token_store.json")
headers = {}
try:
    with open(token_store_path) as f:
        ts = json.load(f)
    access_token = ts.get("access_token", "")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
except Exception:
    pass

req = urllib.request.Request(img_url, headers=headers)
with urllib.request.urlopen(req, timeout=120) as resp:
    with open(OUTPUT_NOBG, "wb") as f:
        shutil.copyfileobj(resp, f)
print(f"[removebg] No-bg saved: {OUTPUT_NOBG} ({os.path.getsize(OUTPUT_NOBG)} bytes)", flush=True)

# Check alpha
from PIL import Image
img = Image.open(OUTPUT_NOBG)
print(f"[removebg] Mode: {img.mode}, Size: {img.size}", flush=True)

if img.mode == "RGBA":
    import numpy as np
    arr = np.array(img)
    alpha = arr[:, :, 3]
    semi_transparent = ((alpha > 0) & (alpha < 255)).sum()
    total_pixels = alpha.size
    ratio = semi_transparent / total_pixels * 100
    print(f"[removebg] Semi-transparent pixels: {semi_transparent}/{total_pixels} = {ratio:.1f}%", flush=True)

# Resize hires to 1024 (keep as hires reference)
hires_1024 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_nobg_1024.png")
img_1024 = img.resize((1024, 1024), Image.LANCZOS)
img_1024.save(hires_1024, "PNG")
print(f"[removebg] 1024px saved: {hires_1024}", flush=True)

# Resize to 256x256
img_256 = img.resize((256, 256), Image.LANCZOS)
img_256.save(OUTPUT_256, "PNG")
print(f"[removebg] 256px saved: {OUTPUT_256}", flush=True)

print(f"SAVED_NOBG={OUTPUT_NOBG}", flush=True)
print(f"SAVED_256={OUTPUT_256}", flush=True)
print("[removebg] SUCCESS", flush=True)
