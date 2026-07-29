# -*- coding: utf-8 -*-
"""马戏节付费包 vs 累充白名单 全量比对。"""
import csv, sys, os, glob, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r"C:/X3/gdconfig-amina-video"
os.chdir(ROOT)

def load(p):
    with open(p, encoding='utf-8', errors='replace', newline='') as f:
        return list(csv.reader(f, delimiter='\t'))

ao = load('tsv/ActvOnline__ActvOnline.tsv')
# 白名单
wl = set()
for r in ao[6:]:
    if r and r[0] == '100599':
        wl = {x for x in r[49].split('|') if x.strip()}

# 马戏节活动（组 143/144）
circus_actv, circus_cid = set(), set()
for r in ao[6:]:
    if len(r) > 38 and r[38].strip() in ('143', '144'):
        circus_actv.add(r[0])
        if len(r) > 4 and r[4].strip():
            circus_cid.add(r[4].strip())

# Pack 主表：ID -> (名, 价格, 累充额度)
pk = {}
for r in load('tsv/Pack__Pack.tsv')[6:]:
    if r and r[0].strip():
        pk[r[0]] = (r[1] if len(r) > 1 else '',
                    r[7] if len(r) > 7 else '',
                    r[41] if len(r) > 41 else '')

# ---- 收集马戏节引用到的 Pack ID ----
used = {}   # packid -> 来源说明

def note(pid, src):
    pid = pid.strip()
    if pid and pid in pk:
        used.setdefault(pid, set()).add(src)

# 1) ChainPack（阶梯礼包）里马戏节相关的
for r in load('tsv/Pack__ChainPack.tsv')[6:]:
    if not r or not r[0].strip():
        continue
    blob = ' '.join(r)
    if '马戏' in blob or '巡游' in blob or '寻宝' in blob:
        for pid in (r[4] if len(r) > 4 else '').split('|'):
            note(pid, f'ChainPack{r[0]}')

# 2) 存钱罐三档（ActvVoyage 马戏 2803）
v = load('tsv/ActvVoyage__ActvVoyage.tsv')
vh = {h: i for i, h in enumerate(v[5]) if h.strip()}
for r in v[6:]:
    if r and r[0] == '2803':
        for f in ('PiggyBankPackID', 'PiggyBankPackID2', 'PiggyBankPackID3'):
            i = vh.get(f)
            if i is not None and i < len(r):
                note(r[i], '存钱罐(2803)')

# 3) 扫全部 tsv 里备注/名字带马戏且形如 PackID 的列（宽扫，后面按价格过滤）
for p in glob.glob('tsv/*.tsv'):
    base = os.path.basename(p)
    if base.startswith('Text') or base == 'Pack__Pack.tsv':
        continue
    try:
        rows = load(p)
    except Exception:
        continue
    if len(rows) < 7:
        continue
    hdr = rows[5]
    pcols = [i for i, h in enumerate(hdr) if 'Pack' in h and 'ID' in h]
    if not pcols:
        continue
    for r in rows[6:]:
        if not r or not r[0].strip():
            continue
        blob = ' '.join(r[:8])
        if not ('马戏' in blob or '巡游' in blob):
            continue
        for i in pcols:
            if i < len(r):
                for pid in re.split(r'[|,;]', r[i]):
                    note(pid, base.replace('.tsv', ''))

# 4) Pack 表里名字带马戏的
for pid, (name, price, ra) in pk.items():
    if '马戏' in name or '巡游' in name or '限时抢购' in name:
        note(pid, 'Pack名')

# ---- 输出：只看真付费包（Price 非空）----
paid = {p: v for p, v in used.items() if pk[p][1].strip()}
missing = {p: v for p, v in paid.items() if p not in wl}
inwl = {p: v for p, v in paid.items() if p in wl}

print('累充白名单(AO100599) 现有 %d 个包' % len(wl))
print('扫到马戏节相关**付费**包 %d 个：在白名单 %d / 缺失 %d' % (len(paid), len(inwl), len(missing)))
print()
if missing:
    print('❌ 缺失清单（需补进白名单）')
    print('%-9s %-26s %-9s %-9s %s' % ('PackID', '名称', '价格', '累充额度', '来源'))
    print('-' * 92)
    for p in sorted(missing, key=lambda x: (pk[x][1], x)):
        name, price, ra = pk[p]
        print('%-9s %-26s %-9s %-9s %s' % (p, name[:24], price, ra, ','.join(sorted(missing[p]))))
else:
    print('✅ 无缺失')

print()
print('（参考）已在白名单的付费包 %d 个：%s' % (len(inwl), ' '.join(sorted(inwl))))
extra = wl - set(paid)
print()
print('（参考）白名单里但本次没扫到的 %d 个（多为其它活动/历史包，不动）：%s' % (len(extra), ' '.join(sorted(extra))))
