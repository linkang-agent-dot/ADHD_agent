# -*- coding: utf-8 -*-
r"""
马戏节开箱大奖皮肤 承接英雄 阿米娜(1020,紫) -> 艾琳娜(1047,橙) 全套改配置。

背景：用户要求大奖皮肤挂在橙色本体上（D35 内可得的橙色本体只有 10 个，艾琳娜是其一）。
主题沿用「魅影魔术师」不变；属性也不用动 —— 两人兵种同为 1(猎人)，PropType 220011 猎人防御通用。

ID 规律：节日皮肤 = 英雄ID×100+序号（足球宝贝 1040→104001 / 兔耳魅影 1034→103401），
        皮肤道具 = 530 + (皮肤ID-100000)。故 1047 → 皮肤 104701 / 道具 5304701（均已核空闲）。

⚠️只 append/替换目标行，不重写全表（保 CRLF/引号零扰动）。
用法: python swap_skin_hero_to_elena.py [--dry-run]
"""
import argparse, io, os, re, sys

REPO = r'C:\x3\wt_circus_float'
OLD_SKIN, NEW_SKIN = '102001', '104701'
OLD_ITEM, NEW_ITEM = '5302001', '5304701'

F_SKIN = r'tsv\Hero__HeroSkin.tsv'
F_ITEM = r'tsv\Item__Item.tsv'
F_CRAFT = r'tsv\ActvCrafting__ActvCraftingReward.tsv'
F_TEXT = r'tsv\i18n\Text__Text.tsv'

# HeroSkin 列改动：列号 -> (旧值断言, 新值)
SKIN_SET = {
    0:  (OLD_SKIN, NEW_SKIN),
    2:  ('魅影魔术师·阿米娜', '魅影魔术师·艾琳娜'),
    3:  ('1020', '1047'),
    5:  ('DK_Img_C_H_20_Skin01', 'DK_Img_C_H_47_Skin01'),
    6:  ('DK_Role_F_20_Skin01', 'DK_Role_F_47_Skin01'),
    8:  ('DK_Role_Pirate', 'DK_Role_M_47'),          # 皮肤沿用本体模型(阿米娜本体也是 Pirate)
    9:  ('DK_Role_C_20_Skin01', 'DK_Role_C_47_Skin01'),
    11: (OLD_ITEM, NEW_ITEM),
    20: ('DK_video_amina_skin01_sbs', 'DK_video_elena_skin01_sbs'),
}
# Item 列改动
ITEM_SET = {
    0:  (OLD_ITEM, NEW_ITEM),
    1:  ('猛兽驯服者·阿米娜', '魅影魔术师·艾琳娜'),      # ⚠️旧残留:07-27改名只改了i18n没改本表
    3:  ('使用后可获得阿米娜的专属皮肤——猛兽驯服者！', '使用后可获得艾琳娜的专属皮肤——魅影魔术师！'),
    8:  (f'{OLD_SKIN}|-1', f'{NEW_SKIN}|-1'),
    20: ('DK_Img_C_H_20_Skin01', 'DK_Img_C_H_47_Skin01'),
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


def edit_row(lines, key, sets, label):
    idx = [i for i, l in enumerate(lines[6:], 6) if l.split('\t')[0] == key]
    if len(idx) != 1:
        raise SystemExit(f'!! {label} {key} 命中 {len(idx)} 行(期望1)')
    fs = lines[idx[0]].split('\t')
    for col, (old, new) in sets.items():
        if col >= len(fs):
            raise SystemExit(f'!! {label} 列{col} 越界')
        if fs[col] != old:
            raise SystemExit(f'!! {label} 列{col} 断言失败: 期望[{old}] 实际[{fs[col]}]')
        fs[col] = new
        print(f'   [{col}] {old} -> {new}')
    lines[idx[0]] = '\t'.join(fs)


def main(dry):
    print('=== 1/4 Hero__HeroSkin ===')
    p, nl, L = load(F_SKIN); edit_row(L, OLD_SKIN, SKIN_SET, 'HeroSkin'); save(p, nl, L, dry)

    print('\n=== 2/4 Item__Item ===')
    p, nl, L = load(F_ITEM); edit_row(L, OLD_ITEM, ITEM_SET, 'Item'); save(p, nl, L, dry)

    print('\n=== 3/4 ActvCraftingReward(开箱奖池大奖) ===')
    p, nl, L = load(F_CRAFT)
    hit = 0
    for i, l in enumerate(L[6:], 6):
        fs = l.split('\t')
        if fs[0] == '11609':
            for c, v in enumerate(fs):
                if v == OLD_ITEM:
                    fs[c] = NEW_ITEM; hit += 1
                    print(f'   行11609 列[{c}] {OLD_ITEM} -> {NEW_ITEM}')
            L[i] = '\t'.join(fs)
    if hit != 1:
        raise SystemExit(f'!! 奖池行改了 {hit} 处(期望1)')
    save(p, nl, L, dry)

    print('\n=== 4/4 i18n ===')
    p, nl, L = load(F_TEXT)
    # 取艾琳娜/阿米娜 16 语官译，用于逐语言换人名
    def find(pred):
        for l in L[6:]:
            fs = l.split('\t')
            if pred(fs[0]):
                return fs
        return None
    role = find(lambda k: 'Dialogue_RoleName' in k and False)  # 占位
    # 从皮肤名行拿阿米娜 16 语；从对白角色名行拿艾琳娜 16 语
    amina_row = find(lambda k: k == 'TXT_HeroSkin_Name_' + OLD_SKIN)
    elena_row = None
    for l in L[6:]:
        fs = l.split('\t')
        if 'Dialogue_RoleName' in fs[0] and len(fs) > 4 and fs[3].strip() == '艾琳娜':
            elena_row = fs; break
    amina_name = None
    for l in L[6:]:
        fs = l.split('\t')
        if 'Dialogue_RoleName' in fs[0] and len(fs) > 4 and fs[3].strip() == '阿米娜':
            amina_name = fs; break
    if not (amina_row and elena_row and amina_name):
        raise SystemExit('!! 取官译失败: 皮肤名行/艾琳娜名行/阿米娜名行 至少缺一')

    renames = {
        f'TXT_HeroSkin_Name_{OLD_SKIN}':     f'TXT_HeroSkin_Name_{NEW_SKIN}',
        f'TXT_HeroSkin_CollectTxt_{OLD_SKIN}': f'TXT_HeroSkin_CollectTxt_{NEW_SKIN}',
        f'TXT_Item_Name_{OLD_ITEM}':         f'TXT_Item_Name_{NEW_ITEM}',
        f'TXT_Item_Desc_{OLD_ITEM}':         f'TXT_Item_Desc_{NEW_ITEM}',
    }
    for i, l in enumerate(L[6:], 6):
        fs = l.split('\t')
        if fs[0] not in renames:
            continue
        old_key = fs[0]
        fs[0] = renames[old_key]
        # 皮肤名 / 道具名：逐语言把人名从 阿米娜->艾琳娜
        if 'Name' in old_key:
            for c in LANGS:
                if c < len(fs) and fs[c].strip() and c < len(amina_name) and c < len(elena_row):
                    a, e = amina_name[c].strip(), elena_row[c].strip()
                    if a and e and a in fs[c]:
                        fs[c] = fs[c].replace(a, e)
        # 道具描述：整句重写(cn/en 手写，其余清空交 i18n 流程补)
        if 'Item_Desc' in old_key:
            for c in LANGS:
                if c < len(fs):
                    fs[c] = ''
            fs[3] = '使用后可获得艾琳娜的专属皮肤——魅影魔术师！'
            fs[4] = "Use to obtain Elena's exclusive skin — Phantom Magician!"
            fs[1] = 'AI'
        L[i] = '\t'.join(fs)
        print(f'   {old_key} -> {fs[0]}   cn={fs[3][:22]}')
    save(p, nl, L, dry)
    print('\n' + ('[dry-run] 未写盘' if dry else '✅ 已写盘'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(); sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main(a.dry_run)
