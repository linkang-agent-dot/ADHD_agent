# -*- coding: utf-8 -*-
"""世界杯半决赛(SF)部署器·prod 83服。与QF的差别:
  tier0(免费)/tier1($4.99) = 原队包 base(队)+t (共用组291335/291101未动·徽章对)
  tier2($9.99)/tier3($19.99) = 4强容器包+t (淘汰队ID重配的4强版:c14=自选组291350/291351·徽章已设成QF队)
用法: python deploy_sf.py [--go]   (默认dry-run)
数据源: KB wc_dashboard_data.json 的 round=SF 场次; cfg=102920+(N-1)*4。"""
import json,ssl,urllib.request,calendar,io,sys,time,datetime,pathlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
ROOT=pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯")
GO="--go" in sys.argv
HOST="https://webgw-cn.tap4fun.com"; UI="https://igame.tap4fun.com"; AUTHF=".igame-auth.json"
ZH={"ARG":"阿根廷","BEL":"比利时","ENG":"英格兰","ESP":"西班牙","FRA":"法国","MAR":"摩洛哥","NOR":"挪威","SUI":"瑞士"}
QN={"ARG":2,"BEL":5,"ENG":18,"ESP":19,"FRA":20,"MAR":30,"NOR":33,"SUI":42}
def base(c): return 894000+QN[c]*10
CONTAINER={"ARG":894010,"BEL":894030,"ENG":894040,"ESP":894060,"FRA":894080,"MAR":894090,"NOR":894100,"SUI":894120}  # 4强容器包基号
def pack(c,t): return base(c)+t if t in (0,1) else CONTAINER[c]+t
TIER=["免费","$4.99","$9.99","$19.99"]
SERVERS=["1170","1270","1310","1350","1390","1400","1420","1440","1460","1510","1530","1540","1550","1560","1570","1580","1590","1600","1610","1620","1630","1640","1650","1660","1670","1680","1690","1700","1710","1720","1730","1740","1750","1760","1770","1780","1790","1800","1810","1820","1830","1840","1850","1860","1870","1880","1890","1900","1910","1920","1930","1940","1950","1960","1970"]+[str(s) for s in range(1980,2251,10)]  # 83服
def utc(s): return calendar.timegm(datetime.datetime.strptime(s,"%Y-%m-%d %H:%M").timetuple())*1000
auth=json.loads((pathlib.Path.home()/AUTHF).read_text(encoding="utf-8"))
H={"accept":"*/*","authorization":f"Bearer {auth['token']}","clientid":auth.get("clientId") or auth.get("clientid"),"content-type":"application/json","gameid":auth.get("gameId","1090"),"regionid":auth.get("regionId","201"),"origin":UI,"referer":UI+"/"}
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
sched=json.loads((ROOT/"wc_dashboard_data.json").read_text(encoding="utf-8"))["schedule"]
now=int(time.time()); OPEN=(now-3600)*1000
payload=[]
for n,m in enumerate(sched,1):
    if m.get("round")!="SF": continue
    A,B=m["a_code"],m["b_code"]; en=utc(m["lock_utc"]); c0=102920+(n-1)*4
    if en<=now*1000: print(f"⚠️跳过 {m['key']} 锁盘已过"); continue
    for t in range(4):
        payload.append({"activityConfigId":str(c0+t),"customParam":json.dumps({"packIdA":pack(A,t),"packIdB":pack(B,t)}),
          "previewTime":0,"endShowTime":0,"startTime":OPEN,"endTime":en,"acrossServer":0,"acrossServerRank":0,
          "name":f"胜负预言·半决赛_{ZH[A]}vs{ZH[B]}_{TIER[t]}","servers":[SERVERS]})
print(f"[prod] SF → {len(payload)}实例, 开启立即, {len(SERVERS)}服{'  [DRY]' if not GO else ''}")
for p in payload: print(f"  cfg={p['activityConfigId']} {p['name']} cp={p['customParam']} end={datetime.datetime.utcfromtimestamp(p['endTime']/1000).strftime('%m-%d %H:%M')}UTC")
r=urllib.request.urlopen(urllib.request.Request(HOST+"/ark/activity/list?pageIndex=1&pageSize=300",headers={k:v for k,v in H.items() if k!='content-type'}),timeout=90,context=ctx)
ex=json.loads(r.read().decode('utf-8','replace')); ex=ex.get('data') if isinstance(ex,dict) else ex
ov=lambda s1,e1,s2,e2: s1<e2 and s2<e1; pcfg={p['activityConfigId'] for p in payload}; dup=[]
for a in ex or []:
    c=str(a.get('activityConfigId'))
    if c not in pcfg: continue
    asrv=set(s for g in (a.get('servers') or []) for s in g)
    for p in payload:
        if p['activityConfigId']==c and [s for s in p['servers'][0] if s in asrv] and a.get('status') in(2,5) and ov(p['startTime'],p['endTime'],a.get('startTime',0),a.get('endTime',0)):
            dup.append((c,a['id'],a.get('status')))
if dup: print("❌查重:活跃重叠",dup[:8]); sys.exit(3)
print("✅查重通过")
if not GO: print("[DRY-RUN] 加--go真发"); sys.exit(0)
ids=[];fail=0
for p in payload:
    try:
        rr=urllib.request.urlopen(urllib.request.Request(HOST+"/ark/activity/submit",data=json.dumps([p],ensure_ascii=True).encode('ascii'),headers=H,method="POST"),timeout=90,context=ctx)
        j=json.loads(rr.read().decode('utf-8','replace'))
        if j.get('success'): ids.append((p['activityConfigId'],(j.get('data') or ['?'])[0]))
        else: fail+=1; print("FAIL",p['activityConfigId'],j.get('message'))
    except Exception as e: fail+=1; print("ERR",p['activityConfigId'],repr(e)[:70])
    time.sleep(0.15)
print(f"提交:成功{len(ids)}/{len(payload)} 失败{fail}")
for c,x in ids: print(f"  cfg={c} 单号={x}")
