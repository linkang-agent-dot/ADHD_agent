# -*- coding: utf-8 -*-
"""微笑营业版主稿: 仅改表情(温和闭口营业笑), 其余逐像素保持。给循环v9当fflf基准帧。"""
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
 "Edit ONLY the facial expression of this character, keep EVERYTHING else pixel-identical to the reference image: "
 "exact same pose, same camera framing and character position and scale, same outfit, same pom-poms in both hands, "
 "same football tucked under her left arm, same hair, same lighting, same plain white background, same painterly art style. "
 "Change only her expression: a warm, gentle, professional cheerleader smile — lips CLOSED, corners of the mouth softly upturned, "
 "eyes warm and friendly looking at the viewer, eyebrows relaxed (not stern). Subtle and natural, not a grin, no teeth. "
)

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=False, timeout=950)

r = run(['--tool', 'generate_image', '--params',
         json.dumps({'prompt': PROMPT, 'model': 'gpt', 'aspect_ratio': '3:4'}, ensure_ascii=False),
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
    dst = os.path.join(OUT, f'smile_base_v1_{i}{ext}')
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
    with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=180) as resp:
        open(dst, 'wb').write(resp.read())
    print('SAVED', dst, os.path.getsize(dst))
print('DONE')
