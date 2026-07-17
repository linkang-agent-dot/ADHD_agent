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
JP = json.load(open(os.path.join(HERE, '_jingcai_pay.json'), encoding='utf-8'))     # 竞猜/通行证 完整付费指标
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

    wc_free = 210976; wc_free_u = 13315
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
        t.append(f"<tr><td class='l'><b>{name}</b></td><td>{part:,}<span class='dim'>（{part/13315*100:.0f}%）</span></td><td>{b}</td>"
                 f"<td>{b/part*100 if part else 0:.1f}%</td><td>{fmt(rev)}</td><td>{pay:,}</td>"
                 f"<td>{b/pay*100 if pay else 0:.1f}%</td><td>${rev/b if b else 0:.0f}</td></tr>")
    t.append('</table>')
    return ''.join(t)

def jc_pay_table():
    """竞猜基本付费分析：完整指标行 + 开箱/通行证同窗参照（列序对齐开箱历史数据对比表）"""
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
    tr = ['<table><tr><th class="l">模块（6/26-' + END[5:] + ' 同窗）</th><th>收入</th><th>买家</th><th>付费玩家付费率*</th><th>付费玩家ARPU*</th><th>ARPPU</th><th>复购</th><th>p50</th><th>p90</th><th>$100+占比</th><th>$500+占比</th><th>max</th></tr>']
    for name, hl, m, opb_override in rows:
        opb = opb_override if opb_override is not None else (m.get('orders', 0)/m['buyers'] if m['buyers'] else 0)
        cls = ' class="row-a"' if hl else ''
        tr.append(f"<tr{cls}><td class='l'><b>{name}</b></td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td>"
                  f"<td>{m['payrate']:.1f}%<span class='dim'>／{m['total_payers']:,}</span></td>"
                  f"<td>${m['rev']/m['total_payers']:.2f}</td>"
                  f"<td>${m['rev']/m['buyers']:.0f}</td><td>{opb:.1f}</td><td>${m['p50']:.0f}</td><td>${m['p90']:.0f}</td>"
                  f"<td>{m['over100']:.1f}%</td><td>{m['over500']:.1f}%</td><td>{fmt(m['max'])}</td></tr>")
    tr.append('</table>')
    tr.append("<div class='dim' style='margin-top:6px'>*付费玩家付费率 = 模块买家 ÷ 有该模块流水的服上同窗总付费人数（竞猜 3,605 / 开箱 4,047 / 通行证 4,240）；付费玩家ARPU = 模块收入 ÷ 同一分母。</div>")
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
    tr = ['<table><tr><th class="l">档位</th><th>收入</th><th>买家/参与</th><th>付费玩家付费率*</th><th>ARPU</th><th>ARPPU</th><th>复购</th><th>max</th></tr>']
    for i, (name, rev, b, pr, arpu, ar, op, mx) in enumerate(rows):
        hl = ' class="row-a"' if i == 0 else ''
        tr.append(f"<tr{hl}><td class='l'>{name}</td><td>{rev}</td><td>{b}</td><td>{pr}</td><td>{arpu}</td><td>{ar}</td><td>{op}</td><td>{mx}</td></tr>")
    tr.append('</table>')
    tr.append(f"<div class='dim' style='margin-top:6px'>*付费玩家付费率 = 该档买家 ÷ 世界杯窗口全服总付费人数（{P:,}）；ARPU 同分母。参考：开箱族付费率 {KX['buyers']/P*100:.1f}% · 通行证 {wm['通行证(130020/21)']['buyers']/P*100:.1f}%。</div>")
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

page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 双节框架回归 · 母题4 改动效果清单 — tap4fun</title>
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
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}}
.chip{{padding:7px 16px;border-radius:20px;border:1px solid var(--border);background:#161b22;color:#8b949e;font-size:12.5px;font-weight:600;cursor:pointer}}
.chip:hover{{color:var(--head)}}
.chip.on{{background:#1f6feb;border-color:#1f6feb;color:#fff}}
.view{{display:none}} .view.on{{display:block}}
.vc{{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:10px}}
td b{{color:var(--head)}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DUAL FESTIVAL REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">母题4 · 改动效果清单</div>
    <a class="sb-item" href="#verdict">结论先行</a>
    <a class="sb-item" href="#sec0">01 · 世界杯模块全景 vs 预期</a>
    <a class="sb-item" href="#seckx">02 · 世界杯开箱效果分析</a>
    <a class="sb-item" href="#secjc">03 · 世界杯竞猜回归（整体）</a>
    <a class="sb-item" href="#sec1">04 · 世界杯 8 条改动</a>
    <a class="sb-item" href="#sec2">05 · 深海节 9 条（待聊）</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 双节框架回归 · 母题4：本届 17 条改动，每条一句话效果<br><em>验证 {N_OK} · 部分 {N_MID} · 证伪 {N_BAD} · 待查 {N_WAIT}</em></h1>
  <div class="meta">窗口 <b>世界杯 6/26-{END[5:]} 全服 · 深海 7/3-{END[5:]} 59服</b> · 数据 <b>Trino v1090 订单全口径（_l1_m4.json）</b> · 决赛/尾段未入，7/21 重跑 _l1_refresh.py 刷终版 · 生成 {now}</div>
</div>

<div class="verdict" id="verdict">
  <div class="vl">VERDICT · 结论先行</div>
  <p><b>① 世界杯开箱 = 正常发挥、未被双节叠开和竞猜礼包挤压（本体效果接近夏日，可以继续开）。唯一结构性正信号 = 外显进付费档（W3）</b>——竞猜侧外显两档占付费 81%、开箱侧出现 $1,415 首个破墙极值；锚点买家 ×2.8 主要来自服基数扩大（扩服+年轻服），不计入改动效果；开箱人均三代横盘 $48-54（详见 02 章）。
  <b>② 最大的两条证伪：转盘连锁形式（D2，判退役坐实+锚点零购买）和双周节奏（D1，部署同开=没有弹药带）。</b>
  <b>③ 竞猜是拉人神器不是收钱模块</b>——参与 {CANYU:,} 人（=窗口总付费人数的 3.2 倍）vs 付费 {fmt(wm['竞猜礼包全档']['rev'])}/160人（转化 1.2%），价值在触达和活跃，变现靠外显档；奖励逐轮升级（W6）没能逆转付费档衰减。</p>
</div>

<div class="page">
<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{N_OK} 条</div><div class="kpi-lbl">验证有效</div><div class="kpi-sub">W3外显进档 · W7扩服 · W8免费下调 · D3大富翁 · D5每日礼包 · D7存钱罐</div></div>
  <div class="kpi r"><div class="kpi-val">{N_BAD} 条</div><div class="kpi-lbl">证伪</div><div class="kpi-sub">D1双周节奏（同开无错峰）· D2转盘形式（判退役）</div></div>
  <div class="kpi y"><div class="kpi-val">{N_MID} 条</div><div class="kpi-lbl">部分有效/存疑</div><div class="kpi-sub">W1竞猜 · W2锚点（基数效应）· W5本服榜 · W6逐轮升级 · D4双BP · D6周卡</div></div>
  <div class="kpi"><div class="kpi-val">{N_WAIT} 条</div><div class="kpi-lbl">待查</div><div class="kpi-sub">W4补钻VIP（无从分离）· D8删折扣券 · D9珍珠贝</div></div>
</div>

<div class="sec" id="sec0"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">世界杯模块全景：各模块收入 × 是否符合该活动类型的预期（6/26-{END[5:]} · 全服 · 总付费 {WC['payers']:,} 人）</div></div>
<div class="card"><div class="ct">模块收入底图 · 悬停看 渗透/ARPPU/复购/max ｜ 许愿池=深海模块，已从世界杯口径剔除</div>
{module_bar(wm, WC_ORDER)}
</div>
<div class="card"><div class="ct">逐模块 · 效果数据 vs 类型基准</div>
{wc_panorama()}
<div class="cb cb-info"><b>结论：世界杯四个收入模块两级分化——开箱族超预期（六代最高+首次破墙），BP 符合预期（形式没动就没变化），竞猜触达超预期但变现远不达预期。</b>收入结构 = 开箱 {fmt(KX['rev'])} &gt; BP {fmt(wm['通行证(130020/21)']['rev'])} &gt; 竞猜 {fmt(wm['竞猜礼包全档']['rev'])}；参与结构完全倒过来 = 竞猜 {CANYU:,} 人 &gt; 兑换 {DH['users']:,} 人 &gt; BP 550 人 &gt; 开箱 387 人——<b>世界杯用竞猜聚人、用开箱收钱，两头都成立，缺的是把 13k 参与者往付费漏斗里送的中间层</b>（$0.99-4.99 宽入口缺位，P2 三板斧的第三板）。</div>
</div></div>

<div class="sec" id="seckx"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">世界杯开箱效果分析：对比夏日开箱 × 情人节开箱</div></div>
<div class="bigcon">大结论：<b>世界杯开箱本体付费效果接近夏日，没有受到双节叠开和竞猜礼包的挤压，效果稳定——可以继续开。</b><br>
<span style="font-size:13px;line-height:2.1">
① <b>头衔+排行榜有效</b>——仅限玩家对深度有需求的排行（跨服榜 1-5 名头衔点燃塔尖 $1,415/$1,330）；<br>
② <b>本服排行榜：需增加有效投放</b>（当前投放吸引力不足，每服 top1 中位 $60 未超夏日）；<br>
③ <b>特殊形式礼包加付费深度：有效</b>——没有挤压到原有的活动付费（开箱本体稳定的前提下多出竞猜/外显档增量）；<br>
④ <b>世界杯皮肤转视频基本不影响收入</b>（Top20 稳定）——可以考虑拓展皮肤投放量、提升皮肤品质，做出<b>双层排行榜需求</b>（类似 P2 主城皮肤的高低档分层）；<br>
⑤ <b>锚点礼包加 VIP 点数：无影响</b>（买家增长为服基数效应，改动本身无净效果）。
</span></div>
<div class="chips">
  <button class="chip on" data-v="kx1">历史数据对比</button>
  <button class="chip" data-v="kx2">转化率·大众段</button>
  <button class="chip" data-v="kx3">转化率·$100以上</button>
  <button class="chip" data-v="kx4">皮肤/头衔 · Top20</button>
  <button class="chip" data-v="kx5">锚点礼包</button>
  <button class="chip" data-v="kx6">本服排行榜</button>
  <button class="chip" data-v="kx7">付费率下钻·新老服</button>
</div>

<div class="view on" id="kx1"><div class="vc">人均三代横盘（$54 → $48 → $52）、复购持平——本体效果 = 正常水平；规模（买家 387）与 max 极值（$1,415）的增长主要来自服基数和 20 天长窗。</div>
<div class="card"><div class="ct">历史数据对比（情人节/夏日/世界杯） · 绝对值受服数/窗口影响，看比率 · 付费率分母见表下注</div>
{kx_table()}<div style="height:10px"></div>{kx_panels()}
</div></div>

<div class="view" id="kx2"><div class="vc">大众段（$0-100）四代分布几乎完全重合——形式改动没有改变大众付费结构。</div>
<div class="card"><div class="ct">四代开箱付费分布 · 大众段（含元旦 · 纵轴=买家占比）</div>
{kx_dist_chart('bucketA', 10, 10, lambda i: f'${{i*10}}-{{i*10+10}}', '>$100', '图A · 大众段 $0-100（每$10一档）')}
</div></div>

<div class="view" id="kx3"><div class="vc">中层（$100-500）没有加深，世界杯只在最右端开了一条缝（max $1,415，六代首次过 $707）。</div>
<div class="card"><div class="ct">四代开箱付费分布 · $100 以上（分母同为该代全部买家）</div>
{kx_dist_chart('bucketB', 19, 100, lambda i: (f'${{(i+1)*100}}-{{(i+2)*100}}' if i < 9 else f'${{(i+1)/10:.1f}}k-{{(i+2)/10:.1f}}k'), '>$2k', '图B · $100 以上（每$100一档 · 横轴=单人付费区间）')}
</div></div>

<div class="view" id="kx4"><div class="vc">头衔在塔尖有效、但只传导到前 2 名——跨服榜第 1-5 名挂"世界之巅"头衔（配置实证），全服 Top2 的 $1,415/$1,330 极值就是争头衔的塔尖竞争；但第 3 名起立刻回落到 $535，Top20 群体、分位数 p95/p99 都没被拉起——头衔证明了外显竞争的付费力，缺的是向下分层的梯子（P2 式 top3 染色/top30 分层让更多人咬）。老服 ARPPU $48→$52 的"深度提高"主要是构成效应（免费券替代低档买家后的均值抬升），不是群体加深。</div>
<div class="card"><div class="ct">Top20 付费额度阶梯 · 悬停看每名次金额 · 下方=各代核心投放注释</div>
{kx_top20_chart()}
{top20_notes()}
<div class="cb cb-info">读法对照 P2 圣诞（上榜线 $1,444/上榜者中位 $2,529，排行皮肤+染色分层让 Top30 互相咬）：X3 头衔只有 1 档、皮肤 top20+ 人人一样，没有分层就没有梯队——世界杯全服 Top2 与第 3 名之间 $800 的断崖就是"缺梯子"的形状。</div>
</div></div>

<div class="view" id="kx5"><div class="vc">锚点 = 正常的 $4.99 小额位；买家 153 人的增长主要是服基数效应（扩服 28+年轻服），不是改动的正向效果；「可复购」是伪归因（配置与前代完全一致）。</div>
<div class="card"><div class="ct">锚点礼包四代对比 + 世界杯锚点按档拆分</div>
{anchor_card()}
<div class="cb cb-info">配置 diff：211012-15 与情人 210712-15 限购列完全一致（差异仅 id/备注/奖励组），情人锚点 max $910 证明前代本来就能复购。95% 买家集中 $4.99 档、高档无人（$49.99 两人 / $99.99 三人）= 价格锚+小额位定位的正常发挥。</div>
</div></div>

<div class="view" id="kx6"><div class="vc">本服排行榜效果有限——窗口近 2 倍长，每服 top1 中位 $60 反而低于夏日 $75，服均仅持平；需要调整投放提升吸引力（并先确认客户端本服 Tab 是否真露出）。</div>
<div class="card"><div class="ct">逐服开箱付费对比 · 榜=活动全程拉通累计</div>
{perserver_card()}
<div class="cb cb-info">⚠️判定前置：该榜配置时标注"客户端双 Tab 露出需程序联调、占位性质"——若未露出，这条是"没上线"而非"无效"，下届补露出后再验一次。</div>
</div></div>

<div class="view" id="kx7"><div class="vc">付费率差距两层：①新服稀释——扩服段只有 7.7%，把全口径拉到 9.6%；②老服成熟段真实下降 20.1% → 13.2%（买家 245 → 133 近腰斩），主因是券供给结构变了：世界杯把开箱券做成竞猜大众奖励，券触达 ×3.9（5,629 → 21,878 人），免费供给替代了 $4.99 入场档的购买动机。夏日付费率的"强点"= 券稀缺、想抽就得买。ARPPU 反而更高（$52 vs $48）——竞猜抢走的不是开箱的钱，是开箱的低档买家。</div>
<div class="card"><div class="ct">新老服拆分 · 券供给对比 · 档位买家梯子</div>
{payrate_drill()}
<div class="cb cb-info">口径注：①窗口机械效应已排除——世界杯 20 天成熟段总付费人数（1,008）反而少于夏日 11 天（1,217），分母没有被长窗撑大；②券来源按 reason 前缀分类有少量污染，但两代总供给/触达对比与免费竞猜档直发数（894尾0=13,315 人/21.1 万张）干净；③中奖邮件加送券为"其他"桶主体（百万级）。</div>
</div></div>
</div>

<div class="sec" id="secjc"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">世界杯竞猜回归 · 整体（6/26-{END[5:]} · 全服）</div></div>
<div class="bigcon">大结论：<b>竞猜是 X3 史上最宽的活动入口（参与 {CANYU:,} 人 = 窗口总付费人数的 3.2 倍），且参与不随淘汰赛缩圈衰减；但它不是收钱模块——付费 {fmt(wm['竞猜礼包全档']['rev'])}/160 人（转化 1.2%）且逐轮衰减，付费主力是搭售的外显两档（81%）。定性 = 拉人和活跃的模块，变现靠外显搭售。</b><br>
<span style="font-size:12.5px">整体指标：付费玩家付费率 <b>{wm['竞猜礼包全档']['buyers']/WC['payers']*100:.1f}%</b>（对照 开箱族 {KX['buyers']/WC['payers']*100:.1f}% · 通行证 {wm['通行证(130020/21)']['buyers']/WC['payers']*100:.1f}%）｜ ARPU <b>${wm['竞猜礼包全档']['rev']/WC['payers']:.2f}</b> ｜ ARPPU <b>${wm['竞猜礼包全档']['arppu']:.1f}</b> ｜ 复购 {wm['竞猜礼包全档']['opb']:.1f} 单 ｜ max {fmt(wm['竞猜礼包全档']['max'])}</span></div>
<div class="chips">
  <button class="chip on" data-v="jc0">基本付费分析</button>
  <button class="chip" data-v="jc1">参与逐日</button>
  <button class="chip" data-v="jc2">按轮：参与 vs 付费</button>
  <button class="chip" data-v="jc3">档位结构</button>
  <button class="chip" data-v="jc4">新老服拆分</button>
</div>

<div class="view on" id="jc0"><div class="vc">买了的人花得不少（ARPPU $44 与开箱 $52 同级、复购 4.1 全场最高），但付费玩家付费率只有 4.4%——不到开箱（9.6%）的一半、通行证（13.0%）的三分之一；p90 $100、$500+ 仅 1.2%，头部薄。竞猜缺的不是客单，是把 1.3 万参与者转成买家的那一步。</div>
<div class="card"><div class="ct">竞猜基本付费指标 · 开箱/通行证同窗参照</div>
{jc_pay_table()}
</div></div>

<div class="view" id="jc1"><div class="vc">参与由比赛日驱动、20 天全程有脉冲无衰减——按轮 7.3k → 10.8k → 8.7k → 8.2k，淘汰赛缩圈不缩人。作为拉活跃入口，生命力贯穿全程。</div>
<div class="card"><div class="ct">参与逐日曲线 · 轮次色带 · 悬停看数</div>
{jc_daily_chart()}
</div></div>

<div class="view" id="jc2"><div class="vc">参与和付费背离：人越聚越多，付费日均 $410 → $158 逐轮走低——奖励逐轮升级没能逆转（见 04 章 W6）。</div>
<div class="card"><div class="ct">按轮对比 · 同轮次窗口</div>
{jc_rounds_chart()}
</div></div>

<div class="view" id="jc3"><div class="vc">付费主力是外显两档（$5,696 · 占 81%），纯券档只卖 $1,332——竞猜本体被玩家当免费玩法，13,315 参与者是全场最大的未转化流量池。</div>
<div class="card"><div class="ct">档位结构 · 付费率分母=世界杯窗口全服总付费人数</div>
{jc_tier_table()}
<div class="cb cb-info">改造方向 = P2 猜酒杯形式（充值即参与 + 排行强循环），量级参考 07-10 漏斗推算（修到猜酒杯转化水平 ≈ 6.5×）。</div>
</div></div>

<div class="view" id="jc4"><div class="vc">参与近一半来自扩服新服（6,493 人·49%）——新服玩家最爱玩竞猜、白嫖盘最大；但参与→付费转化三段均匀地低（老服 1.3% / 年轻服 1.6% / 新服 1.0%）——付费弱不是人群问题，是形式问题（哪个段都不买"加成券"）；年轻老服客单最高（ARPPU $67）。</div>
<div class="card"><div class="ct">竞猜新老服拆分 · 参与 / 转化 / 付费率 / ARPPU</div>
{jc_srv_table()}
<div class="cb cb-info">口径：竞猜部署 83 服（55 老服 1170-1970 + 28 扩服）；参与=asset 894% 去重、付费=894 订单；付费率分母=该段窗口总付费人数。</div>
</div></div>
</div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">世界杯 8 条改动逐条效果</div></div>
<div class="card">
{table(WC_ROWS)}
<div style="margin-top:14px">{round_bar()}</div>
<div class="cb cb-info"><b>结论：世界杯的钱在开箱（{fmt(wm['开箱福箱连锁']['rev'] + wm['开箱券锚点(可复购)']['rev'])}）和通行证（{fmt(wm['通行证(130020/21)']['rev'])}），竞猜的价值在人（13,315 参与）。</b>开箱 = 正常发挥未被挤压；外显进付费档是唯一结构性正信号（马戏节照抄）；中层加深要靠别的手段（阶段奖励宝箱/随机双轨）。</div>
</div></div>

<div class="sec" id="sec2"><div class="sec-head"><div class="sec-num">05</div><div class="sec-title">深海节 9 条改动（7/3-{END[5:]} · 59服 · 总付费 {DS['payers']:,} 人）——待聊，先过完世界杯</div></div>
<div class="card"><div class="ct">模块收入底图 · 悬停看 渗透/ARPPU/复购/max</div>
{module_bar(dm, DS_ORDER)}
</div>
<div class="card">
{table(DS_ROWS)}
<div class="cb cb-info"><b>结论：深海的结构是"大富翁族压舱（$21.7k）+ BP 铺渗透（630 买家）+ 送达层首次成型（每日礼包 290 人）"，输在转盘（形式老化）和节奏（同开无错峰）。</b>零销售注：藏宝图锚点 $0（纯价格锚）；头像框 211019 $0 = <b>实际未上架</b>（该外显改进了 BP 奖励发放），不构成直售反例。</div>
</div></div>

<div class="footer">X3 双节框架回归 · 母题4 改动效果清单 · 数据源=Trino v1090 全口径（_l1_refresh.py → _l1_m4.json） · 生成 {now}</div>
</div></div>
<script>
document.querySelectorAll('.chips').forEach(function(g){{
  var sec = g.parentElement;
  g.querySelectorAll('.chip').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      g.querySelectorAll('.chip').forEach(function(b){{ b.classList.remove('on'); }});
      btn.classList.add('on');
      sec.querySelectorAll('.view').forEach(function(v){{ v.classList.remove('on'); }});
      var t = sec.querySelector('#' + btn.dataset.v);
      if (t) t.classList.add('on');
    }});
  }});
}});
</script>
</body></html>"""

open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
print(f"判定: 有效{N_OK} / 部分{N_MID} / 证伪{N_BAD} / 待查{N_WAIT}")
