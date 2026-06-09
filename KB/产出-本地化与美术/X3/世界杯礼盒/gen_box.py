# -*- coding: utf-8 -*-
import json, subprocess, os, sys, urllib.request, ssl, re, time
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json'))['grfal_cookie']
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
OUTDIR = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'

def run(args):
    return subprocess.run(['python', CALL] + args, capture_output=True, text=True, timeout=150)

def parse_json(out):
    ms = re.findall(r'\{.*\}', out or '', re.S)
    for m in reversed(ms):
        try:
            return json.loads(m)
        except Exception:
            continue
    return None

def download(paths, outname):
    base = 'https://grfal.tap4fun.com'; saved = []
    for i, p in enumerate(paths):
        url = base + p if str(p).startswith('/') else p
        req = urllib.request.Request(url, headers={'Cookie': os.environ['GRFAL_COOKIE']})
        dst = os.path.join(OUTDIR, f'{outname}_pick{i+1}.png')
        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=60) as rr:
            open(dst, 'wb').write(rr.read())
        saved.append(dst); print('SAVED', dst)
    print('DONE', json.dumps(saved, ensure_ascii=False)); return saved

def poll(task_id, outname):
    for _ in range(60):
        d = parse_json(run(['--check-task', task_id]).stdout)
        st = (d or {}).get('status')
        print('status', st, (d or {}).get('elapsed_seconds'))
        if d and d.get('result'):
            return download(d['result'], outname)
        if st in ('success', 'completed', 'done', 'finished'):
            return download(d.get('result', []), outname)
        if st in ('failed', 'error'):
            print('FAILED', d); return []
        time.sleep(15)
    print('TIMEOUT'); return []

mode = sys.argv[1]
if mode == 'submit':
    prompt, ref, outname = sys.argv[2], sys.argv[3], sys.argv[4]
    params = {'prompt': prompt, 'model': 'gemini', 'aspect_ratio': '1:1'}
    d = parse_json(run(['--tool', 'generate_image', '--params', json.dumps(params, ensure_ascii=False),
                        '--file', f'reference_images={ref}', '--submit-only']).stdout)
    print('submit', d)
    poll(d['task_id'], outname)
elif mode == 'poll':
    poll(sys.argv[2], sys.argv[3])
