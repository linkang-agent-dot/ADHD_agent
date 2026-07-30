# -*- coding: utf-8 -*-
r"""补齐琥珀皮肤的 i18n：①修 4 语人名没换成 ②补道具描述 14 语。

【为什么会漏这 4 语】swap_skin_hero_to_amber.py 用「阿米娜各语官译 -> 琥珀各语官译」做字符串替换，
但**阿米娜皮肤名里的人名本身就跟她的官译对不上**（sp/fr/de 官译=Amira、kr=아르미나，
皮肤名里却写的 Amina/아미나——当初译者用了英文名）。找不到匹配串 → 静默跳过，不报错。
教训：这类「按官译替换」的脚本必须**替换后逐语言复验目标词是否出现**，别只看脚本没报错。

术语来源：琥珀官译取自 Dialogue_RoleName 行；「魅影魔术师」各语取自已译好的 TXT_HeroSkin_Name_100901。
句式基线：TXT_Item_Desc_5304001（足球宝贝，同为「使用后可获得X的专属皮肤——Y！」句式）。
"""
import io, os, sys

REPO = r'C:\x3\wt_circus_float'
F = r'tsv\i18n\Text__Text.tsv'
COL = {'cn':3,'en':4,'sp':5,'fr':6,'id':7,'de':8,'kr':9,'zh':10,
       'ru':11,'ua':12,'jp':13,'it':14,'pl':15,'po':16,'tr':17,'th':18}

# ① 4 语人名没换成 —— 直接按目标值写死（旧值断言防误伤）
NAME_FIX = {
    'sp': ('Maga Fantasma · Amina',      'Maga Fantasma · Ámbar'),
    'fr': ('Magicienne Fantôme · Amina', 'Magicienne Fantôme · Ambre'),
    'de': ('Phantom-Magierin · Amina',   'Phantom-Magierin · Bernstein'),
    'kr': ('팬텀 매지션 · 아미나',          '팬텀 매지션 · 엠버'),
}
NAME_KEYS = ('TXT_HeroSkin_Name_100901', 'TXT_Item_Name_5300901')

# ② 道具描述 16 语（en 也顺手对齐基线的 unlock 措辞）
DESC = {
    'cn': '使用后可获得琥珀的专属皮肤——魅影魔术师！',
    'en': 'Use to unlock Amber\'s exclusive skin—Phantom Magician!',
    'sp': '¡Úsalo para desbloquear la apariencia exclusiva de Ámbar: Maga Fantasma!',
    'fr': 'À utiliser pour débloquer l\'apparence exclusive d\'Ambre : Magicienne Fantôme !',
    'id': 'Gunakan untuk membuka skin eksklusif Amber—Pesulap Bayangan!',
    'de': 'Verwende es, um Bernsteins exklusiven Skin freizuschalten – Phantom-Magierin!',
    'kr': '사용하면 엠버의 전용 스킨—팬텀 매지션을 획득할 수 있습니다!',
    'zh': '使用後可獲得琥珀的專屬皮膚——魅影魔術師！',
    'ru': 'Используйте, чтобы открыть эксклюзивный облик Эмбер — Призрачная Волшебница!',
    'ua': 'Використайте, щоб відкрити ексклюзивний образ Ембер — Примарна Чарівниця!',
    'jp': '使用するとアンバーの専用スキン「ファントムマジシャン」を獲得できます！',
    'it': 'Usalo per sbloccare la skin esclusiva di Amber: Maga Fantasma!',
    'pl': 'Użyj, aby odblokować ekskluzywny wygląd Amber — Magiczka Widmo!',
    'po': 'Use para desbloquear a skin exclusiva de Amber—Maga Fantasma!',
    'tr': 'Amber\'ın özel kostümü Hayalet Sihirbaz\'ı açmak için kullan!',
    'th': 'ใช้แล้วจะได้รับสกินพิเศษของแอมเบอร์—นักมายากลเงา!',
}
DESC_KEY = 'TXT_Item_Desc_5300901'


def main(dry):
    p = os.path.join(REPO, F)
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        t = f.read()
    nl = '\r\n' if '\r\n' in t[:4000] else '\n'
    lines = t.replace('\r\n', '\n').split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]

    hit_name = hit_desc = 0
    for i, l in enumerate(lines[6:], 6):
        fs = l.split('\t')
        keys = fs[0].split('|')

        if any(k in NAME_KEYS for k in keys):
            hit_name += 1
            for lang, (old, new) in NAME_FIX.items():
                c = COL[lang]
                if c >= len(fs):
                    raise SystemExit(f'!! 列{c}越界')
                if fs[c].strip() != old:
                    raise SystemExit(f'!! {fs[0][:40]} {lang} 断言失败: 期望[{old}] 实际[{fs[c]}]')
                fs[c] = new
                print(f'   [{lang}] {old} -> {new}')
            lines[i] = '\t'.join(fs)

        if DESC_KEY in keys:
            hit_desc += 1
            for lang, txt in DESC.items():
                c = COL[lang]
                while len(fs) <= c:
                    fs.append('')
                fs[c] = txt
            fs[1] = 'AI'
            lines[i] = '\t'.join(fs)
            print(f'   描述补齐 16 语, cn={fs[3][:24]}')

    if hit_name < 1:
        raise SystemExit('!! 没命中皮肤名/道具名行')
    if hit_desc != 1:
        raise SystemExit(f'!! 描述行命中 {hit_desc} 次(期望1)')

    if not dry:
        with io.open(p, 'w', encoding='utf-8', newline=nl) as f:
            f.write('\n'.join(lines) + '\n')
    print('\n' + ('[dry-run] 未写盘' if dry else f'✅ 已写盘 (名字行 {hit_name} 行, 描述 1 行)'))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main('--dry-run' in sys.argv)
