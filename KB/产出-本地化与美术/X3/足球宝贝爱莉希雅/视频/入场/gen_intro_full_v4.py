# -*- coding: utf-8 -*-
"""完整版带循环直出(10s单条): 入场→舞→颠球→夹球→落定→高冷idle呼吸收尾。
客户端循环播整条(循环点=idle→再次入场)。fflf: 首帧=版图 尾帧=高冷循环首帧。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 认证走 ~/.config/grfal-api/token_store.json 的 Bearer(长效)；勿设 GRFAL_COOKIE(过期cookie优先级更高会顶掉token)
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']
os.environ.pop('GRFAL_COOKIE', None)  # Windows User级环境变量里有过期死cookie,必须pop掉否则顶掉token
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'
OUT = os.path.dirname(os.path.abspath(__file__))
FIRST = os.path.join(OUT, 'intro_plate_v1_2.png')
LAST = os.path.join(OUT, '_loop_first.png')

PROMPT = (
 "A complete cheerleader entrance performance in one continuous take, same character throughout, identical face, outfit and art style. "
 "Locked camera, plain white background, 10 seconds, one natural whole-body motion line with smooth transitions between phases — never abrupt. "
 "Phase 1 (~1.2s): she springs into the scene from the right edge with two light bouncy cheer steps, arriving at center; a soccer ball lies still on the ground at center-front. Her expression: a subtle, composed half-smile, lips closed, restrained and confident. "
 "Phase 2 (~2.3s): an in-place cheer dance — she swings the gold pom-poms high left and right with rhythm in her hips, circles both wrists overhead so the tinsel flares, one small bouncy hop. Motion is big but her expression stays understated, a faint knowing smile. "
 "Phase 3 (~0.5s): the dance settles smoothly; her gaze drops to the ball, quietly focused; she places her right foot on top of the ball. "
 "Phase 4 (~2.2s): she rolls the ball back and flicks it UP with her instep; the ball rises in a slow clear arc; she bounces it once on her right knee, once more on her instep, body bouncing elastically, eyes tracking the ball; the ball moves in slow believable arcs, never disappearing or duplicating. "
 "Phase 5 (~0.8s): the ball pops up to chest height and she catches it smoothly between her LEFT forearm and her side, tucking it under her left arm, pom-pom still in hand. "
 "Phase 6 (~1s): she settles — weight sinks calmly, posture straightens to face the camera, easing into the final reference frame pose; her faint smile fades CONTINUOUSLY into a calm, cool, composed gaze — chin level, eyes steady, self-assured and aloof; the facial change is gradual, never a switch. "
 "Phase 7 (final ~2s): she holds this exact pose in a calm standing idle — only soft natural breathing (chest gently rising), hair tips drifting faintly, an occasional slow blink, cool composed expression unchanged — ending EXACTLY on the final reference frame. "
 "Lips stay closed the whole time. Smooth, coherent, natural; no warping, no flicker, no camera movement. Preserve her exact face, outfit, colors and painterly style."
)

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=False, timeout=950)

params = {'prompt': PROMPT, 'model': 'seadance', 'ref_types': '首帧图像,尾帧图像', 'duration': 10, 'aspect_ratio': '9:16'}
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
    dst = os.path.join(OUT, f'intro_full_v4_{i}{ext}')
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
        if ok: cv2.imencode('.png', fr)[1].tofile(os.path.join(OUT, f'_full4_{tag}.png'))  # cv2.imwrite写不了中文路径
    cap.release()
    print('frames:', n, '→ _segB_first/mid/last.png')
print('DONE')
