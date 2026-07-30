# -*- coding: utf-8 -*-
r"""
马戏节开箱大奖皮肤 承接英雄 阿米娜(1020,紫) -> 琥珀(1009,橙) 全套改配置。

背景：用户要求大奖皮肤挂在橙色本体上。D35 内可得的橙色本体 10 个，
      候选比稿(艾琳娜 1047 vs 琥珀 1009)后 2026-07-29 定琥珀——
      她本体即深紫波浪发+满身金饰+小麦肤色，与「紫金魅影魔术师」同调，换装后辨识度不被服装吃掉。

主题沿用「魅影魔术师」不变。属性也不用动 —— 三人兵种同为 Type=1(猎人)，
PropType 220011 猎人防御通用；Power 150000 不变。

ID 规律：节日皮肤 = 英雄ID×100+序号（阿米娜 1020→102001 / 兔耳魅影 1034→103401），
        皮肤道具 = 530 + (皮肤ID-100000)。故 1009 → 皮肤 100901 / 道具 5300901（均已核空闲）。

⚠️DK 命名不带前导零：琥珀是 _9_ 不是 _09_（本体 DK_Img_C_H_9 / DK_Role_F_9 / DK_Role_C_9 佐证）。
⚠️DK_Model 要跟着换：阿米娜 DK_Role_Pirate → 琥珀 DK_Role_Elf（精灵，取自其本体皮肤行 1009）。

★引用链已全表扫过（2026-07-29），真引用共 5 张表：
    HeroSkin / Item / ActvCraftingReward(开箱大奖) / Reward(6个奖励组) / i18n Text
  其余 11 张表命中 102001 均为同名数字巧合（KVK活动/怪物/任务/事件各自ID段），不改。
  ★★ Reward 那 6 行是裸扫才发现的，只改前四张表会导致「奖励组仍发旧道具」——
     旧道具指向旧皮肤，玩家拿到的是阿米娜皮。别省这一步。

⚠️只 append/替换目标行，不重写全表（保 CRLF/引号零扰动）。
用法: python swap_skin_hero_to_amber.py [--dry-run]
"""
import argparse, io, os, sys

REPO = r'C:\x3\wt_circus_float'
OLD_SKIN, NEW_SKIN = '102001', '100901'
OLD_ITEM, NEW_ITEM = '5302001', '5300901'
OLD_CN,  NEW_CN    = '阿米娜', '琥珀'

F_SKIN  = r'tsv\Hero__HeroSkin.tsv'
F_ITEM  = r'tsv\Item__Item.tsv'
F_CRAFT = r'tsv\ActvCrafting__ActvCraftingReward.tsv'
F_REWARD= r'tsv\Reward__Reward.tsv'
F_TEXT  = r'tsv\i18n\Text__Text.tsv'

# HeroSkin 列改动：列号 -> (旧值断言, 新值)
SKIN_SET = {
    0:  (OLD_SKIN, NEW_SKIN),
    2:  ('魅影魔术师·阿米娜', '魅影魔术师·琥珀'),
    3:  ('1020', '1009'),
    5:  ('DK_Img_C_H_20_Skin01',  'DK_Img_C_H_9_Skin01'),
    6:  ('DK_Role_F_20_Skin01',   'DK_Role_F_9_Skin01'),
    8:  ('DK_Role_Pirate',        'DK_Role_Elf'),          # 皮肤沿用本体模型
    9:  ('DK_Role_C_20_Skin01',   'DK_Role_C_9_Skin01'),
    11: (OLD_ITEM, NEW_ITEM),
    20: ('DK_video_amina_skin01_sbs', 'DK_video_amber_skin01_sbs'),
}
# Item 列改动
ITEM_SET = {
    0:  (OLD_ITEM, NEW_ITEM),
    1:  ('魅影魔术师·阿米娜', '魅影魔术师·琥珀'),
    3:  ('使用后可获得阿米娜的专属皮肤——魅影魔术师！', '使用后可获得琥珀的专属皮肤——魅影魔术师！'),
    8:  (f'{OLD_SKIN}|-1', f'{NEW_SKIN}|-1'),
    20: ('DK_Img_C_H_20_Skin01', 'DK_Img_C_H_9_Skin01'),
}
# Reward 表 6 个奖励组：列3=道具ID 列4=名字备注
REWARD_IDS = ['15920407', '15920412', '15920417', '15920422', '15920427', '15920431']
REWARD_SET = {
    3: (OLD_ITEM, NEW_ITEM),
    4: ('魅影魔术师·阿米娜（英雄皮肤·永久）', '魅影魔术师·琥珀（英雄皮肤·永久）'),
}
# 开箱奖池大奖行：列2=道具ID 列3=备注
CRAFT_ID = '11609'
CRAFT_SET = {
    2: (OLD_ITEM, NEW_ITEM),
    3: ('猛兽驯服者·阿米娜(核心大奖)', '魅影魔术师·琥珀(核心大奖)'),   # 旧残留:改过名没同步本列
}

LANGS = list(range(3, 19))   # cn,en,sp,fr,id,de,kr,zh,ru,ua,jp,it,pl,po,tr,th


def load(rel):
    p = os.path.join(REPO, rel)
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        t = f.read()
    nl = '\r\n' if '\r\n' in t[:4000] else '\n'
    t = t.replace('\r\n', '\n')
    if not t.endswith('\n'):
        t += '\n'
    return p, nl, t.split('\n')[:-1]


def save(p, nl, lines, dry):
    if dry:
        return
    with io.open(p, 'w', encoding='utf-8', newline=nl) as f:
        f.write('\n'.join(lines) + '\n')


def edit_rows(lines, keys, sets, label):
    """按行首ID精确命中若干行，逐列断言旧值后替换。命中数必须等于 len(keys)。"""
    hit = 0
    for i, l in enumerate(lines[6:], 6):
        fs = l.split('\t')
        if fs[0] not in keys:
            continue
        hit += 1
        for col, (old, new) in sets.items():
            if col >= len(fs):
                raise SystemExit(f'!! {label} 行{fs[0]} 列{col} 越界(实际{len(fs)}列)')
            if fs[col] != old:
                raise SystemExit(f'!! {label} 行{fs[0]} 列{col} 断言失败:\n   期望[{old}]\n   实际[{fs[col]}]')
            fs[col] = new
        lines[i] = '\t'.join(fs)
        print(f'   ✓ 行{fs[0]}: ' + ', '.join(f'[{c}]→{n}' for c, (o, n) in sets.items()))
    if hit != len(keys):
        raise SystemExit(f'!! {label} 命中 {hit} 行(期望 {len(keys)})')


def main(dry):
    print('=== 1/5 Hero__HeroSkin (皮肤本体) ===')
    p, nl, L = load(F_SKIN);   edit_rows(L, {OLD_SKIN}, SKIN_SET, 'HeroSkin');  save(p, nl, L, dry)

    print('\n=== 2/5 Item__Item (皮肤道具) ===')
    p, nl, L = load(F_ITEM);   edit_rows(L, {OLD_ITEM}, ITEM_SET, 'Item');      save(p, nl, L, dry)

    print('\n=== 3/5 ActvCraftingReward (开箱奖池大奖) ===')
    p, nl, L = load(F_CRAFT);  edit_rows(L, {CRAFT_ID}, CRAFT_SET, 'Craft');    save(p, nl, L, dry)

    print('\n=== 4/5 Reward__Reward (6个发放该道具的奖励组) ===')
    p, nl, L = load(F_REWARD); edit_rows(L, set(REWARD_IDS), REWARD_SET, 'Reward'); save(p, nl, L, dry)

    print('\n=== 5/5 i18n Text ===')
    p, nl, L = load(F_TEXT)

    # 取阿米娜/琥珀的 16 语官译（从 Dialogue_RoleName 合并行里捞），用于逐语言换人名
    def role_row(cn_name):
        for l in L[6:]:
            fs = l.split('\t')
            if 'Dialogue_RoleName' in fs[0] and len(fs) > 4 and fs[3].strip() == cn_name:
                return fs
        return None
    old_row, new_row = role_row(OLD_CN), role_row(NEW_CN)
    if not (old_row and new_row):
        raise SystemExit(f'!! 取官译失败: 阿米娜行={bool(old_row)} 琥珀行={bool(new_row)}')
    print(f'   官译基线: {old_row[4].strip()} -> {new_row[4].strip()}')

    renames = {
        f'TXT_HeroSkin_Name_{OLD_SKIN}':       f'TXT_HeroSkin_Name_{NEW_SKIN}',
        f'TXT_HeroSkin_CollectTxt_{OLD_SKIN}': f'TXT_HeroSkin_CollectTxt_{NEW_SKIN}',
        f'TXT_Item_Name_{OLD_ITEM}':           f'TXT_Item_Name_{NEW_ITEM}',
        f'TXT_Item_Desc_{OLD_ITEM}':           f'TXT_Item_Desc_{NEW_ITEM}',
    }
    done = set()
    for i, l in enumerate(L[6:], 6):
        fs = l.split('\t')
        if fs[0] not in renames:
            continue
        old_key = fs[0]
        fs[0] = renames[old_key]
        done.add(old_key)
        if 'Name' in old_key:
            # 皮肤名/道具名：逐语言把人名替换成琥珀的该语言官译
            for c in LANGS:
                if c < len(fs) and fs[c].strip() and c < len(old_row) and c < len(new_row):
                    a, b = old_row[c].strip(), new_row[c].strip()
                    if a and b and a in fs[c]:
                        fs[c] = fs[c].replace(a, b)
        if 'Item_Desc' in old_key:
            # 描述整句重写：cn/en 手写，其余清空交 i18n 流程补翻
            for c in LANGS:
                if c < len(fs):
                    fs[c] = ''
            fs[3] = '使用后可获得琥珀的专属皮肤——魅影魔术师！'
            fs[4] = "Use to obtain Amber's exclusive skin — Phantom Magician!"
            fs[1] = 'AI'
        L[i] = '\t'.join(fs)
        print(f'   ✓ {old_key} -> {fs[0]}   cn={fs[3][:24]}')
    missing = set(renames) - done
    if missing:
        raise SystemExit(f'!! i18n 有 key 没命中: {missing}')
    save(p, nl, L, dry)

    print('\n' + ('[dry-run] 未写盘' if dry else '✅ 已写盘'))
    if not dry:
        print('\n后续：① git diff 复核 ② 提交推送 ③ jolt_verify.py dev_festival')
        print('     ④ 美术出图后注册 DK: DK_Img_C_H_9_Skin01 / DK_Role_F_9_Skin01 /')
        print('        DK_Role_C_9_Skin01 (Display_Role.asset) + DK_video_amber_skin01_sbs (Display_Video.asset)')
        print('     ⑤ i18n 补 14 语（道具描述已清空待翻）')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(); sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main(a.dry_run)
