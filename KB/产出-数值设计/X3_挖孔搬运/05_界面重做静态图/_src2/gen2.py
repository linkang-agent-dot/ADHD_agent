# -*- coding: utf-8 -*-
"""X3 挖孔 v2「对齐 X3 现成界面」静态图生成器（1080×1920）
   布局/控件/尺寸/切片全部来自真 prefab 解析结果（见 dig\\*.txt）"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D5 = json.load(open(os.path.join(HERE, 'D5.json'), encoding='utf-8'))
ASSETS = set(os.listdir(os.path.join(HERE, 'assets')))

ITEM, TRS, LV, RANK, EXC, PKG, ACT = D5['ITEM'], D5['TRS'], D5['LV'], D5['RANK'], D5['EXC'], D5['PKG'], D5['ACT']
HOE, RADAR, COIN = 111111000, 111110300, 11119905
DKPOOL = sorted([a for a in ASSETS if a.startswith('dk1511')])
X = 'assets/x3/'


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


def tricon(t):
    return 'assets/dk%s.webp' % t['dk'] if 'dk%s.webp' % t['dk'] in ASSETS else 'assets/151105461.png'


HEAD = '<meta charset="utf-8"><title>%s</title><link rel="stylesheet" href="ui2.css">'


def page(t, body):
    return '<!doctype html><html><head>%s</head><body><div class="stage">%s</div></body></html>' % (HEAD % t, body)


# ---------------------------------------------------------------- 通用件
def item_cell(iid, cnt=None, size=155, name=None, got=False, top=0, left=0, pos=True, gold=False):
    """UIItemTemplate：200 基准等比缩放。font-size 用 em 驱动内部字号"""
    s = ''
    if pos:
        s = 'left:%dpx;top:%dpx;' % (left, top)
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


def act_header(title, desc, time='剩余 2天 13:59:59', gift=None, cur=None, dw=700):
    """X3 标准活动页头：txt_title(24,125,fs52) / Time 药丸(21,203,h60) / txt_desc(25,300,fs36)
       / btn_info 64×64 右上 / 右侧货币位（UIBtnProperty 位）"""
    h = '<div class="actBG"></div><div class="actBGfade"></div><div class="actBGlow"></div>'
    h += '<div class="actTitle ol">%s</div>' % title
    h += '<div class="actTime"><img src="%simg_gift_time.png"><span>距结束：%s</span></div>' % (X, time)
    h += '<div class="actDesc ol" style="width:%dpx">%s</div>' % (dw, desc)
    h += '<div class="btnInfo"></div>'
    if cur:
        h += ('<div class="abs seg13" style="right:23px;top:218px;width:%dpx;height:74px;display:flex;'
              'align-items:center;gap:12px;padding:0 24px"><img src="%s" style="width:52px;height:52px">'
              '<div style="font-size:32px;color:#EED376">%s</div>'
              '<div style="margin-left:auto;font-size:26px;color:#CBB89B">%s</div></div>'
              % (cur[2], icon(cur[0]), cur[1], cur[3]))
    if gift:
        h += ('<div class="btnGift" style="right:%dpx;top:%dpx"><img src="%simg_gift_icon_4.png">'
              '<div class="lb ol">%s</div></div>') % (gift[0], gift[1], X, gift[2])
    return h


def tier_row(top, no, label, items, state, price=None, orig=None, tag=None, note=None, reach=True):
    """UIMultiTierPack.TierItem 1000×167 原件：竖进度线+节点圆点 / 横排道具 125 / 右侧 200×100 金按钮 / 120 折扣角标"""
    cls = 'tier' + (' done' if state == 'bought' else '') + (' reach' if reach else '')
    h = '<div class="%s" style="left:40px;top:%dpx">' % (cls, top)
    h += '<div class="bg"></div>'
    h += '<div class="vline"><i style="height:%s"></i></div>' % ('196px' if reach else '0')
    h += '<div class="pt">%s</div>' % no
    h += ('<div class="abs olL" style="left:118px;top:14px;font-size:30px;color:#5F4430;font-weight:bold">%s</div>'
          % label)
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


def panel17(left, top, w, h, extra=''):
    return ('<div class="panel17under" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"></div>'
            '<div class="panel17" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s</div>') % (
        left + 6, top + 6, w - 12, h - 12, left, top, w, h, extra)


def slider(w, h, pct, txt='', left=None, top=None):
    st = 'width:%dpx;height:%dpx;' % (w, h)
    if left is not None:
        st += 'position:absolute;left:%dpx;top:%dpx;' % (left, top)
    fw = int((w - 18) * pct)
    return ('<div class="sldA" style="%s"><i style="width:%dpx"></i>%s</div>'
            % (st, fw, ('<span>%s</span>' % txt) if txt else ''))


# ================================================================ 05 兑换商店
# 参照 UIActvExchange：Page 1020 宽（top 645 / h 1055，= sz(1020,-865) pos(0,-212.5)）
#                     Grid cell 300×380 spacing(20,80) padding(L40,B70) → 3 列
def s05():
    b = act_header(ACT['nm'] + ' · 无人机补给站',
                   '用挖掘获得的<b style="color:#EED376">核心电量</b>兑换挖掘道具与纪念卡组件。'
                   '活动结束后核心电量将被回收，记得用完。',
                   cur=(COIN, '12,480', 400, '我的核心电量'), dw=660)
    top, ph = 480, 946
    inner = ''
    fn = {'111110300': '标记本关一个探索目标的位置', '111111048': '开出白色及以上纪念卡组件',
          '111111047': '开出绿色及以上纪念卡组件', '111111000': '挖掘地块的消耗道具',
          '111111046': '开出蓝色及以上纪念卡组件'}
    for k, e in enumerate(EXC):
        gi, gn = e['get'][0]
        px = e['give'][0][1]
        cx, cy = k % 3, k // 3
        L, T = 40 + cx * 320, 24 + cy * 460
        inner += '<div class="abs" style="left:%dpx;top:%dpx;width:300px;height:380px">' % (L, T)
        inner += ('<div class="abs" style="inset:0;background:url(%simg_shop_bg_8.png) center/100%% 100%% no-repeat">'
                  '</div>' % X)
        # GoodsItem 220×220 at top 25（UIItemTemplate 自带名字底板 Item_name）
        inner += item_cell(gi, cnt=gn, size=200, left=50, top=22, name=nm2(gi))
        # text_count（bottom 110，深字 #422919）
        inner += ('<div class="abs olL" style="left:0;right:0;top:252px;text-align:center;font-size:30px;'
                  'color:#422919">剩余可兑换 %d 次</div>' % e['limit'])
        # ExchangeItem 价格行（h60，bottom 48）
        inner += ('<div class="abs" style="left:35px;top:300px;width:230px;height:60px;display:flex;align-items:center;'
                  'justify-content:center;gap:10px;background:url(%simg_VIP_bg_jindutiao_1.png) center/100%% 100%% no-repeat">'
                  '<img src="%s" style="width:46px;height:46px"><span style="font-size:34px;color:#FFF6E9">%s</span></div>'
                  % (X, icon(COIN), '{:,}'.format(px)))
        inner += '</div>'
        # Btn_tips 位（300×60，挂在格子下方）→ 放玩家能懂的功效说明
        inner += ('<div class="abs" style="left:%dpx;top:%dpx;width:300px;font-size:25px;color:#CBB89B;'
                  'text-align:center;line-height:1.25">%s</div>' % (L, T + 392, fn.get(str(gi), '')))
    b += panel17(30, top, 1020, ph, inner)
    b += ('<div class="abs" style="left:30px;top:%dpx;width:1020px;text-align:center;font-size:28px;color:#B9A98C">'
          '每种道具的可兑换次数在活动期内共享，用完不再刷新</div>' % (top + ph + 18))
    return page('05 兑换商店 v2', b)


# ================================================================ 08 排行榜（榜单）
# 参照 UIActvDailyRank：StageReward 名次奖励条(1020×320, slider+3宝箱) → Title 条(1020×68)
#                      → UIRankTemplate 930×196 行 → MyRank 496×104 右下吸底
def s08():
    b = act_header(ACT['nm'] + ' · ' + ACT['rankTitle'],
                   '按<b style="color:#EED376">挖掘格数</b>与<b style="color:#EED376">通关进度</b>计分，'
                   '与全部同期服务器一起排名，实时更新。', dw=960)
    # ---- StageReward 1020×320（Slider 52 + 3 个宝箱 200×180 + sp_num 名次板 204×48）----
    sr_top = 462
    b += ('<div class="abs" style="left:30px;top:%dpx;width:1020px"><div class="biaoti2 ol">'
          '积分里程碑奖励（结算后邮件发放）</div></div>' % (sr_top - 76))
    inner = ''
    boxes = [('1,000 分', 'img_Activity_rank_box04.png'), ('3,000 分', 'img_Activity_rank_box05.png'),
             ('6,000 分', 'img_Activity_rank_box04.png')]
    inner += slider(880, 52, .40, '当前 2,410 / 6,000 分', left=70, top=258)
    for i, (lb, bx) in enumerate(boxes):
        cx = 150 + i * 300
        inner += ('<div class="abs" style="left:%dpx;top:4px;width:200px;height:200px">'
                  '<div class="abs" style="left:2px;top:2px;width:196px;height:196px;background:url(%s%s) '
                  'center/contain no-repeat"></div>'
                  '<div class="abs" style="left:-4px;top:-4px;width:208px;height:208px;background:url(%s%s) '
                  'center/contain no-repeat"></div></div>') % (cx, X, 'img_rank_toyxiangkuang.png', X, bx)
        inner += ('<div class="abs ditu1" style="left:%dpx;top:194px;width:204px;height:48px;display:flex;'
                  'align-items:center;justify-content:center;font-size:30px;color:#EEE48E;z-index:5">%s</div>'
                  % (cx - 2, lb))
    b += ('<div class="abs" style="left:30px;top:%dpx;width:1020px;height:320px">%s</div>' % (sr_top, inner))
    # ---- 榜单：biaoti2 标题条 + UIRankTemplate 930×196 行（spacing 10）----
    lt = sr_top + 328
    b += '<div class="abs" style="left:30px;top:%dpx;width:1020px"><div class="biaoti2 ol">总排名（跨服）</div></div>' % lt
    rows = [(1, 'StarDust', '[VOID]', '18,420', 1), (2, '灰岩矿主', '[T4F]', '17,905', 4),
            (3, 'Kuro_9', '[VOID]', '16,688', 7), (4, 'Malik', '[SAND]', '15,240', 11)]
    y = lt + 82
    for k, (r, name, gd, sc, av) in enumerate(rows):
        top = y + k * 206
        b += '<div class="abs rowLB" style="left:75px;top:%dpx;width:930px;height:196px">' % top
        if r <= 3:
            b += ('<div class="abs" style="left:8px;top:8px;width:268px;height:180px;background:url(%simg_cm_rankbg_icon_%s.png) '
                  'left center/contain no-repeat"></div>' % (X, ['1st', '2ed', '3th'][r - 1]))
            b += ('<div class="abs" style="left:24px;top:1px;width:172px;height:194px;background:url(%simg_cm_rank_icon_%s.png) '
                  'center/contain no-repeat"></div>' % (X, ['1st', '2ed', '3th'][r - 1]))
        else:
            b += ('<div class="abs olL" style="left:25px;top:1px;width:190px;height:194px;display:flex;align-items:center;'
                  'justify-content:center;font-size:60px;color:#7F5F38;font-weight:bold">%d</div>' % r)
        b += ('<div class="abs" style="left:212px;top:-4px;width:200px;height:204px">'
              '<div style="position:absolute;inset:0;background:url(%simg_cm_bg_icon_touxiangkuang1.png) '
              'center/contain no-repeat"></div>'
              '<img src="%sImg_C_H_%d.png" style="position:absolute;left:30px;top:26px;width:140px;height:140px;'
              'border-radius:50%%;object-fit:cover">'
              '<div style="position:absolute;inset:0;background:url(%simg_cm_bg_icon_touxiangkuang1.png) '
              'center/contain no-repeat;mix-blend-mode:normal;'
              '-webkit-mask-image:radial-gradient(circle at 50%% 48%%,transparent 0 38%%,#000 40%%)"></div>'
              '</div>' % (X, X, av, X))
        b += ('<div class="abs" style="left:428px;top:34px;width:360px"><div style="font-size:32px;color:#3E2411;'
              'white-space:nowrap"><b style="color:#6C4E33">%s</b>%s</div>'
              '<div style="margin-top:16px;display:flex;align-items:center;gap:10px">'
              '<img src="%simg_cm_icon_integral.png" style="width:56px;height:52px">'
              '<span style="font-size:32px;color:#7F5F38">%s 分</span></div></div>') % (gd, name, X, sc)
        b += ('<div class="abs" style="left:790px;top:30px">%s</div>'
              % item_cell(RANK[min(r - 1, 7)]['it'][0][0], size=135, pos=False))
        b += '</div>'
    # ---- MyRank 496×104（img_Activity_rank_bg02）吸右下，X3 原件位 = 距底 475 ----
    b += ('<div class="abs" style="right:0;bottom:96px;width:496px;height:104px;'
          'background:url(%simg_Activity_rank_bg02.png) center/100%% 100%% no-repeat">'
          '<div class="abs" style="left:78px;top:12px;width:80px;height:80px;background:url(%simg_TXDS_icon_rank.png) '
          'center/contain no-repeat"></div>'
          '<div class="abs" style="left:176px;top:10px;font-size:34px;color:#F9E9C1">我的排名：24</div>'
          '<div class="abs" style="left:176px;top:54px;font-size:26px;color:#FFF1B9">当前 2,410 分 · 可得第 16–30 名奖励</div></div>'
          ) % (X, X)
    b += ('<div class="abs" style="left:30px;bottom:26px;width:1020px;text-align:center;font-size:26px;color:#9d9078">'
          'X3 现成 UIActvDailyRank 无「榜单 / 奖励」双页签 → 名次奖励在同一页内下滚</div>')
    return page('08 排行榜·榜单 v2', b)


# ================================================================ 11 名次奖励
# 参照 UIActvDailyRank 同页下滚段：taizhangliebiao 行 + biaoti2 段标题 + UIItemTemplate 135
def s11():
    b = act_header(ACT['nm'] + ' · 名次奖励',
                   '活动结束后按最终名次通过<b style="color:#EED376">邮件</b>发放，同一名次段奖励相同。')
    b += ('<div class="abs" style="left:30px;top:400px;width:1020px"><div class="biaoti2 ol">名次奖励一览（共 8 档）</div></div>')
    y = 490
    for k, seg in enumerate(RANK):
        mine = (16 <= seg['s'] <= 30) or (seg['s'] <= 24 <= seg['e'])
        mine = seg['s'] == 16
        lbl = ('第 %d 名' % seg['s']) if seg['s'] == seg['e'] else ('第 %d–%d 名' % (seg['s'], seg['e']))
        if mine:
            h = 300
            b += '<div class="abs rowLB" style="left:30px;top:%dpx;width:1020px;height:%dpx">' % (y, h)
            b += '<div class="abs selFrame"></div>'
            b += ('<div class="abs olL" style="left:52px;top:26px;font-size:40px;color:#3E2411;font-weight:bold">%s</div>'
                  '<div class="abs" style="left:52px;top:82px;font-size:28px;color:#B03A16">我在这一档（当前第 24 名）</div>'
                  % lbl)
            xs = 52
            for j, (iid, cnt) in enumerate(seg['it']):
                b += item_cell(iid, cnt=cnt, size=140, left=xs + j * 155, top=132, name=nm2(iid)[:6])
            b += '</div>'
            y += h + 12
        else:
            h = 128
            b += '<div class="abs rowLB" style="left:30px;top:%dpx;width:1020px;height:%dpx">' % (y, h)
            b += ('<div class="abs olL" style="left:52px;top:40px;font-size:36px;color:#3E2411">%s</div>' % lbl)
            for j, (iid, cnt) in enumerate(seg['it'][:2]):
                b += item_cell(iid, cnt=cnt, size=96, left=372 + j * 108, top=16)
            b += ('<div class="abs" style="left:600px;top:44px;font-size=30px;font-size:30px;color:#7F5F38">'
                  '共 %d 项</div>' % len(seg['it']))
            b += ('<div class="abs" style="right:44px;top:40px;font-size:32px;color:#7F5F38">展开 ▾</div>')
            b += '</div>'
            y += h + 12
    b += ('<div class="abs" style="left:30px;top:%dpx;width:1020px;text-align:center;font-size:28px;color:#B9A98C">'
          '未上榜（积分不足 100）不发放名次奖励</div>' % (y + 8))
    return page('11 名次奖励 v2', b)


# ================================================================ 10 直售礼包页
# 参照 UIPackCommonPop.Chain：ChainItem 920×280，行底 img_gift_bg_7（317/0/159/0），
#                             右侧 Btn 204×84，Discount 角标，Soldout 印章
def s10():
    """参照 Recharge/UIMultiTierPack：TopSp(img_cm_bg_1 112) + Content(img_gift_bg_17) + TierItem 1000×167 ×7"""
    b = '<div class="actBG"></div><div class="actBGfade"></div><div class="actBGlow"></div>'
    # TopSp 112 高标题条（UIMultiTierPack 用的是 img_cm_bg_1，不是活动页头）
    b += ('<div class="abs" style="left:0;top:0;width:1080px;height:112px;background:url(%simg_cm_bg_1.png) '
          'center/100%% 100%% no-repeat"></div>' % X)
    b += '<div class="abs ol" style="left:30px;top:22px;font-size:52px;color:#fff">%s</div>' % ACT['pkg']
    b += ('<div class="abs" style="right:36px;top:16px;width:80px;height:84px;background:url(%simg_multi_tier_buy_btn_close.png) '
          'center/contain no-repeat"></div>' % X)
    b += ('<div class="abs ol" style="left:30px;top:126px;width:1000px;font-size:32px;line-height:1.3;color:#F4EACE">'
          '购买后道具立即到账，可直接用于挖掘。每档每人限购 1 次，活动结束前有效。</div>')
    b += ('<div class="actTime" style="top:196px"><img src="%simg_gift_time.png">'
          '<span>距结束：剩余 2天 13:59:59</span></div>' % X)
    packs = [p for p in PKG if p['tab'] == 'common']
    contents = [[(HOE, '30'), (RADAR, '1')], [(HOE, '80'), (RADAR, '3'), (COIN, '2,000')],
                [(HOE, '150'), (RADAR, '5'), (COIN, '5,000')], [(HOE, '320'), (RADAR, '10'), (COIN, '12,000')],
                [(HOE, '700'), (RADAR, '20'), (COIN, '30,000')], [(HOE, '1,800'), (RADAR, '50'), (COIN, '80,000')],
                [(HOE, '3,800'), (RADAR, '110'), (COIN, '180,000')]]
    disc = ['+20%', '+40%', '+80%', '+150%', '+250%', '+400%', '+700%']
    tiername = ['入门', '进阶', '实用', '超值', '豪华', '典藏', '至尊']
    ptop, ph = 292, 1352
    inner = ''
    y = 24
    for k, p in enumerate(packs):
        st = 'bought' if k == 1 else 'buy'
        pr = float(p['price'].strip('$'))
        orig = '$%.2f' % (pr * (1 + int(disc[k].strip('+%')) / 100.0))
        inner += tier_row(y, k + 1, '第 %d 档 · %s' % (k + 1, tiername[k]), contents[k], st,
                          price='US' + p['price'], orig=orig, tag=('超值', disc[k]),
                          note=('每人限购 1 次（已购）' if st == 'bought' else '每人限购 1 次'))
        y += 185
    b += panel17(30, ptop, 1020, ph, inner)
    b += ('<div class="abs" style="left:30px;top:%dpx;width:1020px;text-align:center;font-size:26px;color:#9d9078">'
          '实机为竖向滚动列表（此图把 7 档一次铺完便于评审）</div>' % (ptop + ph + 12))
    return page('10 直售礼包页 v2', b)


# ================================================================ 02 成就礼包
# 参照 UIPackCommonPop.Chain（同一行件）+ UIActvCumRecharge 的进度表达（txt/大数/txt）
def s02():
    """参照 Recharge/UIMultiTierPack（TierItem 1000×167 + 竖进度线/节点）+ UIActvCumRecharge 的进度文案块"""
    b = '<div class="actBG"></div><div class="actBGfade"></div><div class="actBGlow"></div>'
    b += ('<div class="abs" style="left:0;top:0;width:1080px;height:112px;background:url(%simg_cm_bg_1.png) '
          'center/100%% 100%% no-repeat"></div>' % X)
    b += '<div class="abs ol" style="left:30px;top:22px;font-size:52px;color:#fff">%s</div>' % ACT['apkg']
    b += ('<div class="abs" style="right:36px;top:16px;width:80px;height:84px;background:url(%simg_multi_tier_buy_btn_close.png) '
          'center/contain no-repeat"></div>' % X)
    # UIActvCumRecharge 式进度块（小标题 fs35 + 大数 fs58 + 提示）
    b += ('<div class="abs" style="left:30px;top:132px;width:1020px;height:150px">'
          '<div class="abs seg13" style="inset:0"></div>'
          '<div class="abs" style="left:40px;top:18px;font-size:35px;color:#fff">已通关</div>'
          '<div class="abs" style="left:40px;top:60px;font-size:58px;color:#EFDBBD">'
          '<span style="color:#e85b23">17</span> / 120 关</div>'
          '<div class="abs" style="right:40px;top:36px;width:520px;text-align:right;font-size:30px;color:#EFDBBD;'
          'line-height:1.5">已解锁 4 档 · 已购 1 档 · 共 15 档<br>'
          '<span style="color:#EED376">再通关 3 关解锁第 5 档</span></div></div>')
    packs = [p for p in PKG if p['tab'] == 'achievement']
    prices = ['$0.99', '$1.99', '$2.99', '$4.99', '$6.99', '$9.99', '$12.99', '$19.99',
              '$24.99', '$29.99', '$39.99', '$49.99', '$69.99', '$79.99', '$99.99']
    ptop, ph = 302, 1120
    inner, y = '', 24
    for k, p in enumerate(packs):
        st = 'bought' if k == 0 else ('buy' if k <= 3 else 'lock')
        if k > 4:
            continue
        cont = [(HOE, '{:,}'.format(20 * (k + 2))), (RADAR, str(k + 2)),
                (COIN, '{:,}'.format(1000 * (k + 2)))]
        inner += tier_row(y, k + 1, '第 %d 档 · 通关第 %d 关解锁' % (k + 1, p['gate']), cont, st,
                          price='US' + prices[k], tag=None,
                          note=('每人限购 1 次（已购）' if st == 'bought' else ('还需通关 3 关' if st == 'lock' else '每人限购 1 次')),
                          reach=(k <= 3))
        y += 185
    # 未解锁段折成一行（沿用官方列表行底 img_ledger_bg_taizhangliebiao）
    inner += ('<div class="abs rowLB" style="left:40px;top:%dpx;width:1000px;height:130px">'
              '<div class="abs olL" style="left:46px;top:26px;font-size:34px;color:#3E2411">未解锁 · 第 6–15 档</div>'
              '<div class="abs" style="left:46px;top:72px;font-size:27px;color:#7F5F38">'
              '通关第 25 / 30 / 35 / 40 / 45 / 50 / 60 / 70 / 80 / 85 关后依次解锁</div>'
              '<div class="abs" style="right:44px;top:46px;font-size:32px;color:#7F5F38">展开 ▾</div></div>' % y)
    b += panel17(30, ptop, 1020, ph, inner)
    b += ('<div class="abs" style="left:30px;top:%dpx;width:1020px;text-align:center;font-size:26px;color:#9d9078">'
          '档位行 = 克隆 UIMultiTierPack.TierItem；「解锁条件」文字是唯一需要新增的节点</div>' % (ptop + ph + 12))
    return page('02 成就礼包 v2', b)


# ================================================================ 09 关卡奖励预览
# X3 无「长列表关卡预览」现成件 → 骨架借 UIActvDailyRank（biaoti2 标题条 + taizhangliebiao 行）
#                                 + StageTabs 分段页签
def s09():
    b = act_header(ACT['nm'] + ' · 关卡奖励',
                   '共 120 关，已自动定位到当前关。奖励关（level 为负）在「奖励关」页签里单独看。')
    # StageTabs 分段页签（img_Activity_arrow_1/2，h64，spacing -30）
    tabs = ['1–30', '31–60', '61–90', '91–120', '奖励关']
    xx = 26
    for i, t in enumerate(tabs):
        on = (i == 0)
        b += ('<div class="abs stageTab %s" style="left:%dpx;top:400px;width:214px">%s</div>'
              % ('on' if on else 'off', xx, t))
        xx += 214 - 30
    b += '<div class="abs" style="left:30px;top:474px;width:1020px"><div class="biaoti2 ol">第 1–30 关</div></div>'
    y = 556
    rows = [l for l in LV if l['t'] == 1][8:16]
    for k, l in enumerate(rows):
        cur = (l['l'] == 12)
        big = (l['l'] % 10 == 0)
        h = 150
        b += '<div class="abs rowLB" style="left:30px;top:%dpx;width:1020px;height:%dpx">' % (y, h)
        if cur:
            b += '<div class="abs selFrame"></div>'
        b += ('<div class="abs olL" style="left:46px;top:26px;font-size:40px;color:#3E2411;font-weight:bold">第 %d 关</div>'
              % l['l'])
        nb = len(l['b'])
        b += ('<div class="abs" style="left:46px;top:80px;font-size:28px;color:#7F5F38">%d×%d 棋盘 · %s</div>'
              % (l['r'], l['r'], ('不可挖 %d 格' % nb) if nb else '全部地块可挖'))
        if cur:
            b += ('<div class="abs" style="left:300px;top:32px;width:120px;height:52px;display:flex;align-items:center;'
                  'justify-content:center;font-size:28px;color:#FFF6E9;background:url(%simg_cm_anniu1_blue.png) '
                  'center/100%% 100%% no-repeat">当前</div>' % X)
        if big:
            b += ('<div class="abs" style="left:300px;top:32px;width:130px;height:52px;display:flex;align-items:center;'
                  'justify-content:center;font-size:28px;color:#3E2411;background:url(%simg_ledger_bg_ditu1.png) '
                  'center/100%% 100%% no-repeat">大奖关</div>' % X)
        rw = l['rw'] or [[HOE, 1]]
        for j, (iid, cnt) in enumerate(rw[:3]):
            b += item_cell(iid, cnt=cnt, size=112, left=520 + j * 124, top=20)
        # 埋藏宝物缩略
        tg = [t for t in TRS if t['grp'] == 2][:2]
        b += ('<div class="abs" style="right:36px;top:56px;font-size=28px;font-size:28px;color:#7F5F38;'
              'text-align:right">埋藏 %d 件宝物</div>' % max(1, len(l['p'])))
        b += '</div>'
        y += h + 10
    return page('09 关卡奖励预览 v2', b)


# ================================================================ 03 存钱罐
# 参照 UIPiggyBankContent 920×520 面板（左信息右猪 / slider / 额外奖励横排 / UIBtnPurchase / 20倍角标）
#      外套标准弹窗 img_cm_bg_tanchu + img_cm_biaoti + UITitle
def s03():
    b = '<div class="bgFull"></div><div class="bgFullShade"></div><div class="mask"></div>'
    pw, ph, ptop = 1020, 900, 510
    inner = ''
    inner += ('<div class="popTitlePlate ol">能量存钱罐</div><div class="popClose"></div>')
    # PiggyBank 内容面板 920×520
    cl, ct = 50, 130
    inner += ('<div class="abs" style="left:%dpx;top:%dpx;width:920px;height:520px">' % (cl, ct))
    inner += ('<div class="abs" style="left:5px;top:8px;width:910px;height:504px;background:url(%sui_Howtogetit_bg_2.png) '
              'center/100%% 100%% no-repeat"></div>' % X)
    # 右侧存钱罐大图（MainPigBg 448×404）
    inner += ('<div class="abs" style="right:8px;top:58px;width:448px;height:404px;background:url(%s) '
              'center/contain no-repeat"></div>' % 'assets/DigPiggyIcon.png')
    inner += ('<div class="disc" style="right:-18px;top:-18px"><s>取出</s><b>×36</b></div>')
    # 左侧信息列（Bg2 308×448 → 我们放宽到 430）
    inner += ('<div class="abs" style="left:36px;top:36px;width:430px;height:448px;'
              'border-style:solid;border-width:0;border-image:url(%sui_Howtogetit_bg_3.png) 50 100 50 100 fill stretch">'
              '</div>' % X)
    inner += '<div class="abs ol" style="left:66px;top:64px;font-size:38px;color:#fff">能量存钱罐</div>'
    inner += ('<div class="abs" style="left:66px;top:120px;width:250px;height:50px;display:flex;align-items:center;'
              'gap:12px;padding:0 16px;border-style:solid;border-width:0;'
              'border-image:url(%sui_Howtogetit_bg_4.png) 16 50 16 50 fill stretch">'
              '<img src="assets/DigKeyIcon.png" style="width:44px;height:44px">'
              '<span style="font-size:36px;color:#fff">36 / 50</span></div>' % X)
    # slider（ui_piggybank_JDT_1/2）
    inner += ('<div class="abs" style="left:66px;top:190px;width:370px;height:54px;border-style:solid;border-width:0;'
              'border-image:url(%sui_piggybank_JDT_1.png) 12 10 12 10 fill stretch">'
              '<div class="abs" style="left:8px;top:8px;bottom:8px;width:%dpx;border-style:solid;border-width:0;'
              'border-image:url(%sui_piggybank_JDT_2.png) 12 fill stretch"></div>'
              '<div class="abs" style="inset:0;display:flex;align-items:center;justify-content:center;font-size:26px;'
              'color:#3C2A12;font-weight:bold">已存 72%%</div></div>') % (X, int(354 * .72), X)
    inner += ('<div class="abs" style="left:66px;top:258px;width:370px;font-size:26px;color:#EFDBBD;line-height:1.4">'
              '每消耗 2 个能量铲存入 1 个；存满 50 后停止累积。</div>')
    inner += '<div class="abs" style="left:66px;top:330px;font-size:26px;color:#EEDBBD">取出可得</div>'
    inner += item_cell(HOE, cnt=36, size=128, left=66, top=364)
    inner += item_cell(RADAR, cnt=2, size=128, left=210, top=364)
    inner += '</div>'
    # UIBtnPurchase 296×100（gold）+ 原价
    inner += ('<div class="abs" style="left:%dpx;top:%dpx;width:380px;text-align:center;font-size:28px;'
              'color:#8A6A3A"><span style="text-decoration:line-through">价值 $14.97</span></div>'
              % ((pw - 380) // 2, ct + 552))
    inner += ('<div class="abs btnGold ol" style="left:%dpx;top:%dpx;font-size:42px">取出　US$4.99</div>'
              % ((pw - 380) // 2, ct + 594))
    inner += ('<div class="abs" style="left:0;right:0;top:%dpx;text-align:center;font-size:32px;color:#7F5F38">'
              '取出后存钱罐清零，可继续存入</div>' % (ct + 706))
    # 左右翻页箭头（Arrow）
    inner += ('<div class="abs" style="left:8px;top:%dpx;width:60px;height:108px;background:url(%simg_ledger_anniu_jiantou2.png) '
              'center/contain no-repeat"></div>' % (ct + 210, X))
    inner += ('<div class="abs" style="right:8px;top:%dpx;width:60px;height:108px;background:url(%simg_ledger_anniu_jiantou2.png) '
              'center/contain no-repeat;transform:scaleX(-1)"></div>' % (ct + 210, X))
    b += ('<div class="popup" style="top:%dpx;width:%dpx;height:%dpx">%s</div>' % (ptop, pw, ph, inner))
    return page('03 存钱罐 v2', b)


# ================================================================ 04 玩法规则
# 参照 UiActivityCommonRules：全屏台账 BG + TitleBar 127 + Tabs 100 + 行模板 + BottomPublicBtnEmpty 207
def s04():
    b = '<div class="ledgerBG"></div>'
    b += '<div class="ledgerTitleBar"><span class="ol">玩法规则</span></div>'
    # Content 内层黑框 + Tabs
    b += '<div class="blackRound" style="left:24px;top:150px;width:1032px;height:1520px"></div>'
    tabs = ['基础玩法', '工具与探测', '奖励与排行', '道具回收']
    xx = 34
    for i, t in enumerate(tabs):
        on = (i == 0)
        b += ('<div class="abs tabLedger %s" style="left:%dpx;top:170px;width:276px">%s</div>'
              % ('on' if on else 'off', xx, t))
        xx += 276 - 27
    # 正文（ItemTitle / ItemTitleWithBg / ItemText 三种官方行）
    y = 306
    blocks = [('tt', '怎么玩'),
              ('tx', '消耗<b>能量铲</b>挖开棋盘地块。地块下埋着形状各异的<b>探索目标</b>，把某个目标的所有格子全部挖开，即算收集成功，收进异星图鉴。'),
              ('tt', '关卡与推进'),
              ('tx', '共 120 关，逐关推进。每关棋盘尺寸、不可挖地块、埋藏目标都不同；通关后自动进入下一关，并结算该关奖励。'),
              ('tt', '工具与探测仪'),
              ('tx', '使用<b>探测仪</b>可先选定一个探索目标，系统会在本关棋盘上标出它的位置，再挖不靠猜。<b>火箭 / 地雷</b>等工具会在连续挖掘时触发，一次清掉一片地块。'),
              ('tt', '排行与奖励'),
              ('tx', '按<b>挖掘格数</b>与<b>通关进度</b>计分，与全部同期服务器一起排名。积分满 100 分进入排行榜；活动结束后按最终名次通过<b>邮件</b>发放名次奖励。'),
              ('tt', '道具回收'),
              ('tx', '活动结束后，<b>核心电量</b>与未使用的活动道具将被回收，请在结束前用完或兑换。'),
              ]
    for kind, txt in blocks:
        if kind == 't2':
            b += ('<div class="abs itTitleBg olL" style="left:45px;top:%dpx">%s</div>' % (y, txt))
            y += 112
        elif kind == 'tt':
            b += ('<div class="abs itTitle" style="left:45px;top:%dpx;width:990px">%s<i></i></div>' % (y, txt))
            y += 66
        else:
            t = txt.replace('<b>', '<b style="color:#B0651F">')
            h = 150 if len(txt) < 110 else 196
            b += ('<div class="abs itText" style="left:45px;top:%dpx;height:%dpx">%s</div>' % (y, h, t))
            y += h + 16
    # 底部按钮条
    b += ('<div class="ledgerBottom"><div class="bk"></div><div class="ret"></div></div>')
    return page('04 玩法规则 v2', b)


# ================================================================ 12 通行证入口
# 参照 Activity/ActvRank（380×120 入口卡）+ Activity/DailyGift（135）+ Button/UIBtnGift（170）
# 面板不做：点入口 jump_link 到 UIActvBattlePassScore（现成）
def s12():
    b = '<div class="actBG"></div><div class="actBGfade"></div><div class="actBGlow"></div>'
    b += '<div class="actTitle ol">%s</div>' % ACT['nm']
    b += '<div class="actTime"><img src="%simg_gift_time.png"><span>距结束：剩余 2天 13:59:59</span></div>' % X
    b += '<div class="btnInfo"></div>'
    b += ('<div class="abs" style="right:23px;top:216px;width:400px;height:74px;display:flex;align-items:center;'
          'gap:12px;padding:0 24px;border-style:solid;border-width:0;'
          'border-image:url(%sim_bm_bg_13.png) 37 0 34 0 fill stretch">'
          '<img src="%s" style="width:52px;height:52px"><span style="font-size:32px;color:#EED376">1,240</span>'
          '<img src="%s" style="width:52px;height:52px;margin-left:18px">'
          '<span style="font-size:32px;color:#EED376">3</span></div>' % (X, icon(HOE), icon(RADAR)))

    def entry_card(side, w, icon_img, label, extra, flip=False):
        h = '<div class="abs" style="%s:36px;top:352px;width:%dpx;height:120px">' % (side, w)
        h += ('<div class="abs" style="left:28px;right:28px;top:0;bottom:0;border-style:solid;border-width:0;'
              'border-image:url(%simg_Activity_bg_05.png) 28 fill stretch"></div>' % X)
        h += ('<div class="abs" style="left:-8px;top:-10px;width:136px;height:136px;background:url(%s) '
              'center/contain no-repeat;%s"></div>' % (icon_img, 'transform:scaleX(-1)' if flip else ''))
        h += ('<div class="abs ol" style="left:-8px;top:124px;width:136px;text-align:center;font-size:28px;'
              'color:#F4E3C7">%s</div>' % label)
        return h + extra + '</div>'

    # ① 排行榜入口卡（Activity/ActvRank 380×120 原件，露出第 1 名奖励）
    b += entry_card('left', 400, X + 'img_TXDS_icon_rank.png', '排行榜',
                    item_cell(RANK[0]['it'][0][0], size=100, left=142, top=10)
                    + item_cell(RANK[0]['it'][1][0], size=100, left=250, top=10))
    # ② 通行证入口卡（同 ActvRank 骨架 + Lv/进度小标签；面板不做，jump_link 跳 UIActvBattlePassScore）
    pass_extra = (
        '<div class="abs" style="left:140px;top:12px;width:140px;height:44px;display:flex;align-items:center;'
        'justify-content:center;font-size:28px;color:#F7EBCE;border-style:solid;border-width:0;'
        'border-image:url(%simg_Activity_woodenstake_jdt_1.png) 13 16 16 15 fill stretch">Lv.2</div>'
        '<div class="abs" style="left:140px;top:66px;width:140px;text-align:center;font-size:24px;'
        'color:#EFDBBD">150 / 1,000</div>'
        '%s<div class="reddot" style="right:6px;top:-4px"></div>'
    ) % (X, item_cell(11116304, size=100, left=290, top=10))
    b += entry_card('right', 430, X + 'img_gift_icon_4.png', '通行证', pass_extra, flip=True)

    # ③ 关卡标题条 + 棋盘（5×5，格 150）
    b += '<div class="abs biaoti2 ol" style="left:390px;top:516px;width:300px">关卡 12</div>'
    b += ('<div class="abs" style="left:145px;top:610px;width:790px;display:grid;'
          'grid-template-columns:repeat(5,150px);grid-auto-rows:150px;gap:10px;justify-content:center">')
    for i in range(25):
        blk = i in (6, 7, 8, 16, 18)
        b += ('<div style="background:url(assets/gridcellbg%s.png) center/100%% 100%% no-repeat;%s"></div>'
              % ('3' if blk else '1', 'filter:brightness(.7) saturate(.4)' if blk else ''))
    b += '</div>'
    # ④ 说明条（seg13）
    b += ('<div class="abs" style="left:30px;top:1450px;width:1020px;height:140px;border-style:solid;border-width:0;'
          'border-image:url(%sim_bm_bg_13.png) 37 0 34 0 fill stretch"></div>' % X)
    b += ('<div class="abs" style="left:70px;top:1480px;width:940px;text-align:center;font-size:29px;'
          'line-height:1.5;color:#EFDBBD">'
          '通行证在挖孔内<span style="color:#EED376">只做 HUD 入口</span>（右上这张卡）<br>'
          '点击走 jump_link 跳到 X3 现成通行证界面 UIActvBattlePassScore，挖孔内不做面板</div>')
    # ⑤ 底部功能栏（DailyGift 135 范式）
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
    return page('12 通行证入口 v2', b)


PAGES = [
    ('02_成就礼包_v2对齐X3', s02), ('03_存钱罐_v2对齐X3', s03), ('04_玩法规则_v2对齐X3', s04),
    ('05_兑换商店_v2对齐X3', s05), ('08_排行榜_榜单_v2对齐X3', s08), ('09_关卡奖励预览_v2对齐X3', s09),
    ('10_直售礼包页_v2对齐X3', s10), ('11_名次奖励_v2对齐X3', s11), ('12_通行证入口_v2对齐X3', s12),
]

if __name__ == '__main__':
    for n, f in PAGES:
        open(os.path.join(HERE, n + '.html'), 'w', encoding='utf-8').write(f())
    sys.stdout.reconfigure(encoding='utf-8')
    print('generated', len(PAGES))
