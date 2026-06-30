# -*- coding: utf-8 -*-
"""
异国美酒储蓄罐 回归报告 · 每日图表自动更新（纯 Python，供 Windows 计划任务直调）
干啥：拉 datain 日数据 → 重算两张时序图(ARPPU/日流水折线 + 储蓄罐vs纯异国美酒礼包堆叠面积) → 回写 HTML。
只更新「图表 + 数据截至日期」；漏斗/表/KPI 是上线窗快照，不动（用户口径）。
计划任务：直调 python.exe + 本脚本路径（中文路径勿走 .bat）。datain 用持久化 User 环境变量 DATAIN_API_KEY。
"""
import os, sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\ADHD_agent\.claude\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

HTML = r'C:\ADHD_agent\KB\产出-数值设计\X3_异国美酒储蓄罐\异国美酒储蓄罐_增加档位分析.html'
START = '2026-06-15'
LAUNCH = '2026-06-25'
REV = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
PIGGY_IDS = "'500031','500032'"
PURE_IDS  = "'11600','11601','11602'"
# 固定基线（6/15–24 全前期均值，不随时间变）
BM_ARPPU, BM_REV, BM_TOTAL = 9.99, 815, 1563

def q(sql):
    last = None
    for _ in range(2):                     # datain 偶发超时/抖动 → 重试1次(每次上限600s,控制总挂时)
        try:
            return execute_sql(sql, 'TRINO_HF')
        except Exception as e:
            last = e
    raise last

def main():
    pig = {r['pd']: r for r in q(
        "SELECT partition_date pd, count(distinct user_id) b, "
        "round(sum(%s),1) rev FROM v1090.ods_user_order "
        "WHERE iap_id IN (%s) AND pay_status=1 AND partition_date>='%s' GROUP BY partition_date"
        % (REV, PIGGY_IDS, START))}
    pur = {r['pd']: float(r['rev']) for r in q(
        "SELECT partition_date pd, round(sum(%s),1) rev FROM v1090.ods_user_order "
        "WHERE iap_id IN (%s) AND pay_status=1 AND partition_date>='%s' GROUP BY partition_date"
        % (REV, PURE_IDS, START))}
    dates = sorted(pig.keys())
    if not dates:
        print('NO DATA'); return 1
    DATES, ARPPU, REVA, PURE, TOTAL = [], [], [], [], []
    for d in dates:
        b = int(pig[d]['b'] or 0); rv = float(pig[d]['rev'] or 0)
        pv = float(pur.get(d, 0))
        DATES.append('%d/%d' % (int(d[5:7]), int(d[8:10])))
        ARPPU.append(round(rv / b, 2) if b else 0)
        REVA.append(round(rv))
        PURE.append(round(pv))
        TOTAL.append(round(rv + pv))
    asof = dates[-1]                       # 最新数据日（可能未满）
    n = len(dates)
    li = dates.index(LAUNCH) if LAUNCH in dates else 10   # 上线日索引
    # 「后」窗 = 6/26 .. 最新前一天（剔除当天未满）
    post = [i for i, d in enumerate(dates) if d >= '2026-06-26' and i < n - 1]
    mean = lambda xs: round(sum(xs) / len(xs)) if xs else 0
    am_arppu = round(sum(ARPPU[i] for i in post) / len(post), 2) if post else 14.2
    am_rev   = mean([REVA[i] for i in post]) or 1169
    am_total = mean([TOTAL[i] for i in post]) or 1789
    asof_md  = '%d/%d' % (int(asof[5:7]), int(asof[8:10]))

    h = open(HTML, encoding='utf-8').read()
    # 1) 折线数据
    h = re.sub(r'var DATES=\[.*?\];', 'var DATES=[%s];' % ','.join("'%s'" % x for x in DATES), h, 1)
    h = re.sub(r'var ARPPU=\[.*?\];', 'var ARPPU=[%s];' % ','.join(str(x) for x in ARPPU), h, 1)
    h = re.sub(r'var REV=\[.*?\];',   'var REV=[%s];'   % ','.join(str(x) for x in REVA), h, 1)
    # 2) SERIES 后均值（前均固定）
    h = re.sub(r'(arppu:\{data:ARPPU,before:9\.99,after:)[\d.]+', r'\g<1>%.2f' % am_arppu, h, 1)
    h = re.sub(r'(rev:\{data:REV,before:815,after:)[\d.]+', r'\g<1>%d' % am_rev, h, 1)
    # 3) 面积图重绘
    h = re.sub(r'<svg viewBox="0 0 1000 340".*?</svg>', lambda m: area_svg(DATES, PURE, TOTAL, li, post, am_total), h, 1, flags=re.S)
    # 4) 日期文案
    h = re.sub(r'数据截至 \d{4}-\d{2}-\d{2}', '数据截至 %s' % asof, h)
    h = re.sub(r'\d+/\d+ 为当天未满日', '%s 为当天未满日' % asof_md, h)
    open(HTML, 'w', encoding='utf-8').write(h)
    print('OK asof=%s days=%d ARPPU_after=%.2f REV_after=%d TOTAL_after=%d' % (asof, n, am_arppu, am_rev, am_total))
    return 0

def area_svg(DATES, PURE, TOTAL, li, post, am_total):
    W,H,padL,padR,padT,padB,ymax=1000,340,64,22,20,34,2400
    n=len(DATES)
    X=lambda i: padL+(W-padL-padR)*i/(n-1)
    Y=lambda v: padT+(H-padT-padB)*(1-v/ymax)
    Yb=Y(0); g=['<svg viewBox="0 0 %d %d" style="width:100%%;height:auto">'%(W,H)]
    v=0
    while v<=ymax+0.001:
        yy=Y(v); g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#2b3744"/>'%(padL,yy,W-padR,yy))
        g.append('<text x="%g" y="%g" fill="#8b98a5" font-size="12" text-anchor="end">$%d</text>'%(padL-7,yy+4,v)); v+=600
    for i,xl in enumerate(DATES):
        if i%2==0 or i==n-1: g.append('<text x="%g" y="%g" fill="#8b98a5" font-size="12" text-anchor="middle">%s</text>'%(X(i),H-padB+18,xl))
    pp='%g,%g '%(X(0),Yb)+' '.join('%g,%g'%(X(i),Y(PURE[i])) for i in range(n))+' %g,%g'%(X(n-1),Yb)
    g.append('<polygon points="%s" fill="#3b6ea5" fill-opacity="0.55"/>'%pp)
    pg=' '.join('%g,%g'%(X(i),Y(TOTAL[i])) for i in range(n))+' '+' '.join('%g,%g'%(X(i),Y(PURE[i])) for i in range(n-1,-1,-1))
    g.append('<polygon points="%s" fill="#e3b341" fill-opacity="0.5"/>'%pg)
    g.append('<polyline points="%s" fill="none" stroke="#3fb950" stroke-width="3"/>'%(' '.join('%g,%g'%(X(i),Y(TOTAL[i])) for i in range(n))))
    lx=X(li); g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#d29922" stroke-width="1.5" stroke-dasharray="4 4"/>'%(lx,padT,lx,H-padB))
    g.append('<text x="%g" y="%g" fill="#d29922" font-size="11">&#9650; 6/25 上线</text>'%(lx+5,padT+12))
    # 大盘前均(6/15-24=idx0..9 固定) / 后均(post)
    g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#3fb950" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.95"/>'%(X(0),Y(1563),X(9),Y(1563)))
    g.append('<text x="%g" y="%g" fill="#3fb950" font-size="12" text-anchor="middle">大盘前均 $1,563</text>'%(X(4.5),Y(1563)-6))
    if post:
        g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#3fb950" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.95"/>'%(X(post[0]),Y(am_total),X(post[-1]),Y(am_total)))
        g.append('<text x="%g" y="%g" fill="#3fb950" font-size="12" text-anchor="start">后均 $%s</text>'%(X(post[-1])+4,Y(am_total)+4,format(am_total,',')))
    g.append('</svg>'); return ''.join(g)

if __name__=='__main__':
    sys.exit(main())
