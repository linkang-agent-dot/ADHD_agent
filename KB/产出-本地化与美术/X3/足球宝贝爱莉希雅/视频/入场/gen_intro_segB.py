# -*- coding: utf-8 -*-
"""入场视频 Seg B (5-10s): 颠球+夹球+落定。
fflf: 首帧=_segA_last(右脚踩球) 尾帧=_loop_first(循环视频v8首帧=交棒点真像素)。
分镜: 踩球脚背回拨挑起→膝颠一下→脚背再颠→球弹至胸高左前臂兜进左腋→落定回循环首帧姿势。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 认证走 ~/.config/grfal-api/token_store.json 的 Bearer(长效)；勿设 GRFAL_COOKIE(过期cookie优先级更高会顶掉token)
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']
os.environ.pop('GRFAL_COOKIE', None)  # Windows User级环境变量里有过期死cookie,必须pop掉否则顶掉token
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'
OUT = os.path.dirname(os.path.abspath(__file__))
FIRST = os.path.join(OUT, '_segA_last.png')
LAST = os.path.join(OUT, '_loop_first.png')

PROMPT = (
 "A skillful, natural soccer juggling animation of the same cheerleader character, identical face, outfit and art style across all frames. Locked camera, plain white background, she stays around the center spot, holding a gold pom-pom in each hand the whole time. One continuous natural motion line: She starts with her right foot resting on top of the soccer ball, smiling confidently. She rolls the ball back slightly with her sole and flicks it UP with her instep — the ball rises in a clear, slow arc to knee height. She bounces it once on her right knee, then once more gently on her instep, her whole body bouncing elastically with each touch, eyes following the ball. On the last bounce the ball pops up to chest height and she catches it smoothly between her LEFT forearm and her side, tucking it snugly under her left arm, pom-pom still in her left hand. Then she settles: weight sinks calmly into both feet, posture straightens to face the camera, and she eases EXACTLY into the final reference pose — same stance, same arm positions, ball tucked under her left arm, calm confident smile. The ball moves in slow, clear, physically believable arcs and never disappears or duplicates. Keep her mouth in a stable closed smile. Smooth, coherent, natural; no warping, no flicker, no camera movement. Preserve her exact face, outfit, colors and painterly style."
)

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=False, timeout=950)

params = {'prompt': PROMPT, 'model': 'seadance', 'ref_types': '首帧图像,尾帧图像', 'duration': 5, 'aspect_ratio': 'auto'}
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
    dst = os.path.join(OUT, f'intro_segB_v1_{i}{ext}')
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
        if ok: cv2.imencode('.png', fr)[1].tofile(os.path.join(OUT, f'_segB_{tag}.png'))  # cv2.imwrite写不了中文路径
    cap.release()
    print('frames:', n, '→ _segB_first/mid/last.png')
print('DONE')
