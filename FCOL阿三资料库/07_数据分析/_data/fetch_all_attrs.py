# -*- coding: utf-8 -*-
"""补抓全部66名EL + 47名同名TM的34项细项 -> el_tm_attrs_full.json（断点续传+会话轮换限流）"""
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

el_all = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
tm_map = {p['name']: p['uid'] for p in json.load(open(os.path.join(SP, 'tm_list.json'), encoding='utf-8'))['db']}
OUT = os.path.join(SP, 'el_tm_attrs_full.json')
out = {}
if os.path.exists(OUT):
    out = json.load(open(OUT, encoding='utf-8'))
# 种子：已有12人数据
seed = os.path.join(SP, 'el_tm_attrs.json')
if os.path.exists(seed):
    for k, v in json.load(open(seed, encoding='utf-8')).items():
        out.setdefault(k, {}).update(v)

jobs = []  # (name, ver, uid)
for p in el_all:
    if 'EL' not in out.get(p['name'], {}):
        jobs.append((p['name'], 'EL', p['uid']))
    if p['name'] in tm_map and 'TM' not in out.get(p['name'], {}):
        jobs.append((p['name'], 'TM', tm_map[p['name']]))
print('jobs:', len(jobs))

i = 0
fails = 0
while i < len(jobs):
    try:
        get, token = new_session()
    except Exception as e:
        print('handshake fail, backoff 30s', e); time.sleep(30); continue
    for _ in range(2):  # 每会话最多2次
        if i >= len(jobs): break
        name, ver, uid = jobs[i]
        try:
            r = json.loads(get('https://cn.fifaaddict.com/api2?fo4pid=pid%s&locale=cn' % uid, {'X-ARAIWA': token}))
            out.setdefault(name, {})[ver] = {'attr': r['attr'], 'ovr': r['db']['pos1val'], 'salary': r['db']['salary'], 'weight': r['db']['weight'], 'height': r['db']['height'], 'traits': list(r.get('traits', {}).keys()), 'pos1': r['db']['pos1']}
            print('OK', i+1, len(jobs), ver, name, flush=True)
            i += 1; fails = 0
        except Exception as e:
            print('ERR', ver, name, e, flush=True)
            fails += 1
            if fails >= 3:
                print('3连败 backoff 60s'); time.sleep(60); fails = 0
            break
        time.sleep(1.5)
    # checkpoint
    tmpf = OUT + '.tmp'
    open(tmpf, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
    os.replace(tmpf, OUT)
    time.sleep(3.5)
print('ALL_DONE saved', len(out))
