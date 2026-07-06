# -*- coding: utf-8 -*-
"""KB 5维标签补全：kind/domain 优先取同目录已打标签笔记的多数派，兜底用路径映射；
proj/fest/year 只从 路径+文件名 推（遵守 taxonomy：别扫正文）。
用法: python kb_tag.py [--apply]
"""
import os, re, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

KB = r'C:\ADHD_agent\KB'
APPLY = '--apply' in sys.argv

KIND_BY_TOP = {
    '方法论': 'kind/方法论', '通用skill': 'kind/skill', '运营skill': 'kind/skill',
    '工作计划': 'kind/计划',
}
DOMAIN_BY_TOP = {
    '产出-数据分析': 'domain/数据复盘', '产出-节日复盘': 'domain/数据复盘',
    '产出-数值设计': 'domain/配置换皮', '产出-配置换皮': 'domain/配置换皮',
    '产出-配置生成': 'domain/配置换皮', '产出-配置仓库': 'domain/配置换皮',
    '换皮档案': 'domain/配置换皮', '产出-排期部署': 'domain/活动部署',
    '产出-补发邮件': 'domain/通知协作', '产出-交互原型': 'domain/前端',
    '产出-工具与可视化': 'domain/前端', '产出-WhatsNew': 'domain/文档',
    '产出-验证报告': 'domain/运维',
}
FEST_KW = [
    ('世界杯', 'fest/世界杯'), ('深海', 'fest/深海节'), ('拓荒', 'fest/拓荒节'),
    ('夏日', 'fest/夏日节'), ('春节', 'fest/春节'), ('spring', 'fest/春节'),
    ('情人节', 'fest/情人节'), ('科技节', 'fest/科技节'), ('复活节', 'fest/复活节'),
    ('圣诞', 'fest/圣诞节'), ('christmas', 'fest/圣诞节'), ('占星', 'fest/占星节'),
    ('推币机', 'fest/推币机'), ('挖矿', 'fest/挖矿'), ('登月', 'fest/登月节'),
    ('周年庆', 'fest/周年庆'), ('音乐节', 'fest/音乐节'), ('万圣', 'fest/万圣节'),
    ('感恩节', 'fest/感恩节'), ('弹珠', 'fest/弹珠'), ('尼罗', 'fest/尼罗河'),
    ('summer', 'fest/夏日节'),
]
LOC_KW = ('i18n', '翻译', '本地化', '文案', '多语言')
ART_KW = ('出图', '切图', '美术', '皮肤视频', '图标', '表情', '铭牌', '头像框',
          'banner', 'prefab', 'spine', 'dk入库', 'grfal', 'morphix', '素材')
ROOT_OVERRIDES = {  # KB 根目录散笔记，逐篇指定
    'X2 装饰投放.md': ['kind/脑图', 'domain/配置换皮', 'proj/X2', 'year/2026'],
    'X3 世界杯竞猜.md': ['kind/脑图', 'domain/配置换皮', 'proj/X3', 'fest/世界杯', 'year/2026'],
}

def read(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()

def get_tags(txt):
    m = re.match(r'(?s)^---\n(.*?)\n---', txt)
    if not m:
        return None
    tm = re.search(r'^tags:\s*\[(.*?)\]', m.group(1), re.M)
    if tm:
        return [t.strip() for t in tm.group(1).split(',') if t.strip()]
    # yaml 列表式 tags
    tm = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', m.group(1), re.M)
    if tm:
        return re.findall(r'-\s*(\S+)', tm.group(1))
    return None

# 收集全库
files, tagged_by_dir = [], collections.defaultdict(list)
for root, dirs, fns in os.walk(KB):
    dirs[:] = [d for d in dirs if d != '.obsidian' and d != '__pycache__']
    for fn in fns:
        if not fn.endswith('.md'):
            continue
        p = os.path.join(root, fn)
        txt = read(p)
        tags = get_tags(txt)
        files.append((p, txt, tags))
        if tags:
            tagged_by_dir[root].append(tags)

def majority(root, prefix, walk_up=True):
    """同目录（可选逐级向上）找已打标签兄弟的多数派 kind/ 或 domain/。"""
    cur = root
    while len(cur) >= len(KB):
        votes = [t for tags in tagged_by_dir.get(cur, []) for t in tags if t.startswith(prefix)]
        if votes:
            return collections.Counter(votes).most_common(1)[0][0]
        if not walk_up:
            return None
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None

results, flat_tagged = [], []
for p, txt, tags in files:
    rel = os.path.relpath(p, KB)
    if tags is not None:
        if not any('/' in t for t in tags):
            flat_tagged.append(f'{rel}: {tags}')
        continue
    top = rel.split(os.sep)[0]
    if top.startswith('_'):
        continue
    if rel in ROOT_OVERRIDES:
        results.append((p, rel, txt, ROOT_OVERRIDES[rel]))
        continue
    root = os.path.dirname(p)
    hint = rel[len(top):].lower()  # 排除顶层目录名，防「本地化与美术」自匹配
    # kind
    if '交接包' in rel or '教学包' in rel:
        kind = 'kind/交接'
    elif top.startswith('产出') or top == '换皮档案':
        kind = majority(root, 'kind/', walk_up=False) or 'kind/产出'
    else:
        kind = KIND_BY_TOP.get(top) or majority(root, 'kind/') or 'kind/方法论'
    # domain
    if 'token周报' in hint:
        domain = 'domain/个人助理'
    elif top in ('产出-本地化与美术', '方法论') and any(k in hint for k in LOC_KW):
        domain = 'domain/本地化'
    elif top == '产出-本地化与美术':
        domain = 'domain/美术媒体'
    elif top == '方法论' and any(k in hint for k in ART_KW):
        domain = 'domain/美术媒体'
    else:
        domain = DOMAIN_BY_TOP.get(top) or majority(root, 'domain/') or 'domain/文档'
    # proj
    if re.search(r'x3', hint): proj = 'proj/X3'
    elif re.search(r'x2|巨猿', hint): proj = 'proj/X2'
    elif re.search(r'p2', hint): proj = 'proj/P2'
    else: proj = 'proj/通用'
    # fest
    fest = next((v for k, v in FEST_KW if k in hint), None)
    # year
    ym = re.search(r'(202[4-9])', rel)
    year = f'year/{ym.group(1)}' if ym else f'year/{datetime.datetime.fromtimestamp(os.path.getmtime(p)).year}'
    new_tags = [kind, domain, proj] + ([fest] if fest else []) + [year]
    results.append((p, rel, txt, new_tags))

results.sort(key=lambda r: r[1])
for p, rel, txt, new_tags in results:
    print(f'{rel}\n    -> {new_tags}')
print(f'\n共 {len(results)} 篇待补')
if flat_tagged:
    print('\n=== 已有tags但非5维（需人工看） ===')
    print('\n'.join(flat_tagged))

if APPLY:
    n = 0
    for p, rel, txt, new_tags in results:
        tagline = 'tags: [' + ', '.join(new_tags) + ']'
        if txt.startswith('---\n'):
            new = txt.replace('---\n', f'---\n{tagline}\n', 1)
        else:
            new = f'---\n{tagline}\n---\n\n' + txt
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
        n += 1
    print(f'\n[APPLY] 已写入 {n} 篇')
