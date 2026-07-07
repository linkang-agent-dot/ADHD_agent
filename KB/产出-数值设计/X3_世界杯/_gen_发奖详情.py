# -*- coding: utf-8 -*-
"""世界杯竞猜 发奖详情生成器(自动赛果 + 猜中玩家 + 可直接导入的 多语言邮件csv + X3奖励csv + GM命令)。
链路: ESPN自动赛果 → 数仓查猜中(买赢队礼包含免费)+竞猜总人数 → 按档加送券 → iGame拉WC-BP各服雪花→GM加分600。
产出: 世界杯竞猜_发奖详情.html(每场锚点+发奖时间+命中率) + 发奖csv\奖励_{key}.csv(X3 6列GBK直导) + 多语言邮件_{key}.csv(模板转置格式) + GM_{key}.csv。
规则(用户确认): 加送券 免费+5/4.99+15/9.99+30/19.99+60(item1146); BP+600; **买多档=加多次(按笔不去重,一笔礼包=一次押注=一次发放)**。⚠️仅生成给人审,不自动发。
"""
import json, ssl, urllib.request, io, sys, datetime, pathlib, csv
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
ROOT=pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯")
CSVDIR=ROOT/"发奖csv"; CSVDIR.mkdir(exist_ok=True)
sys.path.insert(0, r"C:\ADHD_agent\skills\ai-to-sql\scripts")
import _datain_api as DI
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

ZH={"ALG":"阿尔及利亚","ARG":"阿根廷","AUS":"澳大利亚","AUT":"奥地利","BEL":"比利时","BIH":"波黑","BRA":"巴西","CAN":"加拿大","CIV":"科特迪瓦","COD":"刚果金","COL":"哥伦比亚","CPV":"佛得角","CRO":"克罗地亚","CUW":"库拉索","CZE":"捷克","ECU":"厄瓜多尔","EGY":"埃及","ENG":"英格兰","ESP":"西班牙","FRA":"法国","GER":"德国","GHA":"加纳","HAI":"海地","IRN":"伊朗","IRQ":"伊拉克","JOR":"约旦","JPN":"日本","KOR":"韩国","KSA":"沙特","MAR":"摩洛哥","MEX":"墨西哥","NED":"荷兰","NOR":"挪威","NZL":"新西兰","PAN":"巴拿马","PAR":"巴拉圭","POR":"葡萄牙","QAT":"卡塔尔","RSA":"南非","SCO":"苏格兰","SEN":"塞内加尔","SUI":"瑞士","SWE":"瑞典","TUN":"突尼斯","TUR":"土耳其","URU":"乌拉圭","USA":"美国","UZB":"乌兹别克斯坦"}
EN={"RSA":"south africa","CAN":"canada","BRA":"brazil","JPN":"japan","GER":"germany","PAR":"paraguay","NED":"netherlands","MAR":"morocco","CIV":"ivory","NOR":"norway","FRA":"france","SWE":"sweden","MEX":"mexico","ECU":"ecuador","ENG":"england","COD":"congo","BEL":"belgium","SEN":"senegal","USA":"united states","BIH":"bosnia","ESP":"spain","AUT":"austria","POR":"portugal","CRO":"croatia","SUI":"switzerland","ALG":"algeria","AUS":"australia","EGY":"egypt","ARG":"argentina","CPV":"cape verde","COL":"colombia","GHA":"ghana"}
CODES=sorted(ZH.keys())
def base(c): return 894000+(CODES.index(c)+1)*10
BONUS={0:5,1:15,2:30,3:60}; TIERNAME={0:"免费",1:"$4.99",2:"$9.99",3:"$19.99"}
WCBP_CFG="102243"; RES_ID="1146"

# ===== 多语言邮件:复用 bulk-mail-reissue skill 的模板模块(单一来源·任何补偿/发奖邮件通用) =====
sys.path.insert(0, r"C:\Users\linkang\.claude\skills\bulk-mail-reissue")
from multilang_mail import write_multilang_mail, LANG_CODES
MAIL={
"en":("World Cup Oracle Win!","Congrats on predicting the winner! Here are bonus World Cup Draw Tickets — open the World Cup chest for limited heroes and skins!"),
"cn":("世界杯竞猜命中奖励","恭喜您押中本场胜方！特此加送【世界杯冠军抽奖券】，快去世界杯开箱赢取限定英雄与足球宝贝皮肤！"),
"zh":("世界盃競猜命中獎勵","恭喜您押中本場勝方！特此加送【世界盃冠軍抽獎券】，快去世界盃開箱贏取限定英雄與足球寶貝造型！"),
"fr":("Pronostic gagnant !","Bravo d'avoir prédit le vainqueur ! Voici des Tickets de Tirage de la Coupe du Monde — ouvrez le coffre pour des héros et skins limités !"),
"de":("Orakel-Treffer!","Glückwunsch zur richtigen Vorhersage! Hier sind Bonus-WM-Lose — öffne die WM-Truhe für limitierte Helden und Skins!"),
"ru":("Точный прогноз!","Поздравляем с верным прогнозом! Вот бонусные билеты розыгрыша ЧМ — откройте сундук ради лимитированных героев и скинов!"),
"jp":("勝敗予想的中！","勝者の予想的中おめでとう！ワールドカップ抽選券を進呈します。宝箱を開けて限定ヒーローとスキンをゲット！"),
"kr":("승부 예언 적중!","승자를 맞히신 것을 축하합니다! 월드컵 추첨권을 드립니다 — 월드컵 상자를 열어 한정 영웅과 스킨을 획득하세요!"),
"sp":("¡Acierto en el Oráculo!","¡Felicidades por acertar al ganador! Recibe Tickets de Sorteo del Mundial; ¡abre el cofre por héroes y skins limitados!"),
"id":("Tebakan Tepat!","Selamat menebak pemenang! Ini Tiket Undian Piala Dunia — buka peti untuk hero dan skin terbatas!"),
"th":("ทายผลแม่นยำ!","ยินดีด้วยที่ทายผู้ชนะถูก! รับตั๋วจับรางวัลฟุตบอลโลก เปิดกล่องเพื่อรับฮีโร่และสกินสุดพิเศษ!"),
"ar":("توقع صحيح في كأس العالم!","تهانينا على توقع الفائز! إليك تذاكر سحب كأس العالم الإضافية — افتح صندوق كأس العالم للحصول على أبطال وأزياء محدودة!"),
"ro":("Pronostic corect!","Felicitări pentru ghicirea câștigătorului! Iată bilete bonus la tragerea Cupei Mondiale — deschide cufărul pentru eroi și costume limitate!"),
"nl":("Voorspelling juist!","Gefeliciteerd met het voorspellen van de winnaar! Hier zijn bonus WK-loten — open de WK-kist voor gelimiteerde helden en skins!"),
"tr":("Tahmin tuttu!","Kazananı bildiğiniz için tebrikler! İşte bonus Dünya Kupası Çekiliş Biletleri — sınırlı kahraman ve kostümler için sandığı açın!"),
"po":("Palpite certeiro!","Parabéns por acertar o vencedor! Receba Bilhetes de Sorteio da Copa — abra o baú por heróis e skins limitados!"),
"it":("Pronostico azzeccato!","Complimenti per aver indovinato il vincitore! Ecco Biglietti Estrazione Mondiali bonus — apri il forziere per eroi e skin limitati!"),
"vi":("Dự đoán chính xác!","Chúc mừng bạn đã đoán đúng đội thắng! Nhận Vé Quay Thưởng World Cup — mở rương để nhận anh hùng và trang phục giới hạn!"),
"fa":("پیش‌بینی درست!","تبریک بابت پیش‌بینی درست برنده! این بلیط‌های قرعه‌کشی جام جهانی هدیه — صندوق را باز کنید تا قهرمانان و پوسته‌های محدود را به دست آورید!"),
"pls":("Trafna prognoza!","Gratulujemy odgadnięcia zwycięzcy! Oto bonusowe losy Mistrzostw Świata — otwórz skrzynię po limitowanych bohaterów i skiny!"),
}
def write_mail_csv(path): write_multilang_mail(path, MAIL)   # 走 skill 模块写转置模板
write_mail_csv(CSVDIR/"多语言邮件内容.csv")   # 通用一份(不含队名,可复用)

# 每场本地化邮件:通用贺词 + 「对阵+最终结果」(队名20语言翻译,无emoji无换行,见 _wc_team_i18n)
import _wc_team_i18n as TI
def match_mail(a,b,win,score,pens):
    out={}
    for lang,(t,c) in MAIL.items():
        ta=TI.team_name(a,lang); tb=TI.team_name(b,lang)
        rl=TI.result_line(a,b,win,score,pens,lang)
        out[lang]=(f"{t} - {ta} vs {tb}", f"{c} {rl}")
    return out

_dash=json.loads((ROOT/"wc_dashboard_data.json").read_text(encoding="utf-8"))
sched=_dash["schedule"]
SETTLE_FROM=_dash.get("settle_from","2026-06-26")  # ★下注时间窗起点:R32=6/26·R16=7/3(隔离R32老下注·礼包id跨轮复用必须按日期分)
_cache={}
def espn(ds):
    if ds in _cache: return _cache[ds]
    try:
        r=urllib.request.urlopen(urllib.request.Request(f"https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates={ds}",headers={"User-Agent":"Mozilla/5.0"}),timeout=30,context=ctx)
        _cache[ds]=json.loads(r.read().decode('utf-8',errors='replace')).get('events',[])
    except Exception as e: print("ESPN ERR",ds,repr(e)[:60]); _cache[ds]=[]
    return _cache[ds]
def result_of(m):
    ko=datetime.datetime.strptime(m["kickoff_utc"],"%Y-%m-%d %H:%M")
    etd=(ko-datetime.timedelta(hours=4)).strftime("%Y%m%d"); a,b=m["a_code"],m["b_code"]
    for e in espn(etd):
        comp=e.get('competitions',[{}])[0]; cs=comp.get('competitors',[])
        names=" ".join(c.get('team',{}).get('displayName','').lower() for c in cs)
        if EN[a] in names and EN[b] in names:
            st=comp.get('status',{}).get('type',{})
            if not st.get('completed'): return (False,None,st.get('description','未开始'),None)
            sc={}; sh={}; win=None
            for c in cs:
                nm=c.get('team',{}).get('displayName','').lower(); code=a if EN[a] in nm else b
                sc[code]=c.get('score'); sh[code]=c.get('shootoutScore')
                if c.get('winner'): win=code
            pens=f"{sh.get(a)}-{sh.get(b)}" if sh.get(a) is not None and sh.get(b) is not None else None
            return (True,win,f"{sc.get(a,'?')}-{sc.get(b,'?')}",pens)
    return (False,None,"无ESPN数据",None)
def bp_snowflakes():
    auth=json.loads((pathlib.Path.home()/".igame-auth.json").read_text(encoding="utf-8"))
    h={"accept":"*/*","authorization":f"Bearer {auth['token']}","clientid":auth['clientId'],"gameid":auth.get('gameId','1090'),"regionid":auth.get('regionId','201'),"origin":"https://igame.tap4fun.com","referer":"https://igame.tap4fun.com/"}
    sv={}
    for pi in range(1,12):  # ★翻页兜底:活动数增多后老服BP(如13697)会落到后页,只读第1页会漏(2026-07-03扩服后踩坑)
        r=urllib.request.urlopen(urllib.request.Request(f"https://webgw-cn.tap4fun.com/ark/activity/list?pageIndex={pi}&pageSize=100",headers=h),timeout=90,context=ctx)
        lst=json.loads(r.read().decode('utf-8',errors='replace')); lst=lst.get('data') if isinstance(lst,dict) else lst
        if not lst: break
        for x in lst:
            if str(x.get('activityConfigId'))==WCBP_CFG and x.get('status')==5:
                for rr in (x.get('responses') or []):
                    try:
                        for it in json.loads(rr.get('data','[]')):
                            if it.get('activityId') and it.get('serverId'): sv[str(it['serverId'])]=str(it['activityId'])
                    except: pass
        if len(lst)<100: break
    return sv
def winners_of(win):  # 买赢队礼包的每一笔(不去重·买多档=多笔)
    packs=[base(win)+t for t in range(4)]; inl=",".join(f"'{p}'" for p in packs)
    sql=f"SELECT user_id, TRY_CAST(server_id AS INTEGER) sid, reason_sub_id pack FROM v1090.ods_user_asset WHERE asset_id='Item_1146' AND change_type='1' AND reason_id='buy_gift' AND reason_sub_id IN ({inl}) AND partition_date>='{SETTLE_FROM}' GROUP BY 1,2,3"
    r=DI.execute_sql(sql,'TRINO_HF'); rows=r if isinstance(r,list) else json.loads(r)
    return [{"uid":str(x['user_id']),"sid":str(x['sid']),"tier":int(x['pack'])%10} for x in rows]
def participants_of(a,b):  # 竞猜总人数=买了本场任一队任一档的去重玩家
    packs=[base(a)+t for t in range(4)]+[base(b)+t for t in range(4)]; inl=",".join(f"'{p}'" for p in packs)
    sql=f"SELECT count(distinct user_id||'_'||CAST(server_id AS VARCHAR)) n FROM v1090.ods_user_asset WHERE asset_id='Item_1146' AND change_type='1' AND reason_id='buy_gift' AND reason_sub_id IN ({inl}) AND partition_date>='{SETTLE_FROM}'"
    r=DI.execute_sql(sql,'TRINO_HF'); rows=r if isinstance(r,list) else json.loads(r)
    try: return int(rows[0]['n'])
    except: return 0
WC_SERVERS="1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970"
def paid_reach():  # 付费玩家竞猜触达率=55服付费玩家中买过竞猜礼包的占比(口径见 reference_x3_datain_asset_query)
    sql=f"""WITH paid AS (SELECT distinct user_id FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date>='{SETTLE_FROM}' AND TRY_CAST(server_id AS INTEGER) IN ({WC_SERVERS})),
guess AS (SELECT distinct user_id FROM v1090.ods_user_asset WHERE asset_id='Item_1146' AND change_type='1' AND reason_id='buy_gift' AND reason_sub_id LIKE '894%' AND partition_date>='{SETTLE_FROM}')
SELECT (SELECT count(*) FROM paid) total, (SELECT count(*) FROM paid WHERE user_id IN (SELECT user_id FROM guess)) reached"""
    try:
        r=DI.execute_sql(sql,'TRINO_HF'); rows=r if isinstance(r,list) else json.loads(r)
        return int(rows[0]['total']), int(rows[0]['reached'])
    except Exception as e: print("paid_reach ERR",repr(e)[:80]); return 0,0

print("拉 BP 雪花..."); bp=bp_snowflakes(); print(f"  BP live服雪花 {len(bp)}")
pr_total,pr_reached=paid_reach(); pr_pct=f"{pr_reached/pr_total*100:.1f}%" if pr_total else "—"
print(f"  付费玩家竞猜触达 {pr_reached}/{pr_total}={pr_pct}")
def payout_bj(kutc):
    end=datetime.datetime.strptime(kutc,"%Y-%m-%d %H:%M")+datetime.timedelta(hours=10)  # 完赛(开球+2h)北京
    d=end.replace(hour=13,minute=30,second=0,microsecond=0)
    if end>d: d+=datetime.timedelta(days=1)
    return d.strftime("%m-%d 13:30")

from collections import Counter
rows_overview=[]; sections=[]; total_part=0
for m in sched:
    a,b=m["a_code"],m["b_code"]; key=m["key"]; label=f"{ZH[a]} vs {ZH[b]}"
    comp,win,score,pens=result_of(m); payT=payout_bj(m["kickoff_utc"])
    if not comp:
        rows_overview.append((label,score,"—","—",payT,"—","待赛后")); continue
    scoredisp=score if not pens else f"{score}（点球{pens}）"
    npart=participants_of(a,b); total_part+=npart
    if not win:
        rows_overview.append((label,scoredisp,"平局",str(npart),"—","—","平局无猜中")); continue
    W=winners_of(win); tc=Counter(w['tier'] for w in W)
    nwin_people=len(set((w['sid'],w['uid']) for w in W)); nrows=len(W)
    hit=f"{nwin_people/npart*100:.1f}%" if npart else "—"
    # X3奖励csv(6列GBK,按笔): server,user,[1146*券],,,
    rew=[[w['sid'],w['uid'],f"[{RES_ID}*{BONUS[w['tier']]}]","","",""] for w in W]
    with open(CSVDIR/f"奖励_{key}.csv","w",encoding="gbk",newline="",errors="replace") as f:
        csv.writer(f).writerows(rew)
    # 多语言邮件(本场一份): 通用贺词 + 「对阵+最终结果」(队名20语言翻译)
    _mm=match_mail(a,b,win,score,pens)
    write_multilang_mail(CSVDIR/f"多语言邮件_{key}.csv", _mm)
    # content json(igame_mail_send.py --content 直用格式: {lang:{title,body}})——根治"生成器不出content json要手转"坑(2026-07-07)
    json.dump({k:{"title":v[0],"body":v[1]} for k,v in _mm.items()},
              open(CSVDIR/f"content_{key}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    # GM csv(按笔): server,user,BP雪花,600
    gm=[[w['sid'],w['uid'],bp[w['sid']],600] for w in W if w['sid'] in bp]
    with open(CSVDIR/f"GM_{key}.csv","w",encoding="utf-8",newline="") as f:
        csv.writer(f).writerows(gm)
    # GM加分 txt(实际运用格式=iGame GM输入框命令,整块复制粘贴·；分隔)
    gm_cmds=[f'{{"serverIds": "{r[0]}", "cmd": "addactivityscore", "playerIds": "{r[1]}", "args": ["{r[2]}", "600"]}}；' for r in gm]
    txt=["="*64,
         f"世界杯竞猜 BP结算 GM命令清单 [仅供审核·未执行] — {label}（{ZH[win]} 胜）",
         "="*64,
         "活动     : 世界杯BP(cfg102243) · 各服运行时雪花id(每服不同)",
         "每人加分 : 600 / 笔",
         "GM命令   : addactivityscore (= GMAddActivityScore)",
         f"玩家笔数 : {len(gm)}",
         "",
         "-"*64,
         "① iGame GM 输入框命令（整块复制粘贴进 iGame GM 输入框，； 分隔，一行一条）",
         "-"*64]+gm_cmds+[
         "",
         "-"*64,
         "② 或脚本批量发（自动逐条查 errCode=0）",
         "-"*64,
         f"python ~/.claude/skills/igame-gm-send/scripts/batch_add_score.py --csv 发奖csv/GM_{key}.csv --env prod",
         "",
         "⚠️ 仅供审核未执行。活动id=各服运行时雪花号(非配置号102243)。"]
    (CSVDIR/f"GM加分_{key}.txt").write_text("\n".join(txt),encoding="utf-8")
    # 纯GM命令(只命令·换行分隔·无；无表头,直接整列复制)
    pure=[f'{{"serverIds": "{r[0]}", "cmd": "addactivityscore", "playerIds": "{r[1]}", "args": ["{r[2]}", "600"]}}' for r in gm]
    (CSVDIR/f"GM纯命令_{key}.txt").write_text("\n".join(pure),encoding="utf-8")
    tierstr=" / ".join(f"{TIERNAME[t]}:{tc[t]}笔(各+{BONUS[t]}券)" for t in sorted(tc))
    rows_overview.append((label,scoredisp,ZH[win],str(npart),f"{nwin_people}人/{nrows}笔",hit,"已生成"))
    sections.append((key,label,scoredisp,ZH[win],tierstr,npart,nwin_people,nrows,len(gm),rew[:8]))

def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
now_bj=(datetime.datetime.utcnow()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
ovh="".join("<tr>"+"".join(f"<td>{esc(c)}</td>" for c in r)+"</tr>" for r in rows_overview)
secs=[]
for key,label,score,wname,tierstr,npart,nwp,nrows,ngm,sample in sections:
    secs.append(
      f'<h2 id="{esc(key)}">{esc(label)} — {esc(score)} · 胜方 <b style="color:#3fb950">{esc(wname)}</b></h2>'
      f'<div class=tier>竞猜总人数 {npart} ｜ 猜中 {nwp} 人 / {nrows} 笔(命中率 {nwp/npart*100:.1f}% ) ｜ {esc(tierstr)}</div>'
      f'<div class=files>📁 <a href="发奖csv/奖励_{esc(key)}.csv">奖励名单csv(X3 6列GBK,{nrows}笔)</a> ｜ '
      f'<a href="发奖csv/多语言邮件_{esc(key)}.csv">多语言邮件csv(模板格式直导)</a> ｜ '
      f'<a href="发奖csv/GM_{esc(key)}.csv">GM加分csv({ngm}笔)</a> ｜ <a href="发奖csv/GM加分_{esc(key)}.txt">GM加分txt(复制用)</a></div>'
      f'<details><summary>奖励csv预览(前8笔)</summary><pre>'+esc("\n".join(",".join(r) for r in sample))+'</pre></details>')
html=f'''<!DOCTYPE html><html lang=zh-CN><head><meta charset=UTF-8><title>世界杯竞猜 发奖详情</title>
<style>body{{font-family:"Microsoft YaHei";background:#0d1117;color:#e6edf3;padding:24px}}h1{{font-size:21px}}h2{{font-size:15px;color:#58a6ff;border-left:3px solid #58a6ff;padding-left:8px;margin-top:22px}}.sub{{color:#8b949e;font-size:13px;margin-bottom:12px}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #30363d;padding:6px 9px;text-align:left}}th{{background:#161b22;color:#58a6ff}}.tier{{color:#d29922;font-size:13px;margin:4px 0}}.files a{{color:#58a6ff}}.files{{font-size:13px;margin:6px 0}}pre{{background:#161b22;padding:8px;border-radius:5px;font-size:12px;color:#a5d6ff;overflow-x:auto}}summary{{cursor:pointer;color:#8b949e}}</style></head><body>
<h1>🏆 世界杯竞猜 发奖详情</h1>
<div class=sub>更新(北京) {now_bj} ｜ 赛果=ESPN自动 ｜ 猜中=买赢队礼包(含免费,买多档=多笔多发) ｜ 加送券 免费+5/$4.99+15/$9.99+30/$19.99+60(道具1146) ｜ BP+600/笔 ｜ ⚠️仅供审核,发奖走bulk-mail+batch_add_score,发完把key加settled</div>
<div class=sub style="color:#3fb950">📊 已完赛累计竞猜总人次 <b>{total_part}</b> ｜ 付费玩家竞猜触达率 <b>{pr_pct}</b>（55服付费玩家 {pr_reached}/{pr_total} 买过竞猜礼包）</div>
<h2 style="border:none">📋 各场发奖总览</h2>
<table><thead><tr><th>对阵</th><th>赛果</th><th>胜方</th><th>竞猜总人数</th><th>猜中(人/笔)</th><th>命中率</th><th>发奖状态</th></tr></thead><tbody>{ovh}</tbody></table>
{''.join(secs) or '<p style="color:#6e7681">暂无已完赛场次</p>'}
</body></html>'''
(ROOT/"世界杯竞猜_发奖详情.html").write_text(html,encoding="utf-8")
print("WROTE 世界杯竞猜_发奖详情.html +", len(sections),"场csv ; 累计竞猜总人次",total_part)
for r in rows_overview: print("  ",r)
