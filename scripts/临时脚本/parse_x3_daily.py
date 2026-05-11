import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/x3_daily_data.txt', 'r') as f:
    raw = f.read()

data = eval(raw)
results = data.get('result', [])
columns = {c['key']: c['name'] for c in data.get('columns', [])}

# 过滤有效 DNU > 100
valid = [r for r in results if r.get('bi_dnu') and r['bi_dnu'] > 100]
valid.sort(key=lambda x: x.get('report_date', ''))

print(f'总行数: {len(results)}  有效行(DNU>100): {len(valid)}')

def fmt(v, pct=False):
    if v is None or v == 'NaN': return '-'
    if pct:
        try: return f'{float(v)*100:.1f}%'
        except: return str(v)
    try: return f'{float(v):.2f}'
    except: return str(v)

print(f'\n{"日期":>12} {"DNU":>7} {"LTV_D1":>7} {"LTV_D7":>7} {"LTV14":>7} {"LTV21":>7} {"LTV28":>7} {"付费D7":>7} {"付费D14":>8} {"付费D21":>8} {"留存D1":>7} {"留存D7":>7} {"留存14":>7} {"留存21":>7}')
for r in valid:
    dt = r.get('report_date', '?')
    dnu = r.get('bi_dnu', 0)
    print(f'{dt!s:>12} {dnu:>7} {fmt(r.get("ci_ltv_d_1d")):>7} {fmt(r.get("ci_ltv_d_7d")):>7} {fmt(r.get("ci_ltv_d_14d")):>7} {fmt(r.get("ci_ltv_d_21d")):>7} {fmt(r.get("ci_ltv_d_28d")):>7} {fmt(r.get("ci_pay_rate_d_7d"),True):>7} {fmt(r.get("ci_pay_rate_d_14d"),True):>8} {fmt(r.get("ci_pay_rate_d_21d"),True):>8} {fmt(r.get("ci_active_recent_d30_1d"),True):>7} {fmt(r.get("ci_active_recent_d30_7d"),True):>7} {fmt(r.get("ci_active_recent_d30_14d"),True):>7} {fmt(r.get("ci_active_recent_d30_21d"),True):>7}')

# 计算 LTV 增长斜率
print('\n【LTV 增长分析（DNU加权平均）】')
ltv_keys = [('ci_ltv_d_1d','D1'),('ci_ltv_d_7d','D7'),('ci_ltv_d_14d','D14'),('ci_ltv_d_21d','D21'),('ci_ltv_d_28d','D28')]
prev_ltv = None
for key, label in ltv_keys:
    total_w = sum(r['bi_dnu'] * float(r[key]) for r in valid if r.get(key) not in (None, 'NaN'))
    total_n = sum(r['bi_dnu'] for r in valid if r.get(key) not in (None, 'NaN'))
    if total_n > 0:
        avg = total_w / total_n
        delta = f' (+${avg-prev_ltv:.2f})' if prev_ltv else ''
        print(f'  {label}: ${avg:.2f}{delta}')
        prev_ltv = avg
