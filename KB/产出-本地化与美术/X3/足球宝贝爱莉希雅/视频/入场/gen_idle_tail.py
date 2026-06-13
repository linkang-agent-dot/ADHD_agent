# -*- coding: utf-8 -*-
"""idle 加长块(5s): fflf 首=尾=v5表演段实际尾帧 → 自体无缝,接在表演段后面零跳变。
内容=v8风格高冷待机: 呼吸/发丝/偶尔眨眼/重心微移,表情不变。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 认证走 ~/.config/grfal-api/token_store.json 的 Bearer(长效)；勿设 GRFAL_COOKIE(过期cookie优先级更高会顶掉token)
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']
os.environ.pop('GRFAL_COOKIE', None)  # Windows User级环境变量里有过期死cookie,必须pop掉否则顶掉token
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'
OUT = os.path.dirname(os.path.abspath(__file__))
FIRST = os.path.join(OUT, '_full5_last.png')
LAST = os.path.join(OUT, '_full5_last.png')

PROMPT = (
 "A gentle, natural standing idle of the same character, identical to the first frame — same pose, face, outfit, "
 "football tucked under her left arm, gold pom-poms in both hands, plain white background. "
 "Seamless loop: first and last frame identical, everything eases back to the start. "
 "Subtle, calm motion only: soft natural breathing so the chest gently rises and falls; "
 "hair tips and skirt and pom-pom tinsel drift faintly as in a light breeze; "
 "a very slight natural weight shift and a gentle slow head sway; an occasional slow blink. "
 "Her expression stays the same throughout: calm, cool, composed, self-assured, lips closed, never smiling wider, never opening. "
 "The entire character stays fully inside the frame at all times. "
 "Fixed camera, feet planted, no walking, no gestures. Smooth coherent whole-body motion, no warping, no flicker. "
 "Preserve her exact face, outfit, colors and painterly style."
)

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=False, timeout=950)

params = {'prompt': PROMPT, 'model': 'seadance', 'ref_types': '首帧图像,尾帧图像', 'duration': 5, 'aspect_ratio': '9:16'}
r = run(['--tool', 'generate_video', '--params', json.dumps(params, ensure_ascii=False),
         '--file', f'reference_images={FIRST}', '--file', f'reference_images={LAST}', '--submit-only', '--timeout', '900'])
out = r.stdout.decode('utf-8', 'replace')
print('[submit]', out[:300])
tid = json.loads(out).get('task_id')
print('task_id=', tid)

res = None
for i in range(90):
    time.sleep(20)
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

saved = []
for i, u in enumerate(flat(res), 1):
    url = u if u.startswith('http') else BASE + u
    ext = os.path.splitext(u.split('?')[0])[1] or '.mp4'
    dst = os.path.join(OUT, f'idle_tail_v1_{i}{ext}')
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
    with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=180) as resp:
        open(dst, 'wb').write(resp.read())
    print('SAVED', dst, os.path.getsize(dst)); saved.append(dst)

# 抽首中尾帧给质检 + 尾帧给 Seg B 当首帧
import cv2
for p in saved[:1]:
    cap = cv2.VideoCapture(p)
    n = int(cap.get(7))
    for tag, idx in (('first', 0), ('mid', n // 2), ('last', n - 1)):
        cap.set(1, idx); ok, fr = cap.read()
        if ok: cv2.imencode('.png', fr)[1].tofile(os.path.join(OUT, f'_idletail_{tag}.png'))  # cv2.imwrite写不了中文路径
    cap.release()
    print('frames:', n, '→ _segB_first/mid/last.png')
print('DONE')
