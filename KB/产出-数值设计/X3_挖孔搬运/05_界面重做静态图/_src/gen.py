# -*- coding: utf-8 -*-
"""X3 挖孔 11 屏界面重做静态图 —— HTML 生成器（1080×1920）"""
import json, os, io, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D5 = json.load(open(os.path.join(HERE, '..', 'D5.json'), encoding='utf-8'))
ASSETS = set(os.listdir(os.path.join(HERE, 'assets')))

ITEM = D5['ITEM']; TRS = D5['TRS']; LV = D5['LV']; RANK = D5['RANK']; EXC = D5['EXC']; PKG = D5['PKG']
HOE, RADAR, COIN = 111111000, 111110300, 11119905
DKPOOL = sorted([a for a in ASSETS if a.startswith('dk1511')])


def nm(i):
    i = str(i)
    return (ITEM.get(i, {}).get('nm', '道具' + i)).replace('{0}', '').replace('{1}', '').strip()


def icon(i):
    i = int(i)
    if i == HOE: return 'assets/DigKeyIcon.png'
    if i == RADAR: return 'assets/Icon1.png'
    if i == COIN: return 'assets/IconDigKeyguaji.png'
    dk = ITEM.get(str(i), {}).get('dk', 0)
    if 'it%s.webp' % dk in ASSETS: return 'assets/it%s.webp' % dk
    return 'assets/' + DKPOOL[(dk or i) % len(DKPOOL)]


def tricon(t):
    return 'assets/dk%s.webp' % t['dk'] if 'dk%s.webp' % t['dk'] in ASSETS else 'assets/151105461.png'


def tdim(t):
    h = max(c[0] for c in t['cells']) + 1
    w = max(c[1] for c in t['cells']) + 1
    return h, w


TR = {t['id']: t for t in TRS}

# ---------------------------------------------------------------- 通用骨架
HEAD = """<meta charset="utf-8"><title>%s</title><link rel="stylesheet" href="ui.css">"""


def page(title, body):
    return "<!doctype html><html><head>%s</head><body><div class=\"stage\">%s</div></body></html>" % (HEAD % title, body)


def topbar(shovel='1,240', radar='3'):
    return """
<div class="topbar">
  <div class="topRow1">
    <div class="btnBack"></div>
    <div class="actTitle nine">异星探索</div>
    <div class="btnRule"></div>
    <div class="rss">
      <div class="rssPill nine"><img src="assets/DigKeyIcon.png"><span>%s</span><span class="plus">+</span></div>
      <div class="rssPill nine"><img src="assets/Icon1.png"><span>%s</span></div>
    </div>
  </div>
  <div class="topRow2"><div class="countdown nine">剩余 2天 13:59:59</div></div>
</div>""" % (shovel, radar)


def board_bg():
    """弹窗类屏的底衬：真背景 + 顶栏 + 插槽条 + 5×5 棋盘 + 底部功能栏"""
    slots = ''.join('<div class="slotCell%s"><img src="%s"></div>' % (
        '' if i < 2 else ' off', tricon(TRS[j])) for i, j in enumerate([1, 3, 25, 10]))
    cells = ''
    blocked = {6, 7, 8, 16, 18}
    for r in range(5):
        for c in range(5):
            cells += '<div class="cell%s"><i></i></div>' % (' blk' if r * 5 + c in blocked else '')
    fb = [('assets/IconDigKeyguaji.png', '挂机', True), ('assets/Icon2.png', '图鉴', False),
          ('assets/Icon1.png', '探测仪', False), ('assets/151105567.png', '排行', False),
          ('assets/DigPiggyIcon.png', '礼包', True)]
    btns = ''.join('<div class="funcBtn"><div class="iconWrap"><img src="%s">%s</div><div class="name">%s</div></div>'
                   % (a, '<div class="dot"></div>' if d else '', n) for a, n, d in fb)
    return """
<div class="bg"></div><div class="bgShade"></div>
%s
<div class="slotbar nine"><div class="slotLabel">探索目标</div><div class="slotCells">%s</div></div>
<div class="boardZone">
  <div class="boardHead"><div class="lvBadge nine">关卡 12</div>
    <div class="costTip nine">每格消耗 1 <img src="assets/DigKeyIcon.png"></div></div>
  <div class="board" style="grid-template-columns:repeat(5,168px);grid-auto-rows:168px">%s</div>
</div>
<div class="bottomBar">%s</div>""" % (topbar(), slots, cells, btns)


def scrollbar(top, height, right=0):
    return ('<div class="scrollTrack" style="right:%dpx"></div>'
            '<div class="scrollThumb" style="right:%dpx;top:%dpx;height:%dpx"></div>') % (right, right, top, height)


# ================================================================ 01 挂机领奖
def s01():
    rewards = [(COIN, '10,000'), (HOE, '20'), (RADAR, '2')]
    ri = ''.join(
        '<div style="display:flex;flex-direction:column;align-items:center;gap:10px">'
        '<div class="itemCell" style="width:132px;height:132px"><img src="%s" style="width:116px;height:116px;margin:8px">'
        '<span class="num">×%s</span></div>'
        '<div style="font-size:26px;color:#e8dcc4;max-width:190px;text-align:center">%s</div></div>'
        % (icon(i), n, nm(i)) for i, n in rewards)
    pop = """
<div class="popCard nine" style="width:920px">
  <div class="popClose"></div>
  <div class="popTitle">欢迎回来</div>

  <img src="assets/wurenji.png" style="display:block;margin:0 auto;width:300px">

  <div class="panelDark nine" style="margin-top:20px">
    <div style="display:flex;align-items:baseline;justify-content:space-between">
      <div class="h2t">离线挂机 <span style="color:#ffeab4">4 小时 29 分</span></div>
      <div class="dim">上限 6 小时</div>
    </div>
    <div class="barWrap nine" style="margin-top:14px">
      <div class="barFill" style="width:74.7%%"></div>
      <div class="barText">04:29:00 / 06:00:00</div>
    </div>
    <div class="dim" style="margin-top:12px">满 6 小时后停止累积，记得回来领取</div>
  </div>

  <div class="panelDark nine" style="margin-top:18px">
    <div class="h2t" style="margin-bottom:16px">本次可领取</div>
    <div style="display:flex;justify-content:space-around;align-items:flex-start">%s</div>
  </div>

  <div style="margin-top:30px"><div class="btnGreen nine">领 取</div></div>
  <div style="text-align:center;margin-top:22px">
    <span class="btnBlue nine">去无人机补给站兑换 ›</span>
  </div>
</div>""" % ri
    return page('01 挂机领奖', board_bg() + '<div class="overlay">' + pop + '</div>')


# ================================================================ 02 成就礼包
ACHV_ITEMS = [
    [(HOE, 60), (RADAR, 1), (COIN, 500)],
    [(HOE, 200), (RADAR, 2), (COIN, 2000)],
    [(HOE, 360), (RADAR, 3), (COIN, 3600), (11119797, 1)],
    [(HOE, 800), (RADAR, 5), (COIN, 8000), (11119797, 2)],
]


def achv_items_html(items):
    return ''.join('<div class="itemCell"><img src="%s"><span class="num">×%s</span></div>' % (icon(i), n)
                   for i, n in items)


def s02():
    gates = sorted([p['gate'] for p in PKG if p['tab'] == 'achievement'])  # 15 档
    cur = 12
    bought = [1]
    buyable = [g for g in gates if g <= cur and g not in bought]      # 5, 10
    locked = [g for g in gates if g > cur]                            # 15..85
    price = {1: '$9.99', 5: '$14.99', 10: '$19.99', 15: '$24.99'}

    cards = ''
    for k, g in enumerate(buyable):
        cards += """
<div class="rowGold nine" style="padding:20px 24px;margin-bottom:14px">
  <div style="display:flex;align-items:center;gap:16px">
    <div class="h1t" style="min-width:150px">第 %d 关档</div>
    <div class="boxSm nine" style="font-size:24px;color:#ffd76e">已解锁</div>
    <div style="margin-left:auto;display:flex;flex-direction:column;align-items:center;gap:6px">
      <span class="btnGold nine">%s</span>
      <div class="dim" style="font-size:22px">限购 1 次</div>
    </div>
  </div>
  <div style="display:flex;gap:14px;margin-top:16px">%s</div>
</div>""" % (g, price[g], achv_items_html(ACHV_ITEMS[k + 1]))

    bought_row = """
<div class="row nine" style="display:flex;align-items:center;gap:16px;margin-bottom:12px;opacity:.75">
  <div class="h2t" style="min-width:150px">第 1 关档</div>
  <div class="sub">已购买</div>
  <div style="margin-left:auto" class="dim">3 项奖励 &nbsp;▾</div>
</div>"""

    next_row = """
<div class="row nine" style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
  <div class="h2t" style="min-width:150px">第 15 关档</div>
  <div class="sub">还需通关 <b class="gold">3</b> 关解锁</div>
  <div style="margin-left:auto;display:flex;gap:10px">%s</div>
</div>""" % ''.join('<div class="itemCell" style="width:74px;height:74px;filter:grayscale(.8) brightness(.6)">'
                    '<img src="%s" style="width:62px;height:62px;margin:6px"></div>' % icon(i)
                    for i, n in ACHV_ITEMS[3][:3])

    rest_row = """
<div class="row nine" style="display:flex;align-items:center;gap:16px">
  <div class="h2t" style="min-width:150px">第 20–85 关</div>
  <div class="sub">共 11 档，通关后依次解锁</div>
  <div style="margin-left:auto" class="dim">展开查看 &nbsp;▾</div>
</div>"""

    pop = """
<div class="popCard nine" style="width:980px">
  <div class="popClose"></div>
  <div class="popTitle">成就礼包</div>
  <div class="banner">再通关 3 关，解锁第 15 关档礼包</div>

  <div style="display:flex;align-items:center;gap:18px;margin:20px 0 10px">
    <div class="sub">当前进度 <b class="gold" style="font-size:34px">第 12 关</b></div>
    <div class="plate nine" style="font-size:24px;color:#ffe6b8">已购 1 / 已解锁 3 / 共 15 档</div>
  </div>

  <div class="h2t" style="margin:16px 0 12px">现在可购买（2）</div>
  %s
  <div class="h2t" style="margin:22px 0 12px">已购买（1）</div>
  %s
  <div class="h2t" style="margin:22px 0 12px">未解锁（12）</div>
  %s
  %s
</div>""" % (cards, bought_row, next_row, rest_row)
    return page('02 成就礼包', board_bg() + '<div class="overlay">' + pop + '</div>')


# ================================================================ 03 存钱罐
def s03():
    pop = """
<div class="popCard nine" style="width:820px;padding:34px 44px 40px">
  <div class="popClose"></div>
  <div class="popTitle" style="width:600px">能量存钱罐</div>

  <div style="display:flex;align-items:center;gap:26px;margin-top:6px">
    <img src="assets/DigPiggyIcon.png" style="width:230px;height:230px;flex:none;
      filter:drop-shadow(0 0 26px rgba(255,210,80,.55))">
    <div style="flex:1">
      <div class="h1t" style="font-size:44px">已存 <span class="gold">36</span> <span style="font-size:30px;color:#c9b894">/ 50</span></div>
      <div class="barWrap nine" style="height:38px;margin-top:12px">
        <div class="barFillGold" style="width:72%"></div>
      </div>
      <div class="sub" style="margin-top:14px">每消耗 <b class="gold">2</b> 个能量铲，自动存入 <b class="gold">1</b></div>
      <div class="dim" style="margin-top:6px">存满 50 后停止累积</div>
    </div>
  </div>

  <div class="frameThin nine" style="margin-top:24px;display:flex;align-items:center;gap:16px">
    <img src="assets/DigKeyIcon.png" style="width:70px;height:70px">
    <div class="sub">取出可得 <b class="gold" style="font-size:32px">能量铲 ×36</b></div>
  </div>

  <div style="margin-top:26px"><div class="btnGreen nine">取 出 &nbsp;·&nbsp; $4.99</div></div>
  <div class="dim" style="text-align:center;margin-top:14px">取出后清零，重新开始累积</div>
</div>"""
    return page('03 存钱罐', board_bg() + '<div class="overlay">' + pop + '</div>')


# ================================================================ 04 玩法规则
def s04():
    secs = [
        ('怎么玩', [
            '点击地块消耗 <b class="gold">能量铲</b> 挖掘，挖出本关<b class="gold">全部探索目标</b>即通关。',
            '顶部「探索目标」显示本关要挖的宝物，挖到会自动飞入对应格子。',
            '深色地块为<b class="gold">不可挖</b>区域，不消耗能量铲。',
        ]),
        ('工具与探测仪', [
            '挖掘过程中会随机触发<b class="gold">工具</b>：一次清掉整行、整列或 3×3 区域。',
            '使用<b class="gold">探测仪</b>可先选一个探索目标，在棋盘上标出它的位置。',
        ]),
        ('奖励关卡', [
            '通关途中会插入<b class="gold">奖励关卡</b>：棋盘更小、奖励更好，不显示关卡号。',
            '第 100 关后进入<b class="gold">循环关</b>，可持续获得奖励。',
        ]),
        ('排行与奖励', [
            '挖掘与通关都会累积<b class="gold">积分</b>，积分满 100 进入跨服总排名。',
            '活动结束按最终名次发放<b class="gold">名次奖励</b>，通过邮件送达。',
        ]),
        ('道具回收', [
            '能量铲、探测仪、核心电量为活动道具，<b class="warn">活动结束后统一回收</b>，请及时使用。',
        ]),
    ]
    body = ''
    for i, (h, items) in enumerate(secs):
        lis = ''.join('<div style="display:flex;gap:12px;margin-top:12px">'
                      '<div style="color:#c9a45c;font-size:24px;line-height:1.6">◆</div>'
                      '<div style="flex:1;font-size:29px;color:#e8dcc4;line-height:1.62">%s</div></div>' % t
                      for t in items)
        body += """
<div style="margin-top:%dpx">
  <div style="display:flex;align-items:center;gap:14px">
    <div class="boxSm nine" style="font-size:26px;color:#ffd76e;padding:5px 16px">%d</div>
    <div class="h2t" style="font-size:33px">%s</div>
  </div>
  %s
</div>""" % (0 if i == 0 else 30, i + 1, h, lis)

    pop = """
<div class="popCard nine" style="width:960px">
  <div class="popClose"></div>
  <div class="popTitle">玩法规则</div>
  <div class="panelDark nine" style="padding:28px 34px 34px">%s</div>
</div>""" % body
    return page('04 玩法规则', board_bg() + '<div class="overlay">' + pop + '</div>')


# ================================================================ 05 兑换商店
EXC_DESC = {
    111110300: '标记本关一个探索目标的位置',
    111111048: '开出蓝色及以上纪念卡组件',
    111111047: '开出绿色及以上纪念卡组件',
    111111000: '挖掘地块的消耗道具',
    111111046: '开出白色及以上纪念卡组件',
}


def s05():
    rows = ''
    for e in EXC:
        get_id, get_n = e['get'][0]
        give_id, give_n = e['give'][0]
        rows += """
<div class="row nine" style="display:flex;align-items:center;gap:24px;padding:18px 24px;margin-bottom:16px">
  <div class="itemCell" style="width:120px;height:120px"><img src="%s" style="width:106px;height:106px;margin:7px"></div>
  <div style="flex:1">
    <div class="h1t" style="font-size:34px">%s ×%s</div>
    <div class="sub" style="margin-top:6px">%s</div>
    <div class="dim" style="margin-top:6px">剩余可兑换 <b class="gold">%s</b> 次</div>
  </div>
  <div style="width:250px;flex:none;text-align:right">
    <span class="btnGold nine" style="min-width:230px;text-align:center"><img src="assets/IconDigKeyguaji.png"
      style="width:40px;height:40px;vertical-align:-8px;margin-right:6px">%s</span>
  </div>
</div>""" % (icon(get_id), nm(get_id), get_n, EXC_DESC.get(get_id, ''), e['limit'], '{:,}'.format(give_n))

    pop = """
<div class="popCard nine" style="width:980px">
  <div class="popBack"></div>
  <div class="popTitle">无人机补给站</div>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="sub">用挂机产出的核心电量兑换道具</div>
    <div class="plate nine" style="font-size:28px;color:#ffe8a0;padding:6px 18px">
      <img src="assets/IconDigKeyguaji.png" style="width:44px;height:44px;vertical-align:-10px;margin-right:8px">12,480</div>
  </div>
  %s
  <div class="dim" style="text-align:center;margin-top:10px">核心电量与活动道具将在活动结束后回收</div>
</div>""" % rows
    return page('05 兑换商店', board_bg() + '<div class="overlay">' + pop + '</div>')


# ================================================================ 06 异星图鉴
def s06():
    grp1 = [t for t in TRS if t['grp'] == 1]
    sel = grp1[0]
    h, w = tdim(sel)
    cells = ''
    for i, t in enumerate(grp1[:12]):
        got = i % 3 != 2
        cells += """
<div class="%s" style="position:relative;padding:16px 10px;text-align:center;%s">
  <img src="%s" style="width:158px;height:158px;%s">
  <div style="font-size:26px;color:%s;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">%s</div>
</div>""" % ('rowGold nine' if i == 0 else 'boxSm nine',
             '' if got else 'filter:brightness(.5) saturate(.5)',
             tricon(t), '' if got else 'opacity:.75',
             '#ffeab4' if got else '#8e846c', t['nm'] if got else '未发现')

    miles = [(10, 111111046), (20, 111111047), (30, 111111048), (40, 111110325)]
    mh = ''
    for g, it in miles:
        reach = g <= 27
        mh += """
<div style="display:flex;flex-direction:column;align-items:center;gap:4px">
  <div class="itemCell" style="width:84px;height:84px;%s"><img src="%s" style="width:72px;height:72px;margin:6px"></div>
  <div style="font-size:24px;color:%s">%d 个</div>
</div>""" % ('' if reach else 'filter:grayscale(1) brightness(.6)', icon(it),
             '#ffd76e' if reach else '#8e846c', g)

    return page('06 异星图鉴', """
<div class="fullPage">
  <div class="fpBg"></div>
  <div class="fpHead">
    <div class="btnBack"></div>
    <div class="fpTitle nine">异星图鉴</div>
    <div class="fpHeadRight">已收集 <b>27</b> / 40</div>
  </div>

  <div class="panelDark nine" style="position:relative;margin:24px 34px 0;display:flex;gap:30px;align-items:center">
    <div style="width:300px;height:300px;flex:none;display:flex;align-items:center;justify-content:center;
      background:url(assets/DigKeyBg_Guang.png) center/contain no-repeat">
      <img src="%s" style="width:232px;height:232px">
    </div>
    <div style="flex:1">
      <div class="h1t" style="font-size:42px">%s</div>
      <div class="sub" style="margin-top:10px">%s</div>
      <div style="display:flex;gap:12px;margin-top:16px">
        <div class="boxSm nine" style="font-size:25px;color:#ffd76e">占 %d×%d · 共 %d 格</div>
      </div>
      <div class="sub" style="margin-top:16px;line-height:1.7">
        我的最好成色 <b class="gold">218.22</b><br>全服最好成色 <b class="gold">12,218.44</b></div>
    </div>
  </div>

  <div class="tabs" style="margin:26px 34px 0">
    <div class="tab on nine">普通地形（27/28）</div>
    <div class="tab nine">特殊地形（0/12）</div>
  </div>

  <div style="position:relative;margin:0 34px;flex:1;overflow:hidden">
    <div class="panelDark nine" style="position:absolute;inset:0;padding:24px 26px">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px">%s</div>
      <div class="fadeBot" style="right:26px"></div>
    </div>
    %s
  </div>

  <div class="panelDark nine" style="margin:20px 34px 34px">
    <div style="display:flex;align-items:baseline;justify-content:space-between">
      <div class="h2t">收集进度奖励</div>
      <div class="sub">已收集 <b class="gold">27</b> / 40 个宝物</div>
    </div>
    <div class="barWrap nine" style="height:34px;margin-top:14px"><div class="barFill" style="width:67.5%%"></div></div>
    <div style="display:flex;justify-content:space-between;margin-top:14px">%s</div>
  </div>
</div>""" % (tricon(sel), sel['nm'], sel['ds'], h, w, len(sel['cells']), cells, scrollbar(24, 420, 12), mh))


# ================================================================ 07 探索目标选择器
def s07():
    pick = [TRS[1], TRS[5], TRS[9], TRS[14], TRS[20], TRS[25], TRS[3], TRS[30], TRS[17], TRS[33],
            TRS[7], TRS[38]]
    cards = ''
    for i, t in enumerate(pick):
        h, w = tdim(t)
        shape = ''
        occ = {(c[0], c[1]) for c in t['cells']}
        for r in range(h):
            for c in range(w):
                shape += '<i style="display:block;border-radius:3px;%s"></i>' % ('background:#ffc861' if (r, c) in occ else 'background:rgba(255,255,255,.16)')
        cards += """
<div class="%s" style="position:relative;display:flex;gap:18px;align-items:center;padding:18px 20px">
  %s
  <img src="%s" style="width:126px;height:126px;flex:none">
  <div style="flex:1;min-width:0">
    <div style="font-size:29px;font-weight:bold;color:#ffeab4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">%s</div>
    <div class="dim" style="margin-top:4px">占 %d×%d · %d 格</div>
    <div style="display:grid;grid-template-columns:repeat(%d,16px);grid-auto-rows:16px;gap:3px;margin-top:8px">%s</div>
  </div>
  %s
</div>""" % ('rowGold nine' if i == 1 else 'row nine',
             '<div style="position:absolute;top:6px;right:8px;background:#b8412c;color:#fff;font-size:21px;'
             'padding:2px 12px;border-radius:12px">本关必出</div>' if i in (1, 3) else '',
             tricon(t), t['nm'], h, w, len(t['cells']), w, shape,
             '<img src="assets/x3_check.webp" style="position:absolute;right:14px;bottom:12px;width:56px;height:54px">'
             if i == 1 else '')

    return page('07 探索目标选择器', """
<div class="fullPage">
  <div class="fpBg"></div>
  <div class="fpHead">
    <div class="btnBack"></div>
    <div class="fpTitle nine">选择探索目标</div>
    <div class="fpHeadRight"><img src="assets/Icon1.png">探测仪 <b>3</b></div>
  </div>
  <div class="fpSub">选中一个目标后使用探测仪，会在本关棋盘上标出它的位置。<b class="gold">本关必出</b>=本关一定埋有该宝物。</div>
  <div class="fpBody">
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:18px">%s</div>
    <div class="fadeBot"></div>
    %s
  </div>
  <div class="fpFoot">
    <div class="sub" style="text-align:center;margin-bottom:14px">已选：<b class="gold">%s</b></div>
    <div class="btnGreen nine" style="min-width:640px">开始探测
      <img src="assets/Icon1.png" style="width:52px;height:52px;vertical-align:-12px;margin:0 6px 0 18px">×1</div>
  </div>
</div>""" % (cards, scrollbar(0, 700, 0), pick[1]['nm']))


# ================================================================ 08 排行榜·榜单
FAKE = [('[AOB]StevenJam', 12218), ('[KTA]MoonWalker', 11840), ('[SVR]Ирина', 10932),
        ('[AOB]DustDigger', 9877), ('[NVA]小满', 9310), ('[KTA]Ravager', 8804),
        ('[SVR]Hoshino', 8125), ('[AOB]Cavendish', 7690), ('[TTT]Юрий', 7204),
        ('[NVA]阿卡林', 6688), ('[KTA]Sandstorm', 6120), ('[AOB]Мария', 5804),
        ('[SVR]KingCrab', 5411), ('[TTT]老张', 5008), ('[NVA]Vireo', 4772),
        ('[KTA]DeepCore', 4310)]
MEDAL = ['assets/it151105567.webp', 'assets/it151105568.webp', 'assets/it151105569.webp']


def s08():
    rows = ''
    for i, (n, sc) in enumerate(FAKE):
        no = ('<img src="%s" style="width:76px;height:76px">' % MEDAL[i]) if i < 3 else \
             '<span style="font-size:32px;color:#ffeab4">%d</span>' % (i + 1)
        rows += """
<div class="row nine" style="display:flex;align-items:center;gap:18px;padding:14px 22px;margin-bottom:12px">
  <div style="width:96px;text-align:center;flex:none">%s</div>
  <div style="flex:1;font-size:30px;color:#ffeab4">%s</div>
  <div style="font-size:30px;color:#ffd76e">%s 分</div>
</div>""" % (no, n, '{:,}'.format(sc))

    me = """
<div class="rowGold nine" style="display:flex;align-items:center;gap:18px;padding:16px 22px;margin-top:18px">
  <div style="width:96px;text-align:center;flex:none;font-size:30px;color:#ffb08a">未上榜</div>
  <div style="flex:1"><div style="font-size:30px;color:#ffeab4">我</div>
    <div class="dim" style="margin-top:4px">积分满 100 才进入排行，还需 <b class="gold">38</b> 分</div></div>
  <div style="font-size:30px;color:#ffd76e">62 分</div>
</div>"""

    return page('08 排行榜·榜单', """
<div class="fullPage">
  <div class="fpBg"></div>
  <div class="fpHead">
    <div class="btnBack"></div>
    <div class="fpTitle nine">总排名</div>
    <div class="fpHeadRight">跨服 · 实时更新</div>
  </div>
  <div class="tabs" style="margin:24px 34px 0">
    <div class="tab on nine">排行榜</div><div class="tab nine">名次奖励</div>
  </div>
  <div class="frameThin nine" style="margin:20px 34px 0">
    <div class="sub">按<b class="gold">挖掘格数</b>与<b class="gold">通关进度</b>计分，与全部同期服务器一起排名，实时更新。</div>
  </div>
  <div class="fpBody" style="margin-top:20px">
    <div style="position:absolute;left:0;right:26px;top:0">%s</div>
    <div class="fadeBot" style="right:26px;height:110px"></div>
    %s
  </div>
  <div style="padding:0 34px 40px">%s</div>
</div>""" % (rows, scrollbar(0, 760, 0), me))


# ================================================================ 09 关卡奖励预览
def s09():
    main = [l for l in LV if l['t'] == 1]
    cur = 12
    rows = ''
    for l in main[8:16]:
        tags = ''
        if l['l'] == cur:
            tags += '<div class="boxSm nine" style="font-size:22px;color:#ffd76e">当前</div>'
        if l['rs']:
            tags += '<div class="boxSm nine" style="font-size:22px;color:#ffd76e">大奖关</div>'
        rw = ''.join('<div class="itemLine"><img src="%s">%s ×%s</div>' % (icon(i), nm(i), n) for i, n in l['rw'])
        cls = 'rowGold nine' if (l['l'] == cur or l['rs']) else 'row nine'
        rows += """
<div class="%s" style="display:flex;align-items:center;gap:18px;padding:16px 22px;margin-bottom:12px">
  <div style="width:150px;flex:none;font-size:32px;font-weight:bold;color:#ffe9a8">第 %d 关</div>
  <div style="width:290px;flex:none;white-space:nowrap" class="dim">%d×%d 棋盘 · 每格消耗 %d<br>%s</div>
  <div style="flex:1;display:flex;flex-wrap:wrap;gap:12px">%s</div>
  <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">%s</div>
</div>""" % (cls, l['l'], l['r'], l['o'], l['c'],
             ('不可挖 %d 格' % len(l['b'])) if l['b'] else '全部地块可挖', rw, tags)

    pop = """
<div class="popCard nine" style="width:1010px;height:1580px;display:flex;flex-direction:column">
  <div class="popClose"></div>
  <div class="popTitle">关卡奖励预览</div>
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:16px">
    <div class="sub">共 120 关</div>
    <div class="boxSm nine" style="font-size:23px;color:#ffd76e">金框 = 大奖关</div>
    <div class="boxSm nine" style="font-size:23px;color:#ffd76e">紫框 = 奖励关</div>
    <div class="dim" style="margin-left:auto">已自动定位到当前关</div>
  </div>
  <div style="position:relative;flex:1;overflow:hidden">
    <div style="position:absolute;left:0;right:26px;top:0">
      <div class="h2t" style="margin:0 0 14px">主线关卡（1–100）</div>
      %s
    </div>
    %s
  </div>
</div>""" % (rows, scrollbar(120, 620, 0))
    return page('09 关卡奖励预览', board_bg() + '<div class="overlay">' + pop + '</div>')


# ================================================================ 10 直售礼包页
PK_SAMPLE = [
    [(HOE, 60), (RADAR, 1), (COIN, 500)],
    [(HOE, 200), (RADAR, 2), (COIN, 2000)],
    [(HOE, 360), (RADAR, 3), (COIN, 3600)],
    [(HOE, 800), (RADAR, 5), (COIN, 8000), (11119797, 1)],
    [(HOE, 1800), (RADAR, 10), (COIN, 18000), (11119797, 2)],
    [(HOE, 5000), (RADAR, 25), (COIN, 50000), (111110325, 5)],
    [(HOE, 12000), (RADAR, 60), (COIN, 120000), (111130007, 1)],
]
PK_DISC = [20, 30, 40, 50, 60, 70, 80]


def s10():
    common = [p for p in PKG if p['tab'] == 'common']
    cards = ''
    for i, p in enumerate(common):
        items = ''.join(
            '<div style="width:96px;text-align:center">'
            '<div class="itemCell" style="width:78px;height:78px;margin:0 auto"><img src="%s" style="width:68px;height:68px;margin:5px"></div>'
            '<div style="font-size:18px;color:#c9b894;margin-top:3px;line-height:1.2;height:44px;overflow:hidden">%s</div>'
            '<div style="font-size:21px;color:#ffeab4;line-height:1.1">×%s</div></div>'
            % (icon(a), nm(a), '{:,}'.format(b)) for a, b in PK_SAMPLE[i])
        sold = (i == 0)
        btn = ('<div class="btnOff nine" style="display:block;text-align:center;padding:16px 0">已购买</div>' if sold
               else '<div class="btnGold nine" style="display:block;text-align:center;padding:16px 0">%s</div>' % p['price'])
        cards += """
<div class="rowGold nine" style="position:relative;padding:18px 14px 20px;text-align:center;%s">
  <div style="position:absolute;left:-8px;top:16px;transform:rotate(-13deg);background:linear-gradient(90deg,#ff5d4d,#c8202f);
    color:#fff;font-size:23px;font-weight:bold;padding:4px 20px;box-shadow:0 3px 10px rgba(0,0,0,.5)">-%d%%</div>
  <div style="font-size:26px;color:#ffeab4;font-weight:bold;margin-top:30px">异星探索礼包 %d</div>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin:14px 0 12px;min-height:300px;align-content:flex-start">%s</div>
  %s
  <div class="dim" style="font-size:21px;margin-top:8px">%s</div>
</div>""" % ('filter:saturate(.65) brightness(.9)' if sold else '', PK_DISC[i], i + 1, items, btn,
             '每人限购 1 次（已购）' if sold else '每人限购 1 次')

    return page('10 直售礼包页', """
<div class="fullPage">
  <div class="fpBg"></div>
  <div class="fpHead">
    <div class="btnBack"></div>
    <div class="fpTitle nine">异星探索礼包</div>
    <div class="fpHeadRight"><img src="assets/DigKeyIcon.png">1,240</div>
  </div>
  <div class="fpSub">购买后道具立即到账，可直接用于挖掘。每档<b class="gold">每人限购 1 次</b>，活动结束前有效。</div>
  <div class="fpBody">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px">%s</div>
    <div class="fadeBot"></div>
    %s
  </div>
</div>""" % (cards, scrollbar(0, 900, 0)))


# ================================================================ 11 名次奖励 A / B
def seg_label(s, e):
    return '第 %d 名' % s if s == e else '第 %d–%d 名' % (s, e)


def rk_head(extra=''):
    return """
<div class="fpHead">
  <div class="btnBack"></div>
  <div class="fpTitle nine">总排名</div>
  <div class="fpHeadRight">跨服 · 实时更新</div>
</div>
<div class="tabs" style="margin:24px 34px 0">
  <div class="tab nine">排行榜</div><div class="tab on nine">名次奖励</div>
</div>
<div class="rowGold nine" style="margin:20px 34px 0;display:flex;align-items:center;gap:18px;padding:18px 24px">
  <img src="assets/it151105570.webp" style="width:84px;height:84px">
  <div style="flex:1">
    <div class="h1t" style="font-size:34px">我的名次 <span class="gold">24</span></div>
    <div class="sub" style="margin-top:4px">当前可得「第 16–30 名」奖励</div>
  </div>
  %s
</div>""" % extra


def s11a():
    my = (16, 30)
    rows = ''
    for s in RANK:
        mine = (s['s'], s['e']) == my
        if mine:
            its = ''.join(
                '<div style="width:118px;text-align:center">'
                '<div class="itemCell" style="width:96px;height:96px;margin:0 auto"><img src="%s"></div>'
                '<div style="font-size:21px;color:#d8c9a8;margin-top:6px;line-height:1.25">%s<br>×%s</div></div>'
                % (icon(a), nm(a), '{:,}'.format(b)) for a, b in s['it'])
            rows += """
<div class="rowGold nine" style="padding:20px 24px;margin-bottom:14px">
  <div style="display:flex;align-items:center;gap:16px">
    <div class="h1t" style="font-size:34px">%s</div>
    <div class="boxSm nine" style="font-size:23px;color:#ffd76e">我在这一档</div>
    <div class="dim" style="margin-left:auto">%d 项奖励 &nbsp;▴</div>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:16px">%s</div>
</div>""" % (seg_label(s['s'], s['e']), len(s['it']), its)
        else:
            core = ''.join('<div class="itemLine" style="font-size:25px">'
                           '<img src="%s" style="width:54px;height:54px">%s ×%s</div>' % (icon(a), nm(a), b)
                           for a, b in s['it'][:2])
            rows += """
<div class="row nine" style="display:flex;align-items:center;gap:18px;padding:14px 24px;margin-bottom:12px">
  <div style="width:230px;flex:none;font-size:30px;font-weight:bold;color:#ffe9a8">%s</div>
  <div style="flex:1;display:flex;flex-direction:column;gap:4px">%s</div>
  <div class="dim" style="white-space:nowrap">共 %d 项 &nbsp;▾</div>
</div>""" % (seg_label(s['s'], s['e']), core, len(s['it']))

    return page('11 名次奖励·方案A', """
<div class="fullPage">
  <div class="fpBg"></div>
  %s
  <div class="fpBody" style="margin-top:20px">
    <div style="position:absolute;left:0;right:26px;top:0">%s
      <div class="dim" style="text-align:center;margin-top:6px">共 8 个名次段，点任意段展开查看全部奖励</div>
    </div>
    %s
  </div>
</div>""" % (rk_head(), rows, scrollbar(0, 880, 0)))


def s11b():
    my = (16, 30)
    head = """
<div class="row nine" style="display:flex;align-items:center;gap:16px;padding:12px 22px;margin-bottom:12px">
  <div class="h2t" style="width:230px;flex:none">名次段</div>
  <div class="h2t" style="flex:1">核心大奖（2 项）</div>
  <div class="h2t" style="width:300px;flex:none;text-align:right">其余奖励</div>
</div>"""
    rows = ''
    for s in RANK:
        mine = (s['s'], s['e']) == my
        core = s['it'][:2]
        rest = s['it'][2:]
        corehtml = ''.join(
            '<div style="display:flex;align-items:center;gap:10px">'
            '<div class="itemCell" style="width:64px;height:64px"><img src="%s" style="width:54px;height:54px;margin:5px">'
            '<span class="num" style="font-size:20px">×%s</span></div>'
            '<div style="font-size:24px;color:#ffeab4;line-height:1.2">%s</div></div>' % (icon(a), b, nm(a))
            for a, b in core)
        thumbs = ''.join('<div class="itemCell" style="width:64px;height:64px">'
                         '<img src="%s" style="width:54px;height:54px;margin:5px"></div>' % icon(a)
                         for a, b in rest[:3])
        rows += """
<div class="%s" style="display:flex;align-items:center;gap:16px;padding:10px 22px;margin-bottom:10px">
  <div style="width:230px;flex:none">
    <div style="font-size:30px;font-weight:bold;color:#ffe9a8">%s</div>
    %s
  </div>
  <div style="flex:1;display:flex;flex-direction:column;gap:6px">%s</div>
  <div style="width:300px;flex:none;display:flex;align-items:center;justify-content:flex-end;gap:8px">
    %s<div class="dim" style="white-space:nowrap">+%d 项 ▾</div>
  </div>
</div>""" % ('rowGold nine' if mine else 'row nine', seg_label(s['s'], s['e']),
             '<div class="boxSm nine" style="font-size:21px;color:#ffd76e;margin-top:6px;display:inline-block">我在这一档</div>' if mine else '',
             corehtml, thumbs, len(rest))

    return page('11 名次奖励·方案B', """
<div class="fullPage">
  <div class="fpBg"></div>
  %s
  <div class="fpBody" style="margin-top:20px">
    <div style="position:absolute;left:0;right:26px;top:0">%s%s
      <div class="dim" style="text-align:center;margin-top:6px">点任意行展开该段全部奖励</div>
    </div>
  </div>
</div>""" % (rk_head(), head, rows))


SCREENS = [
    ('01_挂机领奖', s01), ('02_成就礼包', s02), ('03_存钱罐', s03), ('04_玩法规则', s04),
    ('05_兑换商店', s05), ('06_异星图鉴', s06), ('07_探索目标选择器', s07),
    ('08_排行榜_榜单', s08), ('09_关卡奖励预览', s09), ('10_直售礼包页', s10),
    ('11_名次奖励_方案A', s11a), ('11_名次奖励_方案B', s11b),
]

if __name__ == '__main__':
    for name, fn in SCREENS:
        with io.open(os.path.join(HERE, name + '.html'), 'w', encoding='utf-8') as f:
            f.write(fn())
        print('written', name)
