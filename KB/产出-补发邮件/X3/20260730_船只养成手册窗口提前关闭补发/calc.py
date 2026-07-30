import json, io, datetime as dt
from collections import defaultdict
SP = r"C:/Users/linkang/AppData/Local/Temp/claude/C--Users-linkang/21014237-35d5-40c3-82f7-62213693d0e8/scratchpad"
L = lambda f: json.load(io.open(SP+'/'+f, encoding='utf-8'))['data']
P = lambda s: dt.datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
NOW = dt.datetime(2026, 7, 30, 9, 0, 0)

reg = {r['user_id']: P(r['reg_time']) for r in L('regs.json')}
orders, claims = L('orders.json'), L('claims.json')
srv = {o['user_id']: o['server_id'] for o in orders}

def cyc(uid, t):
    r0 = reg[uid].replace(hour=0, minute=0, second=0, microsecond=0)
    k = (t - r0).days // 30
    return k, r0 + dt.timedelta(days=30*k), r0 + dt.timedelta(days=30*(k+1))

# claims per (user, cycle)
cl = defaultdict(lambda: {'metal':0,'wood':0,'n':0})
for c in claims:
    uid = c['user_id']
    if uid not in reg: continue
    k,_,_ = cyc(uid, P(c['created_at']))
    d = cl[(uid,k)]
    d['metal' if c['asset_id']=='Item_55101' else 'wood'] += c['change_count']
    d['n'] += 1

rows = []
for o in orders:
    uid, t = o['user_id'], P(o['created_at'])
    k, s, e = cyc(uid, t)
    mult = 2 if o['iap_id'] == '220006' else 1
    got = cl.get((uid,k), {'metal':0,'wood':0})
    rows.append(dict(user_id=uid, server_id=o['server_id'], iap=o['iap_id'], buy=o['created_at'][:19],
        reg=reg[uid].strftime('%Y-%m-%d'), cycle=k, c_start=s.strftime('%Y-%m-%d'), c_end=e.strftime('%Y-%m-%d'),
        closed=e <= NOW, exp_metal=180*mult, exp_wood=270*mult,
        got_metal=got['metal'], got_wood=got['wood']))

closed = [r for r in rows if r['closed']]
print(f"订单总数 {len(rows)}  |  周期已关闭的订单 {len(closed)}  |  仍在进行中 {len(rows)-len(closed)}")
print(f"已关闭订单涉及玩家 {len(set(r['user_id'] for r in closed))}")
short = []
for r in closed:
    dm, dw = max(0,r['exp_metal']-r['got_metal']), max(0,r['exp_wood']-r['got_wood'])
    if dm or dw:
        r2 = dict(r); r2['d_metal'], r2['d_wood'] = dm, dw; short.append(r2)
print(f"→ 其中没领满的 {len(short)} 单 / {len(set(r['user_id'] for r in short))} 人")
print(f"→ 合计缺 神秘金属 {sum(r['d_metal'] for r in short)} / 高级木板 {sum(r['d_wood'] for r in short)}")
json.dump(short, io.open(SP+'/short.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("\n样例:")
for r in sorted(short, key=lambda x:-(x['d_metal']+x['d_wood']))[:10]:
    print(f"  {r['user_id']}@{r['server_id']} reg={r['reg']} 买={r['buy'][:10]}({r['iap']}) 周期{r['c_start']}~{r['c_end']} 领={r['got_metal']}+{r['got_wood']} 缺={r['d_metal']}+{r['d_wood']}")
