# -*- coding: utf-8 -*-
"""
v2: 按用户反馈修正合并规则
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

festivals = ["万圣节", "感恩节", "圣诞节", "春节", "情人节", "科技节"]

all_packs = {}
for fn in festivals:
    for p in data[fn].get('top_packs', []):
        name = p['name']
        if name not in all_packs:
            all_packs[name] = {"festivals": {}, "module": p['module']}
        if fn not in all_packs[name]["festivals"]:
            all_packs[name]["festivals"][fn] = 0
        all_packs[name]["festivals"][fn] += p['revenue']

# ── v2 合并规则 ──
MERGE_GROUPS = {
    # 1. 大富翁拆为两组
    "大富翁（非异族）": [
        "节日大富翁", "节日大富翁礼包",
        "2025复活节大富翁礼包", "节日大富翁组队礼包",
    ],
    "异族大富翁": [
        "2025异族大富翁", "异族大富翁随机礼包",
    ],

    # 2. 弹珠GACHA全部合并（按节日排期归属，数据本身已按节日拆好）
    "弹珠GACHA": [
        "2025万圣节弹珠随机GACHA礼包", "2025万圣节弹珠GACHA礼包",
        "2026科技节弹珠GACHA",
    ],

    # 3. 皮肤抽奖全部拆出来 → 不合并，各自单独
    #   （机甲GACHA、各期GACHA礼包、一番赏等全部单独列）

    # 4. 推币机保持合并
    "推币机系列": [
        "推币机礼包", "推币机随机GACHA礼包",
    ],

    # 5. 节日BP：拆出组队BP
    "节日BP": [
        "情人节BP", "2025万圣节bp礼包",
    ],
    # 情人节组队BP → 单独

    # 6. 周年庆返场：拆出买三赠一
    "周年庆返场": [
        "S6周年庆特效返场-1限时抢购礼包",
        "周年庆预购连锁_schema6",
    ],
    # 2025周年庆返场买三赠一SCHEMA6 → 单独

    # 7. S300赛车保持合并
    "S300赛车系列": [
        "S300赛车特惠", "S300赛车常驻-高级抽奖券", "S300赛车常驻-升级券",
    ],

    # 8. 黑五全部拆开 → 不合并

    # 9. 预购连锁和终极连锁拆开 → 各自单独

    # 10. 以下保持不变
    "自选周卡": [
        "万圣节自选周卡-schema6", "感恩节自选周卡-schema6",
        "圣诞节自选周卡", "春节自选周卡", "情人节自选周卡",
    ],
    "斗士抽奖系列": [
        "斗士抽奖成就礼包", "斗士抽奖GACHA随机礼包", "斗士抽奖GACHA礼包",
    ],
    "节日高级通行证": [
        "万圣节高级通行证_2025", "感恩节高级通行证_2025",
        "圣诞节高级通行证_2025", "春节高级通行证_2025", "科技节高级通行证_2025",
    ],
    "节日初级通行证": [
        "万圣节初级通行证_2025", "感恩节初级通行证_2025",
        "圣诞节初级通行证_2025", "春节初级通行证_2025", "科技节初级通行证_2025",
    ],
    "行军表情": [
        "2025万圣节-行军表情", "2025圣诞节-行军表情",
        "2025春节-行军表情", "2026情人节-行军表情", "2026科技节-行军表情",
    ],
    "行军特效": [
        "2026春节-行军特效", "2026情人节-行军特效", "2026复活节-行军特效",
    ],
    "幸运多重礼GACHA": [
        "节日-幸运多重礼GACHA礼包",
    ],
}

name_to_group = {}
for group, names in MERGE_GROUPS.items():
    for n in names:
        name_to_group[n] = group

merged = {}
ungrouped = {}

for name, info in all_packs.items():
    group = name_to_group.get(name)
    if group:
        if group not in merged:
            merged[group] = {"festivals": {}, "members": [], "module": info["module"]}
        merged[group]["members"].append(name)
        for fn, rev in info["festivals"].items():
            merged[group]["festivals"][fn] = merged[group]["festivals"].get(fn, 0) + rev
    else:
        ungrouped[name] = info

# 输出
lines = []
lines.append("=" * 70)
lines.append("v2 合并后的子活动（按总收入排序）")
lines.append("=" * 70)

all_items = []
for gname, ginfo in merged.items():
    total = sum(ginfo["festivals"].values())
    all_items.append((gname, ginfo["festivals"], total, ginfo["members"], ginfo["module"], True))

for name, info in ungrouped.items():
    total = sum(info["festivals"].values())
    if total >= 5000:
        all_items.append((name, info["festivals"], total, [], info["module"], False))

all_items.sort(key=lambda x: -x[2])

for i, (name, fest_data, total, members, module, is_merged) in enumerate(all_items, 1):
    tag = "[合并]" if is_merged else ""
    revs = []
    for fn in festivals:
        v = fest_data.get(fn, 0)
        revs.append(f"{fn}:${v:,.0f}" if v > 0 else f"{fn}:—")
    lines.append(f"\n{i:>2}. {tag:6s}{name}  [{module}]  ${total:,.0f}")
    lines.append(f"    {'  '.join(revs)}")
    if members:
        lines.append(f"    = {' + '.join(members)}")

lines.append(f"\n合并后共 {len(all_items)} 行（原 82 行）")
lines.append(f"  合并组 {sum(1 for x in all_items if x[5])} 个, 单独 {sum(1 for x in all_items if not x[5])} 个")

result = '\n'.join(lines)
with open(r'C:\ADHD_agent\_tmp_merge_preview_v2.txt', 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Done: {len(all_items)} items")
