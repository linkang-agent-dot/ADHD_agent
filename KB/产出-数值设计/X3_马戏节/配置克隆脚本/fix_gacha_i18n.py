# -*- coding: utf-8 -*-
r"""马戏扭蛋机 i18n 补全 + 中文源修复。

【背景】2026-07-29 扫描扭蛋机本地化，20 个 key 里 13 个有问题，且其中两处是**中文源本身的问题**，
翻译修不了，必须先改源（x3-translation-automatic「场景B：配置层 bug」）：

  ① TXT_RuleTips_Content_40002 中文残缺——只有「1.投入扭蛋币…」一条，以"1."开头却无下文。
     直接翻等于把残缺固化成 16 语。已按实际配置补全为 4 条，格式照开箱 16043 成熟范式。
     第4条回收价 1 钻/个 = 实配 ItemRecycle `1211,2100|1212,2100` → Reward 组 2100 备注
     「马戏节-道具回收返还(1钻/个)」，已核实非臆测。

  ② TXT_Pack_Name_13031/13032/13033 三档同名「高级扭蛋券礼包」($19.99/$49.99/$99.99)，
     玩家在商店只能靠价格区分。按实配券数 80/200/400 加档位后缀。

【翻译术语来源】同表已译好的兄弟 key：
  「节日扭蛋币」= TXT_Item_Name_1211 / 「高级扭蛋券」= TXT_Item_Name_1212
  「普通奖励」= TXT_ActvCircusGacha_FreePoolName / 「高级奖励」= _PayPoolName
  句式/结构照 TXT_RuleTips_Content_16043（马戏福箱，同节日同类规则）

用法: python fix_gacha_i18n.py [--dry-run] [--repo <配置仓路径>]
     dev 与 dev_festival 两条分支同样缺这 13 个 key，同一脚本跑两遍即可。
"""
import io, os, sys

REPO = r'C:\x3\wt_circus_float'
if '--repo' in sys.argv:
    REPO = sys.argv[sys.argv.index('--repo') + 1]
F = r'tsv\i18n\Text__Text.tsv'
C = {'cn': 3, 'en': 4, 'sp': 5, 'fr': 6, 'id': 7, 'de': 8, 'kr': 9, 'zh': 10,
     'ru': 11, 'ua': 12, 'jp': 13, 'it': 14, 'pl': 15, 'po': 16, 'tr': 17, 'th': 18}

# ── 只补缺失语种（已有值不覆盖），避免推翻别人已校对的译文 ──────────────
FILL = {
 'TXT_ActvCircusGacha_Draw':          {'ua': 'Крутити зараз'},
 'TXT_ActvCircusGacha_PayDraw':       {'ua': 'Покращити нагороди'},
 'TXT_ActvCircusGacha_SkipAnim':      {'ua': 'ПРОПУСТИТИ'},
 'TXT_ActvCircusGacha_FreePoolName':  {'ua': 'Звичайна нагорода'},
 'TXT_ActvCircusGacha_PayPoolName':   {'ua': 'Преміум-нагорода'},
 'TXT_ActvCircusGacha_RewardPreview': {'ua': 'ПЕРЕГЛЯД НАГОРОД'},
 'TXT_ActvCircusGacha_TotalScore': {
    'sp': 'Puntuación total', 'fr': 'Score total', 'id': 'Total Skor',
    'de': 'Gesamtpunktzahl', 'kr': '총 점수', 'zh': '總積分',
    'ru': 'Всего очков', 'ua': 'Усього очок', 'jp': '合計スコア',
    'it': 'Punteggio totale', 'pl': 'Łączny wynik', 'po': 'Pontuação total',
    'tr': 'Toplam Puan', 'th': 'คะแนนรวม'},
 'TXT_RuleTips_Title_40002': {
    'sp': 'Gachapón del Circo', 'fr': 'Gachapon du Cirque', 'id': 'Gacha Sirkus',
    'de': 'Zirkus-Gacha', 'kr': '서커스 뽑기', 'zh': '馬戲扭蛋機',
    'ru': 'Цирковой гача-автомат', 'ua': 'Цирковий гача-автомат',
    'jp': 'サーカスガチャ', 'it': 'Gacha del Circo', 'pl': 'Cyrkowa Gacha',
    'po': 'Gacha do Circo', 'tr': 'Sirk Gacha', 'th': 'กาชาเซอร์คัส'},
}

# ── 中文源修复（连同 16 语一起重写） ───────────────────────────────
NL = '\\n'   # Text 表里换行是字面两字符 \n，不是真换行

RULE = {
 'cn': f"马戏扭蛋机已经上好发条，投币转动，看看今天的运气如何！{NL}{NL}<color=#18962D>【活动介绍】</color>{NL}"
       f"1.活动期间，可消耗【节日扭蛋币】在「普通奖励」池抽奖，支持单抽与十连抽。{NL}"
       f"2.使用【高级扭蛋券】可在「高级奖励」池抽奖，奖励价值更高。{NL}"
       f"3.每次抽奖均可累计积分，积分可用于兑换庆功奖励。{NL}"
       f"4.活动结束后，未使用的【节日扭蛋币】与【高级扭蛋券】将按照每个1钻石的价格进行回收。",
 'zh': f"馬戲扭蛋機已經上好發條，投幣轉動，看看今天的運氣如何！{NL}{NL}<color=#18962D>【活動介紹】</color>{NL}"
       f"1.活動期間，可消耗【節日扭蛋幣】在「普通獎勵」池抽獎，支援單抽與十連抽。{NL}"
       f"2.使用【高級扭蛋券】可在「高級獎勵」池抽獎，獎勵價值更高。{NL}"
       f"3.每次抽獎均可累計積分，積分可用於兌換慶功獎勵。{NL}"
       f"4.活動結束後，未使用的【節日扭蛋幣】與【高級扭蛋券】將按照每個1鑽石的價格進行回收。",
 'en': f"The Circus Gacha Machine is all wound up—drop a coin, give it a spin, and see how lucky you are today!{NL}{NL}<color=#18962D>[Event Details]</color>{NL}"
       f"1. During the event, spend Festival Gacha Coins to draw from the Normal Reward pool. Single and 10x draws are both available.{NL}"
       f"2. Use Premium Gacha Vouchers to draw from the Premium Reward pool for higher-value rewards.{NL}"
       f"3. Every draw earns points, which can be exchanged for celebration rewards.{NL}"
       f"4. After the event ends, any unused Festival Gacha Coins and Premium Gacha Vouchers will be recycled at 1 Diamond each.",
 'sp': f"¡El Gachapón del Circo está listo! Introduce una moneda, gíralo y comprueba tu suerte de hoy.{NL}{NL}<color=#18962D>[Detalles del evento]</color>{NL}"
       f"1. Durante el evento, gasta Monedas de Gacha Festivas para tirar del grupo de Recompensa Normal. Disponibles tiradas simples y x10.{NL}"
       f"2. Usa Vales de Gacha Premium para tirar del grupo de Recompensa Premium, con recompensas de mayor valor.{NL}"
       f"3. Cada tirada otorga puntos, canjeables por recompensas de celebración.{NL}"
       f"4. Al finalizar el evento, las Monedas de Gacha Festivas y los Vales de Gacha Premium sin usar se reciclarán por 1 diamante cada uno.",
 'fr': f"Le Gachapon du Cirque est remonté : insérez une pièce, faites-le tourner et tentez votre chance !{NL}{NL}<color=#18962D>[Détails de l'événement]</color>{NL}"
       f"1. Pendant l'événement, dépensez des Jetons de Gacha de Fête pour tirer dans le lot Récompense Normale. Tirages simples et x10 disponibles.{NL}"
       f"2. Utilisez des Bons de Gacha Premium pour tirer dans le lot Récompense Premium, aux récompenses de plus grande valeur.{NL}"
       f"3. Chaque tirage rapporte des points, échangeables contre des récompenses de célébration.{NL}"
       f"4. À la fin de l'événement, les Jetons de Gacha de Fête et Bons de Gacha Premium inutilisés seront recyclés au prix de 1 diamant chacun.",
 'id': f"Mesin Gacha Sirkus sudah siap—masukkan koin, putar, dan lihat keberuntunganmu hari ini!{NL}{NL}<color=#18962D>[Detail Event]</color>{NL}"
       f"1. Selama event, gunakan Koin Gacha Festival untuk menarik dari pool Hadiah Normal. Tersedia tarikan tunggal dan 10x.{NL}"
       f"2. Gunakan Kupon Gacha Premium untuk menarik dari pool Hadiah Premium dengan hadiah bernilai lebih tinggi.{NL}"
       f"3. Setiap tarikan memberi poin yang dapat ditukar dengan hadiah perayaan.{NL}"
       f"4. Setelah event berakhir, Koin Gacha Festival dan Kupon Gacha Premium yang tidak terpakai akan didaur ulang seharga 1 Berlian per buah.",
 'de': f"Der Zirkus-Gacha-Automat ist aufgezogen – Münze einwerfen, drehen und dein Glück testen!{NL}{NL}<color=#18962D>[Event-Details]</color>{NL}"
       f"1. Gib während des Events Festival-Gacha-Münzen aus, um aus dem Pool „Normale Belohnung“ zu ziehen. Einzel- und 10er-Ziehungen sind möglich.{NL}"
       f"2. Nutze Premium-Gacha-Gutscheine, um aus dem Pool „Premium-Belohnung“ mit höherwertigen Belohnungen zu ziehen.{NL}"
       f"3. Jede Ziehung bringt Punkte, die gegen Feier-Belohnungen eingetauscht werden können.{NL}"
       f"4. Nach Eventende werden nicht genutzte Festival-Gacha-Münzen und Premium-Gacha-Gutscheine für je 1 Diamant zurückgekauft.",
 'kr': f"서커스 뽑기 기계가 준비됐습니다. 코인을 넣고 돌려 오늘의 운을 시험해 보세요!{NL}{NL}<color=#18962D>[이벤트 소개]</color>{NL}"
       f"1. 이벤트 기간 동안 축제 뽑기 코인을 소모해 일반 보상 풀에서 뽑을 수 있습니다. 단일 뽑기와 10연차 모두 가능합니다.{NL}"
       f"2. 고급 뽑기권을 사용하면 더 높은 가치의 고급 보상 풀에서 뽑을 수 있습니다.{NL}"
       f"3. 뽑기를 할 때마다 점수가 누적되며, 점수로 축하 보상을 교환할 수 있습니다.{NL}"
       f"4. 이벤트 종료 후 사용하지 않은 축제 뽑기 코인과 고급 뽑기권은 개당 다이아 1개로 회수됩니다.",
 'ru': f"Цирковой гача-автомат заведён — бросьте монету, крутите и проверьте свою удачу!{NL}{NL}<color=#18962D>[Об ивенте]</color>{NL}"
       f"1. Во время ивента тратьте Праздничные гача-монеты, чтобы крутить пул «Обычная награда». Доступны одиночные и х10 прокрутки.{NL}"
       f"2. Используйте Премиум гача-купоны для пула «Преміум-награда» с более ценными наградами.{NL}"
       f"3. Каждая прокрутка приносит очки, которые можно обменять на праздничные награды.{NL}"
       f"4. После окончания ивента неиспользованные Праздничные гача-монеты и Премиум гача-купоны будут выкуплены по 1 алмазу за штуку.",
 'ua': f"Цирковий гача-автомат заведено — киньте монету, крутіть і перевірте свою удачу!{NL}{NL}<color=#18962D>[Про івент]</color>{NL}"
       f"1. Під час івенту витрачайте Святкові гача-монети, щоб крутити пул «Звичайна нагорода». Доступні одиночні та х10 прокрутки.{NL}"
       f"2. Використовуйте Преміум гача-купони для пулу «Преміум-нагорода» з ціннішими нагородами.{NL}"
       f"3. Кожна прокрутка дає очки, які можна обміняти на святкові нагороди.{NL}"
       f"4. Після завершення івенту невикористані Святкові гача-монети та Преміум гача-купони буде викуплено по 1 алмазу за штуку.",
 'jp': f"サーカスガチャのゼンマイは巻き終わった——コインを入れて回し、今日の運を試そう！{NL}{NL}<color=#18962D>[イベント紹介]</color>{NL}"
       f"1. イベント期間中、フェスガチャコインを消費して「通常報酬」プールを回せます。単発・10連どちらも可能です。{NL}"
       f"2. 上級ガチャチケットを使うと、より価値の高い「上級報酬」プールを回せます。{NL}"
       f"3. ガチャを回すたびにスコアが加算され、スコアは祝勝報酬と交換できます。{NL}"
       f"4. イベント終了後、未使用のフェスガチャコインと上級ガチャチケットは1個につきダイヤ1個で回収されます。",
 'it': f"La Gacha del Circo è carica: inserisci una moneta, girala e scopri quanta fortuna hai oggi!{NL}{NL}<color=#18962D>[Dettagli evento]</color>{NL}"
       f"1. Durante l'evento, spendi Gettoni Gacha della Festa per pescare dal gruppo Ricompensa Normale. Disponibili estrazioni singole e x10.{NL}"
       f"2. Usa i Buoni Gacha Premium per pescare dal gruppo Ricompensa Premium, con premi di valore superiore.{NL}"
       f"3. Ogni estrazione assegna punti, riscattabili per ricompense celebrative.{NL}"
       f"4. Al termine dell'evento, i Gettoni Gacha della Festa e i Buoni Gacha Premium inutilizzati saranno riscattati a 1 diamante ciascuno.",
 'pl': f"Cyrkowa maszyna gacha jest nakręcona — wrzuć monetę, zakręć i sprawdź dzisiejsze szczęście!{NL}{NL}<color=#18962D>[Szczegóły wydarzenia]</color>{NL}"
       f"1. Podczas wydarzenia wydawaj Świąteczne Żetony Gacha, aby losować z puli Zwykłej Nagrody. Dostępne losowania pojedyncze i x10.{NL}"
       f"2. Użyj Kuponów Gacha Premium, aby losować z puli Nagrody Premium o wyższej wartości.{NL}"
       f"3. Każde losowanie daje punkty, które można wymienić na nagrody świętowania.{NL}"
       f"4. Po zakończeniu wydarzenia niewykorzystane Świąteczne Żetony Gacha i Kupony Gacha Premium zostaną odkupione po 1 diamencie za sztukę.",
 'po': f"A Máquina de Gacha do Circo está pronta — insira uma moeda, gire e veja a sua sorte hoje!{NL}{NL}<color=#18962D>[Detalhes do evento]</color>{NL}"
       f"1. Durante o evento, gaste Moedas de Gacha do Festival para girar no grupo Recompensa Normal. Giros simples e x10 disponíveis.{NL}"
       f"2. Use Vales de Gacha Premium para girar no grupo Recompensa Premium, com recompensas de maior valor.{NL}"
       f"3. Cada giro concede pontos, que podem ser trocados por recompensas de celebração.{NL}"
       f"4. Após o evento, as Moedas de Gacha do Festival e os Vales de Gacha Premium não usados serão reciclados por 1 diamante cada.",
 'tr': f"Sirk Gacha Makinesi kuruldu — bir jeton at, çevir ve bugünkü şansını gör!{NL}{NL}<color=#18962D>[Etkinlik Detayları]</color>{NL}"
       f"1. Etkinlik boyunca Festival Gacha Jetonu harcayarak Normal Ödül havuzundan çekiliş yapabilirsin. Tekli ve 10'lu çekilişler mevcuttur.{NL}"
       f"2. Premium Gacha Kuponu kullanarak daha değerli ödüller içeren Premium Ödül havuzundan çekiliş yapabilirsin.{NL}"
       f"3. Her çekiliş puan kazandırır; puanlar kutlama ödülleriyle takas edilebilir.{NL}"
       f"4. Etkinlik bittiğinde kullanılmayan Festival Gacha Jetonları ve Premium Gacha Kuponları adet başına 1 Elmas karşılığında geri alınır.",
 'th': f"เครื่องกาชาเซอร์คัสพร้อมแล้ว—หยอดเหรียญ หมุนเลย แล้วดูว่าวันนี้ดวงคุณเป็นยังไง!{NL}{NL}<color=#18962D>[รายละเอียดกิจกรรม]</color>{NL}"
       f"1. ระหว่างกิจกรรม ใช้เหรียญกาชาเทศกาลเพื่อสุ่มจากพูลรางวัลธรรมดา รองรับทั้งสุ่มเดี่ยวและสุ่ม 10 ครั้ง{NL}"
       f"2. ใช้ตั๋วกาชาพรีเมียมเพื่อสุ่มจากพูลรางวัลพรีเมียมที่มีมูลค่าสูงกว่า{NL}"
       f"3. การสุ่มทุกครั้งจะได้รับคะแนน ซึ่งสามารถนำไปแลกรางวัลฉลองได้{NL}"
       f"4. หลังกิจกรรมสิ้นสุด เหรียญกาชาเทศกาลและตั๋วกาชาพรีเมียมที่เหลือจะถูกรับซื้อคืนในราคาชิ้นละ 1 เพชร",
}

# 三档礼包按实配券数 80/200/400 加档位后缀（原三档同名）
PACKS = {
 '13031': ('高级扭蛋券礼包·80券', 'Premium Gacha Voucher Pack (80)'),
 '13032': ('高级扭蛋券礼包·200券', 'Premium Gacha Voucher Pack (200)'),
 '13033': ('高级扭蛋券礼包·400券', 'Premium Gacha Voucher Pack (400)'),
}
PACK_LANG = {   # 各语「高级扭蛋券礼包」译法（取自 en 既有译名的对应语风格）
 'sp': 'Pack de Vales de Gacha Premium', 'fr': 'Pack de Bons de Gacha Premium',
 'id': 'Paket Kupon Gacha Premium', 'de': 'Premium-Gacha-Gutschein-Paket',
 'kr': '고급 뽑기권 패키지', 'zh': '高級扭蛋券禮包',
 'ru': 'Набор премиум гача-купонов', 'ua': 'Набір преміум гача-купонів',
 'jp': '上級ガチャチケットパック', 'it': 'Pacchetto Buoni Gacha Premium',
 'pl': 'Pakiet Kuponów Gacha Premium', 'po': 'Pacote de Vales de Gacha Premium',
 'tr': 'Premium Gacha Kuponu Paketi', 'th': 'แพ็กตั๋วกาชาพรีเมียม',
}
CHAIN_NAME = {'cn': '高级扭蛋券礼包', 'en': 'Premium Gacha Voucher Pack', **PACK_LANG}


def main(dry):
    p = os.path.join(REPO, F)
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        t = f.read()
    nl = '\r\n' if '\r\n' in t[:4000] else '\n'
    lines = t.replace('\r\n', '\n').split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]

    stat = {'fill': 0, 'rule': 0, 'pack': 0, 'chain': 0}
    for i, l in enumerate(lines[6:], 6):
        fs = l.split('\t')
        ks = fs[0].split('|')

        for k, langs in FILL.items():
            if k in ks:
                for lang, txt in langs.items():
                    c = C[lang]
                    while len(fs) <= c:
                        fs.append('')
                    if fs[c].strip():
                        print(f'   跳过(已有值) {k} [{lang}] = {fs[c][:20]}')
                        continue
                    fs[c] = txt; stat['fill'] += 1
                fs[1] = 'AI'; lines[i] = '\t'.join(fs)

        if 'TXT_RuleTips_Content_40002' in ks:
            for lang, txt in RULE.items():
                c = C[lang]
                while len(fs) <= c:
                    fs.append('')
                fs[c] = txt
            fs[1] = 'AI'; lines[i] = '\t'.join(fs); stat['rule'] = 1

        for pid, (cn, en) in PACKS.items():
            if f'TXT_Pack_Name_{pid}' in ks:
                num = cn.split('·')[1]
                for lang, base in [('cn', cn), ('en', en)] + [(g, f'{v} ({num[:-1]})') for g, v in PACK_LANG.items()]:
                    c = C[lang]
                    while len(fs) <= c:
                        fs.append('')
                    fs[c] = base
                fs[1] = 'AI'; lines[i] = '\t'.join(fs); stat['pack'] += 1

        if 'TXT_ChainPack_Name_707' in ks:
            for lang, txt in CHAIN_NAME.items():
                c = C[lang]
                while len(fs) <= c:
                    fs.append('')
                if not fs[c].strip():
                    fs[c] = txt
            fs[1] = 'AI'; lines[i] = '\t'.join(fs); stat['chain'] = 1

    print(f"\n补缺语 {stat['fill']} 处 / 规则正文 {stat['rule']} 行 / 礼包名 {stat['pack']} 个 / 链名 {stat['chain']} 行")
    if not dry:
        with io.open(p, 'w', encoding='utf-8', newline=nl) as f:
            f.write('\n'.join(lines) + '\n')
        print('✅ 已写盘')
    else:
        print('[dry-run] 未写盘')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main('--dry-run' in sys.argv)
