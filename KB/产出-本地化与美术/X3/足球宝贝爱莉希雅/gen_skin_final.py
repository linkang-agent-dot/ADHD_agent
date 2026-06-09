# -*- coding: utf-8 -*-
"""足球宝贝皮肤 FINAL：用高质量参考图(红底带国徽)的渲染质量/姿势/身份,
套R6V2设计=白金配色(红仅点缀)+国徽换金奖杯徽章+去脸颊国旗+去球/袜世界杯商标字样。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅'
REF=os.path.join(OUT,'质量参考_红底带国徽.png')  # 高质量渲染+姿势,作质量锚

PROMPT=(
 "Use the reference image as the quality and pose anchor: keep the SAME high-quality rendering, SAME character identity "
 "(silver-white-haired beauty), SAME confident full-body standing pose, SAME soccer ball held under one arm, SAME pom-poms, "
 "SAME big number '10' on the jersey, SAME knee-high socks and sneakers, SAME clean white background, same detailed art style. "
 "APPLY THESE DESIGN CHANGES: "
 "(1) recolor the whole outfit from red to WHITE-and-GOLD (white base with gold trim, RED only as a tiny accent). "
 "(2) REPLACE the national team crest on the chest and on the skirt with a stylized GOLD championship trophy emblem "
 "(original stylized gold cup, no brand logos). "
 "(3) REMOVE the national-flag face paint on her cheek (clean face). "
 "(4) REMOVE all World Cup brand text/logos from the soccer ball and the socks — use a plain black-and-white soccer ball "
 "and plain white socks with gold stripes. NO national flags, NO country symbols, NO brand logos anywhere. "
 "Keep the high render quality and natural anatomy of the reference. Full body, official mobile game hero skin splash art, ultra detailed."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gpt','aspect_ratio':'2:3'},ensure_ascii=False),
           '--file',f'reference_images={REF}','--submit-only','--timeout','900'])
    out=r.stdout.decode('utf-8','replace'); print('[submit]',out[:200])
    try: return json.loads(out).get('task_id')
    except: return None
def poll(tid):
    for i in range(70):
        time.sleep(15)
        out=run(['--check-task',str(tid),'--timeout','120']).stdout.decode('utf-8','replace')
        try: d=json.loads(out)
        except: d={}
        st=d.get('status') or ''; print(f'[{i}] {st} {out[:110]}')
        res=d.get('result') or d.get('output')
        if res and st not in ('pending','running','processing',''): return res
        if res and st=='': return res
        if st in ('failed','error','FAILURE'): return None
    return None
def dl(paths):
    s=[]
    for i,p in enumerate(paths if isinstance(paths,list) else [paths]):
        if isinstance(p,dict): p=p.get('url') or p.get('path') or ''
        if not p: continue
        url=p if p.startswith('http') else BASE+p
        dst=os.path.join(OUT,f'足球宝贝爱莉希雅_FINAL_白金高质量_v{i+1}.png')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=90) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst,os.path.getsize(dst)); s.append(dst)
    return s
tid=submit()
if tid:
    res=poll(tid)
    if res: dl(res); print('DONE')
    else: print('NO RESULT')
else: print('SUBMIT FAIL')
