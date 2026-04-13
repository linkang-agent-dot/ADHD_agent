import json, os, urllib.request, base64, ssl, sys
from urllib.parse import urlparse

cfg_path = r'c:\ADHD_agent\.cursor\skills\x2-media\config.json'
with open(cfg_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

GRFAL_URL = cfg['grfal_url']
COOKIE = cfg['grfal_cookie']
DOWNLOADS = os.path.join(os.environ['USERPROFILE'], 'Downloads')

# Use the Gemini mockup as style reference
mockup_path = os.path.join(DOWNLOADS, 'easter2026_chat_skin_gemini.png')
with open(mockup_path, 'rb') as f:
    mockup_b64 = base64.b64encode(f.read()).decode()

# Use existing nameplate references for format/shape
ref_folder = r'D:\CD_UI_NEW_2\2_UI_CUT\T_图标\M铭牌气泡\铭牌道具'
ref_files = ['ItemFrameDeco_Easter2024.png', 'ItemFrameDeco_Christmas2024.png']
ref_b64_list = []
for rf in ref_files:
    rp = os.path.join(ref_folder, rf)
    if os.path.exists(rp):
        with open(rp, 'rb') as f:
            ref_b64_list.append(f"data:image/png;base64,{base64.b64encode(f.read()).decode()}")
        print(f'Loaded reference: {rf}')

prompt = (
    "Generate a single 128x128 pixel game UI nameplate frame icon for Easter 2026 holiday theme. "
    "This is a decorative border/frame that wraps around chat messages in a mobile game. "
    "\n\nIMPORTANT STYLE - Match the Easter border shown in reference image 1 (the mockup):\n"
    "- Delicate pink floral border edges with small cherry blossoms and spring flowers\n"
    "- Colorful Easter eggs (pastel pink, blue, yellow, green) decorating the top-left and bottom corners\n"
    "- A cute white Easter bunny sitting in the bottom-right corner\n"
    "- The CENTER area must be mostly EMPTY/TRANSPARENT (this is where chat text goes)\n"
    "- Clean white/cream inner background, NOT checkered or patterned\n"
    "- Rounded rectangle shape with ornate floral border\n"
    "\nReference images 2 and 3 show the correct SIZE and FORMAT (128x128 PNG with transparency). "
    "Follow their shape and proportions but use the Easter style from reference image 1.\n"
    "\nThe border should be thin and elegant, leaving maximum space in the center. "
    "Pastel spring color palette: soft pink, mint green, sky blue, cream yellow. "
    "3D render style with glossy material, vibrant but soft colors. "
    "Transparent background (PNG). ONE single icon, no grid."
)

ref_images = [f"data:image/png;base64,{mockup_b64}"] + ref_b64_list

payload = {
    "tool": "generate_image",
    "params": {
        "prompt": prompt,
        "model": "gemini",
        "num_images": 1,
        "width": 512,
        "height": 512,
        "reference_images": ref_images
    }
}

data = json.dumps(payload).encode('utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = f'{GRFAL_URL}/api/mcp/call'
req = urllib.request.Request(
    url, data=data,
    headers={'Content-Type': 'application/json', 'Cookie': COOKIE},
    method='POST'
)

print(f'Sending to GRFal... payload {len(data)} bytes')
sys.stdout.flush()

resp = urllib.request.urlopen(req, timeout=300, context=ctx)
result = json.loads(resp.read().decode())
print('Response:', json.dumps(result, indent=2, ensure_ascii=False)[:2000])

if result.get('success') and result.get('result'):
    urls = result['result'] if isinstance(result['result'], list) else [result['result']]
    for img_url in urls:
        if not isinstance(img_url, str) or not img_url.startswith('http'):
            continue
        parsed = urlparse(img_url)
        internal_url = f"http://172.20.90.45:6018{parsed.path}"
        print(f'Downloading from: {internal_url}')
        dl_req = urllib.request.Request(internal_url)
        img_resp = urllib.request.urlopen(dl_req, timeout=120)
        img_data = img_resp.read()
        raw_path = os.path.join(DOWNLOADS, 'easter2026_nameplate_v2_raw.png')
        with open(raw_path, 'wb') as f:
            f.write(img_data)
        print(f'Saved raw: {raw_path} ({len(img_data)} bytes)')

        # Now remove background
        print('Removing background...')
        with open(raw_path, 'rb') as f:
            raw_b64 = base64.b64encode(f.read()).decode()

        bg_payload = {
            "tool": "remove_background",
            "params": {
                "image_paths": [f"data:image/png;base64,{raw_b64}"]
            }
        }
        bg_data = json.dumps(bg_payload).encode('utf-8')
        bg_req = urllib.request.Request(
            url, data=bg_data,
            headers={'Content-Type': 'application/json', 'Cookie': COOKIE},
            method='POST'
        )
        bg_resp = urllib.request.urlopen(bg_req, timeout=300, context=ctx)
        bg_result = json.loads(bg_resp.read().decode())
        print('BG remove result:', json.dumps(bg_result, indent=2, ensure_ascii=False)[:1000])

        if bg_result.get('success') and bg_result.get('result'):
            bg_urls = bg_result['result'] if isinstance(bg_result['result'], list) else [bg_result['result']]
            for bg_url in bg_urls:
                if not isinstance(bg_url, str) or not bg_url.startswith('http'):
                    continue
                bg_parsed = urlparse(bg_url)
                bg_internal = f"http://172.20.90.45:6018{bg_parsed.path}"
                bg_dl = urllib.request.urlopen(urllib.request.Request(bg_internal), timeout=120)
                bg_img_data = bg_dl.read()
                nobg_path = os.path.join(DOWNLOADS, 'easter2026_nameplate_v2_nobg.png')
                with open(nobg_path, 'wb') as f:
                    f.write(bg_img_data)
                print(f'Saved nobg: {nobg_path} ({len(bg_img_data)} bytes)')

                # Resize to 128x128
                from PIL import Image
                im = Image.open(nobg_path).convert('RGBA')
                im_resized = im.resize((128, 128), Image.LANCZOS)
                final_path = os.path.join(DOWNLOADS, 'ItemFrameDeco_Easter2026_v2.png')
                im_resized.save(final_path)
                print(f'Final 128x128: {final_path}')
                break
        break
