# -*- coding: utf-8 -*-
import json, subprocess, os, sys, urllib.request, ssl, re, time
from PIL import Image
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json'))['grfal_cookie']
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
OUTDIR = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'

def run(a): return subprocess.run(['python', CALL] + a, capture_output=True, text=True, timeout=150)
def pj(o):
    for m in reversed(re.findall(r'\{.*\}', o or '', re.S)):
        try: return json.loads(m)
        except Exception: pass
    return None

tid = sys.argv[1]; dst = os.path.join(OUTDIR, sys.argv[2])
res = None
for _ in range(40):
    d = pj(run(['--check-task', tid]).stdout)
    print('status', (d or {}).get('status'), (d or {}).get('elapsed_seconds'))
    if d and d.get('result'): res = d['result']; break
    if (d or {}).get('status') in ('failed', 'error'): print('FAIL', d); sys.exit(1)
    time.sleep(10)
if not res: print('TIMEOUT'); sys.exit(1)
p = res[0] if isinstance(res, list) else res
url = 'https://grfal.tap4fun.com' + p if str(p).startswith('/') else p
req = urllib.request.Request(url, headers={'Cookie': os.environ['GRFAL_COOKIE']})
with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=60) as rr:
    open(dst, 'wb').write(rr.read())
im = Image.open(dst).convert('RGBA'); a = im.getchannel('A')
print('SAVED', dst, 'size', im.size, 'alpha', a.getextrema())
