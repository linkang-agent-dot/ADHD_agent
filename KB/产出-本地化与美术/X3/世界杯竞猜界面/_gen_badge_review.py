# -*- coding: utf-8 -*-
import io, sys, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
import numpy as np

base = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面'
os.chdir(base)

dirs = [('重出FINAL', '队徽48_重出FINAL'), ('重出试点4', '队徽48_重出试点4'),
        ('重抠试点', '队徽48_重抠试点'), ('重出NZL_SWE', '队徽48_重出NZL_SWE')]
best = {}
for tag, d in dirs:
    for f in glob.glob(d + '/WC_Badge_???.png'):
        c = re.search(r'Badge_([A-Z]{3})\.png', os.path.basename(f)).group(1)
        im = Image.open(f).convert('RGBA'); a = np.array(im)[:, :, 3]
        W, H = im.size
        semi = ((a > 30) & (a < 225)).sum() / a.size * 100
        fill = (a > 200).sum() / a.size * 100
        ys, xs = np.where(a > 100)
        if len(xs):
            L = xs.min(); R = W - 1 - xs.max(); T = ys.min(); B = H - 1 - ys.max()
            bbw = (xs.max() - xs.min() + 1) / W * 100
            bbh = (ys.max() - ys.min() + 1) / H * 100
        else:
            L = R = T = B = bbw = bbh = 0
        rel = f.replace(os.sep, '/')
        rec = (rel, tag, round(semi, 1), im.size, round(fill), round(bbw), round(bbh), int(T), int(B), int(L), int(R))
        if c not in best or semi < best[c][2]:
            best[c] = rec

ref = {}
for c in ['BRA', 'ARG']:
    f = '队徽48/WC_Badge_%s.png' % c
    im = Image.open(f).convert('RGBA'); a = np.array(im)[:, :, 3]
    W, H = im.size
    fill = (a > 200).sum() / a.size * 100
    ys, xs = np.where(a > 100)
    L = xs.min(); R = W - 1 - xs.max(); T = ys.min(); B = H - 1 - ys.max()
    bbw = (xs.max() - xs.min() + 1) / W * 100
    bbh = (ys.max() - ys.min() + 1) / H * 100
    ref[c] = (f, '标杆', round(((a > 30) & (a < 225)).sum() / a.size * 100, 1), im.size, round(fill), round(bbw), round(bbh), int(T), int(B), int(L), int(R))

def card(c, rec, isref=False):
    f, tag, semi, sz, fill, bbw, bbh, T, B, L, R = rec
    cls = 'ref' if isref else ''
    cb = '' if isref else ('<label><input type=checkbox class=ck data-code="%s" onchange=save()> 免标准化(已OK)</label>' % c)
    star = ' ★标杆' if isref else ''
    return ('<div class="cd %s"><img src="%s"><div class=nm>%s%s</div>'
            '<div class=mt>%d×%d | 填充%d%% | 占画面 %d×%d%%<br>'
            '边距 上%d 下%d 左%d 右%d px | 半透明%s%%</div>%s</div>'
            ) % (cls, f, c, star, sz[0], sz[1], fill, bbw, bbh, T, B, L, R, semi, cb)


cards = [card(c, ref[c], True) for c in ['BRA', 'ARG']]
for c in sorted(best):
    cards.append(card(c, best[c]))

js = """
function save(){let s=[...document.querySelectorAll('.ck:checked')].map(x=>x.dataset.code);
localStorage.setItem('badge_ok',JSON.stringify(s));render();}
function render(){let s=JSON.parse(localStorage.getItem('badge_ok')||'[]');
document.getElementById('out').textContent=s.length?s.join(' '):'(未勾选)';
document.getElementById('cnt').textContent=s.length;}
function load(){let s=JSON.parse(localStorage.getItem('badge_ok')||'[]');
document.querySelectorAll('.ck').forEach(x=>{x.checked=s.includes(x.dataset.code)});render();}
function clr(){localStorage.removeItem('badge_ok');document.querySelectorAll('.ck').forEach(x=>x.checked=false);render();}
function cp(){navigator.clipboard.writeText(document.getElementById('out').textContent);alert('已复制,发给Kiro');}
window.onload=load;
"""

doc = """<html><head><meta charset=utf-8><style>
body{background:#1a1d29;color:#eee;font-family:sans-serif;padding:20px}
h2{text-align:center}
.bar{position:sticky;top:0;background:#2a2f42;padding:12px;border-radius:8px;margin-bottom:16px;text-align:center;z-index:9}
.bar b{color:#7af} .bar button{margin:0 6px;padding:6px 14px;border-radius:6px;border:0;background:#4a5680;color:#fff;cursor:pointer}
#out{display:inline-block;min-width:200px;background:#1a1d29;padding:4px 10px;border-radius:4px;font-family:monospace}
.g{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;max-width:1400px;margin:auto}
.cd{background:#252a3a;border-radius:10px;padding:10px;text-align:center}
.cd.ref{background:#3a2e1a;border:2px solid #d4a017}
.cd img{width:100%;background:repeating-conic-gradient(#444 0 25%,#383838 0 50%) 50%/20px 20px;border-radius:6px}
.nm{font-size:15px;font-weight:bold;margin-top:6px} .mt{font-size:11px;color:#9ab;margin:4px 0;line-height:1.5}
label{font-size:12px;cursor:pointer;display:block;margin-top:4px;color:#ffd}
</style></head><body>
<h2>世界杯队徽批复 — 勾"免标准化(已OK)"的,其余我做标准化</h2>
<div class=bar>已勾免标准化 <b id=cnt>0</b> 个: <span id=out>(未勾选)</span>
<button onclick=cp()>复制清单</button> <button onclick=clr()>清空</button>
<br><small style="color:#9ab">勾选自动保存,刷新不丢。勾完点"复制清单"发我。标杆BRA/ARG=占画面~83×80%/填充50%</small></div>
<div class=g>__CARDS__</div>
<script>__JS__</script>
</body></html>"""
doc = doc.replace('__CARDS__', ''.join(cards)).replace('__JS__', js)
open('_队徽盘点批复.html', 'w', encoding='utf-8').write(doc)
print('批复页(可存数据)生成,', len(best), '个待批')
