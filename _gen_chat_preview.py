import json, os, urllib.request, base64, ssl, sys

cfg_path = r'c:\ADHD_agent\.cursor\skills\x2-media\config.json'
with open(cfg_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

GRFAL_URL = cfg['grfal_url']
COOKIE = cfg['grfal_cookie']
DOWNLOADS = os.path.join(os.environ['USERPROFILE'], 'Downloads')

nameplate_path = os.path.join(DOWNLOADS, 'ItemFrameDeco_Easter2026_test.png')
with open(nameplate_path, 'rb') as f:
    np_b64 = base64.b64encode(f.read()).decode()

ref1 = (r'C:\Users\linkang\.cursor\projects\c-ADHD-agent\assets'
        r'\c__Users_linkang_AppData_Roaming_Cursor_User_workspaceStorage_'
        r'7d4f74cb3f9ca92bae996d3f4ee49ba0_images_2024__'
        r'-7755a483-51bd-42eb-ae6e-6257f1f08545.png')
with open(ref1, 'rb') as f:
    ref1_b64 = base64.b64encode(f.read()).decode()

prompt = (
    "Create a game chat UI mockup showing a decorative chat skin (nameplate) in a mobile strategy game. "
    "The nameplate is a DECORATIVE BORDER FRAME that WRAPS AROUND the entire chat message bubble. "
    "Reference image 2 shows exactly how it works: the colored ornamental border surrounds the whole chat content area. "
    "Reference image 1 shows the Easter-themed nameplate frame texture to use as the border. "
    "\n\nLayout on dark gray background (#3A3A3A):\n"
    "- Top left: player avatar with the user name '[LGDD]' above the bubble\n"
    "- The chat bubble is WRAPPED by the Easter nameplate border (pastel colors, flowers, bunny, eggs decorations from ref image 1)\n"
    "- Inside the decorated bubble frame:\n"
    "  - Light blue (#D6F5FF) bubble background\n"
    "  - Green (#7ED957) vertical bar on left edge of quote area\n"
    "  - Sender name '[LGDD]今晚就去耍' in sky blue (#5DCCFF)\n"
    "  - Quoted text in golden yellow (#FFE566)\n"
    "  - Body text '你今天已经激活了此类型增益' in teal (#4A9CC8)\n"
    "  - A map screenshot embedded\n"
    "  - '@[S34]PPOPODPOFP' mention in pink (#FF9ECA)\n"
    "\nAdd annotation labels pointing to each color: K:#5DCCFF, L:#FFE566, M:#7ED957, N:#FF9ECA, O:#4A9CC8\n"
    "Style: Professional UI color specification mockup. The key point is the Easter decorative border SURROUNDING the bubble, "
    "just like the red/green borders shown in reference image 2."
)

payload = {
    "tool": "generate_image",
    "params": {
        "prompt": prompt,
        "model": "gemini",
        "num_images": 1,
        "width": 1024,
        "height": 768,
        "reference_images": [
            f"data:image/png;base64,{np_b64}",
            f"data:image/png;base64,{ref1_b64}"
        ]
    }
}

data = json.dumps(payload).encode('utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = f'{GRFAL_URL}/api/mcp/call'
req = urllib.request.Request(
    url,
    data=data,
    headers={
        'Content-Type': 'application/json',
        'Cookie': COOKIE
    },
    method='POST'
)

print(f'Sending to {url} ... payload {len(data)} bytes')
sys.stdout.flush()

resp = urllib.request.urlopen(req, timeout=300, context=ctx)
result = json.loads(resp.read().decode())
print('Response:', json.dumps(result, indent=2, ensure_ascii=False)[:3000])

if result.get('success') and result.get('result'):
    urls = result['result'] if isinstance(result['result'], list) else [result['result']]
    for img_url in urls:
        if not isinstance(img_url, str) or not img_url.startswith('http'):
            continue
        # Rewrite cloudflare tunnel URL to internal IP
        from urllib.parse import urlparse
        parsed = urlparse(img_url)
        path_part = parsed.path
        internal_url = f"http://172.20.90.45:6018{path_part}"
        print(f'Original URL: {img_url}')
        print(f'Internal URL: {internal_url}')
        dl_req = urllib.request.Request(internal_url)
        img_resp = urllib.request.urlopen(dl_req, timeout=120)
        img_data = img_resp.read()
        out_path = os.path.join(DOWNLOADS, 'easter2026_chat_skin_gemini.png')
        with open(out_path, 'wb') as f:
            f.write(img_data)
        print(f'Saved: {out_path} ({len(img_data)} bytes)')
        break
