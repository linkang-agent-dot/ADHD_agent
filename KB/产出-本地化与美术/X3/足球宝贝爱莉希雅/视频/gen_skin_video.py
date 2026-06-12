# -*- coding: utf-8 -*-
"""足球宝贝皮肤 idle 循环视频 v1: kling 首尾帧(首=尾=主稿FINAL)→无缝循环。
极简动作: 呼吸(胸微起伏)+一次wink+发梢微飘, 镜头锁死人物站定。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\视频'
os.makedirs(OUT,exist_ok=True)
REF=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\足球宝贝爱莉希雅_主稿_FINAL.png'

# v6 不再死锁嘴,改求整体自然+可循环:活气放回身体(呼吸/发/重心/头微晃),脸只给呼吸级自然表情
PROMPT=(
 "A gentle, natural looping idle of the same character, consistent with the reference image — "
 "same pose, face, outfit and art style. Seamless loop: first and last frame identical, everything eases back to the start. "
 "Keep the motion subtle and natural, the way a calm character gently breathes when standing still: "
 "soft natural breathing so the chest gently rises and falls; the long hair and the skirt and pompoms drift softly as in a faint breeze; "
 "a very slight natural weight shift and a gentle, slow head sway so she feels alive but stays in place; "
 "the face stays calm and relaxed with a soft natural expression and an occasional gentle blink, mouth relaxed and closed. "
 "Fixed camera, feet planted, no walking, no big gestures. "
 "Smooth, natural, coherent whole-body motion (not separate parts jittering), no warping, no distortion, no flicker. "
 "Preserve her exact face, outfit, colors and art style."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    params={'prompt':PROMPT,'model':'kling','ref_types':'首帧图像,尾帧图像','duration':5,'aspect_ratio':'auto'}
    cmd=['--tool','generate_video','--params',json.dumps(params,ensure_ascii=False),
         '--file',f'reference_images={REF}','--file',f'reference_images={REF}',
         '--submit-only','--timeout','900']
    out=run(cmd).stdout.decode('utf-8','replace'); print('[submit]',out[:300])
    try: return json.loads(out).get('task_id')
    except: return None
def poll(tid):
    for i in range(90):
        time.sleep(20)
        out=run(['--check-task',str(tid),'--timeout','120']).stdout.decode('utf-8','replace')
        try: d=json.loads(out)
        except: d={}
        st=d.get('status') or ''; print(f'[{i}] {st}')
        res=d.get('result') or d.get('output')
        if res and st not in ('pending','running','processing',''): return res
        if res and st=='': return res
        if st in ('failed','error','FAILURE'): print('FAIL',out[:300]); return None
    return None
def flat(x):
    o=[]
    if isinstance(x,list):
        for i in x: o+=flat(i)
    elif isinstance(x,dict): o.append(x.get('url') or x.get('path') or '')
    elif isinstance(x,str): o.append(x)
    return [u for u in o if u]
def dl(paths,prefix):
    s=[]
    for i,u in enumerate(flat(paths),1):
        url=u if u.startswith('http') else BASE+u
        ext=os.path.splitext(u.split('?')[0])[1] or '.mp4'
        dst=os.path.join(OUT,f'{prefix}_{i}{ext}')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=180) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst,os.path.getsize(dst)); s.append(dst)
    return s

tid=submit()
if not tid: print('SUBMIT FAIL'); sys.exit(1)
print('task_id=',tid)
res=poll(tid)
if not res: print('NO RESULT'); sys.exit(1)
vids=dl(res,'足球宝贝_idle循环_v6_自然_kling')
print('DONE', vids)
