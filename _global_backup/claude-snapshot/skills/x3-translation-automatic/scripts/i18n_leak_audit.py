# -*- coding: utf-8 -*-
"""
X3 i18n 泄漏审计 — 确定性检测 Text 表三类"伪完整/未翻译"缺陷。
(2026-06-24 新增: 起因=世界杯抽奖券/深海节多处 cn之外全照抄英文, 空缺审计+肉眼都漏判)

检测三类(完整性, 漏翻/伪完整):
  1. EMPTY     — 目标语言列为空 (block)
  2. EN_LEAK   — cn之外的语言列 == en英文原文 (block): "只翻了中英、其余照抄英文"的伪完整
  3. CJK_LEAK  — 非中日语言列含汉字 (block): 中文泄漏 (zh繁/jp日语汉字排除假阳性)
另 ZH_RAW(warn) — zh列==cn简体疑似未转繁(启发式)

只对"成句"文本判 EN_LEAK, 自动排除符号/数字/标签/百分比/语言选择器等"各语言本就相同"的假阳性。

★换皮残留语义检查 (--reskin-residue, 2026-06-29 新增):
  上面三类只抓"没翻/翻一半"; 换皮(clone源活动)复用源活动的带文本ID时,
  i18n 译文**完整但主题错**(15013累充全16语言译好却写"尼罗"; 16031开箱乌克兰语整段元旦残留),
  完整性审计和肉眼都漏判。residue 模式 = 给"源节日词表"(多语言), 扫范围内每个 key 的全语言 cell
  是否含源节日名 → 命中 = 换皮漏改正文 (block, 类型 RESIDUE)。**换皮收尾必跑**(配合 --prefix/--grep 限定新ID段)。

用法:
  python i18n_leak_audit.py                      # 审计全表(默认X3 Text tsv)
  python i18n_leak_audit.py --changed            # 只审 git diff HEAD 改动过的行(提交前自查首选)
  python i18n_leak_audit.py --prefix TXT_Pack_   # 按 key 前缀
  python i18n_leak_audit.py --grep 世界杯         # 按 cn/key 关键词
  python i18n_leak_audit.py --tsv <path>         # 指定 tsv
  # 换皮残留(从尼罗换皮到世界杯, 扫 RuleTips):
  python i18n_leak_audit.py --src-festival nile --grep RuleTips
  python i18n_leak_audit.py --source-terms "尼罗,尼羅,Nile,Nilo,니로,ナイル" --prefix TXT_RuleTips_
退出码: 0=无 block 泄漏; 1=发现 block 泄漏 (供 hook/CI 用)
"""
import sys, io, csv, re, argparse, subprocess, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DEFAULT_TSV = r'C:\x3\gdconfig\tsv\i18n\Text__Text.tsv'
# 列序(0-indexed): 0=key 1=状态 2=cnbak 3=cn 4=en 5=sp 6=fr 7=id 8=de 9=kr 10=zh 11=ru 12=ua 13=jp 14=it 15=pl 16=po 17=tr 18=th
LANGS = {4:'en',5:'sp',6:'fr',7:'id',8:'de',9:'kr',10:'zh',11:'ru',12:'ua',13:'jp',14:'it',15:'pl',16:'po',17:'tr',18:'th'}
TRANS_COLS = list(range(4,19))                 # 全部翻译列(含en)
NON_CN_NON_EN = [c for c in range(5,19)]       # cn/en之外
CJK = re.compile(r'[一-鿿]')
# CJK泄漏检测排除: zh(繁中)/jp(日语汉字)本就含汉字
CJK_SKIP_COLS = {10, 13}
# 语言选择器等"原文即译文"的 key 白名单(各语言显示本族语名, 本就相同)
WHITELIST_KEY_SUBSTR = ['union_language_', 'ServerName_', 'Discord', 'Facebook', 'union_class_']

# ★换皮源节日"残留词表"(多语言) — 换皮到新节日后, 旧节日名若出现在任意语言cell = 漏改正文。
# key=节日短名, value=该节日各语言专属名/特征词(出现即判残留)。新增节日往这加一行即可复用。
FESTIVAL_RESIDUE = {
    'nile':      ['尼罗', '尼羅', 'Nile', 'Nilo', 'Nilu', 'Işıltı', '니로', 'ナイル', 'ไนล์'],          # 尼罗之辉
    'newyear':   ['天马', '天馬', '糖牌', '新岁', 'Pegasus', 'Candy', 'Фортуни Астри', 'Астра',
                  'старий рік', 'новий рік', '天馬', '페가수스'],                                       # 元旦/天马福箱
    'spring':    ['新春', '春节', '春節', 'Spring Festival', 'Lunar New Year', '설날', '春節祭'],        # 新春
    'valentine': ['情人节', '情人節', 'Valentine', 'San Valentín', 'Saint-Valentin', '발렌타인'],        # 情人节
    'deepsea':   ['深海', '海兽', 'Abyss', 'Abyssal', 'Deep Sea', '심해', '深海節'],                     # 深海节
    'summer':    ['夏日', '恋语', 'Summer', 'Verano', '여름'],                                          # 夏日恋语
}

def norm(s): return (s or '').strip()

def is_real_sentence(en):
    """成句英文: 含≥6字母 且 (有空格 或 长度>12)。排除 '50%'/'VIP{0}'/'S1'/罗马数字 等短码"""
    if not re.search(r'[A-Za-z]', en): return False
    letters = sum(c.isalpha() for c in en)
    return letters >= 6 and (' ' in en or len(en) > 12)

def is_symbol_only(s):
    """纯符号/数字/标签/占位符(无字母无汉字) — 各语言本就相同, 跳过所有泄漏判定"""
    core = re.sub(r'<[^>]*>|\{[^}]*\}|[\s\d%.,:/\-+x×()\[\]#]', '', s)
    return core == ''

def load_rows(tsv):
    with open(tsv, encoding='utf-8', newline='') as f:
        return list(csv.reader(f, delimiter='\t'))

def changed_row_indices(tsv):
    """对比 HEAD 版本, 返回有任意单元格变化的行号集合(0-based)。
    按**行位置**对比(cell编辑不增删行,位置对齐精确;绕开空key/重复key塌缩问题)。
    行数不一致(发生过插入/删除)→返回 None 表示无法精确scope, 调用方退回全表。"""
    cwd = os.path.dirname(tsv)
    rel = subprocess.run(['git','-C',cwd,'ls-files','--full-name',os.path.basename(tsv)],
                         capture_output=True, text=True)
    relpath = rel.stdout.strip() or 'tsv/i18n/Text__Text.tsv'
    head = subprocess.run(['git','-C',cwd,'show',f'HEAD:{relpath}'], capture_output=True)
    if head.returncode != 0:
        head = subprocess.run(['git','-C',r'C:\x3\gdconfig','show','HEAD:tsv/i18n/Text__Text.tsv'], capture_output=True)
    old_rows = list(csv.reader(io.StringIO(head.stdout.decode('utf-8','replace')), delimiter='\t'))
    cur = load_rows(tsv)
    if len(old_rows) != len(cur):
        return None
    return {i for i in range(len(cur)) if old_rows[i] != cur[i]}

def audit(rows, scope=None):
    """scope: None=全表 | set(int)=仅这些行号(0-based) | ('prefix',s) | ('grep',s)"""
    findings = {'EN_LEAK':[], 'CJK_LEAK':[], 'EMPTY':[], 'ZH_RAW':[]}
    for idx, row in enumerate(rows):
        # scope 行号过滤(最先, 含空key行也能命中)
        if isinstance(scope, set) and idx not in scope:
            continue
        if len(row) < 19: row = row + ['']*(19-len(row))
        k = row[0] or ''
        if not k or ('TXT_' not in k and not k.startswith('Text_')): continue
        cn = norm(row[3])
        if not cn or '"typ":"lc"' in (row[3] or ''): continue   # LC占位符跳过
        if any(w in k for w in WHITELIST_KEY_SUBSTR): continue
        if isinstance(scope, tuple):
            mode, val = scope
            if mode=='prefix' and not k.startswith(val): continue
            if mode=='grep' and (val not in k and val not in cn): continue
        en = norm(row[4])
        # EMPTY
        empties = [LANGS[c] for c in TRANS_COLS if not norm(row[c])]
        if empties:
            findings['EMPTY'].append((idx+1, k, cn[:30], empties))
        # CJK_LEAK
        cjk = [LANGS[c] for c in NON_CN_NON_EN if c not in CJK_SKIP_COLS and norm(row[c]) and CJK.search(row[c])]
        if cjk:
            findings['CJK_LEAK'].append((idx+1, k, cn[:30], cjk))
        # EN_LEAK (仅成句en, 排符号行)
        if en and is_real_sentence(en) and not is_symbol_only(en):
            eqs = [LANGS[c] for c in NON_CN_NON_EN if norm(row[c])==en]
            if len(eqs) >= 6:
                findings['EN_LEAK'].append((idx+1, k, cn[:30], f'{len(eqs)}列==en', en[:40]))
        # ZH_RAW (启发式: zh==cn简体 且 cn含简体专用字)
        zh = norm(row[10])
        if zh and zh==cn and not is_symbol_only(cn):
            if re.search(r'[节动获显远荣头礼齐计领锁积语关闭买卖随时间设]', cn):
                findings['ZH_RAW'].append((idx+1, k, cn[:30]))
    return findings

def residue_scan(rows, scope, terms):
    """换皮残留: 范围内每个 key 的全语言cell(col3-18)含任一源节日词 = block。
    terms: list[str] 源节日各语言专属名。大小写不敏感(对拉丁词)。返回 [(line,key,cn,term,langs)]"""
    out = []
    low_terms = [(t, t.lower()) for t in terms]
    for idx, row in enumerate(rows):
        if isinstance(scope, set) and idx not in scope: continue
        if len(row) < 19: row = row + ['']*(19-len(row))
        k = row[0] or ''
        if not k or ('TXT_' not in k and not k.startswith('Text_')): continue
        cn = norm(row[3])
        if not cn: continue
        if isinstance(scope, tuple):
            mode, val = scope
            if mode=='prefix' and not k.startswith(val): continue
            if mode=='grep' and (val not in k and val not in cn): continue
        for term, lt in low_terms:
            hit_cols = [LANGS.get(c, 'cn') for c in range(3,19)
                        if norm(row[c]) and (term in row[c] or lt in row[c].lower())]
            if hit_cols:
                out.append((idx+1, k, cn[:30], term, hit_cols))
                break   # 一个key命中一个源词即够, 不重复刷
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tsv', default=DEFAULT_TSV)
    ap.add_argument('--changed', action='store_true', help='只审 git diff HEAD 改动过的行')
    ap.add_argument('--prefix', help='按 key 前缀过滤')
    ap.add_argument('--grep', help='按 cn/key 关键词过滤')
    ap.add_argument('--src-festival', choices=sorted(FESTIVAL_RESIDUE), help='换皮源节日(内置词表): '+','.join(sorted(FESTIVAL_RESIDUE)))
    ap.add_argument('--source-terms', help='换皮源节日残留词(逗号分隔,多语言), 与--src-festival二选一/可叠加')
    ap.add_argument('--reskin-residue', action='store_true', help='仅跑换皮残留检查(不跑完整性三类)')
    a = ap.parse_args()
    rows = load_rows(a.tsv)
    scope = None
    if a.changed:
        scope = changed_row_indices(a.tsv)
        if scope is None:
            print('[scope] ⚠️ 行数与HEAD不一致(发生过增删行),无法精确定位改动→退回全表审计')
        else:
            print(f'[scope] git diff HEAD 改动行: {len(scope)} 行')
    elif a.prefix: scope = ('prefix', a.prefix)
    elif a.grep:   scope = ('grep', a.grep)

    # ★换皮残留检查
    terms = []
    if a.src_festival: terms += FESTIVAL_RESIDUE[a.src_festival]
    if a.source_terms: terms += [t.strip() for t in a.source_terms.split(',') if t.strip()]
    residue = []
    if terms:
        residue = residue_scan(rows, scope, terms)
        print(f'\n=== RESIDUE 换皮残留(block) [源词:{",".join(terms[:6])}{"..." if len(terms)>6 else ""}]: {len(residue)} ===')
        for it in residue[:50]:
            print(f'  行{it[0]} {it[1][:46]} | cn={it[2]} | 命中"{it[3]}" @ {it[4]}')
        if len(residue)>50: print(f'  ... 还有 {len(residue)-50} 条')
        if a.reskin_residue:
            print(f'\n{"="*40}')
            if residue: print(f'❌ 发现 {len(residue)} 条换皮残留 (源节日名漏改)'); sys.exit(1)
            print('✅ 无换皮残留'); sys.exit(0)
    elif a.reskin_residue:
        print('⚠️ --reskin-residue 需配合 --src-festival 或 --source-terms 指定源节日词'); sys.exit(2)

    f = audit(rows, scope)
    block = len(f['EN_LEAK']) + len(f['CJK_LEAK']) + len(f['EMPTY']) + len(residue)
    def dump(name, items, fmt):
        print(f'\n=== {name}: {len(items)} ===')
        for it in items[:50]: print('  '+fmt(it))
        if len(items)>50: print(f'  ... 还有 {len(items)-50} 条')
    dump('EN_LEAK 英文泄漏(block)', f['EN_LEAK'], lambda x:f'行{x[0]} {x[1][:46]} | cn={x[2]} | {x[3]} | en={x[4]}')
    dump('CJK_LEAK 中文泄漏(block)', f['CJK_LEAK'], lambda x:f'行{x[0]} {x[1][:46]} | cn={x[2]} | 列={x[3]}')
    dump('EMPTY 语言空缺(block)', f['EMPTY'], lambda x:f'行{x[0]} {x[1][:46]} | cn={x[2]} | 缺={x[3]}')
    dump('ZH_RAW zh疑未转繁(warn)', f['ZH_RAW'], lambda x:f'行{x[0]} {x[1][:46]} | cn={x[2]}')
    print(f'\n{"="*40}')
    if block==0:
        print('✅ 无 block 泄漏')
        sys.exit(0)
    else:
        print(f'❌ 发现 {block} 条 block (EN_LEAK={len(f["EN_LEAK"])} CJK_LEAK={len(f["CJK_LEAK"])} EMPTY={len(f["EMPTY"])} RESIDUE={len(residue)})')
        sys.exit(1)

if __name__=='__main__':
    main()
