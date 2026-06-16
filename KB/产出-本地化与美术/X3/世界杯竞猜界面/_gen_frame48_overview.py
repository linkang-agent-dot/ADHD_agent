# -*- coding: utf-8 -*-
import glob, os, re, html

d = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL'
CFG = r'C:\x3\gdconfig\tsv\Personalize__PersonalizeAvatarFrameCfg.tsv'

# 从配置表读 三字码 -> (ID, 中文名)  单一真源
cfg = {}
for l in open(CFG, encoding='utf-8').read().split('\n'):
    c = l.split('\t')
    if c[0].isdigit() and int(c[0]) >= 10028:
        code = c[4].replace('DK_Img_Player_AvatarFrame_WC_', '')
        cfg[code] = (c[0], c[9])

# 每队主图(规范名优先)
files = [os.path.basename(f) for f in glob.glob(os.path.join(d, 'Img_Player_AvatarFrame_WC_*.png'))]
by_code = {}
for f in files:
    mm = re.search(r'WC_([A-Z]{3})', f)
    if mm:
        by_code.setdefault(mm.group(1), []).append(f)

def pick(cands):
    for f in cands:
        if re.fullmatch(r'Img_Player_AvatarFrame_WC_[A-Z]{3}\.png', f):
            return f
    for f in sorted(cands):
        if not re.search(r'(_alt|_transparent|_nobg|_raw|_v\d)', f):
            return f
    return sorted(cands)[0]

main = {c: pick(v) for c, v in by_code.items()}
# 按配置ID排序
ordered = sorted(main.items(), key=lambda kv: int(cfg.get(kv[0], ('99999',''))[0]))

cards = []
for c, f in ordered:
    cid, nm = cfg.get(c, ('—', c))
    cards.append(
        f'<div class="card"><img src="{html.escape(f)}" alt="{c}">'
        f'<div class="lbl">{nm} <span class="code">{c}</span></div>'
        f'<div class="id">ID {cid}</div></div>'
    )

doc = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>世界杯48队头像框总览</title>
<style>
body{{background:#1a1d29;color:#eee;font-family:"Microsoft YaHei",sans-serif;margin:0;padding:24px}}
h1{{text-align:center;font-weight:600}}
.sub{{text-align:center;color:#9aa;margin-bottom:24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;max-width:1600px;margin:0 auto}}
.card{{background:#252a3a;border-radius:12px;padding:12px;text-align:center;transition:.2s}}
.card:hover{{background:#2e3550;transform:translateY(-3px)}}
.card img{{width:100%;max-width:160px;aspect-ratio:1;object-fit:contain;
  background:repeating-conic-gradient(#333 0 25%,#3a3a3a 0 50%) 50%/20px 20px}}
.lbl{{margin-top:8px;font-size:15px}}
.lbl .code{{color:#7af;font-size:12px;margin-left:4px}}
.id{{color:#f3a;font-size:13px;margin-top:2px;font-family:monospace}}
</style></head><body>
<h1>2026 世界杯 48 队头像框</h1>
<div class="sub">模板：环=队色渐变纹理 · 国旗球 · 骨架金饰统一 | 配置表 PersonalizeAvatarFrameCfg ID 10028–10075 | 共 {len(ordered)} 队</div>
<div class="grid">{''.join(cards)}</div>
</body></html>'''

out = os.path.join(d, '_总览48.html')
open(out, 'w', encoding='utf-8').write(doc)
print('总览更新:', out, '| 队数', len(ordered), '| 含配置ID')
miss = [c for c in main if c not in cfg]
print('未匹配配置的队:', miss)
