# -*- coding: utf-8 -*-
"""X3 挖孔 v3「X3 标准弹窗形态」静态图生成器（1080×1920）

v2 的错：把 9 个 panel 子面板画成了「独立整屏页」（自带标题+倒计时+规则钮的页头）。
v3 只换外壳不换内容：
  - 底层 = 挖孔活动主界面（透出）
  - 中层 = 全屏 mask
  - 上层 = X3 标准弹窗壳（img_cm_bg_tanchu 浅米底板 + img_cm_biaoti 660×88 标题板 + 104×104 关闭钮）
壳规格来自真弹窗逐节点解析：Activity/UIActvIdleReward.prefab、Activity/UIActvLuckyWheelProb.prefab
  Animation 1025.93×1213.01 / BG stretch / BG(title) 660×88 @pos(0,-21)
  Title h85 fs46 #F7E497 @pos(0,-63.5) / btn_close 104×104 @pos(-69,-67.4) 右上
  Content 920.74×949.5 @pos(0.74,-43.52)  → 距壳顶 175 / 壳底留 88 给 CTA
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D5 = json.load(open(os.path.join(HERE, 'D5.json'), encoding='utf-8'))
ASSETS = set(os.listdir(os.path.join(HERE, 'assets')))

ITEM, TRS, LV, RANK, EXC, PKG, ACT = D5['ITEM'], D5['TRS'], D5['LV'], D5['RANK'], D5['EXC'], D5['PKG'], D5['ACT']
HOE, RADAR, COIN = 111111000, 111110300, 11119905
DKPOOL = sorted([a for a in ASSETS if a.startswith('dk1511')])
X = 'assets/x3/'

# ---- 弹窗壳几何（真 prefab 值） ----
SHELL_W_TALL, SHELL_H_TALL = 1025, 1213     # UIActvIdleReward / UIActvLuckyWheelProb 的 Animation
SHELL_W_STD = 1020                           # img_cm_bg_tanchu 原图 1022×458，标准宽 1020
CT_TOP = 175                                 # Content 距壳顶
CT_W = 920                                   # Content 宽（= 官方 920.74）


def nm(i):
    i = str(i)
    return (ITEM.get(i, {}).get('nm', '道具' + i)).replace('{0}', '1').replace('{1}', '').strip()


NAME_FIX = {str(HOE): '能量铲', str(RADAR): '探测仪', str(COIN): '核心电量',
            '111111046': '蓝色卡包', '111111047': '绿色卡包', '111111048': '白色卡包',
            '111110350': '异星拓荒者奖牌', '111130002': '紫电苍龙·组件', '111130003': '紫电苍龙·组件'}


def nm2(i):
    return NAME_FIX.get(str(i), nm(i))


def icon(i):
    i = int(i)
    if i == HOE: return 'assets/DigKeyIcon.png'
    if i == RADAR: return 'assets/Icon1.png'
    if i == COIN: return 'assets/IconDigKeyguaji.png'
    dk = ITEM.get(str(i), {}).get('dk', 0)
    if 'it%s.webp' % dk in ASSETS: return 'assets/it%s.webp' % dk
    return 'assets/' + DKPOOL[(dk or i) % len(DKPOOL)]


HEAD = '<meta charset="utf-8"><title>%s</title><link rel="stylesheet" href="ui3.css">'


def page(t, body):
    return '<!doctype html><html><head>%s</head><body><div class="stage">%s</div></body></html>' % (HEAD % t, body)


# ================================================================ 通用件
def item_cell(iid, cnt=None, size=155, name=None, got=False, top=0, left=0, pos=True):
    s = 'left:%dpx;top:%dpx;' % (left, top) if pos else ''
    h = '<div class="%s" style="%swidth:%dpx;height:%dpx;font-size:%dpx;position:%s">' % (
        'item named' if name else 'item', s, size, size, size, 'absolute' if pos else 'relative')
    h += '<img class="ic" src="%s">' % icon(iid)
    if cnt:
        h += '<div class="cnt">×%s</div>' % cnt
    if name:
        h += '<div class="nmp">%s</div>' % name
    if got:
        h += '<div class="got"><img src="%s"></div>' % (X + 'img_TXDS_icon_gou.png')
    return h + '</div>'


def slider(w, h, pct, txt='', left=None, top=None):
    st = 'width:%dpx;height:%dpx;' % (w, h)
    if left is not None:
        st += 'position:absolute;left:%dpx;top:%dpx;' % (left, top)
    return ('<div class="sldA" style="%s"><i style="width:%dpx"></i>%s</div>'
            % (st, int((w - 18) * pct), ('<span>%s</span>' % txt) if txt else ''))


def sbar(right, top, h, thumb_top, thumb_h):
    return ('<div class="sbar" style="right:%dpx;top:%dpx;height:%dpx"><i style="top:%dpx;height:%dpx"></i></div>'
            % (right, top, h, thumb_top, thumb_h))


def tier_row(top, no, label, items, state, price=None, orig=None, tag=None, note=None, reach=True,
             left=0, scale=1.0):
    """UIMultiTierPack.TierItem 1000×167 原件；v3 内缩到 920 内容区 → 整体 scale（内部比例不变）"""
    cls = 'tier' + (' done' if state == 'bought' else '') + (' reach' if reach else '')
    h = '<div class="%s" style="left:%dpx;top:%dpx;transform:scale(%.4f)">' % (cls, left, top, scale)
    h += '<div class="bg"></div>'
    h += '<div class="vline"><i style="height:%s"></i></div>' % ('196px' if reach else '0')
    h += '<div class="pt">%s</div>' % no
    h += '<div class="abs olL" style="left:118px;top:14px;font-size:30px;color:#5F4430;font-weight:bold">%s</div>' % label
    for j, (iid, cnt) in enumerate(items):
        h += item_cell(iid, cnt=cnt, size=118, left=118 + j * 128, top=44)
    if state == 'bought':
        h += '<div class="bought olL">已购买</div>'
    elif state == 'lock':
        h += ('<div class="abs" style="right:88px;top:36px;width:200px;height:100px;display:flex;flex-direction:column;'
              'align-items:center;justify-content:center;border-style:solid;border-width:0;'
              'border-image:url(%simg_cm_anniu_gold.png) 0 36 0 36 fill stretch;filter:grayscale(1) brightness(.78)">'
              '<img src="%simg_battlepass_icon_lock.png" style="width:28px;height:36px">'
              '<b style="font-size:26px;color:#313131">未解锁</b></div>' % (X, X))
    else:
        h += '<div class="btnBuy">'
        if orig:
            h += '<s>%s</s>' % orig
        h += '<b>%s</b></div>' % price
    if tag:
        h += '<div class="tag"><s>%s</s><b>%s</b></div>' % (tag[0], tag[1])
    if note:
        h += ('<div class="abs" style="right:60px;top:126px;width:260px;text-align:center;font-size:23px;'
              'color:#7F5F38">%s</div>' % note)
    return h + '</div>'


# ================================================================ 底层：挖孔活动主界面
def main_under(highlight=None, tipbar=True):
    """弹窗底下透出的挖孔主界面。highlight='pass' 时高亮通行证入口卡。"""
    b = '<div class="actBG"></div><div class="actBGfade"></div><div class="actBGlow"></div>'
    b += '<div class="actTitle ol">%s</div>' % ACT['nm']
    b += '<div class="actTime"><img src="%simg_gift_time.png"><span>距结束：剩余 2天 13:59:59</span></div>' % X
    b += '<div class="btnInfo"></div>'
    # 资源位（UIBtnProperty）
    b += ('<div class="abs seg13" style="right:23px;top:216px;width:400px;height:74px;display:flex;align-items:center;'
          'gap:12px;padding:0 24px">'
          '<img src="%s" style="width:52px;height:52px"><span style="font-size:32px;color:#EED376">1,240</span>'
          '<img src="%s" style="width:52px;height:52px;margin-left:18px">'
          '<span style="font-size:32px;color:#EED376">3</span></div>' % (icon(HOE), icon(RADAR)))

    def entry(side, w, ic, label, extra, flip=False, sel=False):
        h = '<div class="entry" style="%s:36px;top:352px;width:%dpx">' % (side, w)
        h += '<div class="eb"></div>'
        if sel:
            # 点击态：卡被按下的高亮圈（静态图示意，不是新增美术件）
            h += ('<div class="abs" style="left:22px;right:22px;top:-8px;bottom:-8px;'
                  'border:5px solid rgba(255,222,130,.98);border-radius:16px;'
                  'box-shadow:0 0 30px 10px rgba(255,196,52,.70),inset 0 0 22px rgba(255,222,130,.45)">'
                  '</div>')
        h += '<div class="ei" style="background-image:url(%s);%s"></div>' % (ic, 'transform:scaleX(-1)' if flip else '')
        h += '<div class="el ol">%s</div>' % label
        return h + extra + '</div>'

    b += entry('left', 400, X + 'img_TXDS_icon_rank.png', '排行榜',
               item_cell(RANK[0]['it'][0][0], size=100, left=142, top=10)
               + item_cell(RANK[0]['it'][1][0], size=100, left=250, top=10))
    pass_extra = (
        '<div class="abs" style="left:140px;top:12px;width:140px;height:44px;display:flex;align-items:center;'
        'justify-content:center;font-size:28px;color:#F7EBCE;border-style:solid;border-width:0;'
        'border-image:url(%simg_Activity_woodenstake_jdt_1.png) 13 16 16 15 fill stretch">Lv.2</div>'
        '<div class="abs" style="left:140px;top:66px;width:140px;text-align:center;font-size:24px;'
        'color:#EFDBBD">150 / 1,000</div>'
        '%s<div class="reddot" style="right:6px;top:-4px"></div>'
    ) % (X, item_cell(11116304, size=100, left=290, top=10))
    b += entry('right', 430, X + 'img_gift_icon_4.png', '通行证', pass_extra, flip=True,
               sel=(highlight == 'pass'))

    # 关卡标题条 + 5×5 棋盘
    b += '<div class="abs biaoti2 ol" style="left:390px;top:516px;width:300px">关卡 12</div>'
    b += ('<div class="abs" style="left:145px;top:610px;width:790px;display:grid;'
          'grid-template-columns:repeat(5,150px);grid-auto-rows:150px;gap:10px;justify-content:center">')
    for i in range(25):
        blk = i in (6, 7, 8, 16, 18)
        b += ('<div style="background:url(assets/gridcellbg%s.png) center/100%% 100%% no-repeat;%s"></div>'
              % ('3' if blk else '1', 'filter:brightness(.7) saturate(.4)' if blk else ''))
    b += '</div>'
    # 说明条
    if tipbar:
        b += ('<div class="abs seg13" style="left:30px;top:1450px;width:1020px;height:140px"></div>'
              '<div class="abs" style="left:70px;top:1482px;width:940px;text-align:center;font-size:30px;'
              'line-height:1.5;color:#EFDBBD">挖开地块 → 集齐探索目标 → 通关。<br>'
              '底部入口都是<span style="color:#EED376">弹窗</span>，开在这张主界面之上。</div>')
    # 底部功能栏（DailyGift 135 范式）
    fb = [('assets/IconDigKeyguaji.png', '挂机', True), ('assets/Icon2.png', '图鉴', False),
          ('assets/Icon1.png', '探测仪', False), ('assets/DigKeyShop.webp', '兑换', False),
          ('assets/DigPiggyIcon.png', '礼包', True)]
    b += ('<div class="abs" style="left:0;right:0;bottom:34px;display:flex;justify-content:space-around;'
          'align-items:flex-end">')
    for a, n, d in fb:
        b += ('<div style="position:relative;width:170px;display:flex;flex-direction:column;align-items:center;gap:6px">'
              '<div style="position:relative;width:135px;height:135px;background:url(%simg_cm_bg_iconkuang.png) '
              'center/100%% 100%% no-repeat;display:flex;align-items:center;justify-content:center">'
              '<img src="%s" style="width:100px;height:100px;object-fit:contain">%s</div>'
              '<div class="ol" style="font-size:28px;color:#EEDCC1">%s</div></div>'
              % (X, a, '<div class="reddot" style="right:-6px;top:-6px"></div>' if d else '', n))
    b += '</div>'
    return b


# ================================================================ 弹窗壳
def shell(title, inner, w=SHELL_W_TALL, h=SHELL_H_TALL):
    top = (1920 - h) // 2
    s = '<div class="popup" style="top:%dpx;width:%dpx;height:%dpx">' % (top, w, h)
    s += '<div class="popTitlePlate"></div><div class="popTitle">%s</div>' % title
    s += '<div class="popClose" style="left:%dpx"></div>' % (w - 121)
    return s + inner + '</div>'


def content(w_shell, h_content, inner, top=CT_TOP, w=CT_W):
    return ('<div class="popContent" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s</div>'
            % ((w_shell - w) // 2, top, w, h_content, inner))


def popup_page(title_txt, inner, w=SHELL_W_TALL, h=SHELL_H_TALL, highlight=None):
    return main_under(highlight) + '<div class="mask"></div>' + shell(title_txt, inner, w, h)


# ================================================================ 01 挂机领奖（弹窗）
# 真参照 Activity/UIActvIdleReward.prefab（30 GO）：Content 920×949 + 下方 UIBtnUse
def s01():
    W, H = SHELL_W_TALL, 1130
    ch = H - CT_TOP - 116          # 内容区高（底部 116 给 CTA）
    inner = ''
    # 无人机主图（P2 玩法图素）
    inner += ('<div class="abs" style="left:0;right:0;top:14px;text-align:center">'
              '<img src="assets/wurenji.png" style="width:264px"></div>')
    # 时长块（img_ledger_bg_taizhangliebiao 浅米行底 → 深字）
    inner += ('<div class="abs rowLB" style="left:26px;top:224px;width:868px;height:210px">'
              '<div class="abs olL" style="left:44px;top:26px;font-size:40px;color:#3E2411;font-weight:bold">'
              '离线挂机 <span style="color:#B0651F">4 小时 29 分</span></div>'
              '<div class="abs olL" style="right:44px;top:34px;font-size:30px;color:#7F5F38">上限 6 小时</div>'
              '%s'
              '<div class="abs olL" style="left:44px;top:154px;font-size:27px;color:#7F5F38">'
              '满 6 小时后停止累积，记得回来领取</div></div>'
              % slider(780, 56, .747, '04:29:00 / 06:00:00', left=44, top=86))
    # 本次可领取
    inner += '<div class="abs biaoti2 ol" style="left:26px;top:460px;width:868px">本次可领取</div>'
    rewards = [(COIN, '10,000'), (HOE, '20'), (RADAR, '2')]
    for j, (iid, cnt) in enumerate(rewards):
        inner += item_cell(iid, cnt=cnt, size=176, left=100 + j * 248, top=560, name=nm2(iid))
    inner += ('<div class="abs" style="left:26px;top:772px;width:868px;text-align:center;font-size:27px;'
              'color:#5F4430">核心电量可在无人机补给站兑换探测仪与纪念卡组件</div>')
    body = content(W, ch, inner)
    # CTA（UIBtnUse 位）：绿色领取钮 296×100
    body += ('<div class="abs btnGreen" style="left:%dpx;top:%dpx;width:340px;height:100px">领 取</div>'
             % ((W - 340) // 2, H - 108))
    return page('01 挂机领奖 v3弹窗', popup_page('欢迎回来', body, W, H))


# ================================================================ 03 存钱罐（弹窗）
# 真参照 ItemObtain/UIPiggyBankContent.prefab（920×520 内容面板）+ 标准弹窗壳
def s03():
    W, H = SHELL_W_TALL, 1000
    inner = ''
    # PiggyBank 内容面板 920×520（官方原件，直接嵌进 Content 区）
    inner += ('<div class="abs" style="left:0;top:0;width:920px;height:520px">'
              '<div class="abs" style="left:5px;top:8px;width:910px;height:504px;background:url(%sui_Howtogetit_bg_2.png) '
              'center/100%% 100%% no-repeat"></div>' % X)
    inner += ('<div class="abs" style="right:8px;top:58px;width:448px;height:404px;'
              'background:url(assets/DigPiggyIcon.png) center/contain no-repeat"></div>')
    inner += '<div class="disc" style="right:-14px;top:-14px;width:156px;height:156px"><s>价值</s><b>×3</b></div>'
    inner += ('<div class="abs" style="left:36px;top:36px;width:430px;height:448px;border-style:solid;border-width:0;'
              'border-image:url(%sui_Howtogetit_bg_3.png) 50 100 50 100 fill stretch"></div>' % X)
    inner += '<div class="abs ol" style="left:66px;top:60px;font-size:38px;color:#fff">能量存钱罐</div>'
    inner += ('<div class="abs" style="left:66px;top:118px;width:250px;height:50px;display:flex;align-items:center;'
              'gap:12px;padding:0 16px;border-style:solid;border-width:0;'
              'border-image:url(%sui_Howtogetit_bg_4.png) 16 50 16 50 fill stretch">'
              '<img src="assets/DigKeyIcon.png" style="width:44px;height:44px">'
              '<span style="font-size:36px;color:#fff">36 / 50</span></div>' % X)
    inner += ('<div class="abs" style="left:66px;top:188px;width:370px;height:54px;border-style:solid;border-width:0;'
              'border-image:url(%sui_piggybank_JDT_1.png) 12 10 12 10 fill stretch">'
              '<div class="abs" style="left:8px;top:8px;bottom:8px;width:%dpx;border-style:solid;border-width:0;'
              'border-image:url(%sui_piggybank_JDT_2.png) 12 fill stretch"></div>'
              '<div class="abs" style="inset:0;display:flex;align-items:center;justify-content:center;font-size:26px;'
              'color:#3C2A12;font-weight:bold">已存 72%%</div></div>') % (X, int(354 * .72), X)
    inner += ('<div class="abs" style="left:66px;top:252px;width:370px;font-size:25px;color:#EFDBBD;line-height:1.35">'
              '每消耗 2 个能量铲存入 1 个；存满 50 后停止累积。</div>')
    inner += '<div class="abs" style="left:66px;top:322px;font-size:26px;color:#EEDBBD">取出可得</div>'
    inner += item_cell(HOE, cnt=36, size=124, left=66, top=354)
    inner += item_cell(RADAR, cnt=2, size=124, left=206, top=354)
    inner += '</div>'
    # 说明（浅底 → 深字）
    inner += ('<div class="abs rowLB" style="left:20px;top:546px;width:880px;height:118px">'
              '<div class="abs olL" style="left:44px;top:22px;font-size:30px;color:#3E2411">取出后存钱罐清零，可继续存入</div>'
              '<div class="abs olL" style="left:44px;top:64px;font-size:27px;color:#7F5F38">'
              '活动结束时未取出的部分将失效，请在结束前取出</div></div>')
    ch = H - CT_TOP - 148
    body = content(W, ch, inner)
    body += ('<div class="abs" style="left:0;right:0;top:%dpx;text-align:center;font-size:28px;color:#8A6A3A">'
             '<span style="text-decoration:line-through">价值 $14.97</span></div>' % (H - 148))
    body += ('<div class="abs btnGold" style="left:%dpx;top:%dpx;width:420px;height:100px">取出　US$4.99</div>'
             % ((W - 420) // 2, H - 108))
    return page('03 存钱罐 v3弹窗', popup_page('能量存钱罐', body, W, H))


# ================================================================ 02 成就礼包（弹窗·大号壳）
def s02():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 88
    inner = ''
    # 进度块（照 UIActvCumRecharge 的 Layout 三行）
    inner += ('<div class="abs seg13" style="left:16px;top:16px;width:888px;height:140px"></div>'
              '<div class="abs" style="left:56px;top:36px;font-size:33px;color:#fff">已通关</div>'
              '<div class="abs" style="left:56px;top:76px;font-size:54px;color:#EFDBBD">'
              '<span style="color:#e85b23">17</span> / 120 关</div>'
              '<div class="abs" style="right:56px;top:44px;width:470px;text-align:right;font-size:28px;color:#EFDBBD;'
              'line-height:1.5">已解锁 3 档 · 已购 1 档 · 共 15 档<br>'
              '<span style="color:#EED376">再通关 3 关解锁第 4 档</span></div>')
    packs = [p for p in PKG if p['tab'] == 'achievement']
    prices = ['$0.99', '$1.99', '$2.99', '$4.99']
    y, SC = 176, 0.878          # 1000 → 878 宽，塞进 920 内容区（含滚动条留白）
    for k in range(4):
        st = 'bought' if k == 0 else ('lock' if k == 3 else 'buy')
        cont = [(HOE, '{:,}'.format(20 * (k + 2))), (RADAR, str(k + 2)), (COIN, '{:,}'.format(1000 * (k + 2)))]
        inner += tier_row(y, k + 1, '第 %d 档 · 通关第 %d 关解锁' % (k + 1, packs[k]['gate']), cont, st,
                          price='US' + prices[k],
                          note=('每人限购 1 次（已购）' if st == 'bought'
                                else ('还需通关 3 关' if st == 'lock' else '每人限购 1 次')),
                          reach=(k <= 2), left=14, scale=SC)
        y += int(167 * SC) + 10
    inner += ('<div class="abs rowLB" style="left:14px;top:%dpx;width:878px;height:112px">'
              '<div class="abs olL" style="left:44px;top:20px;font-size:32px;color:#3E2411">未解锁 · 第 5–15 档</div>'
              '<div class="abs olL" style="left:44px;top:62px;font-size:25px;color:#7F5F38">'
              '通关第 20 / 25 / 30 / 35 … 85 关后依次解锁</div>'
              '<div class="abs olL" style="right:40px;top:38px;font-size:30px;color:#7F5F38">展开 ▾</div></div>' % y)
    inner += sbar(8, 176, ch - 190, 0, 300)
    body = content(W, ch, inner)
    body += ('<div class="abs popNote" style="top:%dpx">列表竖向滚动 · 共 15 档（图内展示前 4 档 + 折叠段）</div>'
             % (H - 66))
    return page('02 成就礼包 v3弹窗', popup_page('异星探索·成就礼包', body, W, H))


# ================================================================ 10 直售礼包页（弹窗·大号壳）
def s10():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 88
    inner = ''
    inner += ('<div class="abs seg13" style="left:16px;top:16px;width:888px;height:104px"></div>'
              '<div class="abs" style="left:56px;top:38px;width:800px;font-size:29px;line-height:1.4;color:#EFDBBD">'
              '购买后道具立即到账，可直接用于挖掘。<span style="color:#EED376">每档每人限购 1 次</span>，'
              '活动结束前有效。</div>')
    packs = [p for p in PKG if p['tab'] == 'common']
    contents = [[(HOE, '30'), (RADAR, '1')], [(HOE, '80'), (RADAR, '3'), (COIN, '2,000')],
                [(HOE, '150'), (RADAR, '5'), (COIN, '5,000')], [(HOE, '320'), (RADAR, '10'), (COIN, '12,000')],
                [(HOE, '700'), (RADAR, '20'), (COIN, '30,000')], [(HOE, '1,800'), (RADAR, '50'), (COIN, '80,000')],
                [(HOE, '3,800'), (RADAR, '110'), (COIN, '180,000')]]
    disc = ['+20%', '+40%', '+80%', '+150%', '+250%', '+400%', '+700%']
    tiername = ['入门', '进阶', '实用', '超值', '豪华', '典藏', '至尊']
    y, SC = 138, 0.878
    for k in range(5):
        st = 'bought' if k == 1 else 'buy'
        pr = float(packs[k]['price'].strip('$'))
        orig = '$%.2f' % (pr * (1 + int(disc[k].strip('+%')) / 100.0))
        inner += tier_row(y, k + 1, '第 %d 档 · %s' % (k + 1, tiername[k]), contents[k], st,
                          price='US' + packs[k]['price'], orig=orig, tag=('超值', disc[k]),
                          note=('每人限购 1 次（已购）' if st == 'bought' else '每人限购 1 次'),
                          left=14, scale=SC)
        y += int(167 * SC) + 10
    inner += sbar(8, 138, ch - 152, 0, 560)
    body = content(W, ch, inner)
    body += ('<div class="abs popNote" style="top:%dpx">'
             '列表竖向滚动 · 共 7 档（第 6–7 档：典藏 US$49.99 / 至尊 US$99.99，继续下滑查看）</div>' % (H - 66))
    return page('10 直售礼包页 v3弹窗', popup_page('异星探索·补给礼包', body, W, H))


# ================================================================ 05 兑换商店（弹窗·大号壳）
# 真参照 Activity/UIActvExchange.prefab：Grid cell 300×380 spacing(20,80) → 3 列
# v3 内缩：内容区 920 → cell 290×360 spacing(20,52)，比例与官方一致
def s05():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 88
    inner = ''
    # 我的核心电量（货币位）
    inner += ('<div class="abs seg13" style="left:16px;top:14px;width:888px;height:86px;display:flex;align-items:center;'
              'gap:14px;padding:0 32px">'
              '<img src="%s" style="width:56px;height:56px">'
              '<span style="font-size:34px;color:#EED376">12,480</span>'
              '<span style="margin-left:auto;font-size:27px;color:#CBB89B">'
              '活动结束后核心电量将被回收，记得用完</span></div>' % icon(COIN))
    fn = {'111110300': '标出本关一个目标的位置', '111111048': '开出白色及以上卡组件',
          '111111047': '开出绿色及以上卡组件', '111111000': '挖掘地块的消耗道具',
          '111111046': '开出蓝色及以上卡组件'}
    for k, e in enumerate(EXC):
        gi, gn = e['get'][0]
        px = e['give'][0][1]
        cx, cy = k % 3, k // 3
        L, T = 5 + cx * 310, 118 + cy * 412
        inner += '<div class="abs" style="left:%dpx;top:%dpx;width:290px;height:360px">' % (L, T)
        inner += ('<div class="abs" style="inset:0;background:url(%simg_shop_bg_8.png) center/100%% 100%% no-repeat">'
                  '</div>' % X)
        inner += item_cell(gi, cnt=gn, size=194, left=48, top=22, name=nm2(gi))
        inner += ('<div class="abs olL" style="left:0;right:0;top:246px;text-align:center;font-size:28px;'
                  'color:#422919">剩余可兑换 %d 次</div>' % e['limit'])
        inner += ('<div class="abs" style="left:32px;top:288px;width:226px;height:58px;display:flex;align-items:center;'
                  'justify-content:center;gap:10px;background:url(%simg_VIP_bg_jindutiao_1.png) center/100%% 100%% '
                  'no-repeat"><img src="%s" style="width:44px;height:44px">'
                  '<span style="font-size:32px;color:#FFF6E9">%s</span></div>'
                  % (X, icon(COIN), '{:,}'.format(px)))
        inner += '</div>'
        inner += ('<div class="abs" style="left:%dpx;top:%dpx;width:290px;font-size:23px;color:#5F4430;'
                  'text-align:center;line-height:1.2;white-space:nowrap">%s</div>'
                  % (L, T + 370, fn.get(str(gi), '')))
    body = content(W, ch, inner)
    body += ('<div class="abs popNote" style="top:%dpx">每种道具的可兑换次数在活动期内共享，用完不再刷新</div>'
             % (H - 66))
    return page('05 兑换商店 v3弹窗', popup_page('无人机补给站', body, W, H))


# ================================================================ 04 玩法规则（弹窗·大号壳）
# 弹窗形态真参照 Activity/UIActvLuckyWheelProb.prefab（1025×1217 + 竖滚列表 + 关闭钮）
# 正文行沿用 UiActivityCommonRules 的 ItemTitle / ItemText 两种官方模板
def s04():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 68
    inner = ''
    tabs = ['基础玩法', '工具与探测', '奖励与排行', '道具回收']
    xx, tw = 4, 250
    for i, t in enumerate(tabs):
        inner += ('<div class="tabL %s" style="left:%dpx;top:8px;width:%dpx;font-size:34px">%s</div>'
                  % ('on' if i == 0 else 'off', xx, tw, t))
        xx += tw - 27
    blocks = [('tt', '怎么玩'),
              ('tx', '消耗<b>能量铲</b>挖开棋盘地块。地块下埋着形状各异的<b>探索目标</b>，'
                     '把某个目标的所有格子全部挖开，即算收集成功，收进异星图鉴。'),
              ('tt', '关卡与推进'),
              ('tx', '共 120 关，逐关推进。每关棋盘尺寸、不可挖地块、埋藏目标都不同；'
                     '通关后自动进入下一关，并结算该关奖励。'),
              ('tt', '挂机产出'),
              ('tx', '离开活动界面也会持续产出<b>核心电量</b>，上限 6 小时。回来后在「挂机」入口一次领取，'
                     '核心电量可在无人机补给站兑换道具。'),
              ('tt', '存钱罐'),
              ('tx', '每消耗 2 个能量铲会往<b>能量存钱罐</b>里存入 1 个，存满后可一次性取出，'
                     '取出后清零并可继续存入。'),
              ]
    y = 122
    for kind, txt in blocks:
        if kind == 'tt':
            inner += '<div class="itTitle" style="left:26px;top:%dpx;width:868px">%s<i></i></div>' % (y, txt)
            y += 62
        else:
            h = 128 if len(txt) < 60 else 160
            inner += '<div class="itText" style="left:26px;top:%dpx;width:868px;height:%dpx">%s</div>' % (y, h, txt)
            y += h + 16
    inner += sbar(8, 118, ch - 132, 0, 620)
    body = content(W, ch, inner)
    body += ('<div class="abs popNote" style="top:%dpx">4 个页签竖向滚动 · 从主界面右上「规则」钮打开</div>'
             % (H - 52))
    return page('04 玩法规则 v3弹窗', popup_page('玩法规则', body, W, H))


# ================================================================ 08 排行榜（弹窗·大号壳，同页竖滚）
# 真参照 Activity/UIActvDailyRank.prefab：StageReward → Title → UIRankTemplate 930×196 → MyRank 496×104
def s08():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 132          # 底部 132 给 MyRank
    inner = ''
    # StageReward（里程碑条）
    inner += '<div class="abs biaoti2 ol" style="left:16px;top:6px;width:888px">积分里程碑奖励（结算后邮件发放）</div>'
    boxes = [('1,000 分', 'img_Activity_rank_box04.png'), ('3,000 分', 'img_Activity_rank_box05.png'),
             ('6,000 分', 'img_Activity_rank_box04.png')]
    for i, (lb, bx) in enumerate(boxes):
        cx = 122 + i * 260
        inner += ('<div class="abs" style="left:%dpx;top:82px;width:156px;height:156px">'
                  '<div class="abs" style="left:2px;top:2px;width:152px;height:152px;background:url(%simg_rank_toyxiangkuang.png) '
                  'center/contain no-repeat"></div>'
                  '<div class="abs" style="left:-4px;top:-4px;width:164px;height:164px;background:url(%s%s) '
                  'center/contain no-repeat"></div></div>') % (cx, X, X, bx)
        inner += ('<div class="abs" style="left:%dpx;top:226px;width:180px;height:44px;display:flex;'
                  'align-items:center;justify-content:center;font-size:27px;color:#EEE48E;z-index:5;'
                  'background:url(%simg_Activity_rank_bg01.png) center/100%% 100%% no-repeat">%s</div>'
                  % (cx - 12, X, lb))
    inner += slider(830, 50, .40, '当前 2,410 / 6,000 分', left=44, top=282)
    # 榜单
    inner += '<div class="abs biaoti2 ol" style="left:16px;top:346px;width:888px">总排名（跨服）</div>'
    rows = [(1, 'StarDust', '[VOID]', '18,420', 1), (2, '灰岩矿主', '[T4F]', '17,905', 4),
            (3, 'Kuro_9', '[VOID]', '16,688', 7), (4, 'Malik', '[SAND]', '15,240', 11)]
    RS = 0.945                     # UIRankTemplate 930 → 879，塞进 920 内容区
    y = 424
    for k, (r, name, gd, sc, av) in enumerate(rows):
        inner += ('<div class="abs rowLB" style="left:20px;top:%dpx;width:930px;height:196px;'
                  'transform:scale(%.4f);transform-origin:top left">' % (y, RS))
        if r <= 3:
            tag = ['1st', '2ed', '3th'][r - 1]
            inner += ('<div class="abs" style="left:8px;top:8px;width:268px;height:180px;'
                      'background:url(%simg_cm_rankbg_icon_%s.png) left center/contain no-repeat"></div>' % (X, tag))
            inner += ('<div class="abs" style="left:24px;top:1px;width:172px;height:194px;'
                      'background:url(%simg_cm_rank_icon_%s.png) center/contain no-repeat"></div>' % (X, tag))
        else:
            inner += ('<div class="abs olL" style="left:25px;top:1px;width:190px;height:194px;display:flex;'
                      'align-items:center;justify-content:center;font-size:60px;color:#7F5F38;font-weight:bold">%d</div>' % r)
        inner += ('<div class="abs" style="left:212px;top:-4px;width:200px;height:204px">'
                  '<div style="position:absolute;inset:0;background:url(%simg_cm_bg_icon_touxiangkuang1.png) '
                  'center/contain no-repeat"></div>'
                  '<img src="%sImg_C_H_%d.png" style="position:absolute;left:30px;top:26px;width:140px;height:140px;'
                  'border-radius:50%%;object-fit:cover">'
                  '<div style="position:absolute;inset:0;background:url(%simg_cm_bg_icon_touxiangkuang1.png) '
                  'center/contain no-repeat;-webkit-mask-image:radial-gradient(circle at 50%% 48%%,transparent 0 38%%,#000 40%%)">'
                  '</div></div>' % (X, X, av, X))
        inner += ('<div class="abs" style="left:428px;top:34px;width:360px">'
                  '<div style="font-size:32px;color:#3E2411;white-space:nowrap">'
                  '<b style="color:#6C4E33">%s</b>%s</div>'
                  '<div style="margin-top:16px;display:flex;align-items:center;gap:10px">'
                  '<img src="%simg_cm_icon_integral.png" style="width:56px;height:52px">'
                  '<span style="font-size:32px;color:#7F5F38">%s 分</span></div></div>' % (gd, name, X, sc))
        inner += ('<div class="abs" style="left:786px;top:30px">%s</div>'
                  % item_cell(RANK[min(r - 1, 7)]['it'][0][0], size=135, pos=False))
        inner += '</div>'
        y += int(196 * RS) + 10
    inner += sbar(8, 420, ch - 434, 0, 300)
    body = content(W, ch, inner)
    # MyRank 496×104（img_Activity_rank_bg02）固定弹窗底部
    body += ('<div class="abs" style="right:40px;top:%dpx;width:496px;height:104px;'
             'background:url(%simg_Activity_rank_bg02.png) center/100%% 100%% no-repeat">'
             '<div class="abs" style="left:78px;top:12px;width:80px;height:80px;'
             'background:url(%simg_TXDS_icon_rank.png) center/contain no-repeat"></div>'
             '<div class="abs" style="left:172px;top:10px;font-size:34px;color:#F9E9C1;white-space:nowrap">'
             '我的排名：24</div>'
             '<div class="abs" style="left:172px;top:56px;font-size:25px;color:#FFF1B9;white-space:nowrap">'
             '2,410 分 · 第 16–30 名档</div></div>' % (H - 126, X, X))
    body += ('<div class="abs" style="left:52px;top:%dpx;width:400px;font-size:26px;color:#8A6A3A;line-height:1.35">'
             '名次奖励在本弹窗<br>继续下滚查看</div>' % (H - 116))
    return page('08 排行榜 v3弹窗', popup_page('异星探索·排行榜', body, W, H))


# ================================================================ 11 名次奖励（弹窗·大号壳，= 排行榜同弹窗下滚段）
def s11():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 88
    inner = ''
    inner += '<div class="abs biaoti2 ol" style="left:16px;top:6px;width:888px">名次奖励一览（共 8 档）</div>'
    inner += ('<div class="abs" style="left:16px;top:82px;width:888px;font-size:26px;color:#5F4430;text-align:center">'
              '活动结束后按最终名次通过邮件发放，同一名次段奖励相同</div>')
    # 列表已自动滚到「我的档位」：首行从上方裁切进入
    lb_top, lb_h = 126, ch - 126
    rows = ''
    y = -96
    for seg in RANK[2:]:
        mine = (seg['s'] == 16)
        lbl = ('第 %d 名' % seg['s']) if seg['s'] == seg['e'] else ('第 %d–%d 名' % (seg['s'], seg['e']))
        if mine:
            h = 284
            rows += '<div class="abs rowLB" style="left:14px;top:%dpx;width:878px;height:%dpx">' % (y, h)
            rows += '<div class="abs selFrame"></div>'
            rows += ('<div class="abs olL" style="left:46px;top:22px;font-size:38px;color:#3E2411;font-weight:bold">%s</div>'
                     '<div class="abs olL" style="left:46px;top:72px;font-size:27px;color:#B03A16">'
                     '我在这一档（当前第 24 名）</div>' % lbl)
            for j, (iid, cnt) in enumerate(seg['it']):
                rows += item_cell(iid, cnt=cnt, size=126, left=46 + j * 138, top=124, name=nm2(iid)[:6])
            rows += '</div>'
        else:
            h = 118
            rows += '<div class="abs rowLB" style="left:14px;top:%dpx;width:878px;height:%dpx">' % (y, h)
            rows += '<div class="abs olL" style="left:46px;top:36px;font-size:34px;color:#3E2411">%s</div>' % lbl
            for j, (iid, cnt) in enumerate(seg['it'][:2]):
                rows += item_cell(iid, cnt=cnt, size=90, left=330 + j * 100, top=14)
            rows += ('<div class="abs olL" style="left:548px;top:40px;font-size:28px;color:#7F5F38">共 %d 项</div>'
                     % len(seg['it']))
            rows += '<div class="abs olL" style="right:40px;top:36px;font-size:30px;color:#7F5F38">展开 ▾</div>'
            rows += '</div>'
        y += h + 12
        if y > lb_h:
            break
    inner += ('<div class="abs" style="left:0;top:%dpx;width:920px;height:%dpx;overflow:hidden">%s</div>'
              % (lb_top, lb_h, rows))
    inner += sbar(8, 130, ch - 144, 250, 300)
    body = content(W, ch, inner)
    body += ('<div class="abs popNote" style="top:%dpx">'
             '这是「排行榜」同一弹窗继续下滚的段落，不是第二个页签 · 共 8 档</div>' % (H - 66))
    return page('11 名次奖励 v3弹窗', popup_page('异星探索·排行榜', body, W, H))


# ================================================================ 09 关卡奖励预览（弹窗·大号壳）
def s09():
    W, H = SHELL_W_TALL, SHELL_H_TALL
    ch = H - CT_TOP - 88
    inner = ''
    tabs = ['1–30', '31–60', '61–90', '91–120', '奖励关']
    xx, tw = 10, 200
    for i, t in enumerate(tabs):
        inner += ('<div class="stageTab %s" style="left:%dpx;top:10px;width:%dpx">%s</div>'
                  % ('on' if i == 0 else 'off', xx, tw, t))
        xx += tw - 30
    inner += '<div class="abs biaoti2 ol" style="left:16px;top:92px;width:888px">第 1–30 关（已定位到当前关）</div>'
    y = 174
    rows = [l for l in LV if l['t'] == 1][8:14]
    for l in rows:
        cur = (l['l'] == 12)
        big = (l['l'] % 10 == 0)
        h = 144
        inner += '<div class="abs rowLB" style="left:14px;top:%dpx;width:878px;height:%dpx">' % (y, h)
        if cur:
            inner += '<div class="abs selFrame"></div>'
        inner += ('<div class="abs olL" style="left:42px;top:24px;font-size:38px;color:#3E2411;font-weight:bold">'
                  '第 %d 关</div>' % l['l'])
        nb = len(l['b'])
        inner += ('<div class="abs olL" style="left:42px;top:76px;font-size:26px;color:#7F5F38">%d×%d 棋盘 · %s</div>'
                  % (l['r'], l['r'], ('不可挖 %d 格' % nb) if nb else '全部地块可挖'))
        if cur:
            inner += ('<div class="abs" style="left:286px;top:28px;width:116px;height:50px;display:flex;'
                      'align-items:center;justify-content:center;font-size:27px;color:#FFF6E9;'
                      'background:url(%simg_cm_anniu1_blue.png) center/100%% 100%% no-repeat">当前</div>' % X)
        elif big:
            inner += ('<div class="abs ditu1 olL" style="left:286px;top:28px;width:130px;height:50px;display:flex;'
                      'align-items:center;justify-content:center;font-size:26px;color:#8A4F14;'
                      'font-weight:bold">大奖关</div>')
        rw = l['rw'] or [[HOE, 1]]
        for j, (iid, cnt) in enumerate(rw[:3]):
            inner += item_cell(iid, cnt=cnt, size=104, left=452 + j * 116, top=20)
        inner += ('<div class="abs olL" style="right:34px;top:52px;font-size:26px;color:#7F5F38;text-align:right">'
                  '埋藏 %d 件宝物</div>' % max(1, len(l['p'])))
        inner += '</div>'
        y += h + 10
    inner += sbar(8, 172, ch - 186, 40, 240)
    body = content(W, ch, inner)
    body += ('<div class="abs popNote" style="top:%dpx">共 120 关 · 打开时自动定位到当前关</div>' % (H - 66))
    return page('09 关卡奖励预览 v3弹窗', popup_page('关卡奖励预览', body, W, H))


# ================================================================ 12 通行证入口（HUD 入口卡 + 跳转 toast，非弹窗）
def s12():
    b = main_under(highlight='pass', tipbar=False)
    # 点击后的跳转提示 toast（X3 通用提示条，屏幕中部）
    b += ('<div class="toast" style="top:952px">'
          '<img src="%simg_gift_icon_4.png" style="width:64px;height:64px;transform:scaleX(-1)">'
          '正在前往「通行证」…</div>' % X)
    # 说明
    b += ('<div class="abs seg13" style="left:30px;top:1450px;width:1020px;height:150px"></div>'
          '<div class="abs" style="left:70px;top:1470px;width:940px;text-align:center;font-size:29px;'
          'line-height:1.5;color:#EFDBBD">'
          '通行证在挖孔内<span style="color:#EED376">只做 HUD 入口卡</span>（右上这张 ActvRank 380×120）<br>'
          '点击走 jump_link 跳到 X3 现成通行证界面 <b style="color:#EED376">UIActvBattlePassScore</b>，'
          '挖孔内既不做弹窗也不做面板</div>')
    return page('12 通行证入口 v3弹窗', b)


PAGES = [
    ('01_挂机领奖_v3弹窗', s01), ('02_成就礼包_v3弹窗', s02), ('03_存钱罐_v3弹窗', s03),
    ('04_玩法规则_v3弹窗', s04), ('05_兑换商店_v3弹窗', s05), ('08_排行榜_v3弹窗', s08),
    ('09_关卡奖励预览_v3弹窗', s09), ('10_直售礼包页_v3弹窗', s10), ('11_名次奖励_v3弹窗', s11),
    ('12_通行证入口_v3弹窗', s12),
]

if __name__ == '__main__':
    for n, f in PAGES:
        open(os.path.join(HERE, n + '.html'), 'w', encoding='utf-8').write(f())
    sys.stdout.reconfigure(encoding='utf-8')
    print('generated', len(PAGES))
