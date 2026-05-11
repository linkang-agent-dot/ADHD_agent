import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/x3_detail_data.txt', 'r') as f:
    raw = f.read()

data = eval(raw)
results = data.get('result', [])
columns = {c['key']: c['name'] for c in data.get('columns', [])}

valid = [r for r in results if r.get('bi_dnu') and r['bi_dnu'] > 500]
valid.sort(key=lambda x: str(x.get('report_date', '')))

def fmt(v, pct=False, dec=2):
    if v is None or v == 'NaN': return '-'
    if pct:
        try: return f'{float(v)*100:.1f}%'
        except: return str(v)
    try: return f'{float(v):.{dec}f}'
    except: return str(v)

# 找列名映射
ltv_keys = []
arppu_keys = []
pr_keys = []
growth_keys = []
for k, v in columns.items():
    if 'LTV' in v or 'ltv' in k: ltv_keys.append((k, v))
    if 'ARPPU' in v or 'arppu' in k.lower(): arppu_keys.append((k, v))
    if '付费率' in v or 'pay_rate' in k: pr_keys.append((k, v))

# === LTV 曲线 ===
print('='*100)
print('X3 Cohort LTV 曲线 (D1-D20)')
print('='*100)
print(f'{"日期":>12} {"DNU":>7} {"D1":>6} {"D2":>6} {"D3":>6} {"D5":>6} {"D7":>6} {"D10":>6} {"D14":>6} {"D17":>6} {"D20":>6}')
ltv_sums = {d: [0,0] for d in ['1d','2d','3d','5d','7d','10d','14d','17d','20d']}
for r in valid:
    dt = str(r.get('report_date', '?'))
    dnu = r.get('bi_dnu', 0)
    vals = []
    for d in ['1d','2d','3d','5d','7d','10d','14d','17d','20d']:
        k = f'ci_ltv_d_{d}'
        v = r.get(k)
        vals.append(fmt(v))
        if v not in (None, 'NaN'):
            try:
                ltv_sums[d][0] += dnu * float(v)
                ltv_sums[d][1] += dnu
            except: pass
    print(f'{dt:>12} {dnu:>7} ' + ' '.join(f'{v:>6}' for v in vals))

print('\n加权平均 LTV:')
prev = 0
for d, label in [('1d','D1'),('2d','D2'),('3d','D3'),('5d','D5'),('7d','D7'),('10d','D10'),('14d','D14'),('17d','D17'),('20d','D20')]:
    s, n = ltv_sums[d]
    if n > 0:
        avg = s / n
        delta = f' (+${avg-prev:.3f})' if prev else ''
        print(f'  {label}: ${avg:.3f}{delta}')
        prev = avg

# === ARPPU 曲线 ===
print(f'\n{"="*100}')
print('X3 Cohort ARPPU 曲线')
print('='*100)
print(f'{"日期":>12} {"DNU":>7} {"D1":>8} {"D3":>8} {"D7":>8} {"D14":>8} {"D20":>8}')
for r in valid[-20:]:
    dt = str(r.get('report_date', '?'))
    dnu = r.get('bi_dnu', 0)
    vals = []
    for d in ['1d','3d','7d','14d','20d']:
        k = f'ci_arppu_d_{d}'
        v = r.get(k)
        vals.append(fmt(v))
    print(f'{dt:>12} {dnu:>7} ' + ' '.join(f'{v:>8}' for v in vals))

# === 付费率 曲线 ===
print(f'\n{"="*100}')
print('X3 Cohort 付费率 曲线')
print('='*100)
print(f'{"日期":>12} {"DNU":>7} {"D1":>7} {"D3":>7} {"D7":>7} {"D14":>7} {"D20":>7}')
for r in valid[-20:]:
    dt = str(r.get('report_date', '?'))
    dnu = r.get('bi_dnu', 0)
    vals = []
    for d in ['1d','3d','7d','14d','21d']:
        k = f'ci_pay_rate_d_{d}'
        v = r.get(k)
        vals.append(fmt(v, pct=True))
    print(f'{dt:>12} {dnu:>7} ' + ' '.join(f'{v:>7}' for v in vals))

# === 养成进度 ===
print(f'\n{"="*100}')
print('X3 Cohort 养成线进度 (建筑/英雄等级)')
print('='*100)
# 找 key
build_hero_keys = [(k, v) for k, v in columns.items() if '建筑' in v or '英雄' in v or 'SLG' in v.upper()]
print(f'可用养成列: {build_hero_keys}')
print(f'\n{"日期":>12} {"DNU":>7}', end='')
gh_keys = []
for k, v in sorted(columns.items()):
    if any(x in v for x in ['SLG', '英雄等级']):
        gh_keys.append((k, v[:15]))
        print(f' {v[:15]:>15}', end='')
print()
for r in valid[-20:]:
    dt = str(r.get('report_date', '?'))
    dnu = r.get('bi_dnu', 0)
    print(f'{dt:>12} {dnu:>7}', end='')
    for k, v in gh_keys:
        val = r.get(k)
        print(f' {fmt(val):>15}', end='')
    print()
