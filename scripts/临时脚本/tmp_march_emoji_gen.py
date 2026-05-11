import base64, json, urllib.request, ssl, threading, os, sys
from datetime import datetime

# Config
config_path = r'C:\ADHD_agent\.cursor\skills\x2-media\config.json'
with open(config_path) as f:
    config = json.load(f)
cookie = config['grfal_cookie']
grfal_url_api = "https://grfal.tap4fun.com/api/mcp/call"

# Reference images
char_img_path = r'C:\UI\效果图\T-图标\行军表情\11800008.png'
style_img_path = r'C:\Users\linkang\.claude\image-cache\7d1ae8d2-c86f-4ecf-914d-759c3f1eb812\1.png'

def img_to_b64(path):
    with open(path, 'rb') as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

print("Loading reference images...", flush=True)
char_b64 = img_to_b64(char_img_path)
style_b64 = img_to_b64(style_img_path)
print(f"  char_img size: {len(char_b64)} chars", flush=True)
print(f"  style_img size: {len(style_b64)} chars", flush=True)

prompt = (
    "2D game UI icon, vector illustration style, flat color, sticker texture, "
    "dynamic emoji pack first frame, half-body close-up, thick line outline, pure white background, "
    "green orc goblin character with large brown top hat with blue diamond gem on the front, "
    "red-orange thick eyebrows, wide open angry mouth showing teeth, red jewel necklace ornament, "
    "raising middle finger gesture rudely with one hand, "
    "yellow speech bubble chat bubble frame background behind the character, "
    "expressive angry emotion sticker style, game UI march emoji, "
    "ONE SINGLE image, do NOT generate a grid or multiple icons"
)

models = ['gpt', 'gemini', 'jimen_doubao']
results = {}
lock = threading.Lock()
downloads_dir = os.path.expanduser('~/Downloads')
timestamp = datetime.now().strftime('%H%M%S')

def download_and_resize(url, save_path):
    """Download image from URL, handling trycloudflare URL rewriting, resize to 256x256"""
    try:
        from PIL import Image
        import io as _io
        has_pil = True
    except ImportError:
        has_pil = False

    # Rewrite trycloudflare URL to internal IP if needed
    if 'trycloudflare.com' in url and '/app/' in url:
        dl_url = url.replace(url.split('/app/')[0], 'http://172.20.90.45:6018')
        print(f"  URL rewritten to internal: {dl_url[:80]}...", flush=True)
    else:
        dl_url = url

    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(dl_url, headers={"Cookie": cookie})
        with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
            data = r.read()
    except Exception as e1:
        print(f"  Internal download failed ({e1}), trying original URL...", flush=True)
        req2 = urllib.request.Request(url, headers={"Cookie": cookie})
        with urllib.request.urlopen(req2, timeout=60, context=ctx) as r:
            data = r.read()

    if has_pil:
        img = Image.open(_io.BytesIO(data))
        img = img.resize((256, 256), Image.LANCZOS)
        img.save(save_path)
    else:
        # Save as-is without resize if PIL not available
        with open(save_path, 'wb') as f:
            f.write(data)
        print("  WARNING: PIL not found, saved original size (no resize)", flush=True)

    return save_path


def call_api(model):
    print(f"[{model}] Starting...", flush=True)
    try:
        payload = json.dumps({
            "tool": "generate_image",
            "params": {
                "prompt": prompt,
                "model": model,
                "reference_images": [style_b64, char_b64]
            }
        }).encode('utf-8')

        req = urllib.request.Request(
            grfal_url_api,
            data=payload,
            headers={"Content-Type": "application/json", "Cookie": cookie},
            method="POST"
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
            result = json.loads(resp.read())

        print(f"[{model}] API response: {str(result)[:300]}", flush=True)

        if result.get('success') and result.get('result'):
            res_list = result['result']
            url = res_list[0] if isinstance(res_list, list) else res_list
            save_path = os.path.join(downloads_dir, f'march_emoji_{model}_{timestamp}.png')
            download_and_resize(url, save_path)
            with lock:
                results[model] = {'success': True, 'path': save_path, 'url': url}
            print(f"[{model}] ✅ SAVED: {save_path}", flush=True)
        else:
            err = result.get('error') or result.get('message') or str(result)
            with lock:
                results[model] = {'success': False, 'error': err, 'raw': str(result)[:500]}
            print(f"[{model}] ❌ FAILED: {err}", flush=True)

    except Exception as e:
        with lock:
            results[model] = {'success': False, 'error': str(e)}
        print(f"[{model}] ❌ ERROR: {e}", flush=True)


print(f"\nLaunching {len(models)} parallel generations: {models}", flush=True)
threads = [threading.Thread(target=call_api, args=(m,)) for m in models]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=210)

print("\n=== FINAL RESULTS ===")
for model, r in results.items():
    if r.get('success'):
        print(f"✅ [{model}] -> {r['path']}")
    else:
        print(f"❌ [{model}] -> {r.get('error', 'unknown error')}")
        if r.get('raw'):
            print(f"   raw: {r['raw'][:300]}")
