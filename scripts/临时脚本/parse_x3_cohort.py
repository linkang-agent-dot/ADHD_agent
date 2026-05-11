import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/x3_cohort_data.txt', 'r') as f:
    raw = f.read()

data = eval(raw)
results = data.get('result', [])
columns = {c['key']: c['name'] for c in data.get('columns', [])}

# 过滤有效数据（DNU > 0 且有 LTV 数据）
valid = [r for r in results if r.get('bi_dnu') and r['bi_dnu'] > 0 and r.get('ci_ltv_d_1d') is not None]
valid.sort(key=lambda x: x.get('bd_cohort_register', 0))

print(f'总行数: {len(results)}  有效行(DNU>0且有LTV): {len(valid)}')
print(f'\n列映射:')
for k, v in sorted(columns.items()):
    if any(kw in k for kw in ['ltv', 'pay_rate', 'dnu', 'active_recent']):
        print(f'  {k} → {v}')

print(f'\n{"="*120}')
print(f'X3 注册 Cohort 数据（按注册周，有效行）')
print(f'{"="*120}')
print(f'{"Cohort":>7} {"DNU":>8} {"LTV_D1":>8} {"LTV_D7":>8} {"LTV_D14":>9} {"LTV_D21":>9} {"LTV_D28":>9} {"LTV_D35":>9} {"付费率D7":>8} {"付费率D14":>9} {"付费率D21":>9} {"付费率D28":>9} {"留存D1":>7} {"留存D7":>7} {"留存D14":>8} {"留存D21":>8} {"留存D28":>8}')

for r in valid[-30:]:  # 最近30个cohort
    cohort = r.get('bd_cohort_register', '?')
    dnu = r.get('bi_dnu', 0)

    def fmt_val(key, pct=False):
        v = r.get(key)
        if v is None or v == 'NaN': return '-'
        if pct:
            try: return f'{float(v)*100:.1f}%'
            except: return str(v)
        try: return f'{float(v):.2f}'
        except: return str(v)

    ltv1 = fmt_val('ci_ltv_d_1d')
    ltv7 = fmt_val('ci_ltv_d_7d')
    ltv14 = fmt_val('ci_ltv_d_14d')
    ltv21 = fmt_val('ci_ltv_d_21d')
    ltv28 = fmt_val('ci_ltv_d_28d')
    ltv35 = fmt_val('ci_ltv_d_35d')
    pr7 = fmt_val('ci_pay_rate_d_7d', True)
    pr14 = fmt_val('ci_pay_rate_d_14d', True)
    pr21 = fmt_val('ci_pay_rate_d_21d', True)
    pr28 = fmt_val('ci_pay_rate_d_28d', True)
    ret1 = fmt_val('ci_active_recent_d30_1d', True)
    ret7 = fmt_val('ci_active_recent_d30_7d', True)
    ret14 = fmt_val('ci_active_recent_d30_14d', True)
    ret21 = fmt_val('ci_active_recent_d30_21d', True)
    ret28 = fmt_val('ci_active_recent_d30_28d', True)

    print(f'{cohort:>7} {dnu:>8} {ltv1:>8} {ltv7:>8} {ltv14:>9} {ltv21:>9} {ltv28:>9} {ltv35:>9} {pr7:>8} {pr14:>9} {pr21:>9} {pr28:>9} {ret1:>7} {ret7:>7} {ret14:>8} {ret21:>8} {ret28:>8}')

# 汇总平均
print(f'\n{"="*120}')
print('整体加权平均（按DNU加权）:')
total_dnu = sum(r['bi_dnu'] for r in valid)
for key, label in [('ci_ltv_d_1d','LTV_D1'),('ci_ltv_d_7d','LTV_D7'),('ci_ltv_d_14d','LTV_D14'),
                   ('ci_ltv_d_21d','LTV_D21'),('ci_ltv_d_28d','LTV_D28'),('ci_ltv_d_35d','LTV_D35')]:
    weighted = sum(r['bi_dnu'] * float(r[key]) for r in valid if r.get(key) not in (None, 'NaN'))
    dnu_sum = sum(r['bi_dnu'] for r in valid if r.get(key) not in (None, 'NaN'))
    if dnu_sum > 0:
        print(f'  {label}: ${weighted/dnu_sum:.2f}')
