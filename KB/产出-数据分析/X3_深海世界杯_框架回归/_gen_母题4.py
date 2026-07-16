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
  '<b>锚点买家 ×2.8、长成 $4.99 小额复购位</b>——四代锚点买家 48/53/55 → 153 人（占开箱买家 20-22%→40%），95% 集中在 $4.99 档；⚠️归因修正：配置 diff 证实限购列与前代完全一致（情人锚点 max $910=历来可复购），「可复购」是伪归因，真实变化=W4 补钻VIP + 竞猜引流',
  f"锚点 {fmt(wm['开箱券锚点(可复购)']['rev'])} · 153人 · $4.99档 145人", 'ok'),
 ('W3', '外显进付费档<br><span class="dim">$9.99框宝箱 / $19.99表情宝箱 · 开箱大奖=皮肤</span>',
  '<b>外显是付费主力</b>——竞猜侧外显两档卖 {}（占竞猜付费 81%，是纯券档的 4.3 倍）；开箱侧 max <b>$1,415</b>=六代第一次破 $707 买光墙',
  f"框档 {fmt(wm['竞猜$9.99框档(尾2)']['rev'])} + 表情档 {fmt(wm['竞猜$19.99表情档(尾3)']['rev'])} · 开箱max {fmt(wm['开箱福箱连锁']['max'])}", 'ok'),
 ('W4', '全节日锚点礼包补钻石+VIP<br><span class="dim">B线纯券→对齐A线（6/24 v0.41）</span>',
  '<b>锚点买家 ×2.8 的最可能归因</b>——"可复购"证伪后（02章③），钻VIP价值感提升是 WC 锚点与前代唯一的实质配置差异；与竞猜引流不可完全分离，老节日锚点的后续表现下届可当对照',
  '与 W2 同一效果的归因侧', 'mid'),
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
    tr.append("<div class='dim' style='margin-top:6px'>*本卡四代统一不加服过滤（各代全部部署服），与上方三代对打表（按服段筛选）绝对值不同；占开箱买家分母=同口径开箱族买家。</div>")
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
    <a class="sb-item" href="#sec1">03 · 世界杯 8 条改动</a>
    <a class="sb-item" href="#sec2">04 · 深海节 9 条（待聊）</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 双节框架回归 · 母题4：本届 17 条改动，每条一句话效果<br><em>验证 {N_OK} · 部分 {N_MID} · 证伪 {N_BAD} · 待查 {N_WAIT}</em></h1>
  <div class="meta">窗口 <b>世界杯 6/26-{END[5:]} 全服 · 深海 7/3-{END[5:]} 59服</b> · 数据 <b>Trino v1090 订单全口径（_l1_m4.json）</b> · 决赛/尾段未入，7/21 重跑 _l1_refresh.py 刷终版 · 生成 {now}</div>
</div>

<div class="verdict" id="verdict">
  <div class="vl">VERDICT · 结论先行</div>
  <p><b>① 最硬的两条正结论：锚点可复购（W2）+ 外显进付费档（W3）</b>——锚点买家 ×2.8（48-55→153 人，占开箱买家 40%，长成 $4.99 小额复购位；「可复购」经配置 diff 证伪，真实归因=补钻VIP+竞猜引流）；max $1,415 六代第一次凿穿 $707 买光墙；竞猜侧外显两档占付费 81%。但要说清边界：<b>开箱人均三代横盘 $48-54，改动打开的是渗透和头部、不是中层</b>（详见 02 章）。
  <b>② 最大的两条证伪：转盘连锁形式（D2，判退役坐实+锚点零购买）和双周节奏（D1，部署同开=没有弹药带）。</b>
  <b>③ 竞猜是拉人神器不是收钱模块</b>——参与 {CANYU:,} 人（=窗口总付费人数的 3.2 倍）vs 付费 {fmt(wm['竞猜礼包全档']['rev'])}/160人（转化 1.2%），价值在触达和活跃，变现靠外显档；奖励逐轮升级（W6）没能逆转付费档衰减。</p>
</div>

<div class="page">
<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{N_OK} 条</div><div class="kpi-lbl">验证有效</div><div class="kpi-sub">W2锚点复购 · W3外显进档 · W7扩服 · W8免费下调 · D3大富翁 · D5每日礼包 · D7存钱罐</div></div>
  <div class="kpi r"><div class="kpi-val">{N_BAD} 条</div><div class="kpi-lbl">证伪</div><div class="kpi-sub">D1双周节奏（同开无错峰）· D2转盘形式（判退役）</div></div>
  <div class="kpi y"><div class="kpi-val">{N_MID} 条</div><div class="kpi-lbl">部分有效/存疑</div><div class="kpi-sub">W1竞猜（触达强变现弱）· W4锚点归因 · W5本服榜 · W6逐轮升级 · D4双BP · D6周卡</div></div>
  <div class="kpi"><div class="kpi-val">{N_WAIT} 条</div><div class="kpi-lbl">待查</div><div class="kpi-sub">D8删折扣券 · D9珍珠贝</div></div>
</div>

<div class="sec" id="sec0"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">世界杯模块全景：各模块收入 × 是否符合该活动类型的预期（6/26-{END[5:]} · 全服 · 总付费 {WC['payers']:,} 人）</div></div>
<div class="card"><div class="ct">模块收入底图 · 悬停看 渗透/ARPPU/复购/max ｜ 许愿池=深海模块，已从世界杯口径剔除</div>
{module_bar(wm, WC_ORDER)}
</div>
<div class="card"><div class="ct">逐模块 · 效果数据 vs 类型基准</div>
{wc_panorama()}
<div class="cb cb-info"><b>结论：世界杯四个收入模块两级分化——开箱族超预期（六代最高+首次破墙），BP 符合预期（形式没动就没变化），竞猜触达超预期但变现远不达预期。</b>收入结构 = 开箱 {fmt(KX['rev'])} &gt; BP {fmt(wm['通行证(130020/21)']['rev'])} &gt; 竞猜 {fmt(wm['竞猜礼包全档']['rev'])}；参与结构完全倒过来 = 竞猜 {CANYU:,} 人 &gt; 兑换 {DH['users']:,} 人 &gt; BP 550 人 &gt; 开箱 387 人——<b>世界杯用竞猜聚人、用开箱收钱，两头都成立，缺的是把 13k 参与者往付费漏斗里送的中间层</b>（$0.99-4.99 宽入口缺位，P2 三板斧的第三板）。</div>
</div></div>

<div class="sec" id="seckx"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">世界杯开箱效果分析：对打夏日开箱 × 情人节开箱（同方法·各自窗口）</div></div>
<div class="cb cb-warn" style="margin:0 0 14px"><b>本章判定：世界杯开箱本体付费效果接近夏日，没有受到双节叠开和竞猜礼包的挤压，效果稳定——可以继续开；本服排行榜目前效果比较有限，需要调整投放提升吸引力。</b>（分项证据见下 ①-④）</div>
<div class="card"><div class="ct">三代开箱对打 · 绝对值受服数/窗口影响，看比率（ARPPU/复购/占比/max）</div>
{kx_table()}
{kx_panels()}
<div class="cb cb-info"><b>结论：世界杯开箱的提升在"规模"和"头部"，不在"人均"。</b>
① <b>人均横盘</b>——三代 ARPPU $54 → $48 → $52、复购 4.8/4.2/4.5、p50 $5-9，大众段付费结构基本没动（此前"+35%人均爬升"是 D0-D10 同窗口径，全窗被长尾稀释后不成立）。
② <b>锚点买家 ×2.8、集中在 $4.99 档</b>——统一口径四代锚点买家 48/53/55 → 153 人（占开箱买家 20-22% → 40%），做成了低门槛复购位；代价是锚点 ARPPU 走低（$24-56 → $19），拉渗透不拉深度。⚠️归因修正见 ③：「可复购」是伪归因，真实变化=补钻VIP+竞猜引流。
③ <b>天花板打开一条缝</b>——max $555/$550 → $1,415，六代首次有人花过 $707 买光墙；但 $100+ 占比 16%→14%→12% 反而略降：<b>被打开的只是极个别头部，中层（$100-500）没有被加深</b>。
④ 收入 $4.7k → $11.8k → $20.1k 的放大主要来自服基数和 20 天长窗，不能直接归功于形式改动。</div>
</div>

<div class="card"><div class="ct">① 转化率分析 · 四代开箱付费分布（含元旦 · 纵轴=买家占比 · 分段等宽桶双图）</div>
{kx_dist_chart('bucketA', 10, 10, lambda i: f'${i*10}-{i*10+10}', '>$100', '图A · 大众段 $0-100（每$10一档）')}
<div style="height:10px"></div>
{kx_dist_chart('bucketB', 19, 100, lambda i: (f'${(i+1)*100}' if i < 9 else f'${(i+1)/10:.1f}k'), '>$2k', '图B · 鲸鱼段 $100+（每$100一档 · 分母同为该代全部买家）')}
<div class="cb cb-info"><b>结论：四代开箱的付费分布形状高度重合——大众段（$0-100）四条线几乎叠在一起，$100+ 段世界杯的中层（$100-500）占比不高于前三代，唯一差别是尾巴延伸到 $1.4k。</b>分布图直观印证 02 章判断：形式改动没有改变开箱的付费结构，只在最右端开了一条缝。</div>
</div>

<div class="card"><div class="ct">② 皮肤付费效果 · 四代分位数对打（世界杯=首代把皮肤放进开箱大奖+排行榜）</div>
{kx_quantile_chart()}
<div class="cb cb-info"><b>结论：皮肤进大奖没有系统性拉高头部付费——p95（$302 vs 元旦$260/夏日$325）、p99（$460 vs 元旦$610/情人$555）都在历代区间内甚至偏低，头部群体没有因为皮肤而加深，唯一变化是 1 个 $1,415 极值。</b>对照 P2 圣诞排行皮肤（上榜线 $1,444 / 上榜者中位 $2,529）：X3 的跨服榜没有形成头部竞争——皮肤作为大奖"有钩没梯"，从 p99 $460 到上榜线之间缺可花钱的台阶（P2 的做法是排行皮肤+染色分层让 Top30 互相咬）。</div>
</div>

<div class="card"><div class="ct">③ 锚点礼包四代对比 + 世界杯锚点按档拆分</div>
{anchor_card()}
<div class="cb cb-info"><b>结论：锚点买家 ×2.8（48-55 → 153 人），几乎全部集中在 $4.99 档（145/153 人，复购 1.8）——锚点实际长成了"$4.99 小额复购位"。归因修正：「锚点可复购」是伪归因</b>——配置 diff 显示 211012-15 与情人 210712-15 的限购列完全一致（差异仅 id/备注/奖励组），且情人锚点 max $910 证明前代本来就能复购；WC 锚点增长的真实归因 = 补钻石+VIP（6/24 v0.41，价值感提升）+ 竞猜带来的流量。高档基本无人（$49.99 两人/$99.99 三人）＝锚点当不了深度工具，符合价格锚+小额位的定位。</div>
</div>

<div class="card"><div class="ct">④ 本服排行榜效果 · 逐服开箱付费对比（榜=活动全程拉通累计）</div>
{perserver_card()}
<div class="cb cb-info"><b>结论：本服排行榜（6/24 新增）效果未显现——拉通口径下世界杯窗口近 2 倍长，每服 top1 中位 $60 反而低于夏日 $75，服均收入 $261 仅持平（$240），top1≥$100 的服占比也没抬升：榜没把各服头部的开箱付费拉起来。</b>⚠️判定前置条件待确认：该榜配置时明确标注"客户端同时显示跨服+本服两 Tab 需程序联调、占位性质"——需先确认线上客户端是否真露出了本服 Tab；若未露出，这条是"没上线"而非"无效"，下届补露出后再验一次。</div>
</div></div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">世界杯 8 条改动逐条效果</div></div>
<div class="card">
{table(WC_ROWS)}
<div style="margin-top:14px">{round_bar()}</div>
<div class="cb cb-info"><b>结论：世界杯的钱在开箱（{fmt(wm['开箱福箱连锁']['rev'] + wm['开箱券锚点(可复购)']['rev'])}）和通行证（{fmt(wm['通行证(130020/21)']['rev'])}），竞猜的价值在人（13,315 参与）。</b>两条形式改动（锚点可复购+外显进档）的实际战果=锚点买家×2.8 + 头部破墙，人均横盘——马戏节照抄这两条起步，但中层加深要靠别的手段（阶段奖励宝箱/随机双轨）。</div>
</div></div>

<div class="sec" id="sec2"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">深海节 9 条改动（7/3-{END[5:]} · 59服 · 总付费 {DS['payers']:,} 人）——待聊，先过完世界杯</div></div>
<div class="card"><div class="ct">模块收入底图 · 悬停看 渗透/ARPPU/复购/max</div>
{module_bar(dm, DS_ORDER)}
</div>
<div class="card">
{table(DS_ROWS)}
<div class="cb cb-info"><b>结论：深海的结构是"大富翁族压舱（$21.7k）+ BP 铺渗透（630 买家）+ 送达层首次成型（每日礼包 290 人）"，输在转盘（形式老化）和节奏（同开无错峰）。</b>两个零销售要记住：藏宝图锚点 $0（纯价格锚）、头像框 211019 $0（外显单卖 $9.99 无人买——对比外显进抽奖档卖爆，<b>外显要进玩法不要单摆货架</b>）。</div>
</div></div>

<div class="footer">X3 双节框架回归 · 母题4 改动效果清单 · 数据源=Trino v1090 全口径（_l1_refresh.py → _l1_m4.json） · 生成 {now}</div>
</div></div>
</body></html>"""

open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
print(f"判定: 有效{N_OK} / 部分{N_MID} / 证伪{N_BAD} / 待查{N_WAIT}")
