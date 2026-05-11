import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/x3_growth_data.txt', 'r') as f:
    raw = f.read()

data = eval(raw)
results = data.get('result', [])
columns = {c['key']: c['name'] for c in data.get('columns', [])}

# 打印列名映射
print('【列名映射】')
for k, v in sorted(columns.items()):
    if 'dnu' not in k and 'report' not in k:
        print(f'  {k} → {v}')

valid = [r for r in results if r.get('bi_dnu') and r['bi_dnu'] > 500]
valid.sort(key=lambda x: str(x.get('report_date', '')))

# 检查哪些列有非零数据
print(f'\n总行数: {len(results)}  有效行: {len(valid)}')
print('\n【各列非零值统计】')
for k in sorted(columns.keys()):
    if 'dnu' in k or 'report' in k: continue
    nonzero = sum(1 for r in valid if r.get(k) not in (None, 'NaN', 0, 0.0, '0', '0.0'))
    total = sum(1 for r in valid if r.get(k) is not None and r.get(k) != 'NaN')
    if total > 0:
        print(f'  {columns.get(k, k)[:35]:<35} 非零={nonzero}/{total}')

# 打印有数据的列
print('\n【养成线数据（取前20行有效数据）】')
# 识别有数据的 growth 列
growth_cols = []
for k in sorted(columns.keys()):
    if 'dnu' in k or 'report' in k or 'pay' in k or 'ltv' in k or 'arppu' in k: continue
    nonzero = sum(1 for r in valid if r.get(k) not in (None, 'NaN', 0, 0.0))
    if nonzero > 0:
        growth_cols.append(k)

if growth_cols:
    header = f'{"日期":>12} {"DNU":>6}'
    for k in growth_cols:
        nm = columns.get(k, k)[:20]
        header += f' {nm:>20}'
    print(header)
    for r in valid[:30]:
        line = f'{str(r.get("report_date","?")):>12} {r.get("bi_dnu",0):>6}'
        for k in growth_cols:
            v = r.get(k)
            if v is None or v == 'NaN': line += f' {"-":>20}'
            else: line += f' {float(v):>20.2f}'
        print(line)
else:
    print('  所有养成线列均为 0 或空！')
    # 打印一行原始数据看看
    if valid:
        r = valid[0]
        print(f'\n  样本行 (日期={r.get("report_date")}):')
        for k, v in r.items():
            if 'dnu' not in k and 'report' not in k:
                print(f'    {columns.get(k,k)}: {v!r}')
