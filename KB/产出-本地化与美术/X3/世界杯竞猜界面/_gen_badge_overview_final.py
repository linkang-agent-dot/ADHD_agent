# -*- coding: utf-8 -*-
import io, sys, glob, os, re, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
import numpy as np

d = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\队徽48_勋章FINAL'
os.chdir(d)
NAMES = {'ALG':'阿尔及利亚','ARG':'阿根廷','AUS':'澳大利亚','AUT':'奥地利','BEL':'比利时','BIH':'波黑','BRA':'巴西','CAN':'加拿大','CIV':'科特迪瓦','COD':'刚果','COL':'哥伦比亚','CPV':'佛得角','CRO':'克罗地亚','CUW':'库拉索','CZE':'捷克','ECU':'厄瓜多尔','EGY':'埃及','ENG':'英格兰','ESP':'西班牙','FRA':'法国','GER':'德国','GHA':'加纳','HAI':'海地','IRN':'伊朗','IRQ':'伊拉克','JOR':'约旦','JPN':'日本','KOR':'韩国','KSA':'沙特','MAR':'摩洛哥','MEX':'墨西哥','NED':'荷兰','NOR':'挪威','NZL':'新西兰','PAN':'巴拿马','PAR':'巴拉圭','POR':'葡萄牙','QAT':'卡塔尔','RSA':'南非','SCO':'苏格兰','SEN':'塞内加尔','SUI':'瑞士','SWE':'瑞典','TUN':'突尼斯','TUR':'土耳其','URU':'乌拉圭','USA':'美国','UZB':'乌兹别克'}

cards = []
for f in sorted(glob.glob('WC_Badge_???.png')):
    c = re.search(r'Badge_([A-Z]{3})', f).group(1)
    im = Image.open(f).convert('RGBA'); a = np.array(im)[:, :, 3]
    W, H = im.size
    semi = ((a > 30) & (a < 225)).sum() / a.size * 100
    ys, xs = np.where(a > 40)
    L, R, T, B = int(xs.min()), int(W-1-xs.max()), int(ys.min()), int(H-1-ys.max())
    bw = (xs.max()-xs.min()+1)/W*100; bh = (ys.max()-ys.min()+1)/H*100
    nm = NAMES.get(c, c)
    cards.append('<div class=cd><img src="%s"><div class=nm>%s <span>%s</span></div>'
                 '<div class=mt>%d×%d | 占画面 %d×%d%%<br>边距 上%d 下%d 左%d 右%d | 透%s%%</div></div>'
                 % (f, nm, c, W, H, bw, bh, T, B, L, R, round(semi,1)))

doc = """<html><head><meta charset=utf-8><style>
body{background:#1a1d29;color:#eee;font-family:sans-serif;padding:20px}
h2{text-align:center} .sub{text-align:center;color:#9aa;margin-bottom:18px;font-size:13px}
.g{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;max-width:1500px;margin:auto}
.cd{background:#252a3a;border-radius:10px;padding:9px;text-align:center}
.cd img{width:100%;background:repeating-conic-gradient(#444 0 25%,#383838 0 50%) 50%/18px 18px;border-radius:6px}
.nm{font-size:14px;font-weight:bold;margin-top:5px} .nm span{color:#7af;font-size:11px}
.mt{font-size:10px;color:#9ab;margin-top:3px;line-height:1.5}
</style></head><body>
<h2>世界杯48队徽 FINAL — 足球+国旗盾合体勋章</h2>
<div class=sub>统一: 256×256 · 占画面~82% · 透明<5% · 国旗已逐张核对(NZL/RSA/UZB/QAT/ESP重出修正) | 共 __N__ 队</div>
<div class=g>__CARDS__</div></body></html>"""
doc = doc.replace('__N__', str(len(cards))).replace('__CARDS__', ''.join(cards))
open('_总览48_FINAL.html', 'w', encoding='utf-8').write(doc)
print('总览生成,', len(cards), '队')
