# -*- coding: utf-8 -*-
"""繁体列(zh)体检 v2 —— 用 Big5 可编码性做高精度判定。

判据：字符 c 是"真·简化字"当且仅当
    c 无法用 Big5 编码（简化字不在繁体字集里）
  且 s2t(c) 可以用 Big5 编码（它的繁体形是合法繁体字）
这样 台/秘/群/丑/干/征/霉 这类"繁体里本就通用、只是有异体"的字不会误报。
"""
import csv, sys, os, re, glob, json
import opencc

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r"C:/X3/gdconfig-amina-video"
TSV = os.path.join(ROOT, 'tsv/i18n/Text__Text.tsv')
s2t = opencc.OpenCC('s2t')
CN, ZH = 3, 10

def in_big5(ch):
    try:
        ch.encode('big5')
        return True
    except Exception:
        return False

_cache = {}
def is_simplified(ch):
    if ch in _cache:
        return _cache[ch]
    r = False
    if '\u4e00' <= ch <= '\u9fff' and not in_big5(ch):
        t = s2t.convert(ch)
        r = (t != ch and len(t) == 1 and in_big5(t))
    _cache[ch] = r
    return r

def load(p):
    with open(p, encoding='utf-8', errors='replace', newline='') as f:
        return list(csv.reader(f, delimiter='\t'))

# 马戏节 key 判定：只认 TXT_<族>_<ID> 结尾那个 ID
ao = load(os.path.join(ROOT, 'tsv/ActvOnline__ActvOnline.tsv'))
CID = set()
for r in ao[6:]:
    if len(r) > 38 and r[38].strip() in ('143', '144'):
        CID.add(r[0])
        if len(r) > 4 and r[4].strip():
            CID.add(r[4].strip())
for p in glob.glob(os.path.join(ROOT, 'tsv/*.tsv')):
    try:
        rows = load(p)
    except Exception:
        continue
    if len(rows) < 7:
        continue
    for r in rows[6:]:
        if r and r[0].strip() and ('马戏' in ' '.join(r[:4]) or '巡游' in ' '.join(r[:4])):
            CID.add(r[0].strip())

def is_circus(keystr):
    for k in keystr.split('|'):
        m = re.search(r'_(\d{3,})$', k)
        if m and m.group(1) in CID:
            return True
    return False

TAGRE = re.compile(r'<[^>]*>|\{\d+\}|\\n')

rows = load(TSV)
EQ, PART, EMPTY = [], [], []
for r in rows:
    if not r or len(r) <= ZH:
        continue
    k = r[0]
    if not (k.startswith('TXT_') or k.startswith('Text_')):
        continue
    cn, zh = r[CN], r[ZH]
    if not cn.strip() or '"typ":"lc"' in cn:
        continue
    cn_h = TAGRE.sub('', cn)
    need = any(is_simplified(c) for c in cn_h)
    if not zh.strip():
        if need:
            EMPTY.append((k, cn))
        continue
    zh_h = TAGRE.sub('', zh)
    left = sorted({c for c in zh_h if is_simplified(c)})
    if not left:
        continue
    (EQ if zh == cn else PART).append((k, cn, zh, ''.join(left)))

def dump(title, items, n=40):
    cir = [x for x in items if is_circus(x[0])]
    oth = [x for x in items if not is_circus(x[0])]
    print('\n' + '=' * 100)
    print('%s  共 %d 条  （★马戏节 %d / 其它 %d）' % (title, len(items), len(cir), len(oth)))
    print('=' * 100)
    for tag, lst in (('★马戏节', cir), ('  其它(历史遗留)', oth)):
        if not lst:
            continue
        print('--- %s (%d) ---' % (tag, len(lst)))
        for x in lst[:n]:
            key = x[0] if len(x[0]) <= 46 else x[0][:43] + '...'
            print('   %-46s 残留[%s]' % (key, x[3][:16]))
            print('        zh: %s' % x[2][:76])
        if len(lst) > n:
            print('   … 还有 %d 条' % (len(lst) - n))

dump('【A】zh 与 cn 完全相同（整条没转繁）', EQ)
dump('【B】zh 里残留真·简化字', PART)
print('\n【C】cn 需转繁但 zh 为空: %d 条' % len(EMPTY))
for k, cn in EMPTY[:10]:
    print('   %-48s %s' % (k[:46], cn[:34]))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zh_issues2.json')
json.dump({'EQ': EQ, 'PART': PART, 'EMPTY': EMPTY}, open(out, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n明细 -> %s' % out)
