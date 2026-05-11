import json, subprocess, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8")

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

# ── rule translations (cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns) ──
rule_cn = '1.玩家消耗抽奖道具，发射弹珠抽奖即可获取弹珠阶段奖励和弹珠兑换奖励\\n2.弹珠可以碰撞阶段奖励进度，每次碰撞均可填充奖励进度，阶段奖励进度被填满后，即可获取阶段奖励。单个弹珠最多累计5次阶段奖励进度（两侧总计）\\n3.弹珠落入对应的兑换道具格中，即可获取对应数量的兑换道具\\n4.玩家可以使用兑换道具在普通商店中兑换各种奖励\\n5.累计使用50个普通弹珠后，将触发福利关卡，获得50个免费福利弹珠\\n6.福利关卡中弹珠落入洞口可获得高级兑换券，可在高级商店中兑换珍稀奖励\\n7.累计触发福利关卡达到指定次数时，可开启弹珠大师宝箱获得额外奖励\\n8.活动结束后，未使用的抽奖、兑换道具将会回收为15分钟训练加速、1分钟训练加速'
rule_en = '1.Spend a Draw Token to launch a Marble and earn stage rewards plus Exchange Tokens.\\n2.Each time your Marble hits a stage-reward node, the progress bar fills\u2014max it out to claim the prize. A single Marble can accumulate up to 5 stage reward progress (total for both sides).\\n3.When the Marble drops into an exchange slot, you receive the corresponding Exchange Tokens.\\n4.Trade Exchange Tokens for rewards in the Normal Shop.\\n5.After using 50 regular Marbles in total, a Bonus Round is triggered granting 50 free Bonus Marbles.\\n6.In the Bonus Round, Marbles that land in slots award Premium Exchange Tickets redeemable in the Advanced Shop for rare rewards.\\n7.Reaching cumulative Bonus Round milestones unlocks a Marble Master Chest with extra rewards.\\n8.When the event ends, unused Draw and Exchange items convert into 15-minute Training Speedup and 1-minute Training Speedup.'
rule_fr = "1.D\u00e9pensez des Jetons de Tirage pour lancer des Billes et gagner des r\u00e9compenses d'\u00e9tape et des jetons d'\u00e9change.\\n2.Chaque fois qu'une Bille touche un n\u0153ud de r\u00e9compense, la barre de progression se remplit. Remplissez-la pour obtenir le prix. Une seule Bille peut accumuler jusqu'\u00e0 5 progressions (des deux c\u00f4t\u00e9s).\\n3.Lorsqu'une Bille tombe dans une case d'\u00e9change, vous recevez les Jetons correspondants.\\n4.Utilisez les Jetons d'\u00e9change pour \u00e9changer des r\u00e9compenses dans la Boutique Normale.\\n5.Apr\u00e8s avoir utilis\u00e9 50 Billes normales au total, un Tour Bonus se d\u00e9clenche et vous octroie 50 Billes Bonus gratuites.\\n6.Pendant le Tour Bonus, les Billes qui atterrissent dans les cases rapportent des Tickets d'\u00c9change Premium \u00e9changeables en Boutique Avanc\u00e9e.\\n7.Atteindre les jalons cumul\u00e9s de Tours Bonus d\u00e9bloque un Coffre Ma\u00eetre des Billes avec des r\u00e9compenses suppl\u00e9mentaires.\\n8.\u00c0 la fin de l'\u00e9v\u00e9nement, les objets de tirage et d'\u00e9change inutilis\u00e9s sont convertis en Acc\u00e9l\u00e9rations d'Entra\u00eenement de 15 min et 1 min."
rule_de = '1.Setze Zieh-Marken ein, um Murmeln zu starten und Stufen-Belohnungen sowie Tausch-Marken zu erhalten.\\n2.Jedes Mal, wenn eine Murmel einen Belohnungsknoten trifft, f\u00fcllt sich der Fortschrittsbalken. F\u00fclle ihn, um den Preis zu erhalten. Eine einzelne Murmel kann bis zu 5 Stufen-Fortschritte sammeln (beide Seiten zusammen).\\n3.Wenn eine Murmel in einen Tauschplatz f\u00e4llt, erh\u00e4ltst du die entsprechenden Tausch-Marken.\\n4.Verwende Tausch-Marken, um Belohnungen im Normalen Shop einzul\u00f6sen.\\n5.Nach insgesamt 50 normalen Murmeln wird eine Bonusrunde ausgel\u00f6st, die 50 kostenlose Bonus-Murmeln gew\u00e4hrt.\\n6.In der Bonusrunde landen Murmeln in Schlitzen f\u00fcr Premium-Tauschtickets, einl\u00f6sbar im Fortgeschrittenen Shop.\\n7.Erreiche kumulative Bonusrunden-Meilensteine, um eine Murmel-Meister-Truhe mit Extra-Belohnungen freizuschalten.\\n8.Nach dem Event werden unbenutzte Zieh- und Tausch-Gegenst\u00e4nde in 15-Min- und 1-Min-Trainings-Beschleunigungen umgewandelt.'
rule_po = '1.Gaste Fichas de Sorteio para lan\u00e7ar Bolas e ganhar recompensas de etapa e fichas de troca.\\n2.Cada vez que uma Bola atinge um n\u00f3 de recompensa, a barra de progresso \u00e9 preenchida. Complete-a para reivindicar o pr\u00eamio. Uma \u00fanica Bola pode acumular at\u00e9 5 progressos (ambos os lados).\\n3.Quando uma Bola cai em um slot de troca, voc\u00ea recebe as Fichas correspondentes.\\n4.Use Fichas de Troca para resgatar recompensas na Loja Normal.\\n5.Ap\u00f3s usar 50 Bolas normais no total, uma Rodada B\u00f4nus \u00e9 ativada concedendo 50 Bolas B\u00f4nus gratuitas.\\n6.Na Rodada B\u00f4nus, Bolas que caem em slots concedem Bilhetes de Troca Premium resgat\u00e1veis na Loja Avan\u00e7ada.\\n7.Atingir marcos cumulativos de Rodadas B\u00f4nus desbloqueia um Ba\u00fa Mestre de Bolas com recompensas extras.\\n8.Quando o evento terminar, itens de sorteio e troca n\u00e3o utilizados ser\u00e3o convertidos em Acelera\u00e7\u00f5es de Treino de 15 min e 1 min.'
rule_zh = '1.玩家消耗抽獎道具，發射彈珠抽獎即可獲取彈珠階段獎勵和彈珠兌換獎勵\\n2.彈珠可以碰撞階段獎勵進度，每次碰撞均可填充獎勵進度，階段獎勵進度被填滿後，即可獲取階段獎勵。單個彈珠最多累計5次階段獎勵進度（兩側總計）\\n3.彈珠落入對應的兌換道具格中，即可獲取對應數量的兌換道具\\n4.玩家可以使用兌換道具在普通商店中兌換各種獎勵\\n5.累計使用50個普通彈珠後，將觸發福利關卡，獲得50個免費福利彈珠\\n6.福利關卡中彈珠落入洞口可獲得高級兌換券，可在高級商店中兌換珍稀獎勵\\n7.累計觸發福利關卡達到指定次數時，可開啟彈珠大師寶箱獲得額外獎勵\\n8.活動結束後，未使用的抽獎、兌換道具將會回收為15分鐘訓練加速、1分鐘訓練加速'
rule_id = 'Indonesian placeholder'  # will fill below
rule_th = 'Thai placeholder'
rule_sp = 'Spanish placeholder'
rule_ru = 'Russian placeholder'
rule_tr = 'Turkish placeholder'
rule_vi = 'Vietnamese placeholder'
rule_it = 'Italian placeholder'
rule_pl = 'Polish placeholder'
rule_ar = 'Arabic placeholder'
rule_jp = 'Japanese placeholder'
rule_kr = 'Korean placeholder'

# Full translations for remaining languages
rule_id = '1.Gunakan Token Undian untuk meluncurkan Kelereng dan dapatkan hadiah tahap serta token penukaran.\\n2.Setiap kali Kelereng mengenai node hadiah, bar progres terisi. Isi penuh untuk mengklaim hadiah. Satu Kelereng dapat mengumpulkan hingga 5 progres (kedua sisi).\\n3.Saat Kelereng jatuh ke slot penukaran, Anda menerima Token Penukaran yang sesuai.\\n4.Gunakan Token Penukaran untuk menukarkan hadiah di Toko Normal.\\n5.Setelah menggunakan total 50 Kelereng biasa, Ronde Bonus terpicu dan memberikan 50 Kelereng Bonus gratis.\\n6.Di Ronde Bonus, Kelereng yang mendarat di slot memberikan Tiket Penukaran Premium yang dapat ditukar di Toko Lanjutan.\\n7.Mencapai milestone kumulatif Ronde Bonus membuka Peti Master Kelereng dengan hadiah ekstra.\\n8.Saat event berakhir, item undian dan penukaran yang tidak digunakan dikonversi menjadi Percepatan Latihan 15 menit dan 1 menit.'
rule_th = '1.ใช้โทเค็นจับฉลากเพื่อยิงลูกแก้วและรับรางวัลตามขั้นตอนพร้อมโทเค็นแลกเปลี่ยน\\n2.ทุกครั้งที่ลูกแก้วชนโหนดรางวัล แถบความคืบหน้าจะเติมเต็ม เติมเต็มเพื่อรับรางวัล ลูกแก้วหนึ่งลูกสะสมได้สูงสุด 5 ความคืบหน้า (ทั้งสองด้านรวมกัน)\\n3.เมื่อลูกแก้วตกลงในช่องแลกเปลี่ยน คุณจะได้รับโทเค็นแลกเปลี่ยนที่สอดคล้อง\\n4.ใช้โทเค็นแลกเปลี่ยนเพื่อแลกรางวัลในร้านค้าปกติ\\n5.หลังจากใช้ลูกแก้วปกติรวม 50 ลูก รอบโบนัสจะเปิดขึ้นพร้อมลูกแก้วโบนัสฟรี 50 ลูก\\n6.ในรอบโบนัส ลูกแก้วที่ตกลงในช่องจะให้ตั๋วแลกเปลี่ยนพรีเมียมที่แลกได้ในร้านค้าขั้นสูง\\n7.เมื่อถึงเป้าหมายรอบโบนัสสะสม จะปลดล็อคกล่องสมบัติปรมาจารย์ลูกแก้วพร้อมรางวัลพิเศษ\\n8.เมื่อกิจกรรมสิ้นสุด ไอเทมจับฉลากและแลกเปลี่ยนที่ไม่ได้ใช้จะถูกแปลงเป็นเร่งการฝึก 15 นาทีและ 1 นาที'
rule_sp = '1.Gasta Fichas de Sorteo para lanzar Canicas y ganar recompensas de etapa y fichas de intercambio.\\n2.Cada vez que una Canica golpea un nodo de recompensa, la barra de progreso se llena. Compl\u00e9tala para reclamar el premio. Una sola Canica puede acumular hasta 5 progresos (ambos lados).\\n3.Cuando una Canica cae en una ranura de intercambio, recibes las Fichas correspondientes.\\n4.Usa las Fichas de Intercambio para canjear recompensas en la Tienda Normal.\\n5.Despu\u00e9s de usar 50 Canicas normales en total, se activa una Ronda Bonus que otorga 50 Canicas Bonus gratuitas.\\n6.En la Ronda Bonus, las Canicas que caen en ranuras otorgan Tickets de Intercambio Premium canjeables en la Tienda Avanzada.\\n7.Alcanzar hitos acumulativos de Rondas Bonus desbloquea un Cofre Maestro de Canicas con recompensas adicionales.\\n8.Al finalizar el evento, los objetos de sorteo e intercambio no utilizados se convierten en Aceleraciones de Entrenamiento de 15 min y 1 min.'
rule_ru = '1.Тратьте жетоны розыгрыша, чтобы запустить шарики и получить награды этапов и жетоны обмена.\\n2.Каждый раз, когда шарик попадает в узел награды, полоса прогресса заполняется. Заполните её, чтобы получить приз. Один шарик может накопить до 5 прогрессов (с обеих сторон).\\n3.Когда шарик попадает в ячейку обмена, вы получаете соответствующие жетоны обмена.\\n4.Используйте жетоны обмена для получения наград в обычном магазине.\\n5.После использования 50 обычных шариков активируется бонусный раунд с 50 бесплатными бонусными шариками.\\n6.В бонусном раунде шарики, попавшие в лунки, приносят премиум-билеты обмена для продвинутого магазина.\\n7.При достижении кумулятивных вех бонусных раундов открывается сундук мастера шариков с дополнительными наградами.\\n8.По окончании события неиспользованные предметы розыгрыша и обмена конвертируются в 15-мин и 1-мин ускорения тренировки.'
rule_tr = '\u00c7ekili\u015f Jetonlar\u0131 harcayarak Bilye f\u0131rlat\u0131n, a\u015fama \u00f6d\u00fclleri ve takas jetonlar\u0131 kazan\u0131n.\\n2.Bilye her \u00f6d\u00fcl d\u00fc\u011f\u00fcm\u00fcne \u00e7arpt\u0131\u011f\u0131nda ilerleme \u00e7ubu\u011fu dolar. \u00d6d\u00fcl\u00fc almak i\u00e7in doldurun. Tek bir Bilye en fazla 5 ilerleme biriktirebilir (iki taraf toplam\u0131).\\n3.Bilye bir takas yuvas\u0131na d\u00fc\u015ft\u00fc\u011f\u00fcnde ilgili Takas Jetonlar\u0131n\u0131 al\u0131rs\u0131n\u0131z.\\n4.Takas Jetonlar\u0131n\u0131 Normal Ma\u011faza\'da \u00f6d\u00fcller i\u00e7in kullan\u0131n.\\n5.Toplam 50 normal Bilye kulland\u0131ktan sonra Bonus Tur tetiklenir ve 50 \u00fccretsiz Bonus Bilye verilir.\\n6.Bonus Turda yuvalara d\u00fc\u015fen Bilyeler Geli\u015fmi\u015f Ma\u011faza\'da kullan\u0131labilir Premium Takas Biletleri verir.\\n7.K\u00fcm\u00fclatif Bonus Tur kilometre ta\u015flar\u0131na ula\u015fmak, ekstra \u00f6d\u00fcller i\u00e7eren bir Bilye Ustas\u0131 Sand\u0131\u011f\u0131 a\u00e7ar.\\n8.Etkinlik sona erdi\u011finde kullan\u0131lmayan \u00e7ekili\u015f ve takas e\u015fyalar\u0131 15 dk ve 1 dk E\u011fitim H\u0131zland\u0131r\u0131c\u0131lar\u0131na d\u00f6n\u00fc\u015ft\u00fcr\u00fcl\u00fcr.'
rule_vi = '1.S\u1eed d\u1ee5ng V\u00e9 Quay \u0111\u1ec3 b\u1eafn Bi v\u00e0 nh\u1eadn ph\u1ea7n th\u01b0\u1edfng giai \u0111o\u1ea1n c\u00f9ng token \u0111\u1ed5i th\u01b0\u1edfng.\\n2.M\u1ed7i l\u1ea7n Bi ch\u1ea1m v\u00e0o n\u00fat th\u01b0\u1edfng, thanh ti\u1ebfn tr\u00ecnh s\u1ebd \u0111\u01b0\u1ee3c l\u1ea5p \u0111\u1ea7y. L\u1ea5p \u0111\u1ea7y \u0111\u1ec3 nh\u1eadn gi\u1ea3i. M\u1ed9t vi\u00ean Bi c\u00f3 th\u1ec3 t\u00edch l\u0169y t\u1ed1i \u0111a 5 ti\u1ebfn tr\u00ecnh (c\u1ea3 hai b\u00ean).\\n3.Khi Bi r\u01a1i v\u00e0o \u00f4 \u0111\u1ed5i, b\u1ea1n nh\u1eadn \u0111\u01b0\u1ee3c Token \u0110\u1ed5i Th\u01b0\u1edfng t\u01b0\u01a1ng \u1ee9ng.\\n4.D\u00f9ng Token \u0110\u1ed5i Th\u01b0\u1edfng \u0111\u1ec3 \u0111\u1ed5i ph\u1ea7n th\u01b0\u1edfng t\u1ea1i C\u1eeda H\u00e0ng Th\u01b0\u1eddng.\\n5.Sau khi s\u1eed d\u1ee5ng t\u1ed5ng c\u1ed9ng 50 Bi th\u01b0\u1eddng, V\u00f2ng Th\u01b0\u1edfng \u0111\u01b0\u1ee3c k\u00edch ho\u1ea1t t\u1eb7ng 50 Bi Th\u01b0\u1edfng mi\u1ec5n ph\u00ed.\\n6.Trong V\u00f2ng Th\u01b0\u1edfng, Bi r\u01a1i v\u00e0o \u00f4 s\u1ebd nh\u1eadn V\u00e9 \u0110\u1ed5i Cao C\u1ea5p c\u00f3 th\u1ec3 \u0111\u1ed5i t\u1ea1i C\u1eeda H\u00e0ng Cao C\u1ea5p.\\n7.\u0110\u1ea1t c\u00e1c m\u1ed1c V\u00f2ng Th\u01b0\u1edfng t\u00edch l\u0169y s\u1ebd m\u1edf R\u01b0\u01a1ng B\u1eadc Th\u1ea7y Bi v\u1edbi ph\u1ea7n th\u01b0\u1edfng b\u1ed5 sung.\\n8.Khi s\u1ef1 ki\u1ec7n k\u1ebft th\u00fac, v\u1eadt ph\u1ea9m quay v\u00e0 \u0111\u1ed5i ch\u01b0a d\u00f9ng s\u1ebd \u0111\u01b0\u1ee3c chuy\u1ec3n th\u00e0nh T\u0103ng T\u1ed1c Hu\u1ea5n Luy\u1ec7n 15 ph\u00fat v\u00e0 1 ph\u00fat.'
rule_it = "1.Spendi Gettoni Estrazione per lanciare Biglie e ottenere ricompense di tappa e gettoni scambio.\\n2.Ogni volta che una Biglia colpisce un nodo ricompensa, la barra progresso si riempie. Completala per ottenere il premio. Una singola Biglia pu\u00f2 accumulare fino a 5 progressi (entrambi i lati).\\n3.Quando una Biglia cade in uno slot di scambio, ricevi i Gettoni Scambio corrispondenti.\\n4.Usa i Gettoni Scambio per riscattare ricompense nel Negozio Normale.\\n5.Dopo aver usato 50 Biglie normali in totale, si attiva un Round Bonus che concede 50 Biglie Bonus gratuite.\\n6.Nel Round Bonus, le Biglie che atterrano negli slot assegnano Biglietti Scambio Premium riscattabili nel Negozio Avanzato.\\n7.Raggiungere traguardi cumulativi di Round Bonus sblocca uno Scrigno Maestro delle Biglie con ricompense extra.\\n8.Al termine dell'evento, gli oggetti di estrazione e scambio non utilizzati vengono convertiti in Accelerazioni Addestramento da 15 min e 1 min."
rule_pl = '1.Wydaj \u017betony Losowania, aby wystrzeli\u0107 Kulki i zdoby\u0107 nagrody etapowe oraz \u017cetony wymiany.\\n2.Za ka\u017cdym razem, gdy Kulka trafi w w\u0119ze\u0142 nagrody, pasek post\u0119pu si\u0119 zape\u0142nia. Zape\u0142nij go, aby odebra\u0107 nagrod\u0119. Jedna Kulka mo\u017ce zgromadzi\u0107 do 5 post\u0119p\u00f3w (obie strony \u0142\u0105cznie).\\n3.Gdy Kulka wpada do slotu wymiany, otrzymujesz odpowiednie \u017betony Wymiany.\\n4.U\u017cyj \u017beton\u00f3w Wymiany, aby wymienia\u0107 nagrody w Sklepie Zwyk\u0142ym.\\n5.Po u\u017cyciu \u0142\u0105cznie 50 zwyk\u0142ych Kulek uruchamia si\u0119 Runda Bonusowa przyznaj\u0105ca 50 darmowych Kulek Bonusowych.\\n6.W Rundzie Bonusowej Kulki l\u0105duj\u0105ce w slotach daj\u0105 Bilety Wymiany Premium wymienialne w Sklepie Zaawansowanym.\\n7.Osi\u0105gni\u0119cie kumulatywnych kamieni milowych Rund Bonusowych odblokowuje Skrzyni\u0119 Mistrza Kulek z dodatkowymi nagrodami.\\n8.Po zako\u0144czeniu wydarzenia niewykorzystane przedmioty losowania i wymiany zostan\u0105 zamienione na Przyspieszenia Treningu 15 min i 1 min.'
rule_ar = '1.\u0623\u0646\u0641\u0642 \u0631\u0645\u0648\u0632 \u0627\u0644\u0633\u062d\u0628 \u0644\u0625\u0637\u0644\u0627\u0642 \u0627\u0644\u0643\u0631\u0627\u062a \u0648\u0627\u0644\u062d\u0635\u0648\u0644 \u0639\u0644\u0649 \u0645\u0643\u0627\u0641\u0622\u062a \u0627\u0644\u0645\u0631\u0627\u062d\u0644 \u0648\u0631\u0645\u0648\u0632 \u0627\u0644\u062a\u0628\u0627\u062f\u0644.\\n2.\u0641\u064a \u0643\u0644 \u0645\u0631\u0629 \u062a\u0635\u0637\u062f\u0645 \u0641\u064a\u0647\u0627 \u0643\u0631\u0629 \u0628\u0639\u0642\u062f\u0629 \u0645\u0643\u0627\u0641\u0623\u0629\u060c \u064a\u0645\u062a\u0644\u0626 \u0634\u0631\u064a\u0637 \u0627\u0644\u062a\u0642\u062f\u0645. \u0623\u0643\u0645\u0644\u0647 \u0644\u0644\u062d\u0635\u0648\u0644 \u0639\u0644\u0649 \u0627\u0644\u062c\u0627\u0626\u0632\u0629. \u064a\u0645\u0643\u0646 \u0644\u0643\u0631\u0629 \u0648\u0627\u062d\u062f\u0629 \u062a\u062c\u0645\u064a\u0639 \u062d\u062a\u0649 5 \u062a\u0642\u062f\u0645\u0627\u062a (\u0643\u0644\u0627 \u0627\u0644\u062c\u0627\u0646\u0628\u064a\u0646).\\n3.\u0639\u0646\u062f\u0645\u0627 \u062a\u0633\u0642\u0637 \u0643\u0631\u0629 \u0641\u064a \u0641\u062a\u062d\u0629 \u062a\u0628\u0627\u062f\u0644\u060c \u062a\u062d\u0635\u0644 \u0639\u0644\u0649 \u0631\u0645\u0648\u0632 \u0627\u0644\u062a\u0628\u0627\u062f\u0644 \u0627\u0644\u0645\u0642\u0627\u0628\u0644\u0629.\\n4.\u0627\u0633\u062a\u062e\u062f\u0645 \u0631\u0645\u0648\u0632 \u0627\u0644\u062a\u0628\u0627\u062f\u0644 \u0644\u0627\u0633\u062a\u0628\u062f\u0627\u0644 \u0627\u0644\u0645\u0643\u0627\u0641\u0622\u062a \u0641\u064a \u0627\u0644\u0645\u062a\u062c\u0631 \u0627\u0644\u0639\u0627\u062f\u064a.\\n5.\u0628\u0639\u062f \u0627\u0633\u062a\u062e\u062f\u0627\u0645 50 \u0643\u0631\u0629 \u0639\u0627\u062f\u064a\u0629 \u0625\u062c\u0645\u0627\u0644\u0627\u064b\u060c \u064a\u062a\u0645 \u062a\u0641\u0639\u064a\u0644 \u062c\u0648\u0644\u0629 \u0627\u0644\u0645\u0643\u0627\u0641\u0623\u0629 \u0645\u0639 50 \u0643\u0631\u0629 \u0645\u0643\u0627\u0641\u0623\u0629 \u0645\u062c\u0627\u0646\u064a\u0629.\\n6.\u0641\u064a \u062c\u0648\u0644\u0629 \u0627\u0644\u0645\u0643\u0627\u0641\u0623\u0629\u060c \u0627\u0644\u0643\u0631\u0627\u062a \u0627\u0644\u062a\u064a \u062a\u0647\u0628\u0637 \u0641\u064a \u0627\u0644\u0641\u062a\u062d\u0627\u062a \u062a\u0645\u0646\u062d \u062a\u0630\u0627\u0643\u0631 \u062a\u0628\u0627\u062f\u0644 \u0645\u0645\u062a\u0627\u0632\u0629 \u0642\u0627\u0628\u0644\u0629 \u0644\u0644\u0627\u0633\u062a\u0628\u062f\u0627\u0644 \u0641\u064a \u0627\u0644\u0645\u062a\u062c\u0631 \u0627\u0644\u0645\u062a\u0642\u062f\u0645.\\n7.\u0628\u0644\u0648\u063a \u0645\u0639\u0627\u0644\u0645 \u062c\u0648\u0644\u0627\u062a \u0627\u0644\u0645\u0643\u0627\u0641\u0623\u0629 \u0627\u0644\u062a\u0631\u0627\u0643\u0645\u064a\u0629 \u064a\u0641\u062a\u062d \u0635\u0646\u062f\u0648\u0642 \u0633\u064a\u062f \u0627\u0644\u0643\u0631\u0627\u062a \u0628\u0645\u0643\u0627\u0641\u0622\u062a \u0625\u0636\u0627\u0641\u064a\u0629.\\n8.\u0639\u0646\u062f \u0627\u0646\u062a\u0647\u0627\u0621 \u0627\u0644\u062d\u062f\u062b\u060c \u064a\u062a\u0645 \u062a\u062d\u0648\u064a\u0644 \u0639\u0646\u0627\u0635\u0631 \u0627\u0644\u0633\u062d\u0628 \u0648\u0627\u0644\u062a\u0628\u0627\u062f\u0644 \u063a\u064a\u0631 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645\u0629 \u0625\u0644\u0649 \u062a\u0633\u0631\u064a\u0639\u0627\u062a \u062a\u062f\u0631\u064a\u0628 15 \u062f\u0642\u064a\u0642\u0629 \u06481 \u062f\u0642\u064a\u0642\u0629.'
rule_jp = '1.抽選トークンを使ってマーブルを発射し、ステージ報酬と交換トークンを獲得します。\\n2.マーブルが報酬ノードに当たるたびにプログレスバーが溜まります。満タンにすると報酬を獲得できます。1つのマーブルで最大5回分のステージ報酬進捗を蓄積できます（両側合計）。\\n3.マーブルが交換スロットに落ちると、対応する交換トークンを受け取ります。\\n4.交換トークンを使って通常ショップで報酬と交換できます。\\n5.通常マーブルを合計50個使用すると、ボーナスラウンドが発動し、無料のボーナスマーブル50個が付与されます。\\n6.ボーナスラウンドでスロットに落ちたマーブルはプレミアム交換チケットを獲得でき、上級ショップで交換可能です。\\n7.ボーナスラウンドの累計マイルストーンに到達すると、マーブルマスターチェストが開放され、追加報酬を獲得できます。\\n8.イベント終了後、未使用の抽選・交換アイテムは15分訓練加速と1分訓練加速に変換されます。'
rule_kr = '1.뽑기 토큰을 사용하여 구슬을 발사하고 단계 보상과 교환 토큰을 획득하세요.\\n2.구슬이 보상 노드에 맞을 때마다 진행 바가 채워집니다. 가득 채우면 보상을 받을 수 있습니다. 구슬 하나당 최대 5회 단계 보상 진행도를 누적할 수 있습니다 (양쪽 합산).\\n3.구슬이 교환 슬롯에 떨어지면 해당 교환 토큰을 받습니다.\\n4.교환 토큰을 사용하여 일반 상점에서 보상을 교환하세요.\\n5.일반 구슬을 총 50개 사용하면 보너스 라운드가 발동되어 무료 보너스 구슬 50개가 지급됩니다.\\n6.보너스 라운드에서 슬롯에 떨어진 구슬은 고급 상점에서 교환 가능한 프리미엄 교환 티켓을 획득합니다.\\n7.보너스 라운드 누적 마일스톤에 도달하면 추가 보상이 담긴 구슬 마스터 상자가 열립니다.\\n8.이벤트 종료 시 미사용 뽑기 및 교환 아이템은 15분 훈련 가속과 1분 훈련 가속으로 전환됩니다.'

rule_row = [rule_cn, rule_en, rule_fr, rule_de, rule_po, rule_zh, rule_id, rule_th, rule_sp, rule_ru, rule_tr, rule_vi, rule_it, rule_pl, rule_ar, rule_jp, rule_kr, rule_cn]

# ── box name translations ──
box_name = ["ITEM", "marble_master_box_name",
    "弹珠大师宝箱", "Marble Master Chest", "Coffre Maître des Billes", "Murmel-Meister-Truhe",
    "Baú Mestre de Bolas", "彈珠大師寶箱", "Peti Master Kelereng", "กล่องสมบัติปรมาจารย์ลูกแก้ว",
    "Cofre Maestro de Canicas", "Сундук мастера шариков", "Bilye Ustası Sandığı", "Rương Bậc Thầy Bi",
    "Scrigno Maestro delle Biglie", "Skrzynia Mistrza Kulek", "صندوق سيد الكرات",
    "マーブルマスターチェスト", "구슬 마스터 상자", "弹珠大师宝箱"]

# ── box desc translations ──
box_desc = ["ITEM", "marble_master_box_desc",
    '在"庆典弹弹乐"活动中累计触发福利关卡获得的宝箱，开启可获得丰厚奖励。',
    'A chest earned by reaching cumulative Bonus Round milestones in "Festival Pinball". Open it for huge rewards.',
    'Un coffre obtenu en atteignant des jalons cumulés de Tours Bonus dans « Flipper du Festival ». Ouvrez-le pour des récompenses généreuses.',
    'Eine Truhe, die durch kumulative Bonusrunden-Meilensteine im \u201eFestival-Flipper\u201c verdient wird. Öffne sie für tolle Belohnungen.',
    'Um baú obtido ao alcançar marcos cumulativos de Rodadas Bônus no "Pinball do Festival". Abra para recompensas generosas.',
    '在「慶典彈彈樂」活動中累計觸發福利關卡獲得的寶箱，開啟可獲得豐厚獎勵。',
    'Peti yang diperoleh dengan mencapai milestone kumulatif Ronde Bonus di "Pinball Festival". Buka untuk hadiah besar.',
    'กล่องสมบัติที่ได้รับจากการถึงเป้าหมายรอบโบนัสสะสมใน "ปิงปองเทศกาล" เปิดเพื่อรับรางวัลมากมาย',
    'Un cofre obtenido al alcanzar hitos acumulativos de Rondas Bonus en "Pinball del Festival". Ábrelo para obtener grandes recompensas.',
    'Сундук, полученный за достижение кумулятивных вех бонусных раундов в «Фестивале пинбола». Откройте для щедрых наград.',
    '"Festival Pinball" etkinliğinde kümülatif Bonus Tur kilometre taşlarına ulaşarak kazanılan sandık. Büyük ödüller için açın.',
    'Rương nhận được khi đạt các mốc Vòng Thưởng tích lũy trong "Lễ Hội Pinball". Mở để nhận phần thưởng hậu hĩnh.',
    'Uno scrigno ottenuto raggiungendo traguardi cumulativi di Round Bonus nel "Flipper del Festival". Aprilo per ricche ricompense.',
    'Skrzynia zdobyta poprzez osiągnięcie kumulatywnych kamieni milowych Rund Bonusowych w "Festiwalowym Pinballu". Otwórz po bogate nagrody.',
    'صندوق يتم الحصول عليه من خلال بلوغ معالم جولات المكافأة التراكمية في "بينبول المهرجان". افتحه للحصول على مكافآت سخية.',
    '「フェスティバルピンボール」でボーナスラウンドの累計マイルストーンに到達して獲得したチェスト。開けると豪華報酬を獲得できます。',
    '"축제 핀볼"에서 보너스 라운드 누적 마일스톤에 도달하여 획득한 상자입니다. 열어서 풍성한 보상을 받으세요.',
    '在"庆典弹弹乐"活动中累计触发福利关卡获得的宝箱，开启可获得丰厚奖励。']

def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    # 1. Direct update rule in EVENT row 7380 (keep key, replace cn~cns = cols C~T)
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="'EVENT'!C7380:T7380",
        valueInputOption="RAW",
        body={"values": [rule_row]},
    ).execute()
    print("✅ Rule updated: EVENT row 7380 (2025anni_marble_gacha_rule)")

    # 2. Write box name + desc to staging
    ROWS = [box_name, box_desc]

    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()

    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": staging_sheet_id,
                    "startRowIndex": next_row - 1,
                    "endRowIndex": end_row,
                    "startColumnIndex": 0, "endColumnIndex": 1,
                },
                "cell": {
                    "dataValidation": {"condition": {"type": "BOOLEAN"}, "strict": True},
                    "userEnteredValue": {"boolValue": False},
                },
                "fields": "dataValidation,userEnteredValue",
            }
        }]},
    ).execute()

    print(f"✅ Staging: marble_master_box_name + _desc written to rows {next_row}-{end_row}")
    print("Done!")

if __name__ == "__main__":
    main()
