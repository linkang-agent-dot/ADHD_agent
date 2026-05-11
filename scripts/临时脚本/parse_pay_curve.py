import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/cohort_pay_category.txt', 'r') as f:
    data = eval(f.read())

rows = data['data']

# 按 cohort_day pivot
from collections import defaultdict
day_cat = defaultdict(lambda: defaultdict(float))
day_total = defaultdict(float)
all_cats = set()

for r in rows:
    d = r['cohort_day']
    cat = r['pay_category']
    rev = float(r['revenue'])
    day_cat[d][cat] += rev
    day_total[d] += rev
    all_cats.add(cat)

# 合并类目：把已知的活动类目和价格档位整理清楚
# 按"可识别活动"和"价格档位"两个维度展示
cats_activity = ['BP通行证','转盘礼包','链式礼包','海妖转盘','英雄抽卡','许愿池']
cats_price = ['微额(<1)','小额(1-5)','中额(5-20)','大额(20-50)','超大额(50+)']

print('='*120)
print('D0-D35 每日付费分类（已识别活动 + 价格档位未识别部分）')
print('='*120)

# 表头
header = f'{"Day":>4} {"总收入$":>9}'
for c in cats_activity:
    header += f' {c[:6]:>8}'
header += f' {"其他小":>8} {"其他中":>8} {"其他大":>8} {"其他超大":>8}'
print(header)

for d in range(36):
    line = f'{d:>4} {day_total[d]:>9.0f}'
    for c in cats_activity:
        v = day_cat[d].get(c, 0)
        line += f' {v:>8.0f}'
    # 其他按价格
    for c in ['小额(1-5)','中额(5-20)','大额(20-50)','超大额(50+)']:
        v = day_cat[d].get(c, 0)
        line += f' {v:>8.0f}'
    print(line)

# 分阶段汇总
print(f'\n{"="*120}')
print('分阶段汇总：各付费类目收入')
print(f'{"="*120}')
stages = [(0,7,'D0-D7'),(8,13,'D8-D13'),(14,17,'D14-D17'),(18,20,'D18-D20'),(21,27,'D21-D27'),(28,33,'D28-D33')]
all_display = cats_activity + ['小额(1-5)','中额(5-20)','大额(20-50)','超大额(50+)']

header2 = f'{"阶段":<8} {"总收入":>8}'
for c in all_display:
    header2 += f' {c[:8]:>8}'
print(header2)

for s,e,label in stages:
    stage_total = sum(day_total[d] for d in range(s,e+1))
    line = f'{label:<8} {stage_total:>8.0f}'
    for c in all_display:
        v = sum(day_cat[d].get(c,0) for d in range(s,e+1))
        line += f' {v:>8.0f}'
    print(line)

# JSON for dashboard
print(f'\n{"="*120}')
print('Dashboard 数据 (JSON)')
print(f'{"="*120}')
dashboard = []
for d in range(36):
    entry = {'day': d, 'total': round(day_total[d],0)}
    for c in all_display:
        key = c.replace('(','').replace(')','').replace('<','lt').replace('>','gt').replace('-','_')
        entry[key] = round(day_cat[d].get(c,0), 0)
    dashboard.append(entry)
print(json.dumps(dashboard[:5], ensure_ascii=False, indent=2))
print('...')
