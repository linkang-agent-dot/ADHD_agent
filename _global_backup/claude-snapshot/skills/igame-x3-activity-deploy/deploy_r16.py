# -*- coding: utf-8 -*-
"""世界杯16强(R16)竞猜部署器·复用R32 cfg池102920-951·不动wc_dashboard_data.json(保R32结算)。
用法: python deploy_r16.py [--go]   (默认dry-run·查重+预览)
机制: 6场已定R16(M1-M6·ESPN真实对阵)×4档 → cfg=102920+(N-1)*4 → customParam=队基号+档 →
      start=7/3 10:00 UTC(北京18:00) end=各场开球-10min → double-check(同cfg+server+时间重叠status2/5拦) → ascii提交。
M7/M8待R32(7/4)定队后补(改MATCHES加两行重跑)。"""
import json,ssl,urllib.request,calendar,io,sys,time,datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
ZH={"ALG":"阿尔及利亚","ARG":"阿根廷","AUS":"澳大利亚","AUT":"奥地利","BEL":"比利时","BIH":"波黑","BRA":"巴西","CAN":"加拿大","CIV":"科特迪瓦","COD":"刚果金","COL":"哥伦比亚","CPV":"佛得角","CRO":"克罗地亚","CUW":"库拉索","CZE":"捷克","ECU":"厄瓜多尔","EGY":"埃及","ENG":"英格兰","ESP":"西班牙","FRA":"法国","GER":"德国","GHA":"加纳","HAI":"海地","IRN":"伊朗","IRQ":"伊拉克","JOR":"约旦","JPN":"日本","KOR":"韩国","KSA":"沙特","MAR":"摩洛哥","MEX":"墨西哥","NED":"荷兰","NOR":"挪威","NZL":"新西兰","PAN":"巴拿马","PAR":"巴拉圭","POR":"葡萄牙","QAT":"卡塔尔","RSA":"南非","SCO":"苏格兰","SEN":"塞内加尔","SUI":"瑞士","SWE":"瑞典","TUN":"突尼斯","TUR":"土耳其","URU":"乌拉圭","USA":"美国","UZB":"乌兹别克斯坦"}
CODES=sorted(ZH.keys())
def base(c): return 894000+(CODES.index(c)+1)*10
TIER=["免费","$4.99","$9.99","$19.99"]
OLD=["1170","1270","1310","1350","1390","1400","1420","1440","1460","1510","1530","1540","1550","1560","1570","1580","1590","1600","1610","1620","1630","1640","1650","1660","1670","1680","1690","1700","1710","1720","1730","1740","1750","1760","1770","1780","1790","1800","1810","1820","1830","1840","1850","1860","1870","1880","1890","1900","1910","1920","1930","1940","1950","1960","1970"]
NEW=[str(s) for s in range(1980,2251,10)]
SERVERS=OLD+NEW  # 83服
# M1-M6 已定(a,b,开球UTC);M7/M8待定不含
MATCHES=[("CAN","MAR",(2026,7,4,17,0)),("PAR","FRA",(2026,7,4,21,0)),("BRA","NOR",(2026,7,5,20,0)),
         ("MEX","ENG",(2026,7,6,0,0)),("POR","ESP",(2026,7,6,19,0)),("USA","BEL",(2026,7,7,0,0)),
         ("ARG","EGY",(2026,7,7,16,0)),("SUI","COL",(2026,7,7,20,0))]  # M7/M8·ESPN真实对阵(非占位推导)
START=calendar.timegm((2026,7,3,10,0,0))*1000  # 7/3 18:00北京
GO="--go" in sys.argv
SEQ=None
if "--seq" in sys.argv:
    SEQ=set(int(x) for x in sys.argv[sys.argv.index("--seq")+1].split(","))
a=json.loads((__import__('pathlib').Path.home()/".igame-auth.json").read_text(encoding="utf-8"))
H={"accept":"*/*","authorization":f"Bearer {a['token']}","clientid":a.get("clientId") or a.get("clientid"),"content-type":"application/json","gameid":a.get("gameId","1090"),"regionid":a.get("regionId","201"),"origin":"https://igame.tap4fun.com","referer":"https://igame.tap4fun.com/"}
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
payload=[]
for n,(A,B,ko) in enumerate(MATCHES,1):
    if SEQ and n not in SEQ: continue
    end=(calendar.timegm(ko+(0,))-600)*1000  # 开球-10min
    c0=102920+(n-1)*4
    for t in range(4):
        payload.append({"activityConfigId":str(c0+t),"customParam":json.dumps({"packIdA":base(A)+t,"packIdB":base(B)+t}),
          "previewTime":0,"endShowTime":0,"startTime":START,"endTime":end,"acrossServer":0,"acrossServerRank":0,
          "name":f"胜负预言·16强_{ZH[A]}vs{ZH[B]}_{TIER[t]}","servers":[SERVERS]})
def d(ms): return datetime.datetime.utcfromtimestamp(ms/1000).strftime('%m-%d %H:%M')
print(f"[16强M1-6] {len(payload)}实例 start={d(START)}UTC(北京18:00) {len(SERVERS)}服{'  [DRY]' if not GO else ''}")
for n,(A,B,ko) in enumerate(MATCHES,1):
    if SEQ and n not in SEQ: continue
    c0=102920+(n-1)*4; end=(calendar.timegm(ko+(0,))-600)*1000
    print(f"  M{n} {ZH[A]}vs{ZH[B]} cfg{c0}-{c0+3} 结盘={d(end)}UTC")
# double-check
r=urllib.request.urlopen(urllib.request.Request("https://webgw-cn.tap4fun.com/ark/activity/list?pageIndex=1&pageSize=300",headers={k:v for k,v in H.items() if k!='content-type'}),timeout=90,context=ctx)
ex=json.loads(r.read().decode('utf-8','replace')); ex=ex.get('data') if isinstance(ex,dict) else ex
ov=lambda s1,e1,s2,e2: s1<e2 and s2<e1
pcfg={p['activityConfigId'] for p in payload}; dup=[]
for x in ex:
    c=str(x.get('activityConfigId'))
    if c not in pcfg: continue
    asrv=set(s for g in (x.get('servers') or []) for s in g)
    for p in payload:
        if p['activityConfigId']!=c: continue
        if not [s for s in p['servers'][0] if s in asrv]: continue
        if x.get('status') in(2,5) and ov(p['startTime'],p['endTime'],x.get('startTime',0),x.get('endTime',0)):
            dup.append((c,x['id'],x.get('status')))
if dup:
    print("❌ 查重:活跃重叠,拦截:",dup[:8]); sys.exit(3)
print("✅ 查重通过(R32残留在自己时间窗外·不重叠)")
if not GO: print("[DRY-RUN] 加 --go 真发"); sys.exit(0)
ids=[];fail=0
for p in payload:
    try:
        rr=urllib.request.urlopen(urllib.request.Request("https://webgw-cn.tap4fun.com/ark/activity/submit",data=json.dumps([p],ensure_ascii=True).encode('ascii'),headers=H,method="POST"),timeout=90,context=ctx)
        j=json.loads(rr.read().decode('utf-8','replace'))
        if j.get('success'): ids.append((p['activityConfigId'],(j.get('data') or ['?'])[0]))
        else: fail+=1; print("FAIL",p['activityConfigId'],j.get('message'))
    except Exception as e: fail+=1; print("ERR",p['activityConfigId'],repr(e)[:60])
    time.sleep(0.15)
print(f"提交:成功{len(ids)}/{len(payload)} 失败{fail}")
for c,x in ids: print(f"  cfg={c} 单号={x}")
