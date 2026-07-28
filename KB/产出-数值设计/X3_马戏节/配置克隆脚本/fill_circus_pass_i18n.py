# -*- coding: utf-8 -*-
"""
马戏节 通行证族 i18n 补全（福箱通行证新建 4 key + 巡游两包补限定词 + 两条原有 Desc 缺口）

场景判定 = x3-translation-automatic「场景 A：翻译层」——CN 源文全部正确，只是译文缺/丢词，
**不跑 CompositeI18n 扫描**（跑了会把我直接写进 tsv 的行标成"新增"再被重翻），直接改语言列。

翻译方法 = skill 规定的「术语调研→抄术语→组合」，不是机翻：
  马戏福箱 16 语 ← TXT_ActvOnline_ActvName_101026（已定稿）
  通行证   16 语 ← TXT_ActvOnline_ActvName_102251（已定稿）
  高级/至尊档位词 ← TXT_Pack_Name_130047 / 130048（已定稿）
  Desc 句式    ← 各自 en 官译 + 同族 Desc 结构

写法 = 只对目标行做字段替换后 join，其余行原始字节零扰动（git diff 应为等量增删、无结构变化）。

用法: python fill_circus_pass_i18n.py [--dry-run]
"""
import argparse, io, os, sys

REPO = r'C:\x3\wt_circus_float'
TSV  = r'tsv\i18n\Text__Text.tsv'
HEADER_ROWS = 6

# 列号 ← 表头 row0 实测：[3]cn [4]en [5]sp [6]fr [7]id [8]de [9]kr [10]zh繁 [11]ru [12]ua [13]jp [14]it [15]pl [16]po葡 [17]tr [18]th
LANG = ['sp', 'fr', 'id', 'de', 'kr', 'zh', 'ru', 'ua', 'jp', 'it', 'pl', 'po', 'tr', 'th']
COL  = {'cn': 3, 'en': 4, 'sp': 5, 'fr': 6, 'id': 7, 'de': 8, 'kr': 9, 'zh': 10,
        'ru': 11, 'ua': 12, 'jp': 13, 'it': 14, 'pl': 15, 'po': 16, 'tr': 17, 'th': 18}
STATUS_COL = 1

# ---- 译文（14 语，en/cn 已存在不动；zh 为简繁转换非翻译）----
T = {}

# ① 福箱通行证 活动名（对齐 102251 巡游通行证=Parade Pass 的构词，同样不带"马戏"前缀）
T['TXT_ActvOnline_ActvName_102250'] = dict(zip(LANG, [
    'Pase de la Caja de la Suerte',
    'Pass de la Boîte Chance',
    'Tiket Kotak Keberuntungan',
    'Glücksbox-Pass',
    '행운 상자 패스',
    '福箱通行證',
    'Пропуск счастливого сундука',
    'Перепустка щасливого сундука',
    'ラッキーボックスパス',
    'Pass della Scatola Fortunata',
    'Przepustka Skrzyni Szczęścia',
    'Passe da Caixa da Sorte',
    'Şans Kutusu Bileti',
    'บัตรผ่านกล่องนำโชค',
]))

# ② 福箱通行证 描述
T['TXT_ActvOnline_ActvDesc_102250'] = dict(zip(LANG, [
    '¡Abre Cajas de la Suerte del Circo y desbloquea lujosas recompensas del pase!',
    'Ouvrez des Boîtes Chance du Cirque et débloquez de somptueuses récompenses du pass !',
    'Buka Kotak Keberuntungan Sirkus dan buka hadiah mewah dari tiket!',
    'Öffne Zirkus-Glücksboxen und schalte luxuriöse Pass-Belohnungen frei!',
    '서커스 행운 상자를 열고 패스의 호화로운 보상을 획득하세요!',
    '開啟馬戲福箱，解鎖通行證豪華獎勵！',
    'Открывайте цирковые счастливые сундуки и получайте роскошные награды пропуска!',
    'Відкривайте циркові щасливі сундуки та отримуйте розкішні нагороди перепустки!',
    'サーカスラッキーボックスを開けて、パスの豪華報酬を解放しよう！',
    'Apri le Scatole Fortunate del Circo e sblocca lussuose ricompense del pass!',
    'Otwieraj Cyrkowe Skrzynie Szczęścia i odblokuj luksusowe nagrody z przepustki!',
    'Abra Caixas da Sorte do Circo e desbloqueie recompensas luxuosas do passe!',
    'Sirk Şans Kutuları aç ve bilet ödüllerinin kilidini aç!',
    'เปิดกล่องนำโชคละครสัตว์เพื่อปลดล็อกรางวัลสุดหรูจากบัตรผ่าน!',
]))

# ③ 福箱 高级通行证包
T['TXT_Pack_Name_130051'] = dict(zip(LANG, [
    'Pase Avanzado de la Caja de la Suerte',
    'Pass Avancé de la Boîte Chance',
    'Tiket Lanjutan Kotak Keberuntungan',
    'Glücksbox-Premium-Pass',
    '행운 상자 고급 패스',
    '馬戲福箱高級通行證',
    'Продвинутый пропуск счастливого сундука',
    'Просунута перепустка щасливого сундука',
    'ラッキーボックス上級パス',
    'Pass Avanzato della Scatola Fortunata',
    'Zaawansowana Przepustka Skrzyni Szczęścia',
    'Passe Avançado da Caixa da Sorte',
    'Şans Kutusu Gelişmiş Bileti',
    'บัตรผ่านขั้นสูงกล่องนำโชค',
]))

# ④ 福箱 至尊通行证包
T['TXT_Pack_Name_130052'] = dict(zip(LANG, [
    'Pase Supremo de la Caja de la Suerte',
    'Pass Suprême de la Boîte Chance',
    'Tiket Tertinggi Kotak Keberuntungan',
    'Glücksbox-Supreme-Pass',
    '행운 상자 최상급 패스',
    '馬戲福箱至尊通行證',
    'Высший пропуск счастливого сундука',
    'Найвища перепустка щасливого сундука',
    'ラッキーボックス極上パス',
    'Pass Supremo della Scatola Fortunata',
    'Najwyższa Przepustka Skrzyni Szczęścia',
    'Passe Supremo da Caixa da Sorte',
    'Şans Kutusu Üstün Bileti',
    'บัตรผ่านสูงสุดกล่องนำโชค',
]))

# ⑤ 巡游 高级通行证包 —— 补节日限定词（原为无限定词的通用译名，会与福箱包撞名）
T['TXT_Pack_Name_130047'] = dict(zip(LANG, [
    'Pase Avanzado del Desfile',
    'Pass Avancé de la Parade',
    'Tiket Lanjutan Parade',
    'Paraden-Premium-Pass',
    '퍼레이드 고급 패스',
    '馬戲巡遊高級通行證',          # 原本就带限定词，保持
    'Продвинутый парадный пропуск',
    'Просунута парадна перепустка',
    'パレード上級パス',
    'Pass Avanzato della Parata',
    'Zaawansowana Przepustka Parady',
    'Passe Avançado de Desfile',
    'Geçit Gelişmiş Bileti',
    'บัตรผ่านขั้นสูงพาเหรด',
]))

# ⑥ 巡游 至尊通行证包 —— 同上
T['TXT_Pack_Name_130048'] = dict(zip(LANG, [
    'Pase Supremo del Desfile',
    'Pass Suprême de la Parade',
    'Tiket Tertinggi Parade',
    'Paraden-Supreme-Pass',
    '퍼레이드 최상급 패스',
    '馬戲巡遊至尊通行證',          # 原本就带限定词，保持
    'Высший парадный пропуск',
    'Найвища парадна перепустка',
    'パレード極上パス',
    'Pass Supremo della Parata',
    'Najwyższa Przepustka Parady',
    'Passe Supremo de Desfile',
    'Geçit Üstün Bileti',
    'บัตรผ่านสูงสุดพาเหรด',
]))

# ⑦ 巡游通行证 描述（原有缺口，非本次新建）
T['TXT_ActvOnline_ActvDesc_102251'] = dict(zip(LANG, [
    '¡Participa en el Desfile del Circo y desbloquea lujosas recompensas del pase!',
    'Participez à la Parade du Cirque et débloquez de somptueuses récompenses du pass !',
    'Ikuti Parade Sirkus dan buka hadiah mewah dari tiket!',
    'Nimm an der Zirkusparade teil und schalte luxuriöse Pass-Belohnungen frei!',
    '서커스 퍼레이드에 참여하고 패스의 호화로운 보상을 획득하세요!',
    '參與馬戲巡遊，解鎖通行證豪華獎勵！',
    'Участвуйте в цирковом параде и получайте роскошные награды пропуска!',
    'Беріть участь у цирковому параді та отримуйте розкішні нагороди перепустки!',
    'サーカスパレードに参加して、パスの豪華報酬を解放しよう！',
    'Partecipa alla Parata del Circo e sblocca lussuose ricompense del pass!',
    'Weź udział w Cyrkowej Paradzie i odblokuj luksusowe nagrody z przepustki!',
    'Participe do Desfile do Circo e desbloqueie recompensas luxuosas do passe!',
    'Sirk Geçidine katıl ve bilet ödüllerinin kilidini aç!',
    'เข้าร่วมขบวนพาเหรดละครสัตว์เพื่อปลดล็อกรางวัลสุดหรูจากบัตรผ่าน!',
]))

# ⑧ 马戏福箱 描述（原有缺口）——⚠️含 <color> 富文本标签，逐语言必须原样保留
T['TXT_ActvOnline_ActvDesc_101026'] = dict(zip(LANG, [
    '¡Abre la Caja de la Suerte del Circo y gana <color=#2FFF2D>cosméticos raros del Festival del Circo</color> y más!',
    'Ouvrez la Boîte Chance du Cirque pour tenter de gagner des <color=#2FFF2D>cosmétiques rares du Festival du Cirque</color> et plus encore !',
    'Buka Kotak Keberuntungan Sirkus untuk berkesempatan memenangkan <color=#2FFF2D>kosmetik langka Festival Sirkus</color> dan lainnya!',
    'Öffne die Zirkus-Glücksbox für die Chance auf <color=#2FFF2D>seltene Zirkusfest-Kosmetika</color> und mehr!',
    '서커스 행운 상자를 열어 <color=#2FFF2D>서커스 축제 희귀 외형</color> 등 호화 보상을 획득할 기회를 잡으세요!',
    '開啟馬戲福箱，有機會贏取<color=#2FFF2D>馬戲節珍稀外顯</color>等豪華獎勵！',
    'Открывайте цирковой счастливый сундук за шанс получить <color=#2FFF2D>редкие косметические предметы Циркового фестиваля</color> и другие роскошные награды!',
    'Відкривайте цирковий щасливий сундук за шанс отримати <color=#2FFF2D>рідкісні косметичні предмети Циркового фестивалю</color> та інші розкішні нагороди!',
    'サーカスラッキーボックスを開けて、<color=#2FFF2D>サーカスフェス限定の希少外装</color>など豪華報酬を狙おう！',
    'Apri la Scatola Fortunata del Circo per avere la possibilità di vincere <color=#2FFF2D>cosmetici rari del Festival del Circo</color> e altro!',
    'Otwórz Cyrkową Skrzynię Szczęścia, aby zdobyć <color=#2FFF2D>rzadkie kosmetyki Cyrkowego Festiwalu</color> i inne nagrody!',
    'Abra a Caixa da Sorte do Circo para ter a chance de ganhar <color=#2FFF2D>cosméticos raros do Festival do Circo</color> e mais!',
    'Sirk Şans Kutusu\'nu açarak <color=#2FFF2D>nadir Sirk Festivali kozmetikleri</color> ve daha fazlasını kazanma şansı yakala!',
    'เปิดกล่องนำโชคละครสัตว์เพื่อลุ้นรับ <color=#2FFF2D>ไอเทมตกแต่งหายากจากเทศกาลละครสัตว์</color> และรางวัลสุดหรูอื่นๆ!',
]))


def main(dry):
    path = os.path.join(REPO, TSV)
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        txt = f.read()
    if txt and not txt.endswith('\n'):
        txt += '\n'
    lines = txt.split('\n')[:-1]

    hit = {}
    for i, l in enumerate(lines[HEADER_ROWS:], start=HEADER_ROWS):
        k = l.split('\t', 1)[0]
        if k in T:
            if k in hit:
                raise SystemExit(f'!! {k} 命中多行，中止')
            hit[k] = i
    missing = [k for k in T if k not in hit]
    if missing:
        raise SystemExit(f'!! 以下 key 未找到: {missing}')

    changed = 0
    for k, i in hit.items():
        fs = lines[i].split('\t')
        if len(fs) <= COL['th']:
            fs += [''] * (COL['th'] + 1 - len(fs))
        for lang, val in T[k].items():
            c = COL[lang]
            if fs[c] != val:
                fs[c] = val
                changed += 1
        fs[STATUS_COL] = 'AI'
        lines[i] = '\t'.join(fs)
        filled = sum(1 for c in range(3, 19) if fs[c].strip())
        print(f'  {k:<36} 16 语已填 {filled}/16')

    print(f'\n共改写 {changed} 个语言单元格 / {len(hit)} 个 key')
    if dry:
        print('[dry-run] 未写盘')
        return
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines) + '\n')
    print('✅ 已写盘')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    main(a.dry_run)
