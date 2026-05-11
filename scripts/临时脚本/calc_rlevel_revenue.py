import sys
sys.stdout.reconfigure(encoding='utf-8')

# 用户提供的每日 R 级付费金额占比
r_share = [
    {'d':0,'s':70.72,'m':22.02,'l':5.42,'x':1.84},
    {'d':1,'s':57.07,'m':32.03,'l':7.42,'x':3.48},
    {'d':2,'s':49.92,'m':36.94,'l':8.74,'x':4.40},
    {'d':3,'s':43.61,'m':43.84,'l':8.85,'x':3.70},
    {'d':4,'s':44.67,'m':41.61,'l':8.79,'x':4.92},
    {'d':5,'s':40.25,'m':41.76,'l':10.97,'x':7.02},
    {'d':6,'s':38.26,'m':41.99,'l':12.79,'x':6.95},
    {'d':7,'s':35.23,'m':40.94,'l':16.38,'x':7.45},
    {'d':8,'s':34.18,'m':45.22,'l':15.20,'x':5.41},
    {'d':9,'s':32.90,'m':45.07,'l':13.02,'x':9.01},
    {'d':10,'s':31.25,'m':45.63,'l':17.49,'x':5.63},
    {'d':11,'s':30.25,'m':47.01,'l':15.62,'x':7.12},
    {'d':12,'s':31.53,'m':42.40,'l':20.20,'x':5.87},
    {'d':13,'s':27.14,'m':47.80,'l':16.84,'x':8.21},
    {'d':14,'s':27.49,'m':51.74,'l':13.90,'x':6.87},
    {'d':15,'s':26.02,'m':46.04,'l':20.05,'x':7.89},
    {'d':16,'s':23.68,'m':47.53,'l':17.98,'x':10.80},
    {'d':17,'s':23.17,'m':46.42,'l':18.92,'x':11.49},
    {'d':18,'s':26.86,'m':48.07,'l':18.00,'x':7.07},
    {'d':19,'s':23.71,'m':46.34,'l':17.55,'x':12.40},
    {'d':20,'s':25.18,'m':44.68,'l':20.46,'x':9.68},
    {'d':21,'s':22.66,'m':43.04,'l':25.79,'x':8.52},
    {'d':22,'s':25.85,'m':46.27,'l':20.24,'x':7.64},
    {'d':23,'s':20.96,'m':44.43,'l':19.12,'x':15.48},
    {'d':24,'s':23.69,'m':47.14,'l':19.94,'x':9.23},
    {'d':25,'s':26.42,'m':44.79,'l':16.39,'x':12.40},
    {'d':26,'s':27.86,'m':48.59,'l':14.34,'x':9.21},
    {'d':27,'s':25.61,'m':46.55,'l':19.80,'x':8.04},
    {'d':28,'s':22.87,'m':44.19,'l':23.57,'x':9.37},
    {'d':29,'s':29.95,'m':42.66,'l':18.46,'x':8.93},
    {'d':30,'s':23.78,'m':46.61,'l':19.94,'x':9.67},
]

# 整体加权 LTV（从 datain 查询结果，插值补全 D0-D20）
# 已知点: D1=$0.207, D2=$0.267, D3=$0.320, D5=$0.418, D7=$0.501, D10=$0.599, D14=$0.711, D17=$0.786, D20=$0.861
# D21~D28 from earlier query: D21≈$0.90, D28≈$1.05 (extrapolated)
known_ltv = {0:0, 1:0.207, 2:0.267, 3:0.320, 5:0.418, 7:0.501, 10:0.599, 14:0.711, 17:0.786, 20:0.861, 21:0.90, 28:1.05, 30:1.10}

# 线性插值补全 D0-D30
def interp(d):
    keys = sorted(known_ltv.keys())
    if d in known_ltv: return known_ltv[d]
    for i in range(len(keys)-1):
        if keys[i] <= d <= keys[i+1]:
            t = (d - keys[i]) / (keys[i+1] - keys[i])
            return known_ltv[keys[i]] * (1-t) + known_ltv[keys[i+1]] * t
    return known_ltv[keys[-1]]

ltv_curve = [interp(d) for d in range(31)]
# 每日 LTV 增量 = LTV[d] - LTV[d-1]
daily_ltv_delta = [ltv_curve[0]] + [ltv_curve[d] - ltv_curve[d-1] for d in range(1, 31)]

print('='*90)
print('各 R 级每日绝对 LTV 贡献（整体日增量 × R 级当日占比）')
print('='*90)
print(f'{"Day":>4} {"日LTV增":>8} {"小R贡献":>8} {"中R贡献":>8} {"大R贡献":>8} {"超R贡献":>8} {"中R+大R+超R":>12}')

# 累计各 R 级贡献
cum = {'s':0,'m':0,'l':0,'x':0}
for i, rs in enumerate(r_share):
    d = rs['d']
    delta = daily_ltv_delta[d]
    s_rev = delta * rs['s'] / 100
    m_rev = delta * rs['m'] / 100
    l_rev = delta * rs['l'] / 100
    x_rev = delta * rs['x'] / 100
    cum['s'] += s_rev; cum['m'] += m_rev; cum['l'] += l_rev; cum['x'] += x_rev
    mlx = m_rev + l_rev + x_rev
    print(f'{d:>4} {delta:>8.4f} {s_rev:>8.4f} {m_rev:>8.4f} {l_rev:>8.4f} {x_rev:>8.4f} {mlx:>12.4f}')

print(f'\n{"="*90}')
print('各 R 级累计 LTV 贡献 (D0→D30)')
print(f'{"="*90}')
total = cum['s'] + cum['m'] + cum['l'] + cum['x']
for label, key in [('小R','s'),('中R','m'),('大R','l'),('超R','x')]:
    pct = cum[key] / total * 100
    print(f'  {label}: ${cum[key]:.4f}  ({pct:.1f}%)')
print(f'  总计: ${total:.4f}')

# 按阶段汇总
print(f'\n{"="*90}')
print('分阶段各 R 级绝对贡献')
print(f'{"="*90}')
stages = [(0,6,'D0-D6'),(7,13,'D7-D13'),(14,20,'D14-D20'),(21,30,'D21-D30')]
for s_start, s_end, label in stages:
    stage_cum = {'s':0,'m':0,'l':0,'x':0}
    stage_total = 0
    for rs in r_share:
        d = rs['d']
        if s_start <= d <= s_end:
            delta = daily_ltv_delta[d]
            stage_cum['s'] += delta * rs['s'] / 100
            stage_cum['m'] += delta * rs['m'] / 100
            stage_cum['l'] += delta * rs['l'] / 100
            stage_cum['x'] += delta * rs['x'] / 100
            stage_total += delta
    print(f'\n  {label} (日LTV增量合计: ${stage_total:.4f}):')
    for rl, key in [('小R','s'),('中R','m'),('大R','l'),('超R','x')]:
        pct = stage_cum[key] / stage_total * 100 if stage_total > 0 else 0
        print(f'    {rl}: ${stage_cum[key]:.4f}  ({pct:.1f}%)')
