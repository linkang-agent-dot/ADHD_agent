import json, io, csv
from collections import defaultdict
SP = r"C:/Users/linkang/AppData/Local/Temp/claude/C--Users-linkang/21014237-35d5-40c3-82f7-62213693d0e8/scratchpad"
short = json.load(io.open(SP+'/short.json', encoding='utf-8'))

per = defaultdict(lambda: {'srv':None,'m':0,'w':0,'orders':[]})
for r in short:
    d = per[r['user_id']]
    d['srv'] = r['server_id']; d['m'] += r['d_metal']; d['w'] += r['d_wood']
    d['orders'].append(f"{r['iap']}@{r['buy'][:10]}")

print("投诉玩家 2061721 是否在名单:", '2061721' in per, per.get('2061721'))
print("人数", len(per), "金属合计", sum(v['m'] for v in per.values()), "木板合计", sum(v['w'] for v in per.values()))

rows = sorted(per.items(), key=lambda kv: -(kv[1]['m']+kv[1]['w']))
out = SP+'/船只手册窗口提前关闭_补发导入.csv'
with io.open(out, 'w', encoding='gbk', newline='') as f:
    w = csv.writer(f)
    for uid, d in rows:
        items = []
        if d['m']: items.append(f"55101*{d['m']}")
        if d['w']: items.append(f"55100*{d['w']}")
        w.writerow([d['srv'], uid, '[' + ', '.join(items) + ']', '', '', ''])
print("CSV ->", out)
# 服务器分布 & 分档
from collections import Counter
print("涉及服", len(set(d['srv'] for d in per.values())))
tiers = Counter()
for uid,d in rows:
    t = d['m']+d['w']
    tiers['缺≥600(几乎全没领)' if t>=600 else '缺300~599' if t>=300 else '缺<300'] += 1
print(dict(tiers))
print("\n全名单前15:")
for uid,d in rows[:15]:
    print(f"  {d['srv']:>5} {uid:>8}  金属{d['m']:>4} 木板{d['w']:>4}  ({','.join(d['orders'])})")
