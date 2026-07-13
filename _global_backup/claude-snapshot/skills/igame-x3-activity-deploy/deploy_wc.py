# -*- coding: utf-8 -*-
"""世界杯竞猜 批量部署器(可复用·带部署前 double-check + 中文ascii编码)。
用法: python deploy_wc.py <场次> [env] [--go]
  <场次>: 赛程序号(1起),逗号/区间, 如 "9-16" 或 "9,10,11"
  env: prod(默认)/beta/dev ;  --go: 真发(默认 dry,只查重+预览不发)
机制: 读 wc_dashboard_data.json(16场schedule·ESPN时间) → 场序N→cfg=102920+(N-1)*4 →
      4档(免费/4.99/9.99/19.99)customParam=队基号+档 → 开启立即/结束=该场结盘 →
      ★部署前 double-check(同cfg+server+时间重叠+status2/5=重复拦; status8/11=废条目提示) →
      ascii提交(防中文乱码) → 复查。
数据源: 同目录 wc_dashboard_data.json ; 队基号=894000+FIFA字母序队号×10。
"""
import json, ssl, urllib.request, calendar, io, sys, time, datetime, pathlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
ROOT=pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯")
ENVCFG={"prod":("https://webgw-cn.tap4fun.com","https://igame.tap4fun.com",".igame-auth.json"),
        "beta":("https://ms-inner-gateway-qa.tap4fun.com","https://igame-qa.tap4fun.com",".igame-credentials.json"),
        "dev":("https://ms-inner-gateway-dev.tap4fun.com","https://igame-dev.tap4fun.com",".igame-auth-dev.json")}
ZH={"ALG":"阿尔及利亚","ARG":"阿根廷","AUS":"澳大利亚","AUT":"奥地利","BEL":"比利时","BIH":"波黑","BRA":"巴西","CAN":"加拿大","CIV":"科特迪瓦","COD":"刚果金","COL":"哥伦比亚","CPV":"佛得角","CRO":"克罗地亚","CUW":"库拉索","CZE":"捷克","ECU":"厄瓜多尔","EGY":"埃及","ENG":"英格兰","ESP":"西班牙","FRA":"法国","GER":"德国","GHA":"加纳","HAI":"海地","IRN":"伊朗","IRQ":"伊拉克","JOR":"约旦","JPN":"日本","KOR":"韩国","KSA":"沙特","MAR":"摩洛哥","MEX":"墨西哥","NED":"荷兰","NOR":"挪威","NZL":"新西兰","PAN":"巴拿马","PAR":"巴拉圭","POR":"葡萄牙","QAT":"卡塔尔","RSA":"南非","SCO":"苏格兰","SEN":"塞内加尔","SUI":"瑞士","SWE":"瑞典","TUN":"突尼斯","TUR":"土耳其","URU":"乌拉圭","USA":"美国","UZB":"乌兹别克斯坦"}
CODES=sorted(ZH.keys())
SERVERS=["1170","1270","1310","1350","1390","1400","1420","1440","1460","1510","1530","1540","1550","1560","1570","1580","1590","1600","1610","1620","1630","1640","1650","1660","1670","1680","1690","1700","1710","1720","1730","1740","1750","1760","1770","1780","1790","1800","1810","1820","1830","1840","1850","1860","1870","1880","1890","1900","1910","1920","1930","1940","1950","1960","1970"]+[str(s) for s in range(1980,2251,10)]  # 55旧+28新(1980-2250)=83服·对齐deploy_r16真实服集
TIER=["免费","$4.99","$9.99","$19.99"]
def base(c): return 894000+(CODES.index(c)+1)*10
def utc(s): return calendar.timegm(datetime.datetime.strptime(s,"%Y-%m-%d %H:%M").timetuple())*1000
def parse_seq(s):
    out=[]
    for p in s.split(","):
        p=p.strip()
        if "-" in p: a,b=map(int,p.split("-")); out+=list(range(a,b+1))
        else: out.append(int(p))
    return out

args=sys.argv[1:]
seqs=parse_seq(args[0]); env=next((a for a in args[1:] if a in ENVCFG),"prod"); GO="--go" in args
host,ui,authf=ENVCFG[env]
auth=json.loads((pathlib.Path.home()/authf).read_text(encoding="utf-8"))
tok=auth["token"]; cid=auth.get("clientId") or auth.get("clientid")
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
H={"accept":"*/*","authorization":f"Bearer {tok}","clientid":cid,"content-type":"application/json","gameid":auth.get("gameId","1090"),"regionid":auth.get("regionId","201"),"origin":ui,"referer":ui+"/"}
sched={i+1:m for i,m in enumerate(json.loads((ROOT/"wc_dashboard_data.json").read_text(encoding="utf-8"))["schedule"])}
now=int(time.time()); OPEN=(now-3600)*1000
payload=[]
for n in seqs:
    m=sched[n]; A,B=m["a_code"],m["b_code"]; en=utc(m["lock_utc"]); c0=102920+(n-1)*4
    rl={"R32":"32强","R16":"16强","QF":"8强","SF":"半决赛","3RD":"季军","FINAL":"决赛"}.get(m.get("round",""),"32强")
    if en<=now*1000: print(f"⚠️跳过 场{n} {ZH[A]}vs{ZH[B]} 结盘{m['lock_utc']}已过"); continue
    for t in range(4):
        payload.append({"activityConfigId":str(c0+t),"customParam":json.dumps({"packIdA":base(A)+t,"packIdB":base(B)+t}),
          "previewTime":0,"endShowTime":0,"startTime":OPEN,"endTime":en,"acrossServer":0,"acrossServerRank":0,
          "name":f"胜负预言·{rl}_{ZH[A]}vs{ZH[B]}_{TIER[t]}","servers":[SERVERS]})
print(f"[{env}] 场次{seqs} → {len(payload)}实例, 开启立即, {len(SERVERS)}服{'  [DRY-RUN]' if not GO else ''}")
for p in payload: print(f"  cfg={p['activityConfigId']} {p['name']} cp={p['customParam']} end={datetime.datetime.utcfromtimestamp(p['endTime']/1000).strftime('%m-%d %H:%M')}UTC")
# double-check
r=urllib.request.urlopen(urllib.request.Request(host+"/ark/activity/list?pageIndex=1&pageSize=300",headers={k:v for k,v in H.items() if k!='content-type'}),timeout=90,context=ctx)
ex=json.loads(r.read().decode('utf-8',errors='replace')); ex=ex.get('data') if isinstance(ex,dict) else ex
ov=lambda s1,e1,s2,e2: s1<e2 and s2<e1
pcfg={p['activityConfigId'] for p in payload}; dup=[]; bnote=[]
for a in ex:
    c=str(a.get('activityConfigId'))
    if c not in pcfg: continue
    asrv=set(s for g in (a.get('servers') or []) for s in g)
    for p in payload:
        if p['activityConfigId']!=c: continue
        inter=[s for s in p['servers'][0] if s in asrv]
        if not inter: continue
        st=a.get('status')
        if st in (2,5) and ov(p['startTime'],p['endTime'],a.get('startTime',0),a.get('endTime',0)): dup.append((c,a['id'],st,len(inter)))
        elif st in (8,11,14): bnote.append((c,a['id'],st))
if dup:
    print("❌ 查重:重复(同cfg+server+时间重叠+活跃),拦截:")
    for c,i,s,n in dup: print(f"   cfg={c} 已有id={i}(status{s}) {n}服")
    sys.exit(3)
if bnote: print(f"⚠️ status8/11废条目(不阻塞): {bnote[:6]}")
print("✅ 查重通过")
if not GO: print("[DRY-RUN] 加 --go 真发"); sys.exit(0)
ids=[]; fail=0
for p in payload:
    try:
        rr=urllib.request.urlopen(urllib.request.Request(host+"/ark/activity/submit",data=json.dumps([p],ensure_ascii=True).encode('ascii'),headers=H,method="POST"),timeout=90,context=ctx)
        j=json.loads(rr.read().decode('utf-8',errors='replace'))
        if j.get('success'): ids.append((p['activityConfigId'],(j.get('data') or ['?'])[0]))
        else: fail+=1; print("FAIL",p['activityConfigId'],j.get('message'))
    except Exception as e: fail+=1; print("ERR",p['activityConfigId'],repr(e)[:70])
    time.sleep(0.15)
print(f"提交: 成功 {len(ids)}/{len(payload)} 失败 {fail}")
for c,d in ids: print(f"  cfg={c} 单号={d}")
