# -*- coding: utf-8 -*-
"""把周卡4个名称的16语言翻译追加进 Text__Text.tsv（status=AI）。默认 dry-run，--apply 写入。
术语锚=已校对的现有周卡名(加速/招募/材料/船只改装周卡)：周卡=Weekly Pass/週卡。"""
import csv, os, sys, shutil

TSV = r'C:\x3\gdconfig\tsv\i18n\Text__Text.tsv'
STG = os.path.dirname(os.path.abspath(__file__))
# 列序: cn en sp fr id de kr zh ru ua jp it pl po tr th  (col3..col18)
LANGS = ['cn','en','sp','fr','id','de','kr','zh','ru','ua','jp','it','pl','po','tr','th']
DATA = {
 'TXT_Pack_Name_2026101': ['基础周卡','Basic Weekly Pass','Pase Semanal Básico','Pass Hebdomadaire Basique','Kartu Mingguan Dasar','Basis-Wochenpass','기본 주간권','基礎週卡','Базовый недельный пропуск','Базовий тижневий пропуск','ベーシック週間パス','Abbonamento Settimanale Base','Podstawowa Tygodniowa Karta','Passe Semanal Básico','Temel Haftalık Kart','พาสรายสัปดาห์พื้นฐาน'],
 'TXT_Pack_Name_2026102': ['进阶周卡','Advanced Weekly Pass','Pase Semanal Avanzado','Pass Hebdomadaire Avancé','Kartu Mingguan Lanjutan','Fortgeschrittenen-Wochenpass','고급 주간권','進階週卡','Продвинутый недельный пропуск','Просунутий тижневий пропуск','アドバンス週間パス','Abbonamento Settimanale Avanzato','Zaawansowana Tygodniowa Karta','Passe Semanal Avançado','Gelişmiş Haftalık Kart','พาสรายสัปดาห์ขั้นสูง'],
 'TXT_Pack_Name_2026103': ['至尊周卡','Supreme Weekly Pass','Pase Semanal Supremo','Pass Hebdomadaire Suprême','Kartu Mingguan Tertinggi','Supreme-Wochenpass','최상급 주간권','至尊週卡','Высший недельный пропуск','Верховний тижневий пропуск','至尊週間パス','Abbonamento Settimanale Supremo','Najwyższa Tygodniowa Karta','Passe Semanal Supremo','Üstün Haftalık Kart','พาสรายสัปดาห์สูงสุด'],
 'TXT_Pack_Name_2026104': ['周卡全包','Weekly Pass Bundle','Paquete de Pase Semanal','Pack Pass Hebdomadaire','Paket Kartu Mingguan','Wochenpass-Paket','주간권 패키지','週卡全包','Набор недельных пропусков','Набір тижневих пропусків','週間パスセット','Pacchetto Abbonamento Settimanale','Pakiet Tygodniowych Kart','Pacote de Passe Semanal','Haftalık Kart Paketi','แพ็กพาสรายสัปดาห์'],
}
apply = '--apply' in sys.argv

rows = list(csv.reader(open(TSV, encoding='utf-8'), delimiter='\t'))
existing = {r[0] for r in rows if r}
width = max(len(r) for r in rows[:50])  # 对齐现有列宽
print('Text tsv 现有列宽=', width, '总行=', len(rows))

new_rows = []
for key, trans in DATA.items():
    if any(key in r0 for r0 in existing):
        print('[跳过] 已存在:', key); continue
    row = [''] * width
    row[0] = key; row[1] = 'AI'; row[2] = ''
    for j, v in enumerate(trans):
        row[3 + j] = v
    new_rows.append(row)
    print(f'  + {key}: cn={trans[0]} en={trans[1]} zh={trans[7]}')

if apply and new_rows:
    shutil.copy2(TSV, os.path.join(STG, 'Text__Text.PRE_I18N_BACKUP.tsv'))
    rows.extend(new_rows)
    with open(TSV, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(rows)
    print(f'\n[APPLIED] 追加 {len(new_rows)} 行到 Text__Text.tsv（备份 Text__Text.PRE_I18N_BACKUP.tsv）')
else:
    print(f'\n[DRY-RUN] 将追加 {len(new_rows)} 行。--apply 写入。')
