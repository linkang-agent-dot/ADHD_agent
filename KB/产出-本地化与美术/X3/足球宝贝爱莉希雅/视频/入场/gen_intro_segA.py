# -*- coding: utf-8 -*-
"""入场视频 Seg A (0-5s): 入场+跳舞+颠球预备。
首帧=intro_plate(她在右缘迈步+球在地面), seedance 5s, 尾帧不锁(生成后抽实际尾帧给SegB当首帧)。
分镜: 0-1s侧身跃入到中心 / 1-3.5s原地舞(彩球交替高甩+腕画圈+胯律动+小跳) / 3.5-5s舞收+目光落球+右脚尖滑到球底定格。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 认证走 ~/.config/grfal-api/token_store.json 的 Bearer(长效)；勿设 GRFAL_COOKIE(过期cookie优先级更高会顶掉token)
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']
os.environ.pop('GRFAL_COOKIE', None)  # Windows User级环境变量里有过期死cookie,必须pop掉否则顶掉token
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'
OUT = os.path.dirname(os.path.abspath(__file__))
PLATE = os.path.join(OUT, sys.argv[1] if len(sys.argv) > 1 else 'intro_plate_v1_1.png')

PROMPT = (
 "A lively cheerleader entrance-and-dance animation of the same character, identical face, outfit and art style as the first frame. "
 "Locked camera, plain white background; a soccer ball lies still on the ground at center-front and stays untouched on the ground for the WHOLE clip. "
 "One continuous, natural, whole-body motion line (energy flows through hips, chest, shoulders, head — never separate parts moving alone): "
 "First second: she springs into the scene from the right edge with two light bouncy cheer steps, arriving at the center, gold pom-poms swinging with her stride, flashing a bright smile toward the camera. "
 "Then about two and a half seconds of an in-place cheer dance: she swings the pom-poms high left and right in alternation with rhythm in her hips, "
 "then circles both wrists overhead so the gold tinsel flares open, with one small bouncy hop — big joyful motion but her feet stay around the center spot. "
 "Final stretch: the dance settles down smoothly — her gaze drops to the soccer ball on the ground, her smile turns playful and confident, "
 "her weight shifts onto her left leg, her right toe slides forward to rest gently against the bottom of the ball, "
 "pom-poms lowered to her sides, and she HOLDS this ready stance, almost still, for the last half second. "
 "Keep her mouth in a stable closed smile, never opening. Smooth, coherent, natural motion; no warping, no flicker, no camera movement. "
 "Preserve her exact face, outfit, colors and painterly style."
)

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=False, timeout=950)

params = {'prompt': PROMPT, 'model': 'seadance', 'ref_types': '首帧图像', 'duration': 5, 'aspect_ratio': 'auto'}
r = run(['--tool', 'generate_video', '--params', json.dumps(params, ensure_ascii=False),
         '--file', f'reference_images={PLATE}', '--submit-only', '--timeout', '900'])
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
    dst = os.path.join(OUT, f'intro_segA_v1_{i}{ext}')
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
        if ok: cv2.imencode('.png', fr)[1].tofile(os.path.join(OUT, f'_segA_{tag}.png'))  # cv2.imwrite写不了中文路径
    cap.release()
    print('frames:', n, '→ _segA_first/mid/last.png')
print('DONE')
