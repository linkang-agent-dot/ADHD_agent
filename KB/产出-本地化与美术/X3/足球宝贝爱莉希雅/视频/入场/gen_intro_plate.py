# -*- coding: utf-8 -*-
"""入场视频 step1: 开场版图 — 同一角色移到画面右缘迈步入场姿态 + 足球放地面中央。
gpt 改图(保身份), 产出 intro_plate_*.png 作为 Seg A 视频的首帧。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 认证走 ~/.config/grfal-api/token_store.json 的 Bearer(长效)；勿设 GRFAL_COOKIE(过期cookie优先级更高会顶掉token)
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']
os.environ.pop('GRFAL_COOKIE', None)  # Windows User级环境变量里有过期死cookie,必须pop掉否则顶掉token
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'
OUT = os.path.dirname(os.path.abspath(__file__))
REF = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\足球宝贝爱莉希雅_主稿_FINAL.png'

PROMPT = (
 "Recompose this exact character into a new opening shot, keeping her face, hairstyle, outfit, "
 "colors and art style EXACTLY identical to the reference image. New composition: "
 "she is at the RIGHT EDGE of the frame, captured mid-stride as she steps into the scene from off-screen right, "
 "body angled slightly toward the center, one leg forward in a light, bouncy cheerleader step, "
 "holding a golden pom-pom in each hand swinging naturally with the stride. "
 "She does NOT hold a football — instead, a single soccer ball (white with black patches and subtle gold accents, "
 "matching her white-gold outfit style) lies still on the ground near the CENTER-FRONT of the frame. "
 "Plain pure white background like the reference, soft ground shadow under her and under the ball. "
 "Full body visible, same rendering quality and painterly style as the reference."
)

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=False, timeout=950)

r = run(['--tool', 'generate_image', '--params',
         json.dumps({'prompt': PROMPT, 'model': 'gpt', 'aspect_ratio': '2:3'}, ensure_ascii=False),
         '--file', f'reference_images={REF}', '--submit-only', '--timeout', '900'])
out = r.stdout.decode('utf-8', 'replace')
print('[submit]', out[:300])
tid = json.loads(out).get('task_id')
print('task_id=', tid)

res = None
for i in range(60):
    time.sleep(15)
    o = run(['--check-task', str(tid), '--timeout', '120']).stdout.decode('utf-8', 'replace')
    try: d = json.loads(o)
    except Exception: d = {}
    if d.get('success') is False:
        print('FAIL-FAST:', str(d.get('error'))[:200]); sys.exit(1)
    st = d.get('status') or ''
    print(f'[{i}] {st}')
    res = d.get('result') or d.get('output')
    if res and st not in ('pending', 'running', 'processing'): break
    if st in ('failed', 'error', 'FAILURE'):
        print('FAIL', o[:300]); sys.exit(1)

def flat(x):
    o = []
    if isinstance(x, list):
        for i in x: o += flat(i)
    elif isinstance(x, dict): o.append(x.get('url') or x.get('path') or '')
    elif isinstance(x, str): o.append(x)
    return [u for u in o if u]

for i, u in enumerate(flat(res), 1):
    url = u if u.startswith('http') else BASE + u
    ext = os.path.splitext(u.split('?')[0])[1] or '.png'
    dst = os.path.join(OUT, f'intro_plate_v1_{i}{ext}')
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
    with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=180) as resp:
        open(dst, 'wb').write(resp.read())
    print('SAVED', dst, os.path.getsize(dst))
print('DONE')
