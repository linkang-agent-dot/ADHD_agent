# -*- coding: utf-8 -*-
"""世界杯竞猜运营看板生成器。拉 iGame 实时竞猜 + 赛程 schedule 交叉分类 → HTML。
分类: 对阵总览 / 已上线 / 待上线 / 待发奖 / 已发奖。每天北京12:00 由计划任务跑。
数据源: 同目录 wc_dashboard_data.json (schedule 随轮次更新, settled 发完奖加key)。"""
import io, sys, json, ssl, datetime, urllib.request, urllib.error, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯")
DATA = json.loads((ROOT / "wc_dashboard_data.json").read_text(encoding='utf-8'))
OUT = ROOT / "世界杯竞猜运营看板.html"

ZH = {"ALG":"阿尔及利亚","ARG":"阿根廷","AUS":"澳大利亚","AUT":"奥地利","BEL":"比利时","BIH":"波黑",
"BRA":"巴西","CAN":"加拿大","CIV":"科特迪瓦","COD":"刚果(金)","COL":"哥伦比亚","CPV":"佛得角",
"CRO":"克罗地亚","CUW":"库拉索","CZE":"捷克","ECU":"厄瓜多尔","EGY":"埃及","ENG":"英格兰",
"ESP":"西班牙","FRA":"法国","GER":"德国","GHA":"加纳","HAI":"海地","IRN":"伊朗",
"IRQ":"伊拉克","JOR":"约旦","JPN":"日本","KOR":"韩国","KSA":"沙特","MAR":"摩洛哥",
"MEX":"墨西哥","NED":"荷兰","NOR":"挪威","NZL":"新西兰","PAN":"巴拿马","PAR":"巴拉圭",
"POR":"葡萄牙","QAT":"卡塔尔","RSA":"南非","SCO":"苏格兰","SEN":"塞内加尔","SUI":"瑞士",
"SWE":"瑞典","TUN":"突尼斯","TUR":"土耳其","URU":"乌拉圭","USA":"美国","UZB":"乌兹别克斯坦"}
CODES = sorted(ZH.keys())  # 1-indexed 队号
TIER = {0:"免费",1:"$4.99",2:"$9.99",3:"$19.99"}
STATUS = {2:"待开始",5:"进行中",8:"下线申请中",19:"已下线",14:"处理中",4:"未开始"}

def code_of(packid):
    n = (packid - 894000)//10
    return CODES[n-1] if 1 <= n <= 48 else f"?{packid}"
def tier_of(packid):
    return (packid - 894000) % 10
def zh(c): return ZH.get(c, c)
def parse(t): return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M")
def bj(dt_utc): return (dt_utc + datetime.timedelta(hours=8)).strftime("%m-%d %H:%M")

now = datetime.datetime.utcnow()
now_bj = (now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

# ---- 拉 iGame 已部署竞猜 ----
ENV = DATA.get("env","prod")
HOST = {"prod":"https://webgw-cn.tap4fun.com","beta":"https://ms-inner-gateway-qa.tap4fun.com",
        "dev":"https://ms-inner-gateway-dev.tap4fun.com"}[ENV]
UI = {"prod":"https://igame.tap4fun.com","beta":"https://igame-qa.tap4fun.com","dev":"https://igame-dev.tap4fun.com"}[ENV]
AUTHF = {"prod":".igame-auth.json","beta":".igame-credentials.json","dev":".igame-auth-dev.json"}[ENV]
deployed = []   # {cfg,id,a,b,tier,servers,status}
fetch_err = ""
try:
    auth = json.loads((pathlib.Path.home()/AUTHF).read_text(encoding='utf-8'))
    tok = auth['token']; cid = auth.get('clientId') or auth.get('clientid')
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    h = {"accept":"*/*","authorization":f"Bearer {tok}","clientid":cid,"gameid":auth.get('gameId','1090'),
         "regionid":auth.get('regionId','201'),"origin":UI,"referer":UI+"/"}
    r = urllib.request.urlopen(urllib.request.Request(HOST+"/ark/activity/list?pageIndex=1&pageSize=120",headers=h),timeout=60,context=ctx)
    lst = json.loads(r.read().decode('utf-8',errors='replace'))
    lst = lst.get('data') if isinstance(lst,dict) else lst
    for x in lst:
        cfg = str(x.get('activityConfigId',''))
        if not (cfg.isdigit() and 102920 <= int(cfg) <= 102992): continue
        if x.get('status') not in (2,5): continue   # 只看在线/待开始的
        try:
            cp = json.loads(x.get('customParam') or "{}")
            a = int(cp.get('packIdA')); b = int(cp.get('packIdB'))
        except: continue
        srv = [s for g in (x.get('servers') or []) for s in g]
        deployed.append({"cfg":cfg,"id":x.get('id'),"a":code_of(a),"b":code_of(b),
                         "tier":tier_of(a),"servers":srv,"status":x.get('status')})
except Exception as e:
    fetch_err = repr(e)[:160]

def mkey(a,b): return frozenset((a,b))
dep_by_match = {}
for d in deployed:
    dep_by_match.setdefault(mkey(d['a'],d['b']), []).append(d)

# ---- 赛程分类 ----
rows_overview=[]; sec_online=[]; sec_pending=[]; sec_await=[]; sec_rewarded=[]
for m in DATA["schedule"]:
    a,b = m['a_code'], m['b_code']; k = mkey(a,b)
    ko = parse(m['kickoff_utc']); lk = parse(m['lock_utc'])
    deps = dep_by_match.get(k, [])
    is_online = len(deps) > 0
    played = now >= lk
    settled = m['key'] in DATA.get("settled", [])
    # 总览状态
    if settled: ov = "已发奖"
    elif played: ov = "待发奖"
    elif is_online: ov = "已上线"
    else: ov = "待上线"
    rows_overview.append((m, a, b, ko, lk, ov, len(deps)))
    label = f"{zh(a)} vs {zh(b)}"
    if is_online:
        tiers = sorted(deps, key=lambda d:d['tier'])
        tierstr = " / ".join(f"{TIER.get(d['tier'],d['tier'])}(id{d['id']},{STATUS.get(d['status'],d['status'])})" for d in tiers)
        nsrv = max(len(d['servers']) for d in deps)
        sec_online.append((label, m['round'], len(deps), tierstr, nsrv))
    if not is_online and not played:
        sec_pending.append((label, m['round'], bj(ko)))
    if played and not settled:
        sec_await.append((label, m['round'], bj(ko), m.get('result') or "—"))
    if settled:
        sec_rewarded.append((label, m['round'], bj(ko), m.get('result') or "—"))

def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
OVC = {"已发奖":"#3fb950","待发奖":"#f0883e","已上线":"#58a6ff","待上线":"#8b949e"}

ov_html = "\n".join(
    f'<tr><td>{esc(m["round"])}</td><td>{esc(zh(a))} vs {esc(zh(b))}</td><td>{bj(ko)}</td><td>{bj(lk)}</td>'
    f'<td style="color:{OVC[ov]};font-weight:bold">{ov}</td><td>{nd or "-"}</td></tr>'
    for (m,a,b,ko,lk,ov,nd) in rows_overview)
def tbl(rows, cols, fmt):
    if not rows: return '<div class="empty">（暂无）</div>'
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = "\n".join("<tr>"+ "".join(f"<td>{esc(c)}</td>" for c in fmt(r)) +"</tr>" for r in rows)
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

online_html  = tbl(sec_online,  ["对阵","轮次","档数","档位(活动id/状态)","服数"], lambda r:[r[0],r[1],r[2],r[3],r[4]])
pending_html = tbl(sec_pending, ["对阵","轮次","开球(北京)"], lambda r:[r[0],r[1],r[2]])
await_html   = tbl(sec_await,   ["对阵","轮次","开球(北京)","赛果"], lambda r:[r[0],r[1],r[2],r[3]])
reward_html  = tbl(sec_rewarded,["对阵","轮次","开球(北京)","赛果"], lambda r:[r[0],r[1],r[2],r[3]])

errbar = f'<div class="err">⚠️ iGame({ENV}) 拉取失败，已上线/状态可能不准: {esc(fetch_err)}</div>' if fetch_err else ""

html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="3600">
<title>世界杯竞猜运营看板</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;margin:0;background:#0d1117;color:#e6edf3;padding:24px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:22px 0 8px;color:#58a6ff;border-left:3px solid #58a6ff;padding-left:8px}}
.sub{{color:#8b949e;font-size:13px;margin-bottom:6px}}
.cnt{{color:#8b949e;font-size:12px;margin-bottom:14px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-bottom:8px}}
th,td{{border:1px solid #30363d;padding:7px 10px;text-align:left}} th{{background:#161b22;color:#58a6ff}}
tr:nth-child(even){{background:#11161d}}
.empty{{color:#6e7681;font-size:13px;padding:6px 0}}
.err{{background:#3d0d0d;border:1px solid #b91c1c;border-radius:6px;padding:8px 12px;color:#ff9b9b;font-size:12px;margin:8px 0}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;margin-right:6px}}
</style></head><body>
<h1>🏆 世界杯竞猜运营看板</h1>
<div class="sub">环境 <b>{ENV}</b> · 数据来自 iGame 实时 + 赛程表 · 每天北京 12:00 自动刷新（页面每小时自刷）</div>
<div class="cnt">更新时间(北京): <b>{now_bj}</b> ｜ 已上线 {len(sec_online)} 场 · 待上线 {len(sec_pending)} 场 · 待发奖 {len(sec_await)} 场 · 已发奖 {len(sec_rewarded)} 场</div>
{errbar}
<h2>📋 对阵总览</h2>
<table><thead><tr><th>轮次</th><th>对阵</th><th>开球(北京)</th><th>锁盘(北京)</th><th>状态</th><th>已部署档数</th></tr></thead><tbody>
{ov_html}
</tbody></table>
<h2>🟢 已上线竞猜</h2>
{online_html}
<h2>🔵 待上线竞猜（对阵已定、未部署）</h2>
{pending_html}
<h2>🟠 待发奖（已开赛、未结算）</h2>
{await_html}
<h2>✅ 已发奖</h2>
{reward_html}
<div class="cnt" style="margin-top:18px">维护：对阵确定→加进 wc_dashboard_data.json 的 schedule；某场发完奖→把它的 key 加进 settled。生成器 _gen_竞猜运营看板.py。</div>
</body></html>'''
OUT.write_text(html, encoding='utf-8')
print(f"WROTE {OUT}")
print(f"已上线{len(sec_online)} 待上线{len(sec_pending)} 待发奖{len(sec_await)} 已发奖{len(sec_rewarded)}; fetch_err={fetch_err or '无'}")
