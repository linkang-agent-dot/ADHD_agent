"""Worker runner for task 20260615-103650-0ffa - march_emoji MAR face paint"""
import subprocess, json, sys, os, urllib.request, shutil, time

SCRIPT = r"C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py"
REF_IMG = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48\WC_CheerEmote_ENG_raw2.png"
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩"
OUTPUT_HIRES = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_hires.png")
OUTPUT_256 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR.png")
GRFAL_URL = "http://172.20.90.45:6018"

params = {
    "model": "gpt-image-1",
    "prompt": (
        "Using the reference image as the EXACT base: keep the same Q-version chibi character "
        "(platinum blonde long hair, big eyes, open mouth cheering expression, "
        "cheerleader short top + pleated mini skirt + knee-high socks + sneakers), "
        "same pose (both hands each holding one large pom-pom raised up), "
        "same front-facing half-body composition, same head-to-body ratio, same face shape. "
        "ONLY change: "
        "(1) cheerleader top + mini skirt + both pom-poms color scheme to Morocco team colors: "
        "deep red (#C1272D) as dominant color with green (#006233) trim/accents on edges; "
        "(2) add a small clear face paint on the RIGHT cheek at cheekbone: "
        "Morocco flag design = solid red (#C1272D) background with a single green (#006233) "
        "pentagram star centered, approximately coin-sized, clean crisp edges, "
        "does NOT obscure any facial features. "
        "Art style strictly same as reference: clean thick black outlines, "
        "cel-shading 2D illustration, warm high-saturation colors, sticker aesthetic. "
        "Transparent background. "
        "ONE single character centered, do NOT generate multiple characters or a grid layout. "
        "Full character fully visible with generous clear margin around all edges including "
        "pom-poms tips - do NOT crop any part of the character or pom-poms."
    ),
    "size": "1024x1024",
    "quality": "high",
    "background": "transparent",
}

params_str = json.dumps(params)

cmd = [
    sys.executable, SCRIPT,
    "--tool", "generate_image",
    "--params", params_str,
    "--file", f"reference_images={REF_IMG}",
    "--url", GRFAL_URL,
    "--public-url", "none",
    "--timeout", "1200",
    "--no-auth-interactive",
]

print(f"[runner] Starting GRFal generate_image call...", flush=True)
t0 = time.time()

result = subprocess.run(cmd, capture_output=True, text=True, timeout=1250)

elapsed = time.time() - t0
print(f"[runner] Done in {elapsed:.1f}s, exit={result.returncode}", flush=True)

if result.stderr:
    print(f"[runner] STDERR: {result.stderr[:2000]}", flush=True)

if result.stdout:
    print(f"[runner] STDOUT: {result.stdout[:2000]}", flush=True)

# Parse result
try:
    data = json.loads(result.stdout.strip())
except Exception as e:
    print(f"[runner] JSON parse error: {e}", flush=True)
    print(f"[runner] Raw stdout: {result.stdout[:500]}", flush=True)
    sys.exit(1)

if not data.get("success"):
    print(f"[runner] GRFal returned success=false: {data}", flush=True)
    sys.exit(2)

result_urls = data.get("result", [])
if not result_urls:
    print(f"[runner] No result URLs in response: {data}", flush=True)
    sys.exit(3)

img_url = result_urls[0] if isinstance(result_urls, list) else result_urls
print(f"[runner] Got image URL: {img_url}", flush=True)

# Download hires
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[runner] Downloading to {OUTPUT_HIRES}...", flush=True)

# Try downloading with token auth
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
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(OUTPUT_HIRES, "wb") as f:
            shutil.copyfileobj(resp, f)
    print(f"[runner] Hires saved: {OUTPUT_HIRES}", flush=True)
except Exception as e:
    print(f"[runner] Download failed: {e}", flush=True)
    sys.exit(4)

# Resize to 256x256
print(f"[runner] Resizing to 256x256...", flush=True)
try:
    from PIL import Image
    img = Image.open(OUTPUT_HIRES)
    print(f"[runner] Original size: {img.size}, mode: {img.mode}", flush=True)
    img_256 = img.resize((256, 256), Image.LANCZOS)
    img_256.save(OUTPUT_256, "PNG")
    print(f"[runner] 256px saved: {OUTPUT_256}", flush=True)
except ImportError:
    print("[runner] PIL not available, skipping resize", flush=True)
    import shutil as sh
    sh.copy2(OUTPUT_HIRES, OUTPUT_256)

print(f"[runner] SUCCESS", flush=True)
print(f"SAVED_HIRES={OUTPUT_HIRES}", flush=True)
print(f"SAVED_256={OUTPUT_256}", flush=True)
