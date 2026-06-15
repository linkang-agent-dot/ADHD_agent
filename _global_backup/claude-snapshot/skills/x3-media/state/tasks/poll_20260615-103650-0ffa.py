"""Poll GRFal task and download result for task 20260615-103650-0ffa"""
import subprocess, json, sys, os, urllib.request, shutil, time

SCRIPT = r"C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py"
GRFAL_TASK_ID = "generate_image_e235f002_1781492861"
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩"
OUTPUT_HIRES = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR_hires.png")
OUTPUT_256 = os.path.join(OUTPUT_DIR, "WC_FaceEmote_MAR.png")
GRFAL_URL = "http://172.20.90.45:6018"

def check_task(task_id):
    cmd = [
        sys.executable, SCRIPT,
        "--check-task", task_id,
        "--url", GRFAL_URL,
        "--public-url", "none",
        "--no-auth-interactive",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"[poll] exit={result.returncode}", flush=True)
    if result.stderr:
        print(f"[poll] STDERR: {result.stderr[:500]}", flush=True)
    if result.stdout:
        print(f"[poll] STDOUT: {result.stdout[:2000]}", flush=True)
    try:
        return json.loads(result.stdout.strip())
    except Exception as e:
        print(f"[poll] JSON parse error: {e}, raw: {result.stdout[:200]}", flush=True)
        return None

# Poll every 30s, max 20 minutes
MAX_WAIT = 1200
POLL_INTERVAL = 30
t0 = time.time()

# Initial wait
print(f"[poll] Waiting 30s before first check...", flush=True)
time.sleep(30)

while True:
    elapsed = time.time() - t0
    print(f"[poll] Checking at {elapsed:.0f}s...", flush=True)

    data = check_task(GRFAL_TASK_ID)

    if data is None:
        print("[poll] Could not parse response, retrying...", flush=True)
    elif data.get("status") == "success" or (data.get("success") and data.get("result")):
        print(f"[poll] Task completed!", flush=True)

        result_data = data.get("result", [])
        if isinstance(result_data, list) and result_data:
            img_url = result_data[0]
        elif isinstance(result_data, str):
            img_url = result_data
        elif data.get("result"):
            # might be nested
            r = data["result"]
            if isinstance(r, dict):
                img_url = r.get("url") or r.get("image_url") or str(r)
            else:
                img_url = str(r)
        else:
            print(f"[poll] Unexpected result structure: {data}", flush=True)
            sys.exit(5)

        print(f"[poll] Image URL: {img_url}", flush=True)

        # Download
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

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        req = urllib.request.Request(img_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                with open(OUTPUT_HIRES, "wb") as f:
                    shutil.copyfileobj(resp, f)
            print(f"[poll] Hires saved: {OUTPUT_HIRES}", flush=True)
        except Exception as e:
            print(f"[poll] Download failed: {e}", flush=True)
            sys.exit(4)

        # Resize to 256x256
        print(f"[poll] Resizing to 256x256...", flush=True)
        try:
            from PIL import Image
            img = Image.open(OUTPUT_HIRES)
            print(f"[poll] Original size: {img.size}, mode: {img.mode}", flush=True)
            img_256 = img.resize((256, 256), Image.LANCZOS)
            img_256.save(OUTPUT_256, "PNG")
            print(f"[poll] 256px saved: {OUTPUT_256}", flush=True)
        except ImportError:
            print("[poll] PIL not available, copying hires as 256", flush=True)
            shutil.copy2(OUTPUT_HIRES, OUTPUT_256)

        print(f"[poll] SUCCESS", flush=True)
        print(f"SAVED_HIRES={OUTPUT_HIRES}", flush=True)
        print(f"SAVED_256={OUTPUT_256}", flush=True)
        sys.exit(0)

    elif data.get("status") in ("failed", "error"):
        print(f"[poll] Task failed: {data}", flush=True)
        sys.exit(2)
    elif data.get("status") in ("pending", "running", "processing"):
        print(f"[poll] Still {data.get('status')}...", flush=True)
    else:
        print(f"[poll] Unknown status: {data}", flush=True)

    elapsed = time.time() - t0
    if elapsed > MAX_WAIT:
        print(f"[poll] Timeout after {elapsed:.0f}s", flush=True)
        sys.exit(6)

    time.sleep(POLL_INTERVAL)
