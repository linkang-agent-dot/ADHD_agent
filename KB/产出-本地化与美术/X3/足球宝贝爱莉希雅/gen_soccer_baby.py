# -*- coding: utf-8 -*-
"""足球宝贝·爱莉希雅(Hero1040) 皮肤概念稿生成：以她本人立绘 Role_F_40.png 为参考，换世界杯拉拉队造型。
GPT 模型 + reference 注入；generate_image 是 long_running → submit-only 拿 task_id → check-task 轮询。"""
import json, subprocess, os, time, sys, urllib.request, ssl

CFG = r'C:/ADHD_agent/.cursor/skills/x2-media/config.json'
os.environ['GRFAL_COOKIE'] = json.load(open(CFG, encoding='utf-8'))['grfal_cookie']
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'
REF  = r'C:\x3-project\client\Assets\Res\UI\Spirits\Role\FullLength\Role_F_40.png'
OUT  = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅'
os.makedirs(OUT, exist_ok=True)

PROMPT = (
 "Use the reference image character EXACTLY and preserve her identity: same face and facial features, "
 "same long silver-white hair, same fair skin tone, same voluptuous busty figure, "
 "same cartoon stylized 3D-rendered game art style and rendering. "
 "Redesign ONLY her outfit into a sexy World Cup soccer cheerleader (football babe) costume: "
 "a cropped sleeveless soccer jersey baring the midriff in red-white-gold team colors with a number on it, "
 "a short pleated cheer skirt, knee-high striped socks and sport sneakers, "
 "holding a soccer ball under one arm and a pair of colorful pom-poms, small national-flag face paint on one cheek. "
 "Energetic confident cheerleader pose, full body standing, clean white background, "
 "official mobile game hero skin splash art, ultra detailed, high quality."
)

def run(args):
    return subprocess.run(['python', CALL]+args, capture_output=True, text=False, timeout=950)

def submit(model):
    params = {'prompt': PROMPT, 'model': model, 'aspect_ratio': '2:3'}
    r = run(['--tool','generate_image','--params',json.dumps(params,ensure_ascii=False),
             '--file', f'reference_images={REF}', '--submit-only','--timeout','900'])
    out = r.stdout.decode('utf-8','replace')
    print('[submit]', out[:300])
    try: return json.loads(out).get('task_id') or json.loads(out).get('result',{}).get('task_id')
    except: return None

def poll(task_id):
    for i in range(60):
        time.sleep(15)
        r = run(['--check-task', str(task_id), '--timeout','120'])
        out = r.stdout.decode('utf-8','replace')
        try: d = json.loads(out)
        except: d = {}
        st = d.get('status') or d.get('state') or ''
        print(f'[poll {i}] {st} {out[:160]}')
        if d.get('result') or st in ('success','completed','SUCCESS','finished'):
            res = d.get('result') or d.get('output')
            if res: return res
        if st in ('failed','error','FAILURE'): return None
    return None

def download(paths, model):
    saved=[]
    for i,p in enumerate(paths if isinstance(paths,list) else [paths]):
        if isinstance(p,dict): p=p.get('url') or p.get('path') or ''
        if not p: continue
        url = p if p.startswith('http') else BASE+p
        dst = os.path.join(OUT, f'足球宝贝爱莉希雅_{model}_v{i+1}.png')
        req = urllib.request.Request(url, headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=90) as resp:
            open(dst,'wb').write(resp.read())
        print('[saved]', dst, os.path.getsize(dst),'bytes'); saved.append(dst)
    return saved

if __name__=='__main__':
    for model in ['gpt','gemini']:
        print('=== model', model, '===')
        tid = submit(model)
        if not tid: print('submit fail, next model'); continue
        res = poll(tid)
        if res:
            s = download(res, model)
            if s: print('DONE', s); break
        print('no result for', model)
