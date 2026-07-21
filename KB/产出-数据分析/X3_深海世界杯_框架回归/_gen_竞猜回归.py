# -*- coding: utf-8 -*-
"""
X3 双节框架回归 · 母题4（本届17条改动逐条效果）报告生成器
数据源 = _l1_m4.json（_l1_refresh.py 产出，Trino 全口径）+ M1结论 + 结算台账(memory)
用法: python _gen_母题4.py   （终版: 先跑 _l1_refresh.py 2026-07-20 再跑本脚本）
"""
import sys, json, os, datetime
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, '_l1_m4.json'), encoding='utf-8'))
B = json.load(open(os.path.join(HERE, '_wc_bench.json'), encoding='utf-8'))
END = L['END']
OUT = os.path.join(HERE, f"母题4_改动效果清单_{END.replace('-','')}.html")
DS, WC, RD = L['深海节'], L['世界杯'], L['竞猜按轮']
dm, wm = DS['modules'], WC['modules']
KX = B['WC开箱族合并']          # 开箱连锁+锚点 union 口径
CANYU = B['竞猜参与']['users']   # 竞猜参与人数(asset 894%)
DH = B['兑换消耗1147']
K3 = json.load(open(os.path.join(HERE, '_kaixiang.json'), encoding='utf-8'))   # 开箱三代
G_VT = K3['情人节开箱(致她的信)']; G_SM = K3['夏日开箱(复用情人包)']; G_WC = K3['世界杯开箱(福箱)']
KD = json.load(open(os.path.join(HERE, '_kaixiang_deep.json'), encoding='utf-8'))  # 四代分桶/分位/逐服
KG = KD['gens']; PS = KD['perserver']
AN = json.load(open(os.path.join(HERE, '_anchor.json'), encoding='utf-8'))         # 锚点四代+WC按档
JC = json.load(open(os.path.join(HERE, '_jingcai.json'), encoding='utf-8'))         # 竞猜参与(逐日+按轮)
JP = json.load(open(os.path.join(HERE, '_jingcai_pay.json'), encoding='utf-8'))     # 竞猜/通行证 完整付费指标(全服)
JPO = json.load(open(os.path.join(HERE, '_jc_pay_oldsrv.json'), encoding='utf-8'))   # 同套指标·老服段1000-1870(=夏日部署段,跨窗同段可比)
JF59 = json.load(open(os.path.join(HERE, '_jc_form_ds59.json'), encoding='utf-8'))    # WC4形式限深海59服段(ARPU排位统一分母,用户07-21定)
PR = json.load(open(os.path.join(HERE, '_kx_payrate.json'), encoding='utf-8'))      # 开箱付费率下钻(逐服+档位)
TKS = json.load(open(os.path.join(HERE, '_ticket_summer.json'), encoding='utf-8'))  # 券供给对比
GEN_COL = {'元旦开箱': '#4691e8', '情人节开箱': '#8b949e', '夏日开箱': '#2ea856', '世界杯开箱': '#c08a17'}
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def fmt(v): return f"${v:,.0f}"
def M(mods, k): return mods[k]

BADGE = {'ok': ('验证有效', 'ok'), 'bad': ('证伪', 'bad'), 'mid': ('部分/存疑', 'mid'), 'wait': ('待查', 'wait')}

# ============ 17 条改动 ============
WC_ROWS = [
 ('W1', '竞猜玩法全新上线<br><span class="dim">免费+4档按国下注 · X3首个"充值直接参与"型</span>',
  '<b>史上最宽入口、但不是收钱模块</b>——全程参与 ' + f'{CANYU:,}' + ' 人（=窗口总付费人数的 3.2 倍），付费档全程仅 {} / {}人（付费转化 1.2%）',
  f"付费 {fmt(wm['竞猜礼包全档']['rev'])} · 买家 {wm['竞猜礼包全档']['buyers']} · 复购 {wm['竞猜礼包全档']['opb']:.1f}单", 'mid'),
 ('W2', '锚点礼包升级<br><span class="dim">07-13曾归因"改可复购"——已证伪，见02章③</span>',
  '<b>无净效果证据——买家增长主要是服基数效应</b>——锚点买家 48/53/55 → 153 人的增长与开服扩量同步（世界杯口径含 28 扩服+年轻服），95% 集中 $4.99 档 = 正常小额位表现；「可复购」经配置 diff 证伪（限购配置与前代完全一致、情人锚点 max $910 历来可复购）',
  f"锚点 {fmt(wm['开箱券锚点(可复购)']['rev'])} · 153人 · $4.99档 145人", 'mid'),
 ('W3', '外显进付费档<br><span class="dim">$9.99框宝箱 / $19.99表情宝箱 · 开箱大奖=皮肤</span>',
  '<b>外显是付费主力</b>——竞猜侧外显两档卖 {}（占竞猜付费 81%，是纯券档的 4.3 倍）；开箱侧 max <b>$1,415</b>=六代第一次破 $707 买光墙',
  f"框档 {fmt(wm['竞猜$9.99框档(尾2)']['rev'])} + 表情档 {fmt(wm['竞猜$19.99表情档(尾3)']['rev'])} · 开箱max {fmt(wm['开箱福箱连锁']['max'])}", 'ok'),
 ('W4', '全节日锚点礼包补钻石+VIP<br><span class="dim">B线纯券→对齐A线（6/24 v0.41）</span>',
  '归因悬置——锚点买家增长被判为基数效应后，补钻VIP 的独立效果无从评估；老节日锚点下届表现可当对照',
  '—', 'wait'),
 ('W5', '开箱新增本服排行榜<br><span class="dim">皮肤→纪念卡降级奖励 · 活动全程拉通累计</span>',
  '<b>效果未显现（拉通口径）</b>——窗口近 2 倍长，每服 top1 中位 $60 反而低于夏日 $75，服均 $261 仅持平（$240）：榜没把各服头部拉起来；⚠️该榜配置时标注"双Tab露出需程序联调·占位性质"，先确认客户端是否真露出了本服Tab——若未露出是"没上"而非"无效"（详见 02 章④）',
  '逐服对比见 02 章', 'mid'),
 ('W6', '竞猜奖励逐轮升级<br><span class="dim">8强按国直给→4强自选宝箱→决赛冠军框+头衔</span>',
  '<b>升级没有逆转付费衰减</b>——付费档日均 R32 $410 → R16 $456 → QF $237 → SF $158，免费参与却稳定（QF 场均仍 4k~8.4k）：奖励加码补不了"可押队减半"的结构性衰减；决赛（7/19）终验',
  f"按轮: {' → '.join(f'{k} {fmt(v[chr(114)+chr(101)+chr(118)])}' for k, v in RD.items())}", 'mid'),
 ('W7', '扩服 28 新服（1980-2250）<br><span class="dim">D30 口径卡线</span>',
  '<b>贡献世界杯总收入的 37%</b>（$16.1k / 全口径 $43.0k）——年轻服节日弹性显著高于成熟服，扩服是本届最划算的动作之一',
  '来源=母题1 服段拆分', 'ok'),
 ('W8', '免费竞猜奖励下调<br><span class="dim">30分加速→1分</span>',
  '<b>白嫖盘不敏感</b>——下调后免费下注量未见流失（R16 单场峰值 9.8k 人，QF 稳定 4k~8.4k/场）',
  '来源=逐轮结算台账', 'ok'),
]

DS_ROWS = [
 ('D1', '双周双核心循环（弹药带首试）<br><span class="dim">设计: W1转盘铺量 → W2大富翁攻深度</span>',
  '<b>节奏没做出来</b>——部署层转盘/大富翁/BP 全部 7/3 同开 14 天（无错峰），总盘 D0 $10.4k 单调衰减到 $2.2k、无 D7 二次点火：同开=没有弹药带，只有一根长弹药（马戏节要错峰部署才算真弹药带）',
  '来源=母题1 逐日曲线', 'bad'),
 ('D2', '转盘换皮+补藏宝图锚点13021-24<br><span class="dim">尼罗转盘克隆 · 锚点=获取路径修复</span>',
  '<b>判退役坐实</b>——转盘连锁 ARPPU $47.7 / 复购 2.2 单（六代垫底档），锚点 4 档 <b>13 天零购买</b>（仅起价格锚作用）；逐档限购形式第三次证明锁死复购',
  f"转盘 {fmt(dm['转盘连锁5档']['rev'])} · {dm['转盘连锁5档']['buyers']}人 · max {fmt(dm['转盘连锁5档']['max'])} · 锚点 $0", 'bad'),
 ('D3', '大富翁挂拼图子活动+阶段奖改罗盘<br><span class="dim">深海第二周核心</span>',
  '<b>深海压舱石</b>——大富翁族（成就+罗盘连锁+BP大富翁线）合计 $21.7k=深海最大玩法族，成就礼包渗透 14.6%、BP大富翁线渗透 22.6% 全场最高；上届"ARPU 反超 P2"的模块地位保持',
  f"成就 {fmt(dm['大富翁成就礼包']['rev'])} + 罗盘链 {fmt(dm['大富翁罗盘连锁']['rev'])} + BP线 {fmt(dm['BP大富翁线(130036/37)']['rev'])}", 'ok'),
 ('D4', '双 BP 并行<br><span class="dim">远航日志(转盘线) + 航海通行证(大富翁线)</span>',
  '<b>渗透王 + 天花板矮 双坐实</b>——两线合计 $15.7k、买家 397+233 人（渗透全场第一），但 max $30 = 买满即封顶的硬实证；叠加 1.8% 满级事故：<b>别再堆第三条 BP</b>，该修的是单条 BP 的深度',
  f"大富翁线 {fmt(dm['BP大富翁线(130036/37)']['rev'])}/397人 + 转盘线 {fmt(dm['BP转盘线(130035/46)']['rev'])}/233人 · max $30", 'mid'),
 ('D5', '每日礼包 Type29 首次投产<br><span class="dim">5档按第N日解锁</span>',
  '<b>送达层形式生效</b>——290 人买（渗透 16.5% 全场第二）、复购 2.8 单，低价宽入口的作用被验证；⚠️终奖机制事故（买齐者 0 领取、83 人补偿）是执行问题不是形式问题',
  f"{fmt(dm['每日礼包']['rev'])} · {dm['每日礼包']['buyers']}人 · 复购 {dm['每日礼包']['opb']:.1f}单", 'ok'),
 ('D6', '节日周卡新增<br><span class="dim">4档 · 被客户端包拖到 7/9 晚 6 天开卖</span>',
  '<b>形式未获公平验证</b>——只卖 7 天收 $2.3k / 65 人（渗透 3.7%），按日均估晚开损失约 $1.4k（近乎腰斩）；结论=下届让周卡脱离客户端包依赖再验一次',
  f"{fmt(dm['节日周卡']['rev'])} · {dm['节日周卡']['buyers']}人 · max {fmt(dm['节日周卡']['max'])}", 'mid'),
 ('D7', '存钱罐 280001',
  '一次性买断型——145 人买、复购 1.0，$19.99 单价顶格即天花板，中规中矩的送达层补充',
  f"{fmt(dm['存钱罐']['rev'])} · {dm['存钱罐']['buyers']}人", 'ok'),
 ('D8', '兑换商店删随机折扣券',
  '无对照组（没有保留折扣券的平行深海），对兑换节奏的影响不可测——不下结论',
  '—', 'wait'),
 ('D9', '珍珠贝进度系统（免费进度钩）',
  '免费钩无付费流水，对转盘参与的拉动需查活动参与数据——待查',
  '—', 'wait'),
]
# W1 效果句里的格式化占位
WC_ROWS[0] = (*WC_ROWS[0][:2], WC_ROWS[0][2].format(fmt(wm['竞猜礼包全档']['rev']), wm['竞猜礼包全档']['buyers']), *WC_ROWS[0][3:])
WC_ROWS[2] = (*WC_ROWS[2][:2], WC_ROWS[2][2].format(fmt(wm['竞猜$9.99框档(尾2)']['rev'] + wm['竞猜$19.99表情档(尾3)']['rev'])), *WC_ROWS[2][3:])

N_OK = sum(1 for r in WC_ROWS+DS_ROWS if r[4]=='ok')
N_BAD = sum(1 for r in WC_ROWS+DS_ROWS if r[4]=='bad')
N_MID = sum(1 for r in WC_ROWS+DS_ROWS if r[4]=='mid')
N_WAIT = sum(1 for r in WC_ROWS+DS_ROWS if r[4]=='wait')

# ============ 模块收入底图 ============
COLB = {'ok':'#2ea856','bad':'#f85149','mid':'#d29922','wait':'#484f58'}
def module_bar(mods, order, W=1160):
    rows = [(k, mods[k]) for k in order if k in mods]
    L_, R_, RH, GAP, T_ = 240, 190, 30, 10, 14
    H = T_ + len(rows)*(RH+GAP) + 10
    vmax = max(m['rev'] for _, m in rows) * 1.05 or 1
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for ri, (k, m) in enumerate(rows):
        y = T_ + ri*(RH+GAP)
        w = (W-L_-R_) * m['rev']/vmax
        s.append(f'<text x="{L_-10}" y="{y+RH/2+4}" fill="#c9d1d9" font-size="11.5" font-weight="600" text-anchor="end">{k}</text>')
        s.append(f'<rect x="{L_}" y="{y}" width="{max(2,w):.1f}" height="{RH}" fill="#4691e8" fill-opacity="0.85" rx="3">'
                 f'<title>{k} {fmt(m["rev"])} · 买家{m["buyers"]} · 渗透{m["payrate"]:.1f}% · ARPPU ${m["arppu"]:.0f} · 复购{m["opb"]:.1f}单 · max{fmt(m["max"])}</title></rect>')
        s.append(f'<text x="{L_+max(2,w)+8:.1f}" y="{y+RH/2+4}" fill="#f0f6fc" font-size="11" font-weight="700">{fmt(m["rev"])}'
                 f'<tspan fill="#8b949e" font-weight="400" font-size="10">　{m["buyers"]}人 · 复购{m["opb"]:.1f} · max{fmt(m["max"])}</tspan></text>')
    s.append('</svg>')
    return ''.join(s)

def round_bar():
    W, L_, R_, T_, B_ = 560, 60, 20, 36, 40
    PH = 150
    items = [(k, v['rev']/max(1,(datetime.date.fromisoformat(v['win'][11:]) - datetime.date.fromisoformat(v['win'][:10])).days+1)) for k, v in RD.items()]
    vmax = max(v for _, v in items)*1.15
    bw = (W-L_-R_)/len(items)
    s = [f'<svg viewBox="0 0 {W} {T_+PH+B_}" style="width:min(560px,100%);background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    s.append(f'<text x="{L_}" y="{T_-14}" fill="#f0f6fc" font-size="12" font-weight="700">竞猜付费档 · 日均（按轮）</text>')
    for i, (k, v) in enumerate(items):
        x = L_ + i*bw + 10
        h = PH*v/vmax
        y = T_ + PH - h
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-20:.1f}" height="{h:.1f}" fill="#c08a17" rx="4"><title>{k} 付费档合计 {fmt(RD[k]["rev"])}（{RD[k]["win"]}）</title></rect>')
        s.append(f'<text x="{x+(bw-20)/2:.1f}" y="{y-6:.1f}" fill="#f0f6fc" font-size="11" font-weight="700" text-anchor="middle">${v:,.0f}/日</text>')
        s.append(f'<text x="{x+(bw-20)/2:.1f}" y="{T_+PH+16}" fill="#8b949e" font-size="10.5" text-anchor="middle">{k}</text>')
    s.append('</svg>')
    return ''.join(s)

def table(rows):
    tr = []
    for num, chg, eff, dat, v in rows:
        lab, cls = BADGE[v]
        badge = f'<span class="kpi-badge {cls if cls!="wait" else "mid"}" style="{"background:#21262d;color:#8b949e" if v=="wait" else ""}">{lab}</span>'
        tr.append(f'<tr><td style="width:34px;color:#8b949e;font-weight:700">{num}</td>'
                  f'<td class="l" style="width:250px">{chg}</td><td class="l">{eff}</td>'
                  f'<td class="l" style="width:225px;color:#8b949e;font-size:11px">{dat}</td>'
                  f'<td style="width:86px">{badge}</td></tr>')
    return ('<table><tr><th>#</th><th class="l">改动</th><th class="l">一句话效果</th><th class="l">关键数据</th><th>判定</th></tr>'
            + ''.join(tr) + '</table>')

WC_ORDER = ['开箱福箱连锁','通行证(130020/21)','竞猜礼包全档','开箱券锚点(可复购)']

# ============ 世界杯模块全景 vs 类型预期 ============
def pano_row(name, m, bench, judge, badge, money=True):
    if money:
        cells = (f"<td>{fmt(m['rev'])}</td><td>{m['buyers']:,}<span class='dim'>（{m.get('payrate',0):.1f}%）</span></td>"
                 f"<td>${m['arppu']:.0f}</td><td>{m['opb']:.1f}</td><td>{fmt(m['max'])}</td>")
    else:
        cells = f"<td colspan=5 class='l' style='color:#8b949e'>{m}</td>"
    lab, cls = badge
    bstyle = "background:#21262d;color:#8b949e" if cls == "wait" else ""
    return (f"<tr><td class='l' style='width:190px'><b>{name}</b></td>{cells}"
            f"<td class='l' style='width:250px;color:#8b949e;font-size:11px'>{bench}</td>"
            f"<td class='l' style='width:265px'>{judge}　<span class='kpi-badge {cls if cls!='wait' else 'mid'}' style='{bstyle}'>{lab}</span></td></tr>")

# ============ 世界杯开箱效果分析（三代对打）============
def kx_table():
    gens = [('情人节开箱', G_VT, '2/6-2/16 · 55服'), ('夏日开箱', G_SM, '5/29-6/8 · 88服'), ('世界杯开箱', G_WC, f'6/26-{END[5:]} · 全服')]
    tr = ['<table><tr><th class="l">代际（各自窗口·服段）</th><th>收入</th><th>买家</th><th>付费玩家付费率*</th><th>ARPPU</th><th>复购</th><th>p50</th><th>p90</th><th>$100+占比</th><th>$500+占比</th><th>max</th><th>锚点买家(占比)</th></tr>']
    for name, g, meta in gens:
        m = g['合并']; a = g['锚点']; pr = KG[name]['payrate']
        hl = ' class="row-a"' if '世界杯' in name else ''
        tr.append(f"<tr{hl}><td class='l'><b>{name}</b><span class='dim'>　{meta}</span></td>"
                  f"<td>{fmt(m['rev'])}</td><td>{m['buyers']}</td><td>{pr:.1f}%<span class='dim'>／{KG[name]['total_payers']:,}</span></td>"
                  f"<td>${m['arppu']:.0f}</td><td>{m['opb']:.1f}</td>"
                  f"<td>${m['p50']:.0f}</td><td>${m['p90']:.0f}</td><td>{m['over100']:.1f}%</td><td>{m['over500']:.1f}%</td>"
                  f"<td><b>{fmt(m['max'])}</b></td><td>{a['buyers']}人（{a['buyers']/m['buyers']*100:.0f}%）</td></tr>")
    tr.append('</table>')
    tr.append("<div class='dim' style='margin-top:6px'>*付费玩家付费率 = 开箱买家 ÷ 有开箱流水的服上同窗总付费人数（分母随部署面变化：情人 3,540 / 夏日 1,205 / 世界杯 4,047——夏日 20.3% 偏高主因是分母面窄，跨代比较看买家数与 ARPPU 更稳）</div>")
    return ''.join(tr)

# ---- ① 转化率双图（分段等宽桶+双图定式）----
def kx_dist_chart(bucket_key, buckets_n, bucket_w, xlab_fn, tail_lab, title):
    W, H, L, R, T, B = 1160, 330, 52, 16, 30, 62
    pw, ph = W-L-R, H-T-B
    cols = buckets_n + 1
    series = []
    for gen in ['元旦开箱','情人节开箱','夏日开箱','世界杯开箱']:
        g = KG[gen]; total = g['buyers']
        bk = {int(k): v for k, v in g[bucket_key].items()}
        vals = [bk.get(i, 0)/total*100 for i in (range(buckets_n) if bucket_key=='bucketA' else range(1, buckets_n+1))]
        vals.append(bk.get(buckets_n if bucket_key=='bucketA' else 20, 0)/total*100)
        series.append((gen, vals))
    vmax = max(max(v) for _, v in series)*1.12
    def X(i): return L + pw*(i+0.5)/cols
    def Y(v): return T + ph*(1-v/vmax)
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    step = max(2, int(vmax//5))
    for gv in range(0, int(vmax)+1, step):
        s.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W-R}" y2="{Y(gv):.1f}" stroke="{COLB.get("grid","#21262d") if False else "#21262d"}"/>')
        s.append(f'<text x="{L-6}" y="{Y(gv)+4:.1f}" fill="#484f58" font-size="10" text-anchor="end">{gv}%</text>')
    for i in range(cols):
        if cols > 15 and i % 2 == 1 and i < buckets_n:
            continue
        lab = xlab_fn(i) if i < buckets_n else tail_lab
        s.append(f'<text x="{X(i):.1f}" y="{H-46}" fill="#8b949e" font-size="9" text-anchor="middle">{lab}</text>')
    for gen, vals in series:
        c = GEN_COL[gen]; wgt = 2.6 if gen == '世界杯开箱' else 1.6
        pts = ' L '.join(f'{X(i):.1f} {Y(v):.1f}' for i, v in enumerate(vals))
        s.append(f'<path d="M {X(0):.1f} {Y(0):.1f} L {pts} L {X(cols-1):.1f} {Y(0):.1f} Z" fill="{c}" fill-opacity="0.12"/>')
        s.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.4" fill="{c}"><title>{gen} {xlab_fn(i) if i<buckets_n else tail_lab}: {v:.1f}% 买家</title></circle>')
    lx = L
    for gen in ['元旦开箱','情人节开箱','夏日开箱','世界杯开箱']:
        g = KG[gen]
        lab = f"{gen}（{g['buyers']}人·max{fmt(g['max'])}）"
        s.append(f'<line x1="{lx}" y1="{H-22}" x2="{lx+18}" y2="{H-22}" stroke="{GEN_COL[gen]}" stroke-width="2.4"/>')
        s.append(f'<text x="{lx+23}" y="{H-18}" fill="#c9d1d9" font-size="10.5">{lab}</text>')
        lx += 23 + len(lab)*10 + 22
    s.append(f'<text x="{L}" y="{T-10}" fill="#f0f6fc" font-size="12" font-weight="700">{title}</text>')
    s.append('</svg>')
    return ''.join(s)

# ---- ② 分位数对比（皮肤付费效果）----
def kx_quantile_chart():
    qs = [('p50','p50'),('p75','p75'),('p90','p90'),('p95','p95'),('p99','p99')]
    W, H, L, R, T, B = 1160, 300, 52, 16, 34, 56
    pw, ph = W-L-R, H-T-B
    vmax = max(KG[g]['p99'] for g in KG)*1.15
    gw = pw/len(qs)
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for gv in range(0, int(vmax), 100):
        y = T + ph*(1-gv/vmax)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#21262d"/>')
        s.append(f'<text x="{L-6}" y="{y+4:.1f}" fill="#484f58" font-size="10" text-anchor="end">${gv}</text>')
    gens4 = ['元旦开箱','情人节开箱','夏日开箱','世界杯开箱']
    bw = (gw-24)/4
    for qi, (lab, key) in enumerate(qs):
        ox = L + qi*gw + 12
        for gi, gen in enumerate(gens4):
            v = KG[gen][key]
            x = ox + gi*bw
            y = T + ph*(1-v/vmax)
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-4:.1f}" height="{T+ph-y:.1f}" fill="{GEN_COL[gen]}" rx="3"><title>{gen} {lab} ${v:,.0f}</title></rect>')
            if qi >= 3:
                s.append(f'<text x="{x+(bw-4)/2:.1f}" y="{y-4:.1f}" fill="#c9d1d9" font-size="9" text-anchor="middle">${v:,.0f}</text>')
        s.append(f'<text x="{ox+(bw*4)/2:.1f}" y="{H-38}" fill="#8b949e" font-size="11" font-weight="600" text-anchor="middle">{lab}</text>')
    lx = L
    for gen in gens4:
        s.append(f'<rect x="{lx}" y="{H-24}" width="11" height="11" fill="{GEN_COL[gen]}" rx="2"/>')
        s.append(f'<text x="{lx+16}" y="{H-15}" fill="#c9d1d9" font-size="10.5">{gen}</text>')
        lx += 16 + len(gen)*11 + 24
    s.append(f'<text x="{L}" y="{T-12}" fill="#f0f6fc" font-size="12" font-weight="700">单人付费分位数 · 四代开箱（买家口径）</text>')
    s.append('</svg>')
    return ''.join(s)

# ---- ④ 锚点礼包四代对比 ----
def anchor_card():
    gens = [('元旦锚点','纯券·无钻VIP'), ('情人节锚点','纯券·无钻VIP'), ('夏日锚点','纯券·无钻VIP'), ('世界杯锚点','✦补钻石+VIP(6/24)')]
    kx_buyers = {'元旦锚点':'元旦开箱','情人节锚点':'情人节开箱','夏日锚点':'夏日开箱','世界杯锚点':'世界杯开箱'}
    tr = ['<table><tr><th class="l">代际（无服过滤口径*）</th><th class="l">配置状态</th><th>收入</th><th>买家</th><th>占开箱买家</th><th>ARPPU</th><th>复购</th><th>max</th></tr>']
    for name, cfg in gens:
        a = AN[name]; kb = KG[kx_buyers[name]]['buyers']
        hl = ' class="row-a"' if '世界杯' in name else ''
        tr.append(f"<tr{hl}><td class='l'><b>{name}</b></td><td class='l'>{cfg}</td><td>{fmt(a['rev'])}</td><td>{a['buyers']}</td>"
                  f"<td>{a['buyers']/kb*100:.0f}%</td><td>${a['arppu']:.1f}</td><td>{a['opb']:.1f}</td><td>{fmt(a['max'])}</td></tr>")
    tr.append('</table>')
    tr.append('<div style="height:10px"></div><table><tr><th class="l">世界杯锚点按档</th><th>收入</th><th>买家</th><th>ARPPU</th><th>复购</th><th>max</th></tr>')
    for t in ['WC档$4.99','WC档$19.99','WC档$49.99','WC档$99.99']:
        a = AN[t]
        tr.append(f"<tr><td class='l'><b>{t.replace('WC档','')}</b></td><td>{fmt(a['rev'])}</td><td>{a['buyers']}</td><td>${a['arppu']:.1f}</td><td>{a['opb']:.1f}</td><td>{fmt(a['max'])}</td></tr>")
    tr.append('</table>')
    tr.append("<div class='dim' style='margin-top:6px'>*本卡四代统一不加服过滤（各代全部部署服），与上方历史数据对比表（按服段筛选）绝对值不同；占开箱买家分母=同口径开箱族买家。</div>")
    return ''.join(tr)

# ---- 竞猜整体：参与逐日 + 按轮参与vs付费 + 档位结构 ----
ROUND_BANDS = [('R32','2026-06-26','2026-07-02','#4691e8'), ('R16','2026-07-03','2026-07-08','#2ea856'),
               ('QF','2026-07-09','2026-07-12','#c08a17'), ('SF','2026-07-13','2026-07-15','#bc6bd9')]
def jc_daily_chart():
    import datetime as _dt
    d0 = _dt.date(2026,6,26); dN = _dt.date.fromisoformat(END)
    ds = [(d0 + _dt.timedelta(days=i)).isoformat() for i in range((dN-d0).days+1)]
    vals = [JC['daily'].get(d, 0) for d in ds]
    W, H, L, R, T, B = 1160, 300, 56, 14, 40, 50
    pw, ph = W-L-R, H-T-B
    n = len(ds); bw = pw/n
    vmax = max(vals)*1.12
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for a, b_, c in [(x[1], x[2], x[3]) for x in ROUND_BANDS]:
        i0 = ds.index(a) if a in ds else 0; i1 = ds.index(b_) if b_ in ds else n-1
        s.append(f'<rect x="{L+i0*bw:.1f}" y="{T}" width="{(i1-i0+1)*bw:.1f}" height="{ph}" fill="{c}" fill-opacity="0.07"/>')
    for lab, a, b_, c in ROUND_BANDS:
        i0 = ds.index(a) if a in ds else 0; i1 = ds.index(b_) if b_ in ds else n-1
        s.append(f'<text x="{L+(i0+(i1-i0+1)/2)*bw:.1f}" y="{T-8}" fill="{c}" font-size="11" font-weight="700" text-anchor="middle">{lab}·参与 {JC["rounds"][lab]["users"]:,} 人</text>')
    for gv in range(0, int(vmax)+1, 2000):
        y = T + ph*(1-gv/vmax)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#21262d"/>')
        s.append(f'<text x="{L-6}" y="{y+4:.1f}" fill="#484f58" font-size="10" text-anchor="end">{gv//1000}k</text>')
    for i, (d, v) in enumerate(zip(ds, vals)):
        if v <= 0: continue
        x = L + i*bw + 2; hgt = ph*v/vmax
        s.append(f'<rect x="{x:.1f}" y="{T+ph-hgt:.1f}" width="{bw-4:.1f}" height="{hgt:.1f}" fill="#c08a17" fill-opacity="0.85" rx="2"><title>{d} 参与 {v:,} 人</title></rect>')
    for i, d in enumerate(ds):
        if i % 2 == 0:
            s.append(f'<text x="{L+(i+0.5)*bw:.1f}" y="{H-32}" fill="#8b949e" font-size="9" text-anchor="middle">{d[5:]}</text>')
    s.append(f'<text x="{L}" y="{H-12}" fill="#484f58" font-size="10">日参与=当日有竞猜礼包领取/下注记录的去重人数（asset 894% 口径）· 峰谷随比赛日</text>')
    s.append('</svg>')
    return ''.join(s)

def jc_rounds_chart():
    import datetime as _dt
    W, PW, PH, T, B, L = 1160, 560, 170, 40, 44, 64
    s = [f'<svg viewBox="0 0 {W} {T+PH+B}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    panels = [
      ('按轮参与人数（稳中有升 · 不随缩圈衰减）', [(lab, JC['rounds'][lab]['users'], c) for lab, _, __, c in ROUND_BANDS], '{:,}'),
      ('按轮付费日均（逐轮衰减）', [(lab, RD[lab]['rev']/max(1,(_dt.date.fromisoformat(RD[lab]['win'][11:])-_dt.date.fromisoformat(RD[lab]['win'][:10])).days+1), c) for lab, _, __, c in ROUND_BANDS], '${:,.0f}/日'),
    ]
    for pi, (title, items, fv) in enumerate(panels):
        ox = pi*(PW+30)
        vmax = max(v for _, v, _ in items)*1.18
        bw = (PW-L-10)/4
        s.append(f'<text x="{ox+L}" y="{T-14}" fill="#f0f6fc" font-size="12" font-weight="700">{title}</text>')
        for gi, (lab, v, c) in enumerate(items):
            x = ox + L + gi*bw + 8
            y = T + PH*(1-v/vmax)
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-16:.1f}" height="{T+PH-y:.1f}" fill="{c}" rx="4"><title>{lab} {fv.format(v)}</title></rect>')
            s.append(f'<text x="{x+(bw-16)/2:.1f}" y="{y-6:.1f}" fill="#f0f6fc" font-size="11" font-weight="700" text-anchor="middle">{fv.format(v)}</text>')
            s.append(f'<text x="{x+(bw-16)/2:.1f}" y="{T+PH+16}" fill="#8b949e" font-size="10.5" text-anchor="middle">{lab}</text>')
    s.append(f'<text x="{L}" y="{T+PH+36}" fill="#484f58" font-size="10">SF 在途（{JC["rounds"]["SF"]["win"]}）· 付费=竞猜894礼包订单 · 参与=asset 894% 去重</text>')
    s.append('</svg>')
    return ''.join(s)

T20 = json.load(open(os.path.join(HERE, '_kx_top20.json'), encoding='utf-8'))       # 开箱Top20阶梯

def kx_top20_chart():
    """Top20 付费额度阶梯：夏日老服 vs 世界杯老服 vs 世界杯全服"""
    series = [('夏日·老服', [v['tot'] for v in T20['夏日_老服top20']], '#2ea856'),
              ('世界杯·老服', [v['tot'] for v in T20['世界杯_老服top20']], '#c08a17'),
              ('世界杯·全服', [v['tot'] for v in T20['世界杯_全服top20']], '#8b949e'),
              ('深海·转盘族', [v['tot'] for v in T20['深海_转盘top20']], '#4691e8')]
    W, H, L, R, T, B = 1160, 300, 56, 16, 34, 54
    pw, ph = W-L-R, H-T-B
    vmax = max(max(v) for _, v, _ in series)*1.1
    def X(i): return L + pw*i/19
    def Y(v): return T + ph*(1-v/vmax)
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for gv in range(0, int(vmax), 250):
        s.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W-R}" y2="{Y(gv):.1f}" stroke="#21262d"/>')
        s.append(f'<text x="{L-6}" y="{Y(gv)+4:.1f}" fill="#484f58" font-size="10" text-anchor="end">${gv}</text>')
    for i in range(20):
        s.append(f'<text x="{X(i):.1f}" y="{H-36}" fill="#8b949e" font-size="9.5" text-anchor="middle">{i+1}</text>')
    s.append(f'<text x="{L+pw/2:.1f}" y="{H-20}" fill="#8b949e" font-size="10.5" text-anchor="middle">开箱付费额排名（第1~20名）</text>')
    for nm, vals, c in series:
        wgt = 2.4 if '世界杯·老服' in nm else 1.7
        pts = ' L '.join(f'{X(i):.1f} {Y(v):.1f}' for i, v in enumerate(vals))
        s.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3" fill="{c}"><title>{nm} 第{i+1}名 ${v:,.0f}</title></circle>')
    lx = L
    for nm, vals, c in series:
        lab = f"{nm}（top20合计 ${sum(vals):,.0f}）"
        s.append(f'<line x1="{lx}" y1="{T-14}" x2="{lx+18}" y2="{T-14}" stroke="{c}" stroke-width="2.4"/>')
        s.append(f'<text x="{lx+23}" y="{T-10}" fill="#c9d1d9" font-size="10.5">{lab}</text>')
        lx += 23 + len(lab)*10.5 + 26
    s.append('</svg>')
    return ''.join(s)

A64 = json.load(open(os.path.join(HERE, '_top20_assets.json'), encoding='utf-8'))    # 核心投放缩略图

def top20_notes():
    """Top20 各代核心投放注释条（带图）"""
    cards = [
      ('#2ea856', '夏日/情人开箱 · 核心投放', None,
       '<b>无外显大奖</b>——奖池顶配=传奇技能书/玫瑰花瓣（配置实证：组113无超级大奖行），纯养成向奖池。渗透 20.1% 靠的是券稀缺，不是大奖吸引力。'),
      ('#c08a17', '世界杯开箱 · 超级大奖', A64['soccer'],
       '<b>足球宝贝·爱莉希雅皮肤 5304001</b>（首个挂皮肤超级大奖的开箱）——中层没被拉动（$100-500 占比反降），钩子在、坑位浅。'),
      ('#c08a17', '世界杯跨服榜 1-5 名 · 头衔', A64['title'],
       '<b>世界之巅头衔 82004</b>（组30581-84）——点燃塔尖 $1,415/$1,330 两人=头衔竞争付费力的直接证据；第 3 名起回落，缺向下分层。'),
      ('#4691e8', '深海转盘 · 核心大奖', A64['sub'],
       '<b>深海猎手·潜艇行军皮 15065</b>（奖池组321超级大奖）——外显钩子在，但逐档限购 $585 买光墙把深度锁死，Top3 齐顶封顶值。'),
    ]
    h = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px">']
    for c, t, img, txt in cards:
        imghtml = (f'<img src="{img}" style="height:96px;max-width:100%;object-fit:contain;border-radius:4px;display:block;margin:0 auto 8px">'
                   if img else '<div style="height:96px;display:flex;align-items:center;justify-content:center;color:#484f58;font-size:22px;margin-bottom:8px">—</div>')
        h.append(f'<div style="background:#0d1117;border:1px solid #30363d;border-top:3px solid {c};border-radius:6px;padding:12px">'
                 f'<div style="font-size:10.5px;font-weight:700;color:{c};letter-spacing:.5px;margin-bottom:8px">{t}</div>'
                 f'{imghtml}<div style="font-size:11px;line-height:1.7;color:#8b949e">{txt}</div></div>')
    h.append('</div>')
    return ''.join(h)

def payrate_drill():
    """开箱付费率下钻：同服段对齐 + 券供给对比 + 档位买家梯子"""
    ps_rev = {'夏日': {r['sid']: r for r in PS['夏日开箱']}, '世界杯': {r['sid']: r for r in PS['世界杯开箱']}}
    def agg(label, lo, hi):
        P = PR[f"{label}_payers"]; K = PR[f"{label}_kxbuyers"]; RV = ps_rev[label]
        pay = sum(v for k, v in P.items() if lo <= int(k) <= hi)
        kb = sum(v for k, v in K.items() if lo <= int(k) <= hi)
        rev = sum(r['rev'] for sid, r in RV.items() if lo <= int(sid) <= hi)
        return dict(kb=kb, pay=pay, pr=kb/pay*100 if pay else 0, rev=rev, arppu=rev/kb if kb else 0)
    rows_a = [('夏日 · 老服成熟段 1000-1870（同段基准）', agg('夏日', 1000, 1870), '#2ea856'),
              ('世界杯 · 老服成熟段 1000-1870', agg('世界杯', 1000, 1870), '#c08a17'),
              ('世界杯 · 年轻老服 1880-1970', agg('世界杯', 1880, 1970), '#c08a17'),
              ('世界杯 · 扩服新服 1980-2250', agg('世界杯', 1980, 2250), '#c08a17')]
    t = ['<table><tr><th class="l">新老服拆分（同段对齐）</th><th>收入</th><th>开箱买家</th><th>该段总付费人数</th><th>付费玩家付费率</th><th>ARPPU</th></tr>']
    for name, m, c in rows_a:
        hl = ' class="row-a"' if '世界杯 · 老服成熟段' in name else ''
        bar = f'<div style="height:8px;width:{m["pr"]*10:.0f}px;max-width:220px;background:{c};border-radius:4px;display:inline-block;margin-right:8px;vertical-align:middle"></div>'
        t.append(f"<tr{hl}><td class='l'><b>{name}</b></td><td>{fmt(m['rev'])}</td><td>{m['kb']}</td><td>{m['pay']:,}</td>"
                 f"<td class='l'>{bar}<b>{m['pr']:.1f}%</b></td><td>${m['arppu']:.0f}</td></tr>")
    t.append('</table>')

    _tsrc = json.load(open(os.path.join(HERE, '_ticket_sources.json'), encoding='utf-8'))
    _free = next(x for x in _tsrc if x['src'] == '免费竞猜档')
    wc_free = int(float(_free['qty'])); wc_free_u = _free['u']
    sm_u, sm_q = TKS['summer_total']['u'], TKS['summer_total']['qty']
    wc_u, wc_q = TKS['wc_total']['u'], float(TKS['wc_total']['qty'])
    t.append('<div style="height:12px"></div><table><tr><th class="l">开箱券供给对比（获取侧 asset 全量）</th><th>券触达人数</th><th>总发放量</th><th>人均</th></tr>')
    t.append(f"<tr><td class='l'><b>夏日券 1134</b>（无大众免费水管）</td><td>{sm_u:,}</td><td>{sm_q:,.0f}</td><td>{sm_q/sm_u:.0f} 张</td></tr>")
    t.append(f"<tr class='row-a'><td class='l'><b>世界杯券 1146</b>（竞猜免费档+中奖邮件两条大水管）</td><td>{wc_u:,}<span class='dim'>（×{wc_u/sm_u:.1f}）</span></td><td>{wc_q:,.0f}<span class='dim'>（×{wc_q/sm_q:.1f}）</span></td><td>{wc_q/wc_u:.0f} 张</td></tr>")
    t.append(f"<tr><td class='l'>└ 其中：竞猜免费档直发</td><td>{wc_free_u:,}</td><td>{wc_free:,}</td><td class='dim'>另有中奖邮件加送（百万级）</td></tr>")
    t.append('</table>')

    sm_t = {x['iap']: x['buyers'] for x in PR['夏日_tiers']}
    wc_t = {x['iap']: x['buyers'] for x in PR['世界杯_tiers']}
    t.append('<div style="height:12px"></div><table><tr><th class="l">档位买家梯子（连锁5档 + 锚点首档）</th><th>$4.99</th><th>$9.99</th><th>$19.99</th><th>$49.99</th><th>$99.99</th><th>锚点$4.99</th></tr>')
    t.append(f"<tr><td class='l'><b>夏日</b></td><td><b>{sm_t.get('210702',0)}</b></td><td>{sm_t.get('210704',0)}</td><td>{sm_t.get('210706',0)}</td><td>{sm_t.get('210708',0)}</td><td>{sm_t.get('210710',0)}</td><td>{sm_t.get('210712',0)}</td></tr>")
    t.append(f"<tr><td class='l'><b>世界杯（全服）</b></td><td><b>{wc_t.get('211002',0)}</b></td><td>{wc_t.get('211004',0)}</td><td>{wc_t.get('211006',0)}</td><td>{wc_t.get('211008',0)}</td><td>{wc_t.get('211010',0)}</td><td>{wc_t.get('211012',0)}</td></tr>")
    t.append('</table>')
    return ''.join(t)

JSRV = json.load(open(os.path.join(HERE, '_jingcai_srv.json'), encoding='utf-8'))   # 竞猜逐服(付费+参与)

def jc_srv_table():
    """竞猜新老服拆分：参与/转化/付费率/ARPPU 按服段"""
    P = PR['世界杯_payers']
    segs = [('老服成熟段 1000-1870', 1000, 1870), ('年轻老服 1880-1970', 1880, 1970), ('扩服新服 1980-2250', 1980, 2250)]
    t = ['<table><tr><th class="l">服段</th><th>参与人数</th><th>付费买家</th><th>参与→付费转化</th><th>收入</th><th>该段总付费人数</th><th>付费玩家付费率</th><th>ARPPU</th></tr>']
    for name, lo, hi in segs:
        part = sum(v for k, v in JSRV['part'].items() if lo <= int(k) <= hi)
        b = sum(v['b'] for k, v in JSRV['pay'].items() if lo <= int(k) <= hi)
        rev = sum(v['rev'] for k, v in JSRV['pay'].items() if lo <= int(k) <= hi)
        pay = sum(v for k, v in P.items() if lo <= int(k) <= hi)
        t.append(f"<tr><td class='l'><b>{name}</b></td><td>{part:,}<span class='dim'>（{part/CANYU*100:.0f}%）</span></td><td>{b}</td>"
                 f"<td>{b/part*100 if part else 0:.1f}%</td><td>{fmt(rev)}</td><td>{pay:,}</td>"
                 f"<td>{b/pay*100 if pay else 0:.1f}%</td><td>${rev/b if b else 0:.0f}</td></tr>")
    t.append('</table>')
    return ''.join(t)

def _pay_rows(rows):
    """通用付费指标表体: rows=[(name, 高亮, m, opb覆盖)]"""
    tr = ['<table><tr><th class="l">模块</th><th>收入</th><th>买家</th><th>付费玩家付费率*</th><th>付费玩家ARPU*</th><th>ARPPU</th><th>复购</th><th>p50</th><th>p90</th><th>$100+占比</th><th>$500+占比</th><th>max</th></tr>']
    for name, hl, m, opb_override in rows:
        opb = opb_override if opb_override is not None else (m.get('orders', 0)/m['buyers'] if m['buyers'] else 0)
        cls = ' class="row-a"' if hl else ''
        tr.append(f"<tr{cls}><td class='l'><b>{name}</b></td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td>"
                  f"<td>{m['payrate']:.1f}%<span class='dim'>／{m['total_payers']:,}</span></td>"
                  f"<td>${m['rev']/m['total_payers']:.2f}</td>"
                  f"<td>${m['rev']/m['buyers']:.0f}</td><td>{opb:.1f}</td><td>${m['p50']:.0f}</td><td>${m['p90']:.0f}</td>"
                  f"<td>{m['over100']:.1f}%</td><td>{m['over500']:.1f}%</td><td>{fmt(m['max'])}</td></tr>")
    tr.append('</table>')
    return tr

def jc_pay_table_old():
    """对比表：世界杯三模块·老服段 1000-1870 + 夏日开箱（同段跨窗）"""
    s, sm = KG['夏日开箱'], G_SM['合并']
    rows = [
      ('<span class="wcb">世界杯·老服段</span>竞猜（894全档）', True, JPO['竞猜894全档'], None),
      ('<span class="wcb">世界杯·老服段</span>参照 · 世界杯开箱', False, JPO['世界杯开箱'], None),
      ('<span class="wcb">世界杯·老服段</span>参照 · 通行证 130020/21', False, JPO['通行证'], None),
      ('跨窗参照 · 夏日开箱<span class="dim">（上一代同形式 · 连锁+锚点纯开箱 · 不含通行证）</span>', False,
       dict(rev=sm['rev'], buyers=sm['buyers'], payrate=s['payrate'], total_payers=s['total_payers'],
            p50=sm['p50'], p90=sm['p90'], over100=sm['over100'], over500=sm['over500'], max=sm['max']), sm['opb']),
    ]
    tr = _pay_rows(rows)
    tr.append(f"<div class='dim' style='margin-top:6px'>*口径：世界杯三模块限老服段 server 1000-1870（=夏日开箱部署段），付费率分母=该模块有流水的老服段服上同窗总付费人数（竞猜 {JPO['竞猜894全档']['total_payers']:,} / 开箱 {JPO['世界杯开箱']['total_payers']:,} / 通行证 {JPO['通行证']['total_payers']:,} / 夏日 {KG['夏日开箱']['total_payers']:,}）——同段同量级分母，跨窗直接可比；残余差异=窗口长度（世界杯 21 天 vs 夏日 11 天，长窗抬 ARPPU/复购，付费率影响小）。</div>")
    return ''.join(tr)

def jc_pay_table_all():
    """整体表：世界杯全服口径（含28扩服+年轻服）"""
    g = KG['世界杯开箱']
    kb = g['buyers']
    over100 = g['bucketA'].get('10', 0)/kb*100
    over500 = sum(v for k, v in g['bucketB'].items() if int(k) >= 5)/kb*100
    rows = [
      ('竞猜（894全档）', True, JP['竞猜894全档'], None),
      ('参照 · 世界杯开箱', False,
       dict(rev=g['rev'], buyers=kb, payrate=g['payrate'], total_payers=g['total_payers'],
            p50=g['p50'], p90=g['p90'], over100=over100, over500=over500, max=g['max']), G_WC['合并']['opb']),
      ('参照 · 通行证 130020/21', False, JP['通行证'], None),
    ]
    tr = _pay_rows(rows)
    tr.append(f"<div class='dim' style='margin-top:6px'>*全服口径（6/26-{END[5:]}，含 28 扩服+年轻服），付费率分母=有该模块流水的服上同窗总付费人数（竞猜 {JP['竞猜894全档']['total_payers']:,} / 开箱 {KG['世界杯开箱']['total_payers']:,} / 通行证 {JP['通行证']['total_payers']:,}）；付费玩家ARPU = 模块收入 ÷ 同一分母。新服白嫖盘大、付费率被稀释，与夏日（老服段部署）不可直比——对比认上面的老服段口径。</div>")
    return ''.join(tr)

def jc_tier_table():
    """档位表：含付费玩家付费率（分母=世界杯窗口全服总付费人数）与 ARPU（同分母）"""
    P = WC['payers']
    def row(name, key):
        m = wm[key]
        return (name, fmt(m['rev']), str(m['buyers']), f"{m['buyers']/P*100:.1f}%",
                f"${m['rev']/P:.2f}", f"${m['arppu']:.1f}", f"{m['opb']:.1f}", fmt(m['max']))
    g = wm['竞猜礼包全档']
    rows = [
      ('<b>竞猜整体（894全档）</b>', fmt(g['rev']), str(g['buyers']), f"<b>{g['buyers']/P*100:.1f}%</b>",
       f"${g['rev']/P:.2f}", f"${g['arppu']:.1f}", f"{g['opb']:.1f}", fmt(g['max'])),
      ('免费预测档（尾0）', '—', f"{CANYU:,} 人参与", '—', '—', '—', '—', '—'),
      row('$4.99 券档（尾1）', '竞猜$4.99档(尾1)'),
      row('$9.99 框档（尾2·外显）', '竞猜$9.99框档(尾2)'),
      row('$19.99 表情档（尾3·外显）', '竞猜$19.99表情档(尾3)'),
    ]
    STRUCT = ["—",
          "券1 + 钻 + 金币500 + 加速 + 资源袋 <span class='dim'>（参与奖）</span>",
          "券20 + 钻2500 + VIP25　<b>纯资源 · 无外显</b>",
          "券40 + 钻5000 + VIP50 + <b>荣耀之路头像框</b> <span class='dim'>（8强按国直给 / 4强自选宝箱）</span>",
          "券80 + 钻1万 + VIP100 + <b>角色助威表情</b> <span class='dim'>（8强按国直给 / 4强自选宝箱）</span>"]
    tr = ['<table><tr><th class="l">档位</th><th>收入</th><th>买家/参与</th><th>付费玩家付费率*</th><th>ARPU</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">礼包结构（奖励构成）</th></tr>']
    for i, (name, rev, b, pr, arpu, ar, op, mx) in enumerate(rows):
        hl = ' class="row-a"' if i == 0 else ''
        tr.append(f"<tr{hl}><td class='l'>{name}</td><td>{rev}</td><td>{b}</td><td>{pr}</td><td>{arpu}</td><td>{ar}</td><td>{op}</td><td>{mx}</td><td class='l' style='font-size:11px'>{STRUCT[i]}</td></tr>")
    tr.append('</table>')
    tr.append(f"<div class='dim' style='margin-top:6px'>*付费玩家付费率 = 该档买家 ÷ 世界杯窗口全服总付费人数（{P:,}）；ARPU 同分母。参考：开箱族付费率 {KX['buyers']/P*100:.1f}% · 通行证 {wm['通行证(130020/21)']['buyers']/P*100:.1f}%。</div>")
    return ''.join(tr)

def jc_form_table():
    """竞猜 vs 同期各礼包售卖形式（同窗对打·设计目的验证）"""
    PW, PD = WC['payers'], DS['payers']
    def r(form, name, m, P, hl=''):
        return (f"<tr{hl}><td class='l'><b>{form}</b></td><td class='l'>{name}</td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td>"
                f"<td>{m['buyers']/P*100:.1f}%</td><td class='y' style='font-size:13px'><b>${m['rev']/P:.2f}</b></td><td>${m['arppu']:.1f}</td>"
                f"<td>{m['opb']:.1f}</td><td>{fmt(m['max'])}</td></tr>")
    tr = ['<table><tr><th class="l">售卖形式</th><th class="l">模块</th><th>收入</th><th>买家</th><th>付费玩家付费率*</th><th>付费玩家ARPU ★</th><th>ARPPU</th><th>复购</th><th>max</th></tr>']
    P59 = JF59['payers']
    tr.append('<tr><td colspan=9 class="l" style="background:#21262d;color:#8b949e;font-size:11px">世界杯窗 6/26-' + END[5:] + f' · 深海59服段 · 分母 {P59:,}（与下方同段）</td></tr>')
    tr.append(r('竞猜下注（按国+赛果·事件绑定）', '竞猜礼包 894 全档', JF59['竞猜894全档'], P59, ' class="row-a"'))
    tr.append(r('连锁直购（逐档解锁）', '开箱福箱连锁', JF59['开箱福箱连锁'], P59))
    tr.append(r('锚点直购（道具再获取入口）', '开箱券锚点', JF59['开箱券锚点(可复购)'], P59))
    tr.append(r('BP 进度（买断+任务）', '通行证 130020/21', JF59['通行证(130020/21)'], P59))
    tr.append('<tr><td colspan=9 class="l" style="background:#21262d;color:#8b949e;font-size:11px">深海窗 7/3-' + END[5:] + f' · 59服 · 分母 {PD:,}（同一服段）</td></tr>')
    for form, key in [('按日解锁（送达层）','每日礼包'), ('玩法成就（一次性阶梯）','大富翁成就礼包'),
                      ('连锁直购（逐档解锁）','转盘连锁5档'), ('BP 进度·大富翁线','BP大富翁线(130036/37)'),
                      ('BP 进度·转盘线（转盘通行证）','BP转盘线(130035/46)'),
                      ('周卡（买断+日领）','节日周卡'), ('存钱罐（一次性买断）','存钱罐')]:
        tr.append(r(form, key, dm[key], PD))
    tr.append('</table>')
    tr.append("<div class='dim' style='margin-top:6px'>*统一深海59服段（1170-2010）：世界杯 4 形式=世界杯窗该段收入÷该段世界杯窗总付费；深海 6 形式=深海窗同段。服段已统一、残余差异只剩窗口长度（21 天 vs 14 天）。P2 对照仅走收入占比口径，见下方独立占比图。</div>")
    return ''.join(tr)

DSM = json.load(open(os.path.join(HERE, '_ds_monopoly_dist.json'), encoding='utf-8'))  # 深海大富翁分布

def ds_monopoly_chart():
    P2M = json.load(open(os.path.join(HERE, '_p2_monopoly_may.json'), encoding='utf-8'))
    TH = [10,20,50,100,200,300,500,1000]
    ds_v = [DSM['surv'][str(t)] for t in TH]
    kx_v = []
    g = KG['世界杯开箱']
    bA = {int(k): v for k, v in g['bucketA'].items()}
    bB = {int(k): v for k, v in g['bucketB'].items()}
    for t in TH:
        kx_v.append(sum(v for k, v in bA.items() if k >= t//10) if t < 100 else sum(v for k, v in bB.items() if k >= t//100))
    p2_v = [P2M['surv'][str(t)] for t in TH]
    ds_n, kx_n, p2_n = DSM['buyers'], g['buyers'], P2M['buyers']
    series = [
      (f"深海大富翁族（{ds_n}买家·max {fmt(DSM['max'])}）", [v/ds_n*100 for v in ds_v], ds_v, ds_n, '#4691e8'),
      (f"世界杯开箱（{kx_n}买家·max {fmt(g['max'])}）", [v/kx_n*100 for v in kx_v], kx_v, kx_n, '#c08a17'),
      (f"P2节日大富翁·5月拓荒窗（{p2_n:,}买家·max {fmt(P2M['max'])}）", [v/p2_n*100 for v in p2_v], p2_v, p2_n, '#8b949e'),
    ]
    W, H, L, R, T, B = 1160, 330, 64, 24, 44, 56
    pw, ph = W-L-R, H-T-B
    vmax = max(max(v) for _, v, _, _, _ in series)*1.12
    def X(i): return L + pw*i/(len(TH)-1)
    def Y(v): return T + ph*(1-v/vmax)
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁 × 开箱 × P2节日大富翁 · 花到 ≥$X 的买家占比（÷该模块全部买家）</text>')
    for gv in range(0, int(vmax)+1, 10):
        sv.append(f'<line x1="{L}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv}%</text>')
    for i, t in enumerate(TH):
        sv.append(f'<text x="{X(i):.0f}" y="{H-36}" fill="#8b949e" font-size="10.5" text-anchor="middle">≥${t:,}</text>')
    ia, ib = TH.index(50), TH.index(200)
    sv.append(f'<rect x="{X(ia):.0f}" y="{T}" width="{X(ib)-X(ia):.0f}" height="{ph}" fill="#d29922" fill-opacity="0.07"/>')
    sv.append(f'<text x="{(X(ia)+X(ib))/2:.0f}" y="{T+16}" fill="#d29922" font-size="11" font-weight="700" text-anchor="middle">中段：深海大富翁 -47%/-55%/-57% vs P2 -35%/-21%/-50%（复购位差）</text>')
    for nm, pcts, cnts, n, c in series:
        wgt = 2.4 if '深海' in nm else 1.8
        pts = ' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i, v in enumerate(pcts))
        sv.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(pcts):
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="3" fill="{c}"><title>{nm} ≥${TH[i]:,}: {v:.1f}%（{cnts[i]}人）</title></circle>')
    # 斜率标注：深海(上)与P2(下)——斜率=人数比,与占比同值
    _ds_p = [v/ds_n*100 for v in ds_v]; _p2_p = [v/p2_n*100 for v in p2_v]
    for pcts, vals, c, dy in [(_ds_p, ds_v, '#4691e8', -14), (_p2_p, p2_v, '#8b949e', 16)]:
        for i in range(len(vals)-1):
            if vals[i] <= 0: continue
            drop = (vals[i+1]/vals[i]-1)*100
            cc = '#f85149' if drop <= -60 else c
            sv.append(f'<text x="{(X(i)+X(i+1))/2:.0f}" y="{(Y(pcts[i])+Y(pcts[i+1]))/2+dy:.0f}" fill="{cc}" font-size="9.5" font-weight="600" text-anchor="middle">{drop:+.0f}%</text>')
    lx = L
    for nm, pcts, cnts, n, c in series:
        sv.append(f'<line x1="{lx}" y1="{H-16}" x2="{lx+16}" y2="{H-16}" stroke="{c}" stroke-width="2.2"/>')
        sv.append(f'<text x="{lx+21}" y="{H-12}" fill="#c9d1d9" font-size="10.5">{nm}</text>')
        lx += 21 + len(nm)*10.5 + 24
    sv.append('</svg>')
    return ''.join(sv)

def ds_decay_table():
    P2M = json.load(open(os.path.join(HERE, '_p2_monopoly_may.json'), encoding='utf-8'))
    TH = [10,20,50,100,200,300,500,1000]
    g = KG['世界杯开箱']
    bA = {int(k): v for k, v in g['bucketA'].items()}
    bB = {int(k): v for k, v in g['bucketB'].items()}
    kx_v = [(sum(v for k, v in bA.items() if k >= t//10) if t < 100 else sum(v for k, v in bB.items() if k >= t//100)) for t in TH]
    cols = {'深海大富翁族': [DSM['surv'][str(t)] for t in TH],
            '世界杯开箱': kx_v,
            'P2节日大富翁(5月)': [P2M['surv'][str(t)] for t in TH]}
    tr = ['<table style="margin-top:10px"><tr><th class="l">段</th>' + ''.join(f'<th>{k}</th>' for k in cols) + '<th class="l">参照</th></tr>']
    for i in range(len(TH)-1):
        seg = f"≥${TH[i]:,} → ≥${TH[i+1]:,}"
        cells = []
        for k, vals in cols.items():
            if vals[i] <= 0:
                cells.append('<td>—</td>'); continue
            d = (vals[i+1]/vals[i]-1)*100
            cls = ' class="r"' if d <= -60 else (' class="g"' if d >= -40 else '')
            cells.append(f'<td{cls}>{d:+.0f}%<span class="dim">（{vals[i]}→{vals[i+1]}人）</span></td>')
        ref = '自然常数带 -30~40%' if i == 0 else ''
        tr.append(f'<tr><td class="l"><b>{seg}</b></td>' + ''.join(cells) + f'<td class="l dim">{ref}</td></tr>')
    tr.append('</table>')
    tr.append('<div class="dim" style="margin-top:6px">绿=在自然常数带内（≥-40%）；红=塌方（≤-60%）；括号内为人数。</div>')
    return ''.join(tr)

# ==== 深海大富翁族 深度下钻（_monopoly_deep.json）====
MD = json.load(open(os.path.join(HERE, '_monopoly_deep.json'), encoding='utf-8'))

def dice_survival_chart():
    """进度停留曲线：累计掷骰次数≥N 的玩家数（三线：全量/白嫖/族付费）"""
    TH = [1,20,50,100,150,250,350,500,700]
    allv  = [MD['survival']['all'][str(t)] for t in TH]
    freev = [MD['survival']['free'][str(t)] for t in TH]
    payv  = [MD['survival']['payer'][str(t)] for t in TH]
    series = [
      (f"全量掷骰玩家", allv,  '#4691e8', 2.4),
      (f"白嫖玩家",     freev, '#8b949e', 1.9),
      (f"族付费玩家",   payv,  '#c08a17', 2.2),
    ]
    W,H,L,R,T,B = 1160,344,58,132,46,56
    pw,ph = W-L-R, H-T-B
    vmax = max(allv)*1.1
    def X(i): return L+pw*i/(len(TH)-1)
    def Y(v): return T+ph*(1-v/vmax)
    sv=[f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁进度停留 · 累计掷骰次数 ≥N 的玩家数（横轴=阶段奖档 抽20/50/…/700）</text>')
    for gv in range(0,int(vmax)+1,1000):
        sv.append(f'<line x1="{L}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv//1000 if gv else 0}k</text>')
    ia,ib = TH.index(350), TH.index(500)
    sv.append(f'<rect x="{X(ia):.0f}" y="{T}" width="{X(ib)-X(ia):.0f}" height="{ph}" fill="#f85149" fill-opacity="0.09"/>')
    dropf = (freev[ib]/freev[ia]-1)*100
    sv.append(f'<text x="{(X(ia)+X(ib))/2:.0f}" y="{T+15}" fill="#f85149" font-size="11" font-weight="700" text-anchor="middle">免费墙</text>')
    sv.append(f'<text x="{(X(ia)+X(ib))/2:.0f}" y="{T+30}" fill="#f85149" font-size="10" text-anchor="middle">白嫖 {freev[ia]:,}→{freev[ib]:,} ({dropf:.0f}%)</text>')
    for i,t in enumerate(TH):
        sv.append(f'<text x="{X(i):.0f}" y="{H-36}" fill="#8b949e" font-size="10.5" text-anchor="middle">≥{t}</text>')
    for nm,vals,c,wgt in series:
        pts=' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i,v in enumerate(vals))
        sv.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i,v in enumerate(vals):
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="3" fill="{c}"><title>{nm} ≥{TH[i]}次: {v:,}人</title></circle>')
    ly=T+8
    labels=[(f"全量 {MD['dice_total_players']:,}人",'#4691e8'),(f"白嫖 {MD['dice_free']:,}人",'#8b949e'),(f"族付费 {MD['dice_payers']}人",'#c08a17')]
    for nm,c in labels:
        sv.append(f'<line x1="{W-R+8}" y1="{ly}" x2="{W-R+24}" y2="{ly}" stroke="{c}" stroke-width="2.6"/>')
        sv.append(f'<text x="{W-R+28}" y="{ly+4}" fill="#c9d1d9" font-size="10">{nm}</text>')
        ly+=20
    sv.append('</svg>')
    return ''.join(sv)

def dice_decay_table():
    TH=[1,20,50,100,150,250,350,500,700]
    cols={'全量':[MD['survival']['all'][str(t)] for t in TH],
          '白嫖':[MD['survival']['free'][str(t)] for t in TH],
          '族付费':[MD['survival']['payer'][str(t)] for t in TH]}
    tr=['<table style="margin-top:10px"><tr><th class="l">档间</th>'+''.join(f'<th>{k}</th>' for k in cols)+'<th class="l">读法</th></tr>']
    notes={('350','500'):'免费骰子耗尽墙：白嫖塌方、付费不掉'}
    for i in range(len(TH)-1):
        seg=f"≥{TH[i]} → ≥{TH[i+1]}"
        cells=[]
        for k,vals in cols.items():
            d=(vals[i+1]/vals[i]-1)*100
            cls=' class="r"' if d<=-60 else (' class="g"' if d>=-40 else '')
            cells.append(f'<td{cls}>{d:+.0f}%<span class="dim">（{vals[i]:,}→{vals[i+1]:,}）</span></td>')
        note=notes.get((str(TH[i]),str(TH[i+1])),'')
        tr.append(f'<tr><td class="l"><b>{seg}</b></td>'+''.join(cells)+f'<td class="l dim">{note}</td></tr>')
    tr.append('</table>')
    tr.append(f'<div class="dim" style="margin-top:6px">分位：全量 p50={MD["dice_pct_all"]["p50"]:.0f}次 / p99={MD["dice_pct_all"]["p99"]:.0f}；族付费 p50={MD["dice_pct_payer"]["p50"]:.0f}次 / p99={MD["dice_pct_payer"]["p99"]:.0f} / max={MD["dice_pct_payer"]["mx"]:.0f}。红=塌方≤-60%，绿=常数带≥-40%。</div>')
    return ''.join(tr)

def family_dissect_card():
    order=['成就礼包','BP大富翁线','存钱罐','罗盘连锁']
    form={'成就礼包':'阶梯买断','BP大富翁线':'通行证 · 硬封顶$30','存钱罐':'单笔买断','罗盘连锁':'连锁 · 可复购'}
    comp=MD['deepsea_components']; tot=sum(comp[k]['rev'] for k in order)
    tr=['<table><tr><th class="l">族内件</th><th>收入</th><th>买家</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">付费形态</th></tr>']
    for k in order:
        m=comp[k]; hl=' class="row-a"' if k=='罗盘连锁' else ''
        tr.append(f"<tr{hl}><td class='l'><b>{k}</b></td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td><td>${m['arppu']:.1f}</td><td>{m['opb']:.1f}单</td><td>{fmt(m['max'])}</td><td class='l dim'>{form[k]}</td></tr>")
    tr.append(f"<tr><td class='l'><b>族合计</b></td><td><b>{fmt(tot)}</b></td><td class='l dim' colspan='5'>四件里三件是买断制（复购 1-2 单、硬封顶 $20-687）；唯一可复购的罗盘连锁（3.1 单/max $255）只覆盖 138 人</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def server_seg_card():
    seg=MD['server_seg']; names={'mature':'成熟老服 1170-1870','young':'年轻服 1880-2010'}
    tr=['<table><tr><th class="l">服段</th><th>大富翁族买家</th><th>收入</th><th>付费玩家付费率*</th><th>ARPPU</th></tr>']
    for s in ['mature','young']:
        m=seg[s]
        tr.append(f"<tr><td class='l'><b>{names[s]}</b></td><td>{m['buyers']}</td><td>{fmt(m['rev'])}</td><td>{m['payrate']:.1f}%<span class='dim'>（分母{m['payers']:,}）</span></td><td>${m['arppu']:.1f}</td></tr>")
    tr.append('</table>')
    tr.append('<div class="dim" style="margin-top:6px">*付费玩家付费率=该服段大富翁族买家÷该服段窗口总付费人数。两段付费率(34.2%/33.0%)与 ARPPU($44.8/$43.2)几乎完全对称=新老服通吃的稳定压舱石。</div>')
    return ''.join(tr)

def family_expansion_chart():
    months=MD['chain_by_month']; comp=MD['deepsea_components']
    ds_tot=sum(comp[k]['rev'] for k in comp)
    bars=[(m['m'][5:]+'月\n连锁', m['rev'], '#3a4150') for m in months]
    bars.append(('深海\n四件套', ds_tot, '#4691e8'))
    W,H,L,R,T,B=1160,300,56,20,64,54
    pw,ph=W-L-R,H-T-B
    vmax=max(b[1] for b in bars)*1.14
    n=len(bars); bw=pw/n*0.6
    sv=[f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁族扩张 · 老版航海之路(纯连锁 207xxx)月度 vs 深海四件套(窗口收入)</text>')
    sv.append(f'<text x="{L}" y="43" fill="#8b949e" font-size="11">连锁本身月度 $3-6k 随服基数缓涨；深海把盘子做到 {fmt(ds_tot)} 全靠新增件（成就礼包+BP大富翁线+存钱罐）</text>')
    for i,(nm,v,c) in enumerate(bars):
        x=L+pw*i/n+(pw/n-bw)/2; y=T+ph*(1-v/vmax)
        sv.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{T+ph-y:.0f}" fill="{c}" rx="3"><title>{nm} {fmt(v)}</title></rect>')
        sv.append(f'<text x="{x+bw/2:.0f}" y="{y-6:.0f}" fill="#f0f6fc" font-size="10" font-weight="700" text-anchor="middle">{fmt(v)}</text>')
        for li,seg in enumerate(nm.split("\n")):
            sv.append(f'<text x="{x+bw/2:.0f}" y="{H-32+li*13}" fill="#8b949e" font-size="9.5" text-anchor="middle">{seg}</text>')
    sv.append('</svg>')
    return ''.join(sv)

# ---- P2 春节异族大富翁 · 上限参照（_p2_monopoly_cny.json）----
P2C = json.load(open(os.path.join(HERE, '_p2_monopoly_cny.json'), encoding='utf-8'))

def p2cny_chart():
    """深海大富翁族 vs P2春节异族大富翁 vs P2五月节日大富翁 · 占比 survival（跨游戏口径）"""
    P2M = json.load(open(os.path.join(HERE, '_p2_monopoly_may.json'), encoding='utf-8'))
    TH = [10, 20, 50, 100, 200, 300, 500, 1000]
    ds_v = [DSM['surv'][str(t)] for t in TH]
    cny_v = [P2C['surv'][str(t)] for t in TH]
    may_v = [P2M['surv'][str(t)] for t in TH]
    ds_n, cny_n, may_n = DSM['buyers'], P2C['buyers'], P2M['buyers']
    series = [
      (f"深海大富翁族（{ds_n}买家·max {fmt(DSM['max'])}·14天）", [v/ds_n*100 for v in ds_v], ds_v, '#4691e8'),
      (f"P2春节异族大富翁（{cny_n:,}买家·max {fmt(P2C['max'])}·28天·固定+随机双轨）", [v/cny_n*100 for v in cny_v], cny_v, '#a371f7'),
      (f"P2节日大富翁·5月拓荒窗（{may_n:,}买家·max {fmt(P2M['max'])}·浅盘对照）", [v/may_n*100 for v in may_v], may_v, '#8b949e'),
    ]
    W, H, L, R, T, B = 1160, 340, 64, 24, 44, 72
    pw, ph = W-L-R, H-T-B
    vmax = max(max(v) for _, v, _, _ in series)*1.12
    def X(i): return L + pw*i/(len(TH)-1)
    def Y(v): return T + ph*(1-v/vmax)
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁形式的深度上限 · 花到 ≥$X 的买家占比（÷该模块全部买家）</text>')
    for gv in range(0, int(vmax)+1, 10):
        sv.append(f'<line x1="{L}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv}%</text>')
    for i, t in enumerate(TH):
        sv.append(f'<text x="{X(i):.0f}" y="{H-52}" fill="#8b949e" font-size="10.5" text-anchor="middle">≥${t:,}</text>')
    ia = TH.index(200)
    sv.append(f'<rect x="{X(ia):.0f}" y="{T}" width="{X(len(TH)-1)-X(ia):.0f}" height="{ph}" fill="#a371f7" fill-opacity="0.07"/>')
    sv.append(f'<text x="{(X(ia)+X(len(TH)-1))/2:.0f}" y="{T+16}" fill="#a371f7" font-size="11" font-weight="700" text-anchor="middle">深水区：X3 3.4%→0 vs P2春节 13.4%→3.7%（随机轨顶档人均 12.9 单撑起）</text>')
    for nm, pcts, cnts, c in series:
        wgt = 2.4 if '深海' in nm else (2.2 if '春节' in nm else 1.6)
        pts = ' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i, v in enumerate(pcts))
        sv.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(pcts):
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="3" fill="{c}"><title>{nm} ≥${TH[i]:,}: {v:.1f}%（{cnts[i]:,}人）</title></circle>')
    ly = H-30
    lx = L
    for nm, pcts, cnts, c in series:
        sv.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+16}" y2="{ly}" stroke="{c}" stroke-width="2.2"/>')
        sv.append(f'<text x="{lx+21}" y="{ly+4}" fill="#c9d1d9" font-size="10.5">{nm}</text>')
        lx += 21 + len(nm)*9.2 + 20
        if lx > W-320: lx = L; ly += 18
    sv.append('</svg>')
    return ''.join(sv)

def p2cny_decay_table():
    TH = [10, 20, 50, 100, 200, 300, 500, 1000]
    cols = {'深海大富翁族': [DSM['surv'][str(t)] for t in TH],
            'P2春节异族大富翁': [P2C['surv'][str(t)] for t in TH]}
    tr = ['<table style="margin-top:10px"><tr><th class="l">段</th>' + ''.join(f'<th>{k}</th>' for k in cols) + '<th class="l">参照</th></tr>']
    for i in range(len(TH)-1):
        seg = f"≥${TH[i]:,} → ≥${TH[i+1]:,}"
        cells = []
        for k, vals in cols.items():
            if vals[i] <= 0:
                cells.append('<td>—</td>'); continue
            d = (vals[i+1]/vals[i]-1)*100
            cls = ' class="r"' if d <= -60 else (' class="g"' if d >= -40 else '')
            cells.append(f'<td{cls}>{d:+.0f}%<span class="dim">（{vals[i]:,}→{vals[i+1]:,}人）</span></td>')
        ref = '自然常数带 -30~40%' if i == 0 else ''
        tr.append(f'<tr><td class="l"><b>{seg}</b></td>' + ''.join(cells) + f'<td class="l dim">{ref}</td></tr>')
    tr.append('</table>')
    tr.append('<div class="dim" style="margin-top:6px">绿=常数带内（≥-40%）；红=塌方（≤-60%）。P2 春节全程 -21~-39% 无一段塌方=每一段都有货架接；X3 $50 起连续塌方。</div>')
    return ''.join(tr)

def p2cny_track_card():
    cf = P2C['components']['2025异族大富翁']; cr = P2C['components']['异族大富翁随机礼包']
    def toprow(name):
        ts = [t for t in P2C['tiers'][name] if t['price'] >= 90]
        return (sum(t['buyers'] for t in ts), sum(t['orders'] for t in ts), sum(t['rev'] for t in ts))
    fb, fo, fr = toprow('2025异族大富翁'); rb, ro, rr = toprow('异族大富翁随机礼包')
    tr = ['<table><tr><th class="l">轨</th><th>收入</th><th>买家</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">档位结构要点</th></tr>']
    tr.append(f"<tr><td class='l'><b>固定轨（2025异族大富翁）</b></td><td>{fmt(cf['rev'])}</td><td>{cf['buyers']:,}</td><td>${cf['arppu']:.0f}</td><td>{cf['opb']:.1f}单</td><td>{fmt(cf['max'])}</td>"
              f"<td class='l dim'>$1.99 宽入口 ~1,150 人 → $4.99 中段复购 2.3 单 → 顶档 $99.99 {fb}人 {fo}单（{fmt(fr)}=固定轨 {fr/cf['rev']*100:.0f}%）</td></tr>")
    tr.append(f"<tr class='row-a'><td class='l'><b>随机轨（异族大富翁随机礼包）</b></td><td>{fmt(cr['rev'])}</td><td>{cr['buyers']}</td><td><b>${cr['arppu']:.0f}</b></td><td><b>{cr['opb']:.1f}单</b></td><td>{fmt(cr['max'])}</td>"
              f"<td class='l dim'>只设 $4.99-99.99 五档、无限复购；顶档 {rb}人 {ro}单（{fmt(rr)}=随机轨 {rr/cr['rev']*100:.0f}%）——12% 的买家贡献全族 48% 收入</td></tr>")
    tr.append(f"<tr><td class='l'><b>合计（28天）</b></td><td><b>{fmt(P2C['rev'])}</b></td><td>{P2C['buyers']:,}</td><td class='l dim' colspan='4'>max ${P2C['max']:,.0f}；vs X3 深海大富翁族 $26.9k/469 买家/max $792——同形式差 9 倍盘子、7 倍单人天花板</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

# ---- ③ 本服排行榜效果（逐服）----
def perserver_card():
    rows = []
    for label, win in [('世界杯开箱', f'6/26-{END[5:]}·20天拉通'), ('夏日开箱', '5/29-6/8·11天拉通')]:
        ps = PS[label]; n = len(ps)
        tot = sum(r['rev'] for r in ps); t1 = sorted(r['top1'] for r in ps)
        b = sum(r['buyers'] for r in ps)
        t1_100 = sum(1 for v in t1 if v >= 100)
        rows.append((label, win, n, tot/n, b/n, t1[n//2], max(t1), t1_100, t1_100/n*100))
    tr = ['<table><tr><th class="l">代际（拉通口径）</th><th>有开箱流水的服</th><th>服均收入</th><th>服均买家</th><th>每服top1中位</th><th>每服top1最高</th><th>top1≥$100的服</th></tr>']
    for label, win, n, avg, bavg, t1med, t1max, n100, p100 in rows:
        hl = ' class="row-a"' if '世界杯' in label else ''
        tr.append(f"<tr{hl}><td class='l'><b>{label}</b><span class='dim'>　{win}</span></td><td>{n}</td><td>{fmt(avg)}</td>"
                  f"<td>{bavg:.1f}</td><td>{fmt(t1med)}</td><td>{fmt(t1max)}</td><td>{n100}（{p100:.0f}%）</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def kx_panels():
    """四联小图：ARPPU / 买家规模 / 锚点买家占比 / max"""
    gens = [('情人', G_VT, '#8b949e'), ('夏日', G_SM, '#2ea856'), ('世界杯', G_WC, '#c08a17')]
    panels = [('ARPPU $（横盘）', lambda g: g['合并']['arppu'], '${:.0f}', 60),
              ('买家规模（受服数/窗口加持）', lambda g: g['合并']['buyers'], '{:.0f}', 420),
              ('锚点买家占开箱买家 %', lambda g: g['锚点']['buyers']/g['合并']['buyers']*100, '{:.0f}%', 50),
              ('单人最高 max $', lambda g: g['合并']['max'], '${:,.0f}', 1500)]
    PW, PH, T_, B_, L_ = 270, 190, 38, 36, 46
    W = PW*4 + 60
    s = [f'<svg viewBox="0 0 {W} {PH+T_+B_}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for pi, (title, f, fv, vmax) in enumerate(panels):
        ox = pi*(PW+20)
        s.append(f'<text x="{ox+L_}" y="{T_-14}" fill="#f0f6fc" font-size="12" font-weight="700">{title}</text>')
        bw = (PW-L_-10)/3
        for gi, (nm, g, c) in enumerate(gens):
            v = f(g)
            x = ox + L_ + gi*bw + 6
            y = T_ + PH*(1-min(1, v/vmax))
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-12:.1f}" height="{T_+PH-y:.1f}" fill="{c}" rx="4"><title>{nm} {fv.format(v)}</title></rect>')
            s.append(f'<text x="{x+(bw-12)/2:.1f}" y="{y-6:.1f}" fill="#f0f6fc" font-size="11" font-weight="700" text-anchor="middle">{fv.format(v)}</text>')
            s.append(f'<text x="{x+(bw-12)/2:.1f}" y="{T_+PH+16}" fill="#8b949e" font-size="10" text-anchor="middle">{nm}</text>')
    s.append('</svg>')
    return ''.join(s)

def wc_panorama():
    rows = [
      pano_row('开箱族（连锁+券锚点）', dict(KX, payrate=KX['buyers']/WC['payers']*100),
        '同方法基准：情人 ARPPU $54/max $555 · 夏日 $48/max $550（人均历代横盘）',
        '<b>规模与天花板超预期，人均横盘</b>——买家 387 三代最多、max $1,415 首次破墙；ARPPU $52 与前两代持平（详见 02 章）', ('部分超预期','ok')),
      pano_row('通行证 130020/21', wm['通行证(130020/21)'],
        f"同ID同型基准：夏日窗 ARPPU $24.0/max $30 · 情人窗 $28.8/max $60",
        '<b>符合预期</b>——形式没动人均持平（$28.5），渗透全场第一但天花板矮：BP 仍是渗透工具不是深度工具', ('符合预期','meet')),
      pano_row('竞猜（894全档）', dict(wm['竞猜礼包全档'], payrate=wm['竞猜礼包全档']['buyers']/WC['payers']*100),
        f"X3 无前例 · 对位 P2 猜酒杯（充值直接参与型，对位差 $14.7/付费玩家）",
        f"<b>触达超预期、变现不达预期</b>——参与 {CANYU:,} 人（付费人数的 3.2 倍）但付费转化仅 1.2%，离猜酒杯的变现形态差一个'充值即参与+排行强循环'", ('触达超/变现不达','mid')),
      pano_row('兑换商店 101339', f"消耗侧参与 {DH['users']:,} 人 · 消耗荣耀金币 {DH['amount']/10000:.0f} 万（无直接收入）",
        '消耗出口型：预期=让竞猜/开箱产出的货币有处花',
        '<b>符合预期</b>——参与出口健康，一半以上竞猜参与者进店消费', ('符合预期','meet'), money=False),
      pano_row('累充 100597 / 签到 101403', '积分驱动/免费签到，无独立收入；参与数据未查',
        '驱动型模块：预期=为付费模块导流', '待查——不影响收入总账', ('待查','wait'), money=False),
      pano_row('排行榜（跨服1005+本服1006）/ 外显投放', '框48+荣耀之路8+冠军外显+纪念卡+皮肤5304001；投放面（领取人数）未查',
        '外显进付费档的部分已在竞猜/开箱收入中体现', '待查——投放触达面留给外显专项', ('待查','wait'), money=False),
    ]
    return ('<table><tr><th class="l">模块</th><th>收入</th><th>买家（渗透）</th><th>ARPPU</th><th>复购</th><th>max</th>'
            '<th class="l">类型基准（该活动类型的预期）</th><th class="l">是否符合预期</th></tr>' + ''.join(rows) + '</table>')
DS_ORDER = ['大富翁成就礼包','BP大富翁线(130036/37)','转盘连锁5档','BP转盘线(130035/46)','每日礼包','存钱罐','大富翁罗盘连锁','拜访礼包','节日周卡','装饰礼包','许愿池','藏宝图锚点4档','头像框(深海印记)']


# ============ 竞猜页图表（表格图形化） ============
def _hbar(rows, title, fmtv, W=1040, hl_idx=None):
    """横条图: rows=[(label, value, color, sub)], hl_idx=高亮行"""
    L, R, RH, GAP, T = 300, 250, 26, 9, 40
    H = T + len(rows)*(RH+GAP) + 12
    vmax = max(v for _, v, _, _ in rows) * 1.06 or 1
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">{title}</text>')
    for ri, (lab, v, c, sub) in enumerate(rows):
        y = T + ri*(RH+GAP)
        w = (W-L-R)*v/vmax
        fw = '800' if ri == hl_idx else '600'
        fc = '#f0f6fc' if ri == hl_idx else '#c9d1d9'
        sv.append(f'<text x="{L-10}" y="{y+RH/2+4}" fill="{fc}" font-size="11.5" font-weight="{fw}" text-anchor="end">{lab}</text>')
        sv.append(f'<rect x="{L}" y="{y}" width="{max(2,w):.0f}" height="{RH}" fill="{c}" fill-opacity="{1 if ri==hl_idx else 0.8}" rx="3"><title>{lab}: {fmtv.format(v)} {sub}</title></rect>')
        sv.append(f'<text x="{L+max(2,w)+8:.0f}" y="{y+RH/2+4}" fill="#f0f6fc" font-size="11.5" font-weight="700">{fmtv.format(v)}<tspan fill="#8b949e" font-weight="400" font-size="10.5">　{sub}</tspan></text>')
    sv.append('</svg>')
    return ''.join(sv)

def _panels(panels, cats, W=1040, frame=None):
    """多联小图: panels=[(title,fmtv,vmax,[v...])], cats=[(名,色)]; frame=(起,止,标签)用虚线框住第起~止根柱（含）"""
    n = len(panels)
    PW = (W - (n-1)*18)//n
    PH, B, L = 170, 34, 46
    T = 40 if frame is None else 66
    sv = [f'<svg viewBox="0 0 {W} {PH+T+B}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for pi, (title, fmtv, vmax, vals) in enumerate(panels):
        ox = pi*(PW+18)
        sv.append(f'<text x="{ox+L}" y="{T-14 if frame is None else 22}" fill="#f0f6fc" font-size="12" font-weight="700">{title}</text>')
        bw = (PW-L-8)/len(cats)
        if frame:
            i0, i1, flab = frame
            fx = ox + L + i0*bw + 1
            fw_ = (i1-i0+1)*bw - 4
            sv.append(f'<rect x="{fx:.0f}" y="{T-24}" width="{fw_:.0f}" height="{PH+50}" fill="none" stroke="#c08a17" stroke-width="1.2" stroke-dasharray="5 4" rx="6"/>')
            if pi == 0:
                sv.append(f'<text x="{fx+2:.0f}" y="{T-30}" fill="#c08a17" font-size="10" font-weight="700">{flab}</text>')
        for ci, ((nm, c), v) in enumerate(zip(cats, vals)):
            x = ox + L + ci*bw + 5
            y = T + PH*(1-min(1, v/vmax))
            sv.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw-10:.0f}" height="{T+PH-y:.0f}" fill="{c}" rx="3"><title>{nm} {fmtv.format(v)}</title></rect>')
            sv.append(f'<text x="{x+(bw-10)/2:.0f}" y="{y-5:.0f}" fill="#f0f6fc" font-size="11" font-weight="700" text-anchor="middle">{fmtv.format(v)}</text>')
            sv.append(f'<text x="{x+(bw-10)/2:.0f}" y="{T+PH+15}" fill="#8b949e" font-size="10" text-anchor="middle">{nm}</text>')
    sv.append('</svg>')
    return ''.join(sv)

def jc_pay_chart_old():
    """对比图：世界杯三模块限老服段 1000-1870（=夏日部署段）vs 夏日开箱——同段跨窗可比"""
    s = KG['夏日开箱']
    cats = [('竞猜', '#c08a17'), ('开箱', '#4691e8'), ('通行证', '#8b949e'), ('夏日开箱', '#2ea856')]
    jq, kx, tz = JPO['竞猜894全档'], JPO['世界杯开箱'], JPO['通行证']
    return _panels([
        ('付费玩家付费率 %', '{:.1f}%', 23, [jq['payrate'], kx['payrate'], tz['payrate'], s['payrate']]),
        ('付费玩家ARPU $ ★', '${:.2f}', 11, [jq['rev']/jq['total_payers'], kx['rev']/kx['total_payers'], tz['rev']/tz['total_payers'], s['rev']/s['total_payers']]),
        ('ARPPU $', '${:.0f}', 78, [jq['rev']/jq['buyers'], kx['rev']/kx['buyers'], tz['rev']/tz['buyers'], s['rev']/s['buyers']]),
        ('复购 单/人', '{:.1f}', 7, [jq['orders']/jq['buyers'], kx['orders']/kx['buyers'], tz['orders']/tz['buyers'], G_SM['合并']['opb']]),
    ], cats, frame=(0, 2, '世界杯 · 老服段 1000-1870（6/26-' + END[5:] + '）'))

def jc_pay_chart_all():
    """整体图：世界杯全服口径（含28扩服+年轻服），看整体量级，不与夏日直比"""
    g = KG['世界杯开箱']
    cats = [('竞猜', '#c08a17'), ('开箱', '#4691e8'), ('通行证', '#8b949e')]
    jq, tz = JP['竞猜894全档'], JP['通行证']
    return _panels([
        ('付费玩家付费率 %', '{:.1f}%', 15, [jq['payrate'], g['payrate'], tz['payrate']]),
        ('付费玩家ARPU $ ★', '${:.2f}', 6, [jq['rev']/jq['total_payers'], g['rev']/g['total_payers'], tz['rev']/tz['total_payers']]),
        ('ARPPU $', '${:.0f}', 60, [jq['rev']/jq['buyers'], g['rev']/g['buyers'], tz['rev']/tz['buyers']]),
        ('复购 单/人', '{:.1f}', 9, [jq['orders']/jq['buyers'], G_WC['合并']['opb'], tz['orders']/tz['buyers']]),
    ], cats)

def jc_form_chart():
    P59, PD_ = JF59['payers'], DS['payers']
    rows = []
    for lab, m, P, c in [
        ('X3 竞猜下注（免费+加成包）', JF59['竞猜894全档'], P59, '#c08a17'),
        ('开箱连锁', JF59['开箱福箱连锁'], P59, '#c08a17'),
        ('开箱券锚点', JF59['开箱券锚点(可复购)'], P59, '#c08a17'),
        ('世界杯通行证', JF59['通行证(130020/21)'], P59, '#c08a17'),
        ('大富翁成就礼包', dm['大富翁成就礼包'], PD_, '#4691e8'),
        ('BP大富翁', dm['BP大富翁线(130036/37)'], PD_, '#4691e8'),
        ('转盘通行证', dm['BP转盘线(130035/46)'], PD_, '#4691e8'),
        ('转盘连锁', dm['转盘连锁5档'], PD_, '#4691e8'),
        ('每日礼包', dm['每日礼包'], PD_, '#4691e8'),
        ('大富翁存钱罐', dm['存钱罐'], PD_, '#4691e8'),
        ('节日周卡', dm['节日周卡'], PD_, '#4691e8'),
    ]:
        rows.append((lab, m['rev']/P, c, f"付费率 {m['buyers']/P*100:.1f}% · 复购 {m['opb']:.1f}"))
    rows.sort(key=lambda r: -r[1])
    hl = next(i for i, r in enumerate(rows) if 'X3 竞猜' in r[0])
    return _hbar(rows, '付费玩家 ARPU 排位 ★ · 统一深海59服段分母（金=世界杯窗6/26-' + END[5:] + ' / 蓝=深海窗7/3-' + END[5:] + ' · 同段可比）', '${:.2f}', hl_idx=hl)

def jc_share_chart():
    """P2 对比唯一口径：竞猜收入占同期节日总盘比例（人群属性不同，绝对值/ARPU不可跨游戏直比）"""
    P2B = json.load(open(os.path.join(HERE, '_p2_wc_bet.json'), encoding='utf-8'))
    x3_share = wm['竞猜礼包全档']['rev'] / 97944 * 100
    p2_share = P2B['rev'] / 700000 * 100
    rows = [
        (f"X3 竞猜 ÷ 双节总盘（{fmt(wm['竞猜礼包全档']['rev'])} / $97,944）", x3_share, '#c08a17', ''),
        (f"P2 竞猜 ÷ 月周期节日盘（{fmt(P2B['rev'])} / ~$70万·用户口径）", p2_share, '#8b949e', ''),
    ]
    return _hbar(rows, '竞猜收入占同期节日总盘比例——跨游戏唯一可比口径（人群属性不同，ARPU/绝对值不直比）', '{:.1f}%')

def jc_tier_chart():
    rows = [
        (f'免费预测档（参与 {CANYU:,} 人）', 0.001, '#3a4150', '参与奖：券1+钻+金币——无收入'),
        ('$4.99 券档 · 纯资源无外显', wm['竞猜$4.99档(尾1)']['rev'], '#3a4150', f"{wm['竞猜$4.99档(尾1)']['buyers']}人 · 复购 {wm['竞猜$4.99档(尾1)']['opb']:.1f}"),
        ('$9.99 框档 · 带头像框', wm['竞猜$9.99框档(尾2)']['rev'], '#c08a17', f"{wm['竞猜$9.99框档(尾2)']['buyers']}人 · 复购 {wm['竞猜$9.99框档(尾2)']['opb']:.1f}"),
        ('$19.99 表情档 · 带助威表情', wm['竞猜$19.99表情档(尾3)']['rev'], '#c08a17', f"{wm['竞猜$19.99表情档(尾3)']['buyers']}人 · 复购 {wm['竞猜$19.99表情档(尾3)']['opb']:.1f}"),
    ]
    return _hbar(rows, '档位收入结构（金=带外显的档 · 灰=纯资源档）', '${:,.0f}')

def jc_srv_chart():
    P = PR['世界杯_payers']
    segs = [('老服成熟段', 1000, 1870, '#c08a17'), ('年轻老服', 1880, 1970, '#4691e8'), ('扩服新服', 1980, 2250, '#8b949e')]
    part, conv, pr_ = [], [], []
    cats = []
    for name, lo, hi, c in segs:
        pt = sum(v for k, v in JSRV['part'].items() if lo <= int(k) <= hi)
        b = sum(v['b'] for k, v in JSRV['pay'].items() if lo <= int(k) <= hi)
        pay = sum(v for k, v in P.items() if lo <= int(k) <= hi)
        part.append(pt); conv.append(b/pt*100 if pt else 0); pr_.append(b/pay*100 if pay else 0)
        cats.append((name, c))
    return _panels([
        ('参与人数', '{:,.0f}', 7000, part),
        ('参与→付费转化 %', '{:.1f}%', 2.0, conv),
        ('付费玩家付费率 %', '{:.1f}%', 7, pr_),
    ], cats)


JCF = json.load(open(os.path.join(HERE, '_jc_funnel.json'), encoding='utf-8'))
JRS = json.load(open(os.path.join(HERE, '_jc_round_sku.json'), encoding='utf-8'))

def jc_funnel_chart():
    """免费档曝光漏斗 + 参与深度×付费转化"""
    W, H = 1040, 250
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    # 左：漏斗
    fx, fw, T = 40, 430, 46
    steps = [('曝光（83服窗口活跃）', JCF['active'], '#3a4150', ''),
             ('参与（领包/下注）', 13348, '#c08a17', f"参与率 {13348/JCF['active']*100:.0f}%"),
             ('付费（894买家）', 161, '#f85149', '转化 1.2%')]
    sv.append(f'<text x="{fx}" y="26" fill="#f0f6fc" font-size="12.5" font-weight="700">免费竞猜曝光漏斗</text>')
    for i, (lab, v, c, note) in enumerate(steps):
        y = T + i*62
        w = max(10, fw * v / steps[0][1])
        sv.append(f'<rect x="{fx}" y="{y}" width="{w:.0f}" height="34" fill="{c}" rx="4"><title>{lab}: {v:,}</title></rect>')
        sv.append(f'<text x="{fx+max(w,10)+10:.0f}" y="{y+15}" fill="#f0f6fc" font-size="12" font-weight="700">{v:,}</text>')
        sv.append(f'<text x="{fx+max(w,10)+10:.0f}" y="{y+30}" fill="#8b949e" font-size="10.5">{lab}　<tspan fill="#d29922" font-weight="700">{note}</tspan></text>')
    # 右：参与深度×转化
    ox, PW, PH, T2, L2 = 540, 470, 150, 56, 60
    sv.append(f'<text x="{ox+L2}" y="26" fill="#f0f6fc" font-size="12.5" font-weight="700">参与深度 × 付费转化（柱=转化率 · 标签=人数）</text>')
    labs = {'a.1场':'1场','b.2-4场':'2-4场','c.5-9场':'5-9场','d.10-15场':'10-15场','e.16场+':'16场+'}
    dep = JCF['depth']
    vmax = 3.0
    bw = (PW-L2)/len(dep)
    for i, r in enumerate(dep):
        cv = r['payers']/r['users']*100
        x = ox + L2 + i*bw + 6
        y = T2 + PH*(1-cv/vmax)
        sv.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw-12:.0f}" height="{T2+PH-y:.0f}" fill="#c08a17" rx="3"><title>{labs[r["bk"]]}: {r["users"]:,}人 付费{r["payers"]} 转化{cv:.1f}%</title></rect>')
        sv.append(f'<text x="{x+(bw-12)/2:.0f}" y="{y-6:.0f}" fill="#f0f6fc" font-size="10.5" font-weight="700" text-anchor="middle">{cv:.1f}%</text>')
        sv.append(f'<text x="{x+(bw-12)/2:.0f}" y="{T2+PH+14}" fill="#8b949e" font-size="9.5" text-anchor="middle">{labs[r["bk"]]}</text>')
        sv.append(f'<text x="{x+(bw-12)/2:.0f}" y="{T2+PH+27}" fill="#484f58" font-size="9" text-anchor="middle">{r["users"]:,}人</text>')
    sv.append('</svg>')
    return ''.join(sv)

def jc_permatch_table():
    N = {'R32': 16, 'R16': 8, 'QF': 4, 'SF+': 2}
    tr = ['<table style="margin-top:10px"><tr><th>轮</th><th>场数</th><th>付费总额</th><th>单场收入</th><th>单买家单场产出</th><th>外显档占比</th></tr>']
    base = None
    for rd, n in N.items():
        d = JRS[rd]; tot = d['_all']['rev']; b = d['_all']['b']
        pm = tot/n; pb = tot/b/n
        wai = (d.get('2',{}).get('rev',0)+d.get('3',{}).get('rev',0))/tot*100 if tot else 0
        if base is None: base = pm
        hl = ' class="row-a"' if rd == 'SF+' else ''
        tr.append(f"<tr{hl}><td><b>{rd}</b></td><td>{n}</td><td>{fmt(tot)}</td><td>{fmt(pm)}<span class='dim'>（{pm/base:.1f}×R32）</span></td><td><b>${pb:.1f}</b></td><td>{wai:.0f}%</td></tr>")
    tr.append('</table>')
    return ''.join(tr)


JMS = json.load(open(os.path.join(HERE, '_jc_match_sku.json'), encoding='utf-8'))['matches']

def jc_match_chart():
    """SKU 拆到每场：上=参与人数 / 下=付费按档堆叠（时间序·锁盘日窗口·防跨轮复用）"""
    ms = JMS
    n = len(ms)
    W, L, R = 1160, 56, 14
    H1, H2, T1, GAPP, XH = 150, 170, 40, 46, 84
    H = T1 + H1 + GAPP + H2 + XH
    pw = W - L - R
    bw = pw / n
    RCOL = {'R32': '#3a4150', 'R16': '#2ea856', 'QF': '#c08a17', 'SF': '#bc6bd9', 'FINAL': '#f85149'}
    TCOL = {'1': '#3a4150', '2': '#4691e8', '3': '#c08a17'}
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    # 上面板：参与
    pmax = max(m['part'] for m in ms) * 1.12
    sv.append(f'<text x="{L}" y="24" fill="#f0f6fc" font-size="12.5" font-weight="700">每场参与人数（色=轮次）</text>')
    for gv in range(0, int(pmax)+1, 4000):
        y = T1 + H1*(1-gv/pmax)
        sv.append(f'<line x1="{L}" y1="{y:.0f}" x2="{W-R}" y2="{y:.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L-5}" y="{y+4:.0f}" fill="#484f58" font-size="9.5" text-anchor="end">{gv//1000}k</text>')
    for i, m in enumerate(ms):
        x = L + i*bw + 2
        h = H1 * m['part']/pmax
        sv.append(f'<rect x="{x:.0f}" y="{T1+H1-h:.0f}" width="{bw-4:.0f}" height="{h:.0f}" fill="{RCOL[m["round"]]}" fill-opacity="0.9" rx="2"><title>{m["key"]} {m["kickoff"][:10]} 参与 {m["part"]:,}</title></rect>')
    # 下面板：付费按档堆叠
    T2 = T1 + H1 + GAPP
    rmax = max(m['rev'] for m in ms) * 1.15
    sv.append(f'<text x="{L}" y="{T2-16}" fill="#f0f6fc" font-size="12.5" font-weight="700">每场付费 · 按档堆叠（灰=$4.99券 / 蓝=$9.99框 / 金=$19.99表情）</text>')
    for gv in range(0, int(rmax)+1, 200):
        y = T2 + H2*(1-gv/rmax)
        sv.append(f'<line x1="{L}" y1="{y:.0f}" x2="{W-R}" y2="{y:.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L-5}" y="{y+4:.0f}" fill="#484f58" font-size="9.5" text-anchor="end">${gv}</text>')
    for i, m in enumerate(ms):
        x = L + i*bw + 2
        y0 = T2 + H2
        for t in ('1','2','3'):
            v = m[f't{t}_rev']
            if v <= 0: continue
            h = H2 * v/rmax
            sv.append(f'<rect x="{x:.0f}" y="{y0-h:.0f}" width="{bw-4:.0f}" height="{max(1,h):.0f}" fill="{TCOL[t]}" rx="1"><title>{m["key"]} 尾{t}: ${v:,.0f}（{m[f"t{t}_u"]}人）</title></rect>')
            y0 -= h
        if m['rev'] >= 400:
            sv.append(f'<text x="{x+(bw-4)/2:.0f}" y="{T2+H2-H2*m["rev"]/rmax-5:.0f}" fill="#f0f6fc" font-size="9" font-weight="700" text-anchor="middle">${m["rev"]:,.0f}</text>')
    # X 轴：场次标签（斜排）
    for i, m in enumerate(ms):
        lab = m['key'].split('-',1)[1] if '-' in m['key'] else m['key']
        xx = L + i*bw + bw/2
        sv.append(f'<text x="{xx:.0f}" y="{T2+H2+12}" fill="#8b949e" font-size="8.5" text-anchor="end" transform="rotate(-45 {xx:.0f} {T2+H2+12})">{lab}</text>')
    # 图例（轮次）
    lx = L
    for rd, c in RCOL.items():
        sv.append(f'<rect x="{lx}" y="{H-16}" width="10" height="10" fill="{c}" rx="2"/>')
        sv.append(f'<text x="{lx+15}" y="{H-7}" fill="#c9d1d9" font-size="10">{rd}</text>')
        lx += 15 + len(rd)*8 + 22
    sv.append('</svg>')
    return ''.join(sv)


SF4 = json.load(open(os.path.join(HERE, '_jc_sf4_trend.json'), encoding='utf-8'))

def jc_sf4_chart(key='t23', title='外显合计（$9.99+$19.99）'):
    RDS = ['R32', 'R16', 'QF', 'SF', 'FINAL']
    REGIME = ['通用宝箱', '通用宝箱', '该国直给', '4强自选宝箱', '冠军外显']
    TCOL = {'ESP': '#c08a17', 'ARG': '#4691e8', 'ENG': '#2ea856', 'FRA': '#bc6bd9'}
    SHORT = {('FRA','QF'), ('ESP','SF')}
    def val(code, rd):
        r = SF4[code][rd]
        if key == 't23': return r['t23'], r['u23']
        return r[f'{key}_rev'], r[f'{key}_u']
    W, H, L, R, T, B = 1160, 340, 60, 24, 58, 64
    pw, ph = W-L-R, H-T-B
    vmax = max(val(c, rd)[0] for c in TCOL for rd in RDS) * 1.18 or 1
    def X(i): return L + pw*i/(len(RDS)-1)
    def Y(v): return T + ph*(1-v/vmax)
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L}" y="22" fill="#f0f6fc" font-size="13" font-weight="700">四强四队 · {title} 按轮付费 × 投放形态（空心点=窗口受限）</text>')
    sv.append(f'<rect x="{X(3.5):.0f}" y="{T}" width="{X(4)-X(3.5)+20:.0f}" height="{ph}" fill="#f85149" fill-opacity="0.06"/>')
    step = max(20, int(vmax//4/10)*10)
    for gv in range(0, int(vmax)+1, step):
        sv.append(f'<line x1="{L}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">${gv}</text>')
    for i, rd in enumerate(RDS):
        sv.append(f'<text x="{X(i):.0f}" y="{H-42}" fill="#c9d1d9" font-size="11.5" font-weight="700" text-anchor="middle">{rd}</text>')
        sv.append(f'<text x="{X(i):.0f}" y="{H-28}" fill="#8b949e" font-size="9.5" text-anchor="middle">{REGIME[i]}</text>')
    for code, c in TCOL.items():
        seq = []
        for i, rd in enumerate(RDS):
            if rd == 'FINAL' and code in ('ENG', 'FRA'): continue
            v, u = val(code, rd)
            seq.append((i, v, u))
        path = ' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i, v, _ in seq)
        sv.append(f'<path d="M {path}" fill="none" stroke="{c}" stroke-width="2.2"/>')
        for i, v, u in seq:
            hollow = (code, RDS[i]) in SHORT
            fill = '#0d1117' if hollow else c
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="4" fill="{fill}" stroke="{c}" stroke-width="2"><title>{code} {RDS[i]}（{REGIME[i]}）{title} ${v:,.0f} / {u}人{"（窗口受限）" if hollow else ""}</title></circle>')
            sv.append(f'<text x="{X(i):.0f}" y="{Y(v)-10:.0f}" fill="{c}" font-size="9.5" font-weight="700" text-anchor="middle">${v:,.0f}</text>')
    lx = L
    for code, c in TCOL.items():
        sv.append(f'<line x1="{lx}" y1="{H-12}" x2="{lx+16}" y2="{H-12}" stroke="{c}" stroke-width="2.4"/>')
        sv.append(f'<text x="{lx+21}" y="{H-8}" fill="#c9d1d9" font-size="10.5">{code}</text>')
        lx += 21 + 40
    sv.append('</svg>')
    return ''.join(sv)

# ============ 独立页：世界杯竞猜回归 ============
OUT2 = os.path.join(HERE, f"世界杯竞猜回归_{END.replace('-','')}.html")
page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 世界杯竞猜回归 — tap4fun</title>
<style>
:root{{--dark:#0d1117;--card:#161b22;--border:#30363d;--text:#c9d1d9;--head:#f0f6fc;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--dark);color:var(--text);font-size:13.5px;display:flex;min-height:100vh}}
.sidebar{{width:220px;background:var(--dark);border-right:1px solid var(--border);position:fixed;top:0;left:0;bottom:0;overflow-y:auto;z-index:10}}
.sb-logo{{padding:20px 18px 12px;border-bottom:1px solid var(--border)}}
.sb-logo .brand{{font-size:18px;font-weight:800;color:var(--head)}} .sb-logo .brand span{{color:var(--accent)}}
.sb-logo .sub{{font-size:10.5px;color:#484f58;margin-top:2px;letter-spacing:.5px}}
.sb-nav{{padding:12px 0}}
.sb-item{{display:block;padding:9px 18px;font-size:12.5px;color:#8b949e;text-decoration:none;border-left:3px solid transparent}}
.sb-item:hover{{background:#21262d;color:var(--head)}}
.sb-label{{padding:10px 18px 4px;font-size:10px;font-weight:700;letter-spacing:1.5px;color:#484f58;text-transform:uppercase}}
.content{{margin-left:220px;flex:1}}
.hero-bar{{background:linear-gradient(135deg,#0d1117,#161b22);border-bottom:1px solid var(--border);padding:28px 48px}}
.hero-bar h1{{font-size:1.5em;font-weight:800;color:var(--head);line-height:1.3}}
.hero-bar h1 em{{color:var(--yellow);font-style:normal}}
.hero-bar .meta{{font-size:11.5px;color:#484f58;margin-top:6px}} .hero-bar .meta b{{color:var(--accent)}}
.verdict{{margin:20px 48px 0;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:6px;padding:16px 22px}}
.verdict .vl{{font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--yellow);text-transform:uppercase;margin-bottom:5px}}
.verdict p{{font-size:13px;line-height:1.85}} .verdict b{{color:var(--head)}}
.page{{padding:24px 48px 48px}}
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}}
.kpi{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;border-top:3px solid var(--accent)}}
.kpi.g{{border-top-color:var(--green)}} .kpi.r{{border-top-color:var(--red)}} .kpi.y{{border-top-color:var(--yellow)}}
.kpi-val{{font-size:1.9em;font-weight:800;color:var(--head)}}
.kpi-lbl{{font-size:11.5px;color:#8b949e;margin-top:5px;font-weight:600}}
.kpi-sub{{font-size:11px;color:#484f58;margin-top:3px}}
.kpi-badge{{display:inline-block;padding:2px 8px;border-radius:3px;font-size:10px;font-weight:700}}
.kpi-badge.ok{{background:#1b3a2a;color:var(--green)}} .kpi-badge.bad{{background:#3b1212;color:var(--red)}} .kpi-badge.mid{{background:#3b2e12;color:var(--yellow)}} .kpi-badge.meet{{background:#0d2137;color:var(--accent)}}
.sec{{scroll-margin-top:20px}}
.sec-head{{display:flex;align-items:center;gap:10px;margin:28px 0 12px}}
.sec-num{{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#0d1117;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.sec-title{{font-size:15px;font-weight:700;color:var(--head)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 22px;margin-bottom:14px}}
.ct{{font-size:11px;font-weight:700;color:#8b949e;letter-spacing:.5px;text-transform:uppercase;border-left:3px solid var(--accent);padding-left:10px;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#21262d;color:var(--head);padding:8px 10px;text-align:center;font-weight:600;border-bottom:1px solid var(--border)}}
th.l,td.l{{text-align:left}}
td{{padding:9px 10px;border-bottom:1px solid #21262d;text-align:center;vertical-align:top;line-height:1.6}}
tr:hover td{{background:#161b2299}}
.dim{{color:#484f58;font-size:11px}}
.row-a{{background:#21262d!important}} .row-a td{{color:var(--head);font-weight:700}}
.bigcon{{background:linear-gradient(135deg,#1b2436,#161b22);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:8px;padding:16px 20px;font-size:14.5px;line-height:2;color:var(--text);margin-bottom:14px}} .bigcon b{{color:var(--head)}}
.con-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:14px}}
.con-card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px 16px;display:flex;flex-direction:column;gap:8px;font-size:12.5px;line-height:1.85}}
.con-card:hover{{border-color:#1f6feb66}}
.con-head{{display:flex;align-items:center;gap:9px}}
.con-num{{flex:none;width:22px;height:22px;border-radius:50%;background:#0d2137;border:1px solid #1f6feb55;color:var(--accent);font-size:11px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.con-head .t{{font-size:13px;font-weight:700;color:var(--head)}}
.con-body{{color:var(--text)}} .con-body b{{color:var(--head)}}
.con-link{{margin-top:auto;align-self:flex-start;font-size:11px;font-weight:700;color:var(--accent);text-decoration:none;background:#0d2137;border:1px solid #1f6feb44;border-radius:20px;padding:3px 12px}}
.con-link:hover{{background:#1f6feb;color:#fff}}
.wcb{{display:inline-block;padding:1px 6px;margin-right:7px;border:1px solid #c08a17;border-radius:4px;color:#c08a17;font-size:9.5px;font-weight:700;vertical-align:1px}}
.backtop{{margin-left:auto;font-size:11px;font-weight:600;color:#8b949e;text-decoration:none;border:1px solid var(--border);border-radius:20px;padding:3px 11px}}
.backtop:hover{{color:var(--head);background:#21262d}}
.vlin,.ct{{scroll-margin-top:20px}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}}
.chip{{padding:7px 16px;border-radius:20px;border:1px solid var(--border);background:#161b22;color:#8b949e;font-size:12.5px;font-weight:600;cursor:pointer}}
.chip:hover{{color:var(--head)}}
.chip.on{{background:#1f6feb;border-color:#1f6feb;color:#fff}}
.view{{display:none}} .view.on{{display:block}}
.vlin{{display:block;margin-bottom:14px}}
.vc{{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:10px}}
td b{{color:var(--head)}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">WC ORACLE REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">世界杯竞猜回归</div>
    <a class="sb-item" href="#secjc">结论先行</a>
    <a class="sb-item" href="#jsec1">01 · 基本付费分析</a>
    <a class="sb-item" href="#jsec2">02 · 形式对比 · P2对照</a>
    <a class="sb-item" href="#jsec3">03 · 参与面</a>
    <a class="sb-item" href="#jsec4">04 · 档位 SKU 结构</a>
    <a class="sb-item" href="#jsec5">05 · 新老服拆分</a>
    <a class="sb-item" href="母题4_改动效果清单_{END.replace('-','')}.html">← 返回双节回归总页</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 世界杯竞猜回归<br><em>史上最宽入口 · 形式份额及格 · 变现靠外显与"充值即下注"改造</em></h1>
  <div class="meta">窗口 <b>6/26-{END[5:]} · 全服</b> · 数据 <b>Trino v1090/v1041 订单+资产</b> · 世界杯 7/20 收官后终版刷新 · 生成 {now}</div>
</div>

<div class="page">
<div class="sec" id="secjc"><div class="sec-head"><div class="sec-num">★</div><div class="sec-title">世界杯竞猜回归 · 整体结论（6/26-{END[5:]} · 全服）</div></div>
<div class="bigcon">总判词：<b>整体效果符合预期</b>——占同期节日总盘份额 <b>7.2%</b> ≈ P2 同题竞猜（~7%），形式在盘内吃到的份额已达 P2 水平，拉动及格；聚人全场第一（{CANYU:,} 人参与=窗口总付费人数 3.2 倍），变现中游偏下——付费玩家 ARPU <b>${JF59['竞猜894全档']['rev']/JF59['payers']:.2f}，十个售卖形式排第 6</b>（统一深海59服段口径）：只有开箱连锁（${JF59['开箱福箱连锁']['rev']/JF59['payers']:.2f}）的四成、深海成就礼包（${dm['大富翁成就礼包']['rev']/DS['payers']:.2f}）/BP 大富翁线（${dm['BP大富翁线(130036/37)']['rev']/DS['payers']:.2f}）的一半弱，只高于每日礼包/存钱罐/周卡等送达层与锚点；绝对额（全服总账）{fmt(wm['竞猜礼包全档']['rev'])} ≈ 开箱族（{fmt(KX['rev'])}）的 1/3。六条核心结论：<br>
<span style="font-size:13px;line-height:2.05">
① <b>免费竞猜曝光有效、转化难</b>——83 服活跃的 31% 参与，但参与→付费仅 1.2%（重度 16 场+也只 2.4%），免费名义投放=付费收入的 7.5 倍 → 保留，但免费档 ROI 拉到最低 <a class="con-link" style="padding:1px 10px;margin-left:2px" href="#jcfree">03 · 免费档漏斗 ↓</a><br>
② <b>逐轮奖励升级有效</b>——付费日均下降只是可押场次 16→8→4→2 腰斩的结构必然，单场口径下单场收入=首轮的 1.3-1.9 倍、单买家单场产出 $2.1→$10.1 持续走高 <a class="con-link" style="padding:1px 10px;margin-left:2px" href="#jc2">03 · 按轮单场口径 ↓</a><br>
③ <b>参与追热闹、付费追确定性</b>——付费向强弱悬殊局集中：ARGvEGY $545 全赛程第一（命中率 93.6%），均势局 SUIvCOL 参与 1.3 万全场第一但付费仅 $305；决赛=唯一光环例外（$485·外显占 89%） <a class="con-link" style="padding:1px 10px;margin-left:2px" href="#jcmatch">04 · 场级 SKU 拆分 ↓</a><br>
④ <b>SKU：玩家是"看奖励/ROI"买的</b>——外显两档占竞猜付费 81%、纯资源 $4.99 档只卖 {fmt(wm['竞猜$4.99档(尾1)']['rev'])}；国家头像框基本没用（框档全程平稳、QF 换该国直给也不抬），买得多的全是强弱悬殊局＝中奖确定性高＝实际 ROI 高（猜中另有加送）。<b>正向 SKU 三要素＝通用元素＋限定感强＋ROI 高</b>——冠军外显（通用+强限定）$485/外显占 89% 实证；$4.99 入门档决赛 11 人/场＝低价高确定性同逻辑 <a class="con-link" style="padding:1px 10px;margin-left:2px" href="#jc3">04 · 档位 SKU 结构 ↓</a><br>
⑤ <b>人群无足球国家狂热，RU 地区有所排斥</b>——参与结构≈活跃基线（题材对大盘中性），唯 RU 全链路欠额（活跃 25%→参与 17%→付费 6%，没进世界杯没队可押）；付费向英语区集中（US+GB 53%）→ 赛事选题要算参赛国×玩家母国覆盖度 <a class="con-link" style="padding:1px 10px;margin-left:2px" href="#jcgeo">03 · 国家结构四口径 ↓</a><br>
⑥ <b>玩家还有额外付费空间可挖</b>——增量共存两次验证（竞猜挂在开箱旁、开箱本体付费未被冲击；外显档挂进竞猜又额外收 {fmt(wm['竞猜$9.99框档(尾2)']['rev']+wm['竞猜$19.99表情档(尾3)']['rev'])}），说明现有货架没吃满玩家付费意愿；竞猜是世界杯限定形式（赛事驱动、不可常态复用），这块空间<b>后续换其他形式承接</b>＝限时抢购、强消耗扭蛋机、皮肤开箱优化三模块 <a class="con-link" style="padding:1px 10px;margin-left:2px" href="#jc5">02 · 形式对比与改造路径 ↓</a>
</span></div>

<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{CANYU:,}</div><div class="kpi-lbl">全程参与（史上最宽入口）</div><div class="kpi-sub">= 总付费人数 3.2 倍 · 31% 活跃参与率 · 缩圈不缩人</div></div>
  <div class="kpi"><div class="kpi-val">7.2%</div><div class="kpi-lbl">占同期节日总盘份额</div><div class="kpi-sub">≈ P2 同题竞猜 ~7% · 形式拉动及格</div></div>
  <div class="kpi y"><div class="kpi-val">{fmt(wm['竞猜礼包全档']['rev'])}</div><div class="kpi-lbl">竞猜付费 · {wm['竞猜礼包全档']['buyers']} 买家</div><div class="kpi-sub">付费玩家付费率 {wm['竞猜礼包全档']['buyers']/WC['payers']*100:.1f}%（开箱 {KX['buyers']/WC['payers']*100:.1f}% · 通行证 {wm['通行证(130020/21)']['buyers']/WC['payers']*100:.1f}%）</div></div>
  <div class="kpi r"><div class="kpi-val">${JF59['竞猜894全档']['rev']/JF59['payers']:.2f}</div><div class="kpi-lbl">付费玩家 ARPU（十形式第 6 · 深海59服段口径）</div><div class="kpi-sub">开箱连锁 ${JF59['开箱福箱连锁']['rev']/JF59['payers']:.2f} 的四成 · ARPPU ${JF59['竞猜894全档']['arppu']:.0f} · 复购 {JF59['竞猜894全档']['opb']:.1f} 单</div></div>
</div>

<div class="cb cb-info" style="margin:0 0 14px">完整付费三件套（付费率 / ARPU / ARPPU）及开箱、通行证同窗参照 <a class="con-link" style="margin:0 0 0 6px" href="#jc0">详见 01 · 基本付费分析 ↓</a></div>

<div class="sec" id="jsec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">基本付费分析（整体三件套 · 开箱/通行证参照）</div><a class="backtop" href="#secjc">↑ 整体结论</a></div></div>
<div class="vlin" id="jc0"><div class="vc">竞猜形式的<b>付费率转化不太行</b>（老服段 {JPO['竞猜894全档']['payrate']:.1f}%，为开箱 {JPO['世界杯开箱']['payrate']:.1f}% 的一半、夏日开箱 {KG['夏日开箱']['payrate']:.1f}% 的三分之一），<b>付费深度还可以</b>（ARPPU ${JPO['竞猜894全档']['rev']/JPO['竞猜894全档']['buyers']:.0f} · 复购 {JPO['竞猜894全档']['orders']/JPO['竞猜894全档']['buyers']:.1f} 单），且<b>没有冲击开箱本体</b>——同段开箱 ARPPU ${JPO['世界杯开箱']['rev']/JPO['世界杯开箱']['buyers']:.0f}，高于夏日的 ${G_SM['合并']['rev']/G_SM['合并']['buyers']:.0f}。</div>
<div class="card"><div class="ct">对比图 · 世界杯老服段（1000-1870）vs 夏日开箱——同段跨窗可比</div>
{jc_pay_chart_old()}
<div style="height:10px"></div>
{jc_pay_table_old()}
</div>
<div class="card"><div class="ct">整体图 · 世界杯全服（含 28 扩服+年轻服）——看整体量级，不与夏日直比</div>
{jc_pay_chart_all()}
<div style="height:10px"></div>
{jc_pay_table_all()}
</div></div>
<div class="sec" id="jsec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">形式对比 · 设计目的验证（含 P2 同题对照）</div><a class="backtop" href="#secjc">↑ 整体结论</a></div></div>
<div class="vlin" id="jc5"><div class="vc">最关键指标=付费玩家 ARPU（该形式从每个付费玩家身上拉动了多少，统一深海59服段分母）：<b>竞猜 ${JF59['竞猜894全档']['rev']/JF59['payers']:.2f}，十个形式排第 6</b>——只有开箱连锁（${JF59['开箱福箱连锁']['rev']/JF59['payers']:.2f}）的四成、深海成就礼包（${dm['大富翁成就礼包']['rev']/DS['payers']:.2f}）/BP大富翁线（${dm['BP大富翁线(130036/37)']['rev']/DS['payers']:.2f}）的一半弱，只高于每日礼包/存钱罐/周卡等送达层与锚点。<b>按设计目的（用竞猜形式拉动礼包付费）判定：拉动不达预期</b>（低于开箱/成就/BP 等主力售卖形式）；形式特征=复购 {JF59['竞猜894全档']['opb']:.1f} 单（与开箱 {JF59['开箱福箱连锁']['opb']:.1f} 同级·事件驱动天然多次）+外显档占 81%——"买加成赌胜负"没成为付费理由，付费理由是外显和参与感。</div>
<div class="card"><div class="ct">竞猜 vs 同期各礼包售卖形式 · 同窗对打（三件套+复购+max）</div>
{jc_form_chart()}
<div style="height:10px"></div>
{jc_form_table()}
<div class="cb cb-warn"><b>占比口径（用户定·判定主口径）：按"竞猜 ÷ 同期节日总盘"的份额看，两家几乎一样——X3 {wm['竞猜礼包全档']['rev']/1000:.1f}k ÷ 双节盘 $97.9k = <span style="font-size:14px">7.2%</span>，P2 ~$49k ÷ 月周期节日盘 ~$70万 ≈ <span style="font-size:14px">7%</span>。</b>也就是说：<b>竞猜形式在各自盘内吃到的份额已达 P2 水平，"形式拉动"及格；7 倍的绝对差距来自节日大盘的规模与深度系统差（P2 节日盘=X3 的 7 倍、节日 ARPPU 2.2×），不应记在竞猜形式头上。</b><span class="dim">口径注：同窗严格口径（7/3-16）P2 份额为 30.7%（节日标记盘 $159,806），但 P2 七月新节日包标记疑似不全（同窗节日占比 24% &lt; 常态 44-50%），分母偏低致份额虚高，故判定采用月周期口径。</span></div>
{jc_share_chart()}
<div class="cb cb-info"><b>形式机制差（改造方向的依据，非跨人群量化对比）：P2 的竞猜=充值即下注——无免费档、$4.99/9.99/19.99 三档、不限购，复购 8.3 单/人全靠赛事天然多次；X3 的竞猜=免费下注+可选加成包，付费是旁挂的。</b>在同样 ~7% 的盘内份额下，P2 这套形式在 $70 万的盘里拿走 $49k，X3 在 $9.8 万的盘里拿走 $7k——X3 要把竞猜份额做大，路径不是给礼包加料，而是①把付费下注做成主循环（充值即参与）②保留免费档当拉新钩子（13,348 参与盘是 X3 独有资产）。</div>
</div></div>
<div class="sec" id="jsec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">参与面：逐日曲线与按轮走势</div><a class="backtop" href="#secjc">↑ 整体结论</a></div></div>
<div class="vlin" id="jc1"><div class="vc">参与由比赛日驱动、20 天全程有脉冲无衰减——按轮 7.3k → 10.8k → 8.7k → 8.2k，淘汰赛缩圈不缩人。作为拉活跃入口，生命力贯穿全程。</div>
<div class="card"><div class="ct">参与逐日曲线 · 轮次色带 · 悬停看数</div>
{jc_daily_chart()}
</div></div>
<div class="vlin" id="jc2"><div class="vc">按轮走势要用"单场口径"读（用户判定：逐轮奖励升级还是可以的）：日均下降是可押场次 16→8→4→2 腰斩的结构必然；换算单场后，<b>单场收入升到 R32 基线的 1.3-1.9 倍、单买家单场产出 $2.1 → $5.0 → $5.8 → $10.1 持续走高、外显档占比 80%→85%</b>——奖励逐轮升级（8强直给→4强自选）有效抬高了每场产出与买家质量。</div>
<div class="card"><div class="ct">按轮对比 · 同轮次窗口</div>
{jc_rounds_chart()}
{jc_permatch_table()}
</div></div>
<div class="vlin" id="jcfree"><div class="vc">免费竞猜档判定（用户定）：对每场曝光有帮助——83 服窗口活跃 43,179 人里 <b>31% 参与了竞猜</b>（13,348 人），但很难转化到付费层（1.2%，参与 16 场+的重度玩家也只有 2.4%）——<b>可以保留，但免费档 ROI 应拉到最低，这次偏高了</b>：免费直发券 21.1 万张（按锚点价名义 ≈$52.7k）= 竞猜付费收入的 7.5 倍，另有猜中邮件百万级加送。</div>
<div class="card"><div class="ct">免费档曝光漏斗 · 参与深度×付费转化</div>
{jc_funnel_chart()}
<div class="cb cb-info">深度与转化正相关但天花板极低（16 场+ 仅 2.4%）——不是玩家不深度参与，是免费供给足够玩完整届、无需付费；下调免费档（券/资源）不影响参与（W8 已证白嫖盘对奖励下调不敏感），能直接改善这个 ROI。</div>
</div></div>

<div class="vlin" id="jcgeo"><div class="vc">参与玩家的国家结构 ≈ 活跃基线（无"足球国家狂热"，竞猜是全体玩家的活动）；唯一显著欠额=俄罗斯（活跃 25% → 参与 17% → 付费 6%），<b>原因很简单：俄罗斯没进世界杯，没有自己的队可押</b>（用户判定）；付费面向英语区集中（US+GB 53%）。</div>
<div class="card"><div class="ct">设备国家分布 · 四口径对照（窗口 6/26-7/20）</div>
<table><tr><th class="l">国家</th><th>活跃基线(83服)</th><th>竞猜参与(13,657)</th><th>竞猜付费(177)</th><th>大盘付费(10,992)</th></tr>
<tr><td class="l"><b>US</b></td><td>29%</td><td>26%</td><td class="y"><b>45%</b></td><td>42%</td></tr>
<tr><td class="l"><b>RU</b></td><td>25%</td><td class="r">17%</td><td class="r">6%</td><td>15%</td></tr>
<tr><td class="l">DE</td><td>9%</td><td>10%</td><td>7%</td><td>8%</td></tr>
<tr><td class="l">GB</td><td>6%</td><td>5%</td><td>8%</td><td>5%</td></tr>
<tr><td class="l">FR</td><td>6%</td><td>5%</td><td>3%</td><td>3%</td></tr>
<tr><td class="l">MX / BR</td><td>4% / 4%</td><td>3% / –</td><td>–</td><td>–</td></tr></table>
<div class="cb cb-info">口径：country=设备国家（login/order 自带列）；竞猜付费 177 人为小样本（±4pp 只读大差异）；数据 `_jc_country.json`。启示：赛事竞猜类活动的参与上限受"玩家母国是否在赛事中"影响——选题材/做本地化推送时把参赛国覆盖度算进去。</div>
</div></div>

<div class="sec" id="jsec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">档位 SKU 结构</div><a class="backtop" href="#secjc">↑ 整体结论</a></div></div>
<div class="vlin" id="jc3"><div class="vc">SKU 结构说明一切：$4.99 是<b>纯资源无外显</b>（券+钻+VIP），只卖 {fmt(wm['竞猜$4.99档(尾1)']['rev'])}；$9.99/$19.99 一挂上外显（框/表情）立刻拉到 {fmt(wm['竞猜$9.99框档(尾2)']['rev']+wm['竞猜$19.99表情档(尾3)']['rev'])}、占竞猜付费 {(wm['竞猜$9.99框档(尾2)']['rev']+wm['竞猜$19.99表情档(尾3)']['rev'])/wm['竞猜礼包全档']['rev']*100:.0f}%——<b>竞猜的付费驱动是外显、不是加成券</b>。{CANYU:,} 参与者是全场最大的未转化流量池。</div>
<div class="card"><div class="ct">档位结构 · 付费率分母=世界杯窗口全服总付费人数</div>
{jc_tier_chart()}
<div style="height:10px"></div>
{jc_tier_table()}
<div style="height:14px"></div>
<div class="ct" id="jcmatch">SKU 拆到每场比赛 · 31 场（每场窗口=轮开盘日→该场锁盘日，防 pack 跨轮复用；SF 外显档已按 4强容器包映射）</div>
{jc_match_chart()}
<div class="card" style="margin-top:14px"><div class="ct">四强四队 · 外显档（$9.99+$19.99）按轮付费趋势 × 投放形态（数据 _jc_sf4_trend.json）</div>
<div class="chips" id="sf4chips">
  <button class="chip on" data-v="sf4a">外显合计</button>
  <button class="chip" data-v="sf4b">$4.99 券档</button>
  <button class="chip" data-v="sf4c">$9.99 框档</button>
  <button class="chip" data-v="sf4d">$19.99 表情档</button>
</div>
<div class="view on" id="sf4a">{jc_sf4_chart('t23', '外显合计（$9.99+$19.99）')}</div>
<div class="view" id="sf4b">{jc_sf4_chart('t1', '$4.99 券档')}</div>
<div class="view" id="sf4c">{jc_sf4_chart('t2', '$9.99 框档')}</div>
<div class="view" id="sf4d">{jc_sf4_chart('t3', '$19.99 表情档')}</div>
<div style="height:10px"></div>
<table><tr><th class="l">队</th><th>R32<span class="dim">·通用宝箱</span></th><th>R16<span class="dim">·通用宝箱</span></th><th>QF<span class="dim">·该国直给框/表情</span></th><th>SF<span class="dim">·4强自选宝箱</span></th><th>决赛<span class="dim">·冠军外显</span></th></tr>
<tr><td class="l"><b>ESP</b></td><td>$250 / 17人</td><td>$170 / 13</td><td>$190 / 13</td><td>$20 / 1<span class="dim">（窗口2天）</span></td><td class="y"><b>$140 / 11</b></td></tr>
<tr><td class="l"><b>ARG</b></td><td>$280 / 17</td><td class="g">$410 / 25<span class="dim">（悬殊场ARGvEGY）</span></td><td>$180 / 14</td><td>$170 / 11</td><td class="y"><b>$300 / 21（五轮最高买家）</b></td></tr>
<tr><td class="l">ENG</td><td>$160 / 10</td><td>$150 / 10</td><td>$140 / 11</td><td>$80 / 7</td><td>—</td></tr>
<tr><td class="l">FRA</td><td>$150 / 9</td><td class="g">$420 / 27<span class="dim">（悬殊场PARvFRA）</span></td><td>$90 / 7<span class="dim">（QF1窗口1天）</span></td><td>$140 / 10</td><td>—</td></tr></table>
<div class="cb cb-info"><b>结论（用户判定）：国家头像框/表情基本没用——玩家是"看奖励/ROI"买的</b>：付费高的场次全是强弱悬殊局（中奖确定性=实际 ROI 高），同价位档（$9.99/$19.99）不因国家定制增长；对 $4.99 入门档有一定提升（单场买家 3.4 → 决赛 11 人/场＝低价高确定性）。<b>正向 SKU 三要素＝通用元素＋限定感强＋ROI 高</b>。⚠️口径区分：开箱券锚点 211012（另一个 $4.99）反而付费率腰斩（1.5%→0.67%，竞猜引流后期减弱）。①QF 通用宝箱→该国直给，四队全部持平或降（剔窗口干扰后依然无提升）；②SF 自选宝箱同样无提升；③决赛冠军外显明确有效（ARG 21 买家=五轮最高、两队合计 $440）；④ARG/FRA 的峰值都在各自悬殊场——<b>付费跟场次的确定性与意义走（悬殊局、冠军战），不跟投放形态走：外显的付费驱动是稀缺/纪念意义，不是国家定制</b>。窗口注：QF1 仅 1 天、SF1 仅 2 天，趋势判读已剔除这两点。</div>
</div>
<div class="cb cb-info"><b>结论（用户判定）：①付费向"强弱悬殊局"集中——胜负确定性高=收益确定，玩家买竞猜礼包倾向押稳赢局：ARGvEGY $545（命中率 93.6% 一边倒）全赛程第一、BRAvJPN $430、ARGvCPV $210 均为各轮悬殊局头部；对照均势局 SUIvCOL（命中率 48.4%）参与 1.3 万全场第一但付费仅 $305——参与追热闹、付费追确定性。②决赛是唯一例外（ESPvARG 势均力敌仍 $485 第二）＝光环场，冠军外显收尾有效（外显档占 89%）。③外显档（蓝+金）几乎每场占大头、纯券档全程陪跑——SKU 结论到场级依然成立；④QF 起单场付费效率抬升（升级奖励生效，见 03 章单场口径）。</b></div>
<div class="cb cb-info">改造方向 = P2 猜酒杯形式（充值即参与 + 排行强循环），量级参考 07-10 漏斗推算（修到猜酒杯转化水平 ≈ 6.5×）。</div>
</div></div>
<div class="sec" id="jsec5"><div class="sec-head"><div class="sec-num">05</div><div class="sec-title">新老服拆分</div><a class="backtop" href="#secjc">↑ 整体结论</a></div></div>
<div class="vlin" id="jc4"><div class="vc">参与近一半来自扩服新服（6,493 人·49%）——新服玩家最爱玩竞猜、白嫖盘最大；但参与→付费转化三段均匀地低（老服 1.3% / 年轻服 1.6% / 新服 1.0%）——付费弱不是人群问题，是形式问题（哪个段都不买"加成券"）；年轻老服客单最高（ARPPU $67）。</div>
<div class="card"><div class="ct">竞猜新老服拆分 · 参与 / 转化 / 付费率 / ARPPU</div>
{jc_srv_chart()}
<div style="height:10px"></div>
{jc_srv_table()}
<div class="cb cb-info">口径：竞猜部署 83 服（55 老服 1170-1970 + 28 扩服）；参与=asset 894% 去重、付费=894 订单；付费率分母=该段窗口总付费人数。</div>
</div></div>
</div>
</div></div>
<script>
var g = document.getElementById('sf4chips');
if (g) {{
  var box = g.parentElement;
  g.querySelectorAll('.chip').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      g.querySelectorAll('.chip').forEach(function(x) {{ x.classList.remove('on'); }});
      btn.classList.add('on');
      box.querySelectorAll('.view').forEach(function(v) {{ v.classList.remove('on'); }});
      var t = box.querySelector('#' + btn.dataset.v);
      if (t) t.classList.add('on');
    }});
  }});
}}
</script>
</body></html>"""
open(OUT2, 'w', encoding='utf-8').write(page)
print('OK ->', OUT2)
