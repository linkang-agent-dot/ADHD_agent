# -*- coding: utf-8 -*-
"""抓时刻独有(有TM无EL)53人的34项细项 -> tm_only_attrs.json（断点续传+会话轮换限流）
这次连 r['db'] 整个存下来（含 foot_weak 等，之前只存子集是坑）"""
import json, time, os, sys, urllib.request, http.cookiejar, uuid
sys.stdout.reconfigure(encoding='utf-8')
SP = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'

def new_session():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    def get(url, hdrs=None):
        h = {'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Referer': 'https://cn.fifaaddict.com/fo4db'}
        if hdrs: h.update(hdrs)
        return op.open(urllib.request.Request(url, headers=h), timeout=25).read().decode('utf-8')
    token = get('https://cn.fifaaddict.com/api2?rq=araiwa&t=' + uuid.uuid4().hex).strip()
    return get, token

tm_all = json.load(open(os.path.join(SP, 'tm_list.json'), encoding='utf-8'))['db']
el_names = {p['name'] for p in json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']}
OUT = os.path.join(SP, 'tm_only_attrs.json')
out = {}
if os.path.exists(OUT):
    out = json.load(open(OUT, encoding='utf-8'))

jobs = [(p['name'], p['uid']) for p in tm_all if p['name'] not in el_names and p['name'] not in out]
print('jobs:', len(jobs), flush=True)

i = 0
fails = 0
while i < len(jobs):
    try:
        get, token = new_session()
    except Exception as e:
        print('handshake fail, backoff 30s', e, flush=True); time.sleep(30); continue
    for _ in range(2):
        if i >= len(jobs): break
        name, uid = jobs[i]
        try:
            r = json.loads(get('https://cn.fifaaddict.com/api2?fo4pid=pid%s&locale=cn' % uid, {'X-ARAIWA': token}))
            out[name] = {'attr': r['attr'], 'ovr': r['db']['pos1val'], 'salary': r['db']['salary'],
                         'weight': r['db']['weight'], 'height': r['db']['height'],
                         'traits': list(r.get('traits', {}).keys()), 'pos1': r['db']['pos1'], 'db': r['db']}
            print('OK', i + 1, len(jobs), name, flush=True)
            i += 1; fails = 0
        except Exception as e:
            print('ERR', name, e, flush=True)
            fails += 1
            if fails >= 3:
                print('3连败 backoff 60s', flush=True); time.sleep(60); fails = 0
            break
        time.sleep(1.5)
    tmpf = OUT + '.tmp'
    open(tmpf, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
    os.replace(tmpf, OUT)
    time.sleep(3.5)
print('ALL_DONE saved', len(out), flush=True)
